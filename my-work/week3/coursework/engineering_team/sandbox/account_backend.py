import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, List, Any

def get_share_price(symbol: str) -> float:
    prices = {
        "AAPL": 150.00,
        "TSLA": 250.00,
        "GOOGL": 2800.00,
    }
    normalized = symbol.strip().upper()
    if normalized not in prices:
        raise ValueError(f"Unsupported symbol: {symbol}")
    return prices[normalized]

def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"

def validate_positive_amount(amount: float, field_name: str = "amount") -> None:
    if amount <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")

def validate_non_negative_amount(amount: float, field_name: str = "amount") -> None:
    if amount < 0:
        raise ValueError(f"{field_name} cannot be negative.")

def validate_positive_quantity(quantity: int) -> None:
    if not isinstance(quantity, int) or quantity <= 0:
        raise ValueError("Quantity must be an integer greater than zero.")

def normalize_symbol(symbol: str) -> str:
    if not symbol or not str(symbol).strip():
        raise ValueError("Symbol cannot be empty.")
    return str(symbol).strip().upper()

@dataclass
class Transaction:
    transaction_id: str
    timestamp: datetime
    transaction_type: str
    symbol: Optional[str]
    quantity: Optional[int]
    price: Optional[float]
    amount: float
    cash_balance_after: float
    description: str

def create_transaction(
    transaction_type: str,
    symbol: Optional[str],
    quantity: Optional[int],
    price: Optional[float],
    amount: float,
    cash_balance_after: float,
    description: str,
) -> Transaction:
    return Transaction(
        transaction_id=generate_id("txn"),
        timestamp=datetime.now(),
        transaction_type=transaction_type,
        symbol=symbol,
        quantity=quantity,
        price=price,
        amount=amount,
        cash_balance_after=cash_balance_after,
        description=description,
    )

@dataclass
class Account:
    account_id: str
    owner_name: str
    cash_balance: float
    total_deposited: float
    holdings: Dict[str, int]
    transactions: List[Transaction]
    created_at: datetime

