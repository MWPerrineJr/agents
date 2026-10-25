import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Callable


class AccountError(Exception):
    pass


class AccountNotFoundError(AccountError):
    pass


class ValidationError(AccountError):
    pass


class InsufficientFundsError(AccountError):
    pass


class InsufficientSharesError(AccountError):
    pass


class UnknownSymbolError(AccountError):
    pass


def get_share_price(symbol: str) -> Decimal:
    prices = {
        "AAPL": Decimal("150.00"),
        "TSLA": Decimal("250.00"),
        "GOOGL": Decimal("2800.00"),
    }
    normalized = symbol.upper()
    if normalized not in prices:
        raise UnknownSymbolError(f"Unsupported symbol: {symbol}")
    return prices[normalized]


class TransactionType(Enum):
    CREATE_ACCOUNT = "CREATE_ACCOUNT"
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True)
class Transaction:
    transaction_id: str
    account_id: str
    transaction_type: TransactionType
    timestamp: datetime
    symbol: str | None
    quantity: int | None
    price: Decimal | None
    cash_amount: Decimal
    cash_balance_after: Decimal
    description: str


@dataclass
class Account:
    account_id: str
    owner_name: str
    created_at: datetime
    initial_deposit: Decimal
    cash_balance: Decimal
    holdings: dict[str, int]
    transactions: list[Transaction]


@dataclass(frozen=True)
class HoldingReportRow:
    symbol: str
    quantity: int
    current_price: Decimal
    market_value: Decimal


@dataclass(frozen=True)
class PortfolioSummary:
    account_id: str
    owner_name: str
    cash_balance: Decimal
    holdings_value: Decimal
    total_value: Decimal
    initial_deposit: Decimal
    net_cash_contributions: Decimal
    profit_loss_from_initial_deposit: Decimal
    profit_loss_excluding_cash_flows: Decimal


