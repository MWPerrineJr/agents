from dataclasses import dataclass
from datetime import datetime

SUPPORTED_SYMBOLS: tuple[str, ...] = ("AAPL", "TSLA", "GOOGL")


def normalize_symbol(symbol: str) -> str:
    if not isinstance(symbol, str):
        raise ValueError("Symbol must be a string.")
    normalized = symbol.strip().upper()
    if not normalized:
        raise ValueError("Symbol cannot be empty.")
    return normalized


def get_share_price(symbol: str) -> float:
    symbol = normalize_symbol(symbol)
    if symbol == "AAPL":
        return 150.00
    elif symbol == "TSLA":
        return 250.00
    elif symbol == "GOOGL":
        return 2800.00
    else:
        raise ValueError(f"Unsupported symbol: {symbol}.")


def validate_positive_amount(amount: float, field_name: str = "amount") -> None:
    if amount <= 0:
        raise ValueError(f"{field_name.capitalize()} must be greater than zero.")


def validate_positive_quantity(quantity: int) -> None:
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        raise ValueError("Quantity must be a positive integer.")
    if quantity <= 0:
        raise ValueError("Quantity must be a positive integer.")


@dataclass
class Transaction:
    transaction_id: int
    timestamp: datetime
    transaction_type: str
    symbol: str | None
    quantity: int | None
    price: float | None
    amount: float
    cash_balance_after: float


@dataclass
class Holding:
    symbol: str
    quantity: int
    current_price: float
    market_value: float


@dataclass
class PortfolioSummary:
    account_id: str
    cash_balance: float
    holdings_value: float
    total_portfolio_value: float
    total_deposits: float
    total_withdrawals: float
    net_contributions: float
    profit_loss: float


class Account:
    def __init__(self, account_id: str, initial_deposit: float) -> None:
        if not isinstance(account_id, str) or not account_id.strip():
            raise ValueError("Account ID is required.")
        if initial_deposit < 0:
            raise ValueError("Initial deposit cannot be negative.")
        
        self.account_id = account_id.strip()
        self.initial_deposit = float(initial_deposit)
        self.cash_balance = float(initial_deposit)
        self.total_deposits = float(initial_deposit)
        self.total_withdrawals = 0.0
        self.holdings: dict[str, int] = {}
        self.transactions: list[Transaction] = []
        self._next_transaction_id = 1
        
        self._record_transaction(
            transaction_type="CREATE_ACCOUNT",
            amount=self.initial_deposit,
        )

    def deposit(self, amount: float) -> Transaction:
        validate_positive_amount(amount, "Amount")
        self.cash_balance += float(amount)
        self.total_deposits += float(amount)
        return self._record_transaction("DEPOSIT", float(amount))

    def withdraw(self, amount: float) -> Transaction:
        validate_positive_amount(amount, "Amount")
        if amount > self.cash_balance:
            raise ValueError("Insufficient cash balance.")
        self.cash_balance -= float(amount)
        self.total_withdrawals += float(amount)
        return self._record_transaction("WITHDRAW", float(amount))

    def buy(self, symbol: str, quantity: int) -> Transaction:
        symbol = normalize_symbol(symbol)
        if symbol not in SUPPORTED_SYMBOLS:
            raise ValueError(f"Unsupported symbol: {symbol}.")
        validate_positive_quantity(quantity)
        
        price = get_share_price(symbol)
        total_cost = price * quantity
        
        if total_cost > self.cash_balance:
            raise ValueError(f"Insufficient cash to buy {quantity} shares of {symbol}.")
            
        self.cash_balance -= total_cost
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        
        return self._record_transaction(
            transaction_type="BUY",
            amount=total_cost,
            symbol=symbol,
            quantity=quantity,
            price=price
        )

    def sell(self, symbol: str, quantity: int) -> Transaction:
        symbol = normalize_symbol(symbol)
        if symbol not in SUPPORTED_SYMBOLS:
            raise ValueError(f"Unsupported symbol: {symbol}.")
        validate_positive_quantity(quantity)
        
        current_quantity = self.holdings.get(symbol, 0)
        if quantity > current_quantity:
            raise ValueError(f"Cannot sell {quantity} shares of {symbol}; only {current_quantity} held.")
            
        price = get_share_price(symbol)
        proceeds = price * quantity
        
        self.cash_balance += proceeds
        self.holdings[symbol] -= quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
            
        return self._record_transaction(
            transaction_type="SELL",
            amount=proceeds,
            symbol=symbol,
            quantity=quantity,
            price=price
        )

    def get_holdings(self) -> list[Holding]:
        result = []
        for symbol in sorted(self.holdings.keys()):
            quantity = self.holdings[symbol]
            price = get_share_price(symbol)
            result.append(Holding(
                symbol=symbol,
                quantity=quantity,
                current_price=price,
                market_value=price * quantity
            ))
        return result

    def get_transactions(self) -> list[Transaction]:
        return list(self.transactions)

    def get_portfolio_summary(self) -> PortfolioSummary:
        holdings_value = sum(holding.market_value for holding in self.get_holdings())
        total_portfolio_value = self.cash_balance + holdings_value
        net_contributions = self.total_deposits - self.total_withdrawals
        profit_loss = total_portfolio_value - net_contributions
        
        return PortfolioSummary(
            account_id=self.account_id,
            cash_balance=self.cash_balance,
            holdings_value=holdings_value,
            total_portfolio_value=total_portfolio_value,
            total_deposits=self.total_deposits,
            total_withdrawals=self.total_withdrawals,
            net_contributions=net_contributions,
            profit_loss=profit_loss
        )

    def get_profit_loss_from_initial_deposit(self) -> float:
        summary = self.get_portfolio_summary()
        return summary.total_portfolio_value - self.initial_deposit

    def get_cash_balance(self) -> float:
        return self.cash_balance

    def _record_transaction(
        self,
        transaction_type: str,
        amount: float,
        symbol: str | None = None,
        quantity: int | None = None,
        price: float | None = None,
    ) -> Transaction:
        transaction = Transaction(
            transaction_id=self._next_transaction_id,
            timestamp=datetime.now(),
            transaction_type=transaction_type,
            symbol=symbol,
            quantity=quantity,
            price=price,
            amount=amount,
            cash_balance_after=self.cash_balance
        )
        self.transactions.append(transaction)
        self._next_transaction_id += 1
        return transaction


def transaction_to_row(transaction: Transaction) -> list[str | int | float | None]:
    return [
        transaction.transaction_id,
        transaction.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        transaction.transaction_type,
        transaction.symbol or "",
        transaction.quantity or "",
        transaction.price if transaction.price is not None else "",
        transaction.amount,
        transaction.cash_balance_after,
    ]


def holding_to_row(holding: Holding) -> list[str | int | float]:
    return [
        holding.symbol,
        holding.quantity,
        holding.current_price,
        holding.market_value,
    ]


def summary_to_rows(summary: PortfolioSummary, profit_loss_from_initial: float) -> list[list[str | float]]:
    return [
        ["Account ID", summary.account_id],
        ["Cash Balance", summary.cash_balance],
        ["Holdings Value", summary.holdings_value],
        ["Total Portfolio Value", summary.total_portfolio_value],
        ["Total Deposits", summary.total_deposits],
        ["Total Withdrawals", summary.total_withdrawals],
        ["Net Contributions", summary.net_contributions],
        ["Profit/Loss vs Net Contributions", summary.profit_loss],
        ["Profit/Loss vs Initial Deposit", profit_loss_from_initial],
    ]
