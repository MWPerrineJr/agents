from dataclasses import dataclass, field
from datetime import datetime
from copy import deepcopy

SUPPORTED_SYMBOLS = ("AAPL", "TSLA", "GOOGL")
DEFAULT_PRICES = {
    "AAPL": 150.00,
    "TSLA": 250.00,
    "GOOGL": 2800.00
}

class AccountError(Exception):
    """Base exception for account management errors."""

class AccountNotFoundError(AccountError):
    """Raised when an account id is not found."""

class DuplicateAccountError(AccountError):
    """Raised when trying to create an account that already exists."""

class ValidationError(AccountError):
    """Raised when an operation is invalid."""

class InsufficientFundsError(AccountError):
    """Raised when cash balance is insufficient."""

class InsufficientSharesError(AccountError):
    """Raised when share holdings are insufficient."""

class UnknownSymbolError(AccountError):
    """Raised when a share symbol is not supported."""

@dataclass
class Transaction:
    transaction_id: int
    timestamp: datetime
    account_id: str
    transaction_type: str
    amount: float | None = None
    symbol: str | None = None
    quantity: int | None = None
    price: float | None = None
    cash_balance_after: float = 0.0

TRANSACTION_DEPOSIT = "DEPOSIT"
TRANSACTION_WITHDRAW = "WITHDRAW"
TRANSACTION_BUY = "BUY"
TRANSACTION_SELL = "SELL"

@dataclass
class Account:
    account_id: str
    cash_balance: float = 0.0
    total_deposited: float = 0.0
    holdings: dict[str, int] = field(default_factory=dict)
    transactions: list[Transaction] = field(default_factory=list)

def get_share_price(symbol: str) -> float:
    """
    Return the current fixed share price for a supported symbol.
    """
    symbol = symbol.upper().strip()
    if symbol not in DEFAULT_PRICES:
        raise UnknownSymbolError(f"Unsupported symbol: {symbol}")
    return DEFAULT_PRICES[symbol]