class AccountService:
    def __init__(self, price_lookup: Callable[[str], Decimal] | None = None) -> None:
        self.price_lookup = price_lookup or get_share_price
        self._accounts: dict[str, Account] = {}

    def _normalize_symbol(self, symbol: str) -> str:
        return symbol.strip().upper()

    def _normalize_money(self, amount: Decimal | int | float | str) -> Decimal:
        try:
            return Decimal(str(amount))
        except InvalidOperation:
            raise ValidationError(f"Invalid monetary amount: {amount}")

    def _validate_positive_money(self, amount: Decimal, field_name: str) -> None:
        if amount <= Decimal("0"):
            raise ValidationError(f"{field_name} must be greater than zero.")

    def _validate_positive_quantity(self, quantity: int) -> None:
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValidationError("Quantity must be a positive integer.")

    def _get_account_or_raise(self, account_id: str) -> Account:
        if account_id not in self._accounts:
            raise AccountNotFoundError(f"Account '{account_id}' not found.")
        return self._accounts[account_id]

    def _new_transaction_id(self) -> str:
        return str(uuid.uuid4())

    def _utc_now(self) -> datetime:
        return datetime.now(timezone.utc)

    def _record_transaction(
        self,
        account: Account,
        transaction_type: TransactionType,
        symbol: str | None,
        quantity: int | None,
        price: Decimal | None,
        cash_amount: Decimal,
        description: str,
    ) -> Transaction:
        account.cash_balance += cash_amount
        tx = Transaction(
            transaction_id=self._new_transaction_id(),
            account_id=account.account_id,
            transaction_type=transaction_type,
            timestamp=self._utc_now(),
            symbol=symbol,
            quantity=quantity,
            price=price,
            cash_amount=cash_amount,
            cash_balance_after=account.cash_balance,
            description=description,
        )
        account.transactions.append(tx)
        return tx

    def create_account(self, owner_name: str, initial_deposit: Decimal | int | float | str) -> Account:
        if not owner_name or not str(owner_name).strip():
            raise ValidationError("Owner name must not be blank.")
        
        deposit_dec = self._normalize_money(initial_deposit)
        self._validate_positive_money(deposit_dec, "Initial deposit")

        account_id = str(uuid.uuid4())
        account = Account(
            account_id=account_id,
            owner_name=owner_name.strip(),
            created_at=self._utc_now(),
            initial_deposit=deposit_dec,
            cash_balance=Decimal("0"),
            holdings={},
            transactions=[],
        )
        self._accounts[account_id] = account

        self._record_transaction(
            account=account,
            transaction_type=TransactionType.CREATE_ACCOUNT,
            symbol=None,
            quantity=None,
            price=None,
            cash_amount=deposit_dec,
            description="Account created with initial deposit",
        )
        return account

    def get_account(self, account_id: str) -> Account:
        return self._get_account_or_raise(account_id)

    def list_accounts(self) -> list[Account]:
        return list(self._accounts.values())

    def deposit(self, account_id: str, amount: Decimal | int | float | str) -> Transaction:
        account = self._get_account_or_raise(account_id)
        amount_dec = self._normalize_money(amount)
        self._validate_positive_money(amount_dec, "Deposit amount")

        return self._record_transaction(
            account=account,
            transaction_type=TransactionType.DEPOSIT,
            symbol=None,
            quantity=None,
            price=None,
            cash_amount=amount_dec,
            description="Deposit",
        )

    def withdraw(self, account_id: str, amount: Decimal | int | float | str) -> Transaction:
        account = self._get_account_or_raise(account_id)
        amount_dec = self._normalize_money(amount)
        self._validate_positive_money(amount_dec, "Withdrawal amount")

        if amount_dec > account.cash_balance:
            raise InsufficientFundsError("Withdrawal amount exceeds available cash balance.")

        return self._record_transaction(
            account=account,
            transaction_type=TransactionType.WITHDRAW,
            symbol=None,
            quantity=None,
            price=None,
            cash_amount=-amount_dec,
            description="Withdrawal",
        )

    def buy_shares(self, account_id: str, symbol: str, quantity: int) -> Transaction:
        account = self._get_account_or_raise(account_id)
        symbol = self._normalize_symbol(symbol)
        self._validate_positive_quantity(quantity)

        price = self.price_lookup(symbol)
        total_cost = price * quantity

        if total_cost > account.cash_balance:
            raise InsufficientFundsError("Insufficient funds to buy shares.")

        account.holdings[symbol] = account.holdings.get(symbol, 0) + quantity

        return self._record_transaction(
            account=account,
            transaction_type=TransactionType.BUY,
            symbol=symbol,
            quantity=quantity,
            price=price,
            cash_amount=-total_cost,
            description=f"Bought {quantity} shares of {symbol}",
        )

    def sell_shares(self, account_id: str, symbol: str, quantity: int) -> Transaction:
        account = self._get_account_or_raise(account_id)
        symbol = self._normalize_symbol(symbol)
        self._validate_positive_quantity(quantity)

        held_quantity = account.holdings.get(symbol, 0)
        if quantity > held_quantity:
            raise InsufficientSharesError("Selling more shares than currently held.")

        price = self.price_lookup(symbol)
        proceeds = price * quantity

        account.holdings[symbol] -= quantity
        if account.holdings[symbol] == 0:
            del account.holdings[symbol]

        return self._record_transaction(
            account=account,
            transaction_type=TransactionType.SELL,
            symbol=symbol,
            quantity=quantity,
            price=price,
            cash_amount=proceeds,
            description=f"Sold {quantity} shares of {symbol}",
        )

    def get_holdings(self, account_id: str) -> dict[str, int]:
        account = self._get_account_or_raise(account_id)
        return dict(account.holdings)

    def get_holdings_report(self, account_id: str) -> list[HoldingReportRow]:
        account = self._get_account_or_raise(account_id)
        report = []
        for symbol, quantity in account.holdings.items():
            if quantity > 0:
                current_price = self.price_lookup(symbol)
                market_value = current_price * quantity
                report.append(HoldingReportRow(
                    symbol=symbol,
                    quantity=quantity,
                    current_price=current_price,
                    market_value=market_value,
                ))
        return report

    def get_holdings_at(
        self,
        account_id: str,
        as_of: datetime | None = None,
        transaction_id: str | None = None,
    ) -> dict[str, int]:
        account = self._get_account_or_raise(account_id)
        if as_of is not None and transaction_id is not None:
            raise ValidationError("Provide either as_of or transaction_id, not both.")
        
        if as_of is None and transaction_id is None:
            return dict(account.holdings)
            
        if transaction_id is not None:
            if not any(tx.transaction_id == transaction_id for tx in account.transactions):
                raise ValidationError("Transaction ID not found for this account.")
                
        holdings: dict[str, int] = {}
        for tx in account.transactions:
            if as_of is not None and tx.timestamp > as_of:
                break
                
            if tx.transaction_type == TransactionType.BUY:
                if tx.symbol and tx.quantity is not None:
                    holdings[tx.symbol] = holdings.get(tx.symbol, 0) + tx.quantity
            elif tx.transaction_type == TransactionType.SELL:
                if tx.symbol and tx.quantity is not None:
                    holdings[tx.symbol] -= tx.quantity
                    if holdings[tx.symbol] == 0:
                        del holdings[tx.symbol]
                        
            if transaction_id is not None and tx.transaction_id == transaction_id:
                break
                
        return {sym: qty for sym, qty in holdings.items() if qty > 0}

    def list_transactions(self, account_id: str) -> list[Transaction]:
        account = self._get_account_or_raise(account_id)
        return list(account.transactions)

    def list_transactions_by_type(
        self,
        account_id: str,
        transaction_type: TransactionType,
    ) -> list[Transaction]:
        account = self._get_account_or_raise(account_id)
        return [tx for tx in account.transactions if tx.transaction_type == transaction_type]

    def calculate_holdings_value(self, account_id: str) -> Decimal:
        account = self._get_account_or_raise(account_id)
        value = Decimal("0")
        for symbol, quantity in account.holdings.items():
            if quantity > 0:
                value += self.price_lookup(symbol) * quantity
        return value

    def calculate_total_value(self, account_id: str) -> Decimal:
        account = self._get_account_or_raise(account_id)
        return account.cash_balance + self.calculate_holdings_value(account_id)

    def calculate_net_cash_contributions(self, account_id: str) -> Decimal:
        account = self._get_account_or_raise(account_id)
        net_cash = Decimal("0")
        for tx in account.transactions:
            if tx.transaction_type in (TransactionType.CREATE_ACCOUNT, TransactionType.DEPOSIT):
                net_cash += tx.cash_amount
            elif tx.transaction_type == TransactionType.WITHDRAW:
                net_cash += tx.cash_amount  # Withdrawals are negative cash_amount
        return net_cash

    def calculate_profit_loss_from_initial_deposit(self, account_id: str) -> Decimal:
        account = self._get_account_or_raise(account_id)
        return self.calculate_total_value(account_id) - account.initial_deposit

    def calculate_profit_loss_excluding_cash_flows(self, account_id: str) -> Decimal:
        return self.calculate_total_value(account_id) - self.calculate_net_cash_contributions(account_id)

    def get_portfolio_summary(self, account_id: str) -> PortfolioSummary:
        account = self._get_account_or_raise(account_id)
        holdings_value = self.calculate_holdings_value(account_id)
        total_value = account.cash_balance + holdings_value
        net_cash = self.calculate_net_cash_contributions(account_id)
        
        return PortfolioSummary(
            account_id=account.account_id,
            owner_name=account.owner_name,
            cash_balance=account.cash_balance,
            holdings_value=holdings_value,
            total_value=total_value,
            initial_deposit=account.initial_deposit,
            net_cash_contributions=net_cash,
            profit_loss_from_initial_deposit=total_value - account.initial_deposit,
            profit_loss_excluding_cash_flows=total_value - net_cash,
        )