class AccountService:
    def __init__(self) -> None:
        self.account: Optional[Account] = None

    def create_account(self, owner_name: str, initial_deposit: float) -> Account:
        if not owner_name or not str(owner_name).strip():
            raise ValueError("Owner name cannot be empty.")
        validate_non_negative_amount(initial_deposit, "initial deposit")
        
        self.account = Account(
            account_id=generate_id("acct"),
            owner_name=str(owner_name).strip(),
            cash_balance=float(initial_deposit),
            total_deposited=float(initial_deposit),
            holdings={},
            transactions=[],
            created_at=datetime.now(),
        )
        
        txn = create_transaction(
            transaction_type="CREATE_ACCOUNT",
            symbol=None,
            quantity=None,
            price=None,
            amount=float(initial_deposit),
            cash_balance_after=float(initial_deposit),
            description=f"Account created with initial deposit of {initial_deposit}",
        )
        self.account.transactions.append(txn)
        
        return self.account

    def get_account(self) -> Account:
        if not self.account:
            raise ValueError("No account has been created.")
        return self.account

    def deposit(self, amount: float) -> Account:
        account = self.get_account()
        validate_positive_amount(amount)
        
        account.cash_balance += float(amount)
        account.total_deposited += float(amount)
        
        txn = create_transaction(
            transaction_type="DEPOSIT",
            symbol=None,
            quantity=None,
            price=None,
            amount=float(amount),
            cash_balance_after=account.cash_balance,
            description=f"Deposited {amount}",
        )
        account.transactions.append(txn)
        
        return account

    def withdraw(self, amount: float) -> Account:
        account = self.get_account()
        validate_positive_amount(amount)
        
        if amount > account.cash_balance:
            raise ValueError("Insufficient cash balance.")
            
        account.cash_balance -= float(amount)
        
        # Policy: Withdrawals decrease total_deposited, but not below zero
        account.total_deposited = max(0.0, account.total_deposited - float(amount))
        
        txn = create_transaction(
            transaction_type="WITHDRAW",
            symbol=None,
            quantity=None,
            price=None,
            amount=float(amount),
            cash_balance_after=account.cash_balance,
            description=f"Withdrew {amount}",
        )
        account.transactions.append(txn)
        
        return account

    def buy(self, symbol: str, quantity: int) -> Account:
        account = self.get_account()
        norm_symbol = normalize_symbol(symbol)
        validate_positive_quantity(quantity)
        
        price = get_share_price(norm_symbol)
        total_cost = price * quantity
        
        if total_cost > account.cash_balance:
            raise ValueError("Insufficient cash balance.")
            
        account.cash_balance -= total_cost
        account.holdings[norm_symbol] = account.holdings.get(norm_symbol, 0) + quantity
        
        txn = create_transaction(
            transaction_type="BUY",
            symbol=norm_symbol,
            quantity=quantity,
            price=price,
            amount=total_cost,
            cash_balance_after=account.cash_balance,
            description=f"Bought {quantity} shares of {norm_symbol} at {price}",
        )
        account.transactions.append(txn)
        
        return account

    def sell(self, symbol: str, quantity: int) -> Account:
        account = self.get_account()
        norm_symbol = normalize_symbol(symbol)
        validate_positive_quantity(quantity)
        
        if norm_symbol not in account.holdings or account.holdings[norm_symbol] < quantity:
            raise ValueError("Insufficient shares to sell.")
            
        price = get_share_price(norm_symbol)
        total_value = price * quantity
        
        account.cash_balance += total_value
        account.holdings[norm_symbol] -= quantity
        
        if account.holdings[norm_symbol] == 0:
            del account.holdings[norm_symbol]
            
        txn = create_transaction(
            transaction_type="SELL",
            symbol=norm_symbol,
            quantity=quantity,
            price=price,
            amount=total_value,
            cash_balance_after=account.cash_balance,
            description=f"Sold {quantity} shares of {norm_symbol} at {price}",
        )
        account.transactions.append(txn)
        
        return account

    def get_holdings(self) -> Dict[str, int]:
        account = self.get_account()
        return dict(account.holdings)

    def get_holdings_report(self) -> List[Dict[str, Any]]:
        account = self.get_account()
        report = []
        for symbol, quantity in account.holdings.items():
            price = get_share_price(symbol)
            report.append({
                "symbol": symbol,
                "quantity": quantity,
                "current_price": price,
                "market_value": price * quantity,
            })
        return report

    def get_transactions(self) -> List[Transaction]:
        account = self.get_account()
        return list(account.transactions)

    def get_transactions_report(self) -> List[Dict[str, Any]]:
        account = self.get_account()
        report = []
        for txn in account.transactions:
            report.append({
                "timestamp": txn.timestamp.isoformat(sep=" ", timespec="seconds"),
                "type": txn.transaction_type,
                "symbol": txn.symbol if txn.symbol is not None else "",
                "quantity": txn.quantity if txn.quantity is not None else "",
                "price": txn.price if txn.price is not None else "",
                "amount": txn.amount,
                "cash_balance_after": txn.cash_balance_after,
                "description": txn.description,
            })
        return report

    def get_cash_balance(self) -> float:
        return self.get_account().cash_balance

    def calculate_holdings_value(self) -> float:
        account = self.get_account()
        total = 0.0
        for symbol, quantity in account.holdings.items():
            total += get_share_price(symbol) * quantity
        return total

    def calculate_portfolio_value(self) -> float:
        return self.get_cash_balance() + self.calculate_holdings_value()

    def calculate_profit_loss(self) -> float:
        account = self.get_account()
        return self.calculate_portfolio_value() - account.total_deposited

    def get_account_summary(self) -> Dict[str, Any]:
        account = self.get_account()
        return {
            "account_id": account.account_id,
            "owner_name": account.owner_name,
            "cash_balance": account.cash_balance,
            "holdings_value": self.calculate_holdings_value(),
            "portfolio_value": self.calculate_portfolio_value(),
            "total_deposited": account.total_deposited,
            "profit_loss": self.calculate_profit_loss(),
            "created_at": account.created_at.isoformat(sep=" ", timespec="seconds"),
        }