class AccountService:
    def __init__(self) -> None:
        self._accounts: dict[str, Account] = {}
        self._next_transaction_id: int = 1

    def create_account(self, account_id: str, initial_deposit: float = 0.0) -> Account:
        account_id = self._validate_account_id(account_id)
        if initial_deposit < 0:
            raise ValidationError("Initial deposit must not be negative.")
        if account_id in self._accounts:
            raise DuplicateAccountError(f"Account '{account_id}' already exists.")
        
        account = Account(account_id=account_id)
        self._accounts[account_id] = account
        
        if initial_deposit > 0:
            account.cash_balance += initial_deposit
            account.total_deposited += initial_deposit
            self._record_transaction(
                account=account,
                transaction_type=TRANSACTION_DEPOSIT,
                amount=initial_deposit
            )
        
        return account

    def get_account(self, account_id: str) -> Account:
        account_id = account_id.strip()
        if account_id not in self._accounts:
            raise AccountNotFoundError(f"Account '{account_id}' was not found.")
        return self._accounts[account_id]

    def list_accounts(self) -> list[str]:
        return sorted(self._accounts.keys())

    def deposit(self, account_id: str, amount: float) -> Account:
        account = self.get_account(account_id)
        amount = self._validate_positive_amount(amount, "Deposit amount")
        
        account.cash_balance += amount
        account.total_deposited += amount
        self._record_transaction(
            account=account,
            transaction_type=TRANSACTION_DEPOSIT,
            amount=amount
        )
        return account

    def withdraw(self, account_id: str, amount: float) -> Account:
        account = self.get_account(account_id)
        amount = self._validate_positive_amount(amount, "Withdrawal amount")
        
        if account.cash_balance < amount:
            raise InsufficientFundsError("Insufficient funds.")
            
        account.cash_balance -= amount
        self._record_transaction(
            account=account,
            transaction_type=TRANSACTION_WITHDRAW,
            amount=amount
        )
        return account

    def buy_shares(self, account_id: str, symbol: str, quantity: int) -> Account:
        account = self.get_account(account_id)
        symbol = self._normalize_symbol(symbol)
        quantity = self._validate_positive_quantity(quantity)
        
        price = get_share_price(symbol)
        total_cost = price * quantity
        
        if account.cash_balance < total_cost:
            raise InsufficientFundsError("Insufficient funds.")
            
        account.cash_balance -= total_cost
        account.holdings[symbol] = account.holdings.get(symbol, 0) + quantity
        
        self._record_transaction(
            account=account,
            transaction_type=TRANSACTION_BUY,
            symbol=symbol,
            quantity=quantity,
            price=price
        )
        return account

    def sell_shares(self, account_id: str, symbol: str, quantity: int) -> Account:
        account = self.get_account(account_id)
        symbol = self._normalize_symbol(symbol)
        quantity = self._validate_positive_quantity(quantity)
        
        if account.holdings.get(symbol, 0) < quantity:
            raise InsufficientSharesError("Insufficient shares.")
            
        price = get_share_price(symbol)
        total_revenue = price * quantity
        
        account.cash_balance += total_revenue
        account.holdings[symbol] -= quantity
        
        if account.holdings[symbol] == 0:
            del account.holdings[symbol]
            
        self._record_transaction(
            account=account,
            transaction_type=TRANSACTION_SELL,
            symbol=symbol,
            quantity=quantity,
            price=price
        )
        return account

    def get_cash_balance(self, account_id: str) -> float:
        account = self.get_account(account_id)
        return account.cash_balance

    def get_holdings(self, account_id: str) -> dict[str, int]:
        account = self.get_account(account_id)
        return dict(account.holdings)

    def get_transactions(self, account_id: str) -> list[Transaction]:
        account = self.get_account(account_id)
        return list(account.transactions)

    def get_holdings_report(self, account_id: str) -> list[dict[str, object]]:
        account = self.get_account(account_id)
        report = []
        for symbol, quantity in account.holdings.items():
            price = get_share_price(symbol)
            report.append({
                "symbol": symbol,
                "quantity": quantity,
                "current_price": price,
                "market_value": price * quantity
            })
        return report

    def get_transactions_report(self, account_id: str) -> list[dict[str, object]]:
        account = self.get_account(account_id)
        report = []
        for t in account.transactions:
            report.append({
                "transaction_id": t.transaction_id,
                "timestamp": t.timestamp.isoformat(),
                "transaction_type": t.transaction_type,
                "amount": t.amount,
                "symbol": t.symbol,
                "quantity": t.quantity,
                "price": t.price,
                "cash_balance_after": t.cash_balance_after
            })
        return report

    def get_portfolio_value(self, account_id: str) -> float:
        account = self.get_account(account_id)
        holdings_value = sum(quantity * get_share_price(symbol) for symbol, quantity in account.holdings.items())
        return account.cash_balance + holdings_value

    def get_profit_loss(self, account_id: str) -> float:
        account = self.get_account(account_id)
        portfolio_value = self.get_portfolio_value(account_id)
        return portfolio_value - account.total_deposited

    def get_account_summary(self, account_id: str) -> dict[str, float | str]:
        account = self.get_account(account_id)
        portfolio_value = self.get_portfolio_value(account_id)
        holdings_value = portfolio_value - account.cash_balance
        profit_loss = portfolio_value - account.total_deposited
        
        return {
            "account_id": account.account_id,
            "cash_balance": account.cash_balance,
            "holdings_value": holdings_value,
            "portfolio_value": portfolio_value,
            "total_deposited": account.total_deposited,
            "profit_loss": profit_loss
        }

    def _validate_account_id(self, account_id: str) -> str:
        if not account_id:
            raise ValidationError("Account ID must not be blank.")
        account_id = account_id.strip()
        if not account_id:
            raise ValidationError("Account ID must not be blank.")
        return account_id

    def _validate_positive_amount(self, amount: float, field_name: str = "amount") -> float:
        if amount <= 0:
            raise ValidationError(f"{field_name} must be greater than zero.")
        return float(amount)

    def _validate_positive_quantity(self, quantity: int) -> int:
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValidationError("Quantity must be an integer greater than zero.")
        return quantity

    def _normalize_symbol(self, symbol: str) -> str:
        if not symbol or not symbol.strip():
            raise ValidationError("Symbol must not be blank.")
        symbol = symbol.upper().strip()
        if symbol not in DEFAULT_PRICES:
            raise UnknownSymbolError(f"Unsupported symbol: {symbol}")
        return symbol

    def _record_transaction(
        self,
        account: Account,
        transaction_type: str,
        amount: float | None = None,
        symbol: str | None = None,
        quantity: int | None = None,
        price: float | None = None,
    ) -> Transaction:
        transaction = Transaction(
            transaction_id=self._next_transaction_id,
            timestamp=datetime.now(),
            account_id=account.account_id,
            transaction_type=transaction_type,
            amount=amount,
            symbol=symbol,
            quantity=quantity,
            price=price,
            cash_balance_after=account.cash_balance
        )
        self._next_transaction_id += 1
        account.transactions.append(transaction)
        return transaction