def format_money(amount: Decimal) -> str:
    if amount < 0:
        return f"-${-amount:,.2f}"
    return f"${amount:,.2f}"


def transaction_to_row(transaction: Transaction) -> list[str]:
    # Timestamp, Type, Symbol, Quantity, Price, Cash Amount, Cash Balance After, Description, Transaction ID
    return [
        transaction.timestamp.isoformat(),
        transaction.transaction_type.value,
        transaction.symbol or "",
        str(transaction.quantity) if transaction.quantity is not None else "",
        format_money(transaction.price) if transaction.price is not None else "",
        format_money(transaction.cash_amount),
        format_money(transaction.cash_balance_after),
        transaction.description,
        transaction.transaction_id,
    ]


def holding_report_row_to_row(row: HoldingReportRow) -> list[str]:
    # Symbol, Quantity, Current Price, Market Value
    return [
        row.symbol,
        str(row.quantity),
        format_money(row.current_price),
        format_money(row.market_value),
    ]


def portfolio_summary_to_rows(summary: PortfolioSummary) -> list[list[str]]:
    return [
        ["Cash Balance", format_money(summary.cash_balance)],
        ["Holdings Value", format_money(summary.holdings_value)],
        ["Total Account Value", format_money(summary.total_value)],
        ["Initial Deposit", format_money(summary.initial_deposit)],
        ["Net Cash Contributions", format_money(summary.net_cash_contributions)],
        ["P/L From Initial Deposit", format_money(summary.profit_loss_from_initial_deposit)],
        ["P/L Excluding Cash Flows", format_money(summary.profit_loss_excluding_cash_flows)],
    ]
