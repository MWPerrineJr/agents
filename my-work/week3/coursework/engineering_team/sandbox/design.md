# Design: Simple Account Management System for Trading Simulation

## Overview

Build a single-user trading simulation account management system with:

- Account creation
- Deposits and withdrawals
- Buy/sell share recording
- Cash balance validation
- Share holding validation
- Portfolio valuation using `get_share_price(symbol)`
- Profit/loss calculation versus initial deposit
- Holdings reporting
- Transaction history reporting
- Gradio 6 frontend

All files must live in the same sandbox directory. No packages or subdirectories.

Only Python standard library and `gradio` are available.

---

# File Structure

```text
backend.py
app.py
test_backend.py
```

---

# Responsibilities

## backend_engineer

Owns:

```text
backend.py
```

Implement the trading account domain model, validation logic, transaction recording, portfolio reporting, and fixed-price share price function.

## frontend_engineer

Owns:

```text
app.py
```

Implement a Gradio 6 app that uses the backend classes/functions. The app should allow users to create an account, deposit, withdraw, buy, sell, view account summary, view holdings, and view transactions.

## test_engineer

Owns:

```text
test_backend.py
```

Implement unit tests for backend behavior using only the Python standard library, preferably `unittest`.

---

# Backend Design

## File: `backend.py`

### Purpose

Contains all business logic and data structures. The backend must not depend on Gradio.

---

## Constants

```python
SUPPORTED_SYMBOLS: tuple[str, ...]
```

Expected value:

```python
("AAPL", "TSLA", "GOOGL")
```

---

## Function: `get_share_price`

```python
def get_share_price(symbol: str) -> float:
    ...
```

### Behavior

Returns a fixed current share price for supported symbols.

Suggested fixed prices:

```python
AAPL  -> 150.00
TSLA  -> 250.00
GOOGL -> 2800.00
```

### Validation

- Normalize `symbol` to uppercase and strip whitespace.
- Raise `ValueError` if the symbol is unsupported.

### Example

```python
get_share_price("aapl") == 150.00
```

---

## Class: `Transaction`

Use a dataclass.

```python
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
```

### Field Definitions

| Field | Meaning |
|---|---|
| `transaction_id` | Sequential integer starting at 1 |
| `timestamp` | Time transaction was recorded |
| `transaction_type` | `"CREATE_ACCOUNT"`, `"DEPOSIT"`, `"WITHDRAW"`, `"BUY"`, `"SELL"` |
| `symbol` | Share symbol for buy/sell, otherwise `None` |
| `quantity` | Share quantity for buy/sell, otherwise `None` |
| `price` | Share price used for buy/sell, otherwise `None` |
| `amount` | Cash amount of the transaction |
| `cash_balance_after` | Cash balance after transaction completes |

---

## Class: `Holding`

Use a dataclass.

```python
@dataclass
class Holding:
    symbol: str
    quantity: int
    current_price: float
    market_value: float
```

---

## Class: `PortfolioSummary`

Use a dataclass.

```python
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
```

### Calculation Rules

```python
holdings_value = sum(quantity * get_share_price(symbol) for each holding)
total_portfolio_value = cash_balance + holdings_value
net_contributions = total_deposits - total_withdrawals
profit_loss = total_portfolio_value - net_contributions
```

This is better than comparing against only the first deposit because the system supports multiple deposits and withdrawals.

However, the requirement says “profit or loss from the initial deposit.” To support that wording explicitly, the account should also track:

```python
initial_deposit: float
```

The app may display both:

- Profit/loss versus net contributions
- Profit/loss versus initial deposit

If keeping the backend simpler, expose only `profit_loss` as total value minus net contributions.

---

## Class: `Account`

```python
class Account:
    def __init__(self, account_id: str, initial_deposit: float) -> None:
        ...
```

### Internal State

```python
self.account_id: str
self.initial_deposit: float
self.cash_balance: float
self.total_deposits: float
self.total_withdrawals: float
self.holdings: dict[str, int]
self.transactions: list[Transaction]
self._next_transaction_id: int
```

### Initialization Behavior

- Validate `account_id` is non-empty.
- Validate `initial_deposit >= 0`.
- Set `cash_balance = initial_deposit`.
- Set `initial_deposit = initial_deposit`.
- Set `total_deposits = initial_deposit`.
- Set `total_withdrawals = 0`.
- Initialize empty holdings.
- Record a `"CREATE_ACCOUNT"` transaction.
- If desired, this transaction amount should equal `initial_deposit`.

---

# Backend Public Methods

## Method: `deposit`

```python
def deposit(self, amount: float) -> Transaction:
    ...
```

### Behavior

- Validate `amount > 0`.
- Increase cash balance.
- Increase `total_deposits`.
- Record and return a `"DEPOSIT"` transaction.

### Raises

```python
ValueError
```

If amount is zero or negative.

---

## Method: `withdraw`

```python
def withdraw(self, amount: float) -> Transaction:
    ...
```

### Behavior

- Validate `amount > 0`.
- Validate `amount <= cash_balance`.
- Decrease cash balance.
- Increase `total_withdrawals`.
- Record and return a `"WITHDRAW"` transaction.

### Required Constraint

The user must not be able to withdraw funds that would leave a negative cash balance.

### Raises

```python
ValueError
```

If:

- Amount is zero or negative.
- Amount exceeds current cash balance.

---

## Method: `buy`

```python
def buy(self, symbol: str, quantity: int) -> Transaction:
    ...
```

### Behavior

- Normalize symbol.
- Validate quantity is a positive integer.
- Get current price using `get_share_price(symbol)`.
- Calculate total cost:

```python
total_cost = price * quantity
```

- Validate `total_cost <= cash_balance`.
- Decrease cash balance by `total_cost`.
- Increase holdings for the symbol.
- Record and return a `"BUY"` transaction.

### Required Constraint

The user must not be able to buy more shares than they can afford.

### Raises

```python
ValueError
```

If:

- Unsupported symbol.
- Quantity is not positive.
- Total cost exceeds cash balance.

---

## Method: `sell`

```python
def sell(self, symbol: str, quantity: int) -> Transaction:
    ...
```

### Behavior

- Normalize symbol.
- Validate quantity is a positive integer.
- Validate current holdings for symbol are at least quantity.
- Get current price using `get_share_price(symbol)`.
- Calculate proceeds:

```python
proceeds = price * quantity
```

- Increase cash balance by proceeds.
- Decrease holdings for the symbol.
- Remove symbol from holdings if quantity becomes zero.
- Record and return a `"SELL"` transaction.

### Required Constraint

The user must not be able to sell shares they do not have.

### Raises

```python
ValueError
```

If:

- Unsupported symbol.
- Quantity is not positive.
- Quantity exceeds held shares.

---

## Method: `get_holdings`

```python
def get_holdings(self) -> list[Holding]:
    ...
```

### Behavior

Return the current holdings as a list of `Holding` objects.

Each holding should include:

```python
symbol
quantity
current_price
market_value
```

Sort holdings alphabetically by symbol for deterministic display and testing.

---

## Method: `get_transactions`

```python
def get_transactions(self) -> list[Transaction]:
    ...
```

### Behavior

Return a copy of the transaction list.

Use:

```python
return list(self.transactions)
```

Do not return the internal list directly.

---

## Method: `get_portfolio_summary`

```python
def get_portfolio_summary(self) -> PortfolioSummary:
    ...
```

### Behavior

Calculate and return:

```python
cash_balance
holdings_value
total_portfolio_value
total_deposits
total_withdrawals
net_contributions
profit_loss
```

---

## Method: `get_profit_loss_from_initial_deposit`

```python
def get_profit_loss_from_initial_deposit(self) -> float:
    ...
```

### Behavior

Calculate:

```python
get_portfolio_summary().total_portfolio_value - self.initial_deposit
```

This satisfies the explicit wording of “profit or loss from the initial deposit.”

---

## Method: `get_cash_balance`

```python
def get_cash_balance(self) -> float:
    ...
```

### Behavior

Return current cash balance.

---

## Method: `_record_transaction`

Private helper.

```python
def _record_transaction(
    self,
    transaction_type: str,
    amount: float,
    symbol: str | None = None,
    quantity: int | None = None,
    price: float | None = None,
) -> Transaction:
    ...
```

### Behavior

- Create a `Transaction`.
- Use current datetime.
- Use current `_next_transaction_id`.
- Store cash balance after the operation.
- Append transaction to transaction list.
- Increment `_next_transaction_id`.
- Return created transaction.

---

## Helper Function: `normalize_symbol`

```python
def normalize_symbol(symbol: str) -> str:
    ...
```

### Behavior

- Validate symbol is a string.
- Strip whitespace.
- Convert to uppercase.
- Validate non-empty.
- Return normalized symbol.

### Raises

```python
ValueError
```

If invalid.

---

## Helper Function: `validate_positive_amount`

```python
def validate_positive_amount(amount: float, field_name: str = "amount") -> None:
    ...
```

### Behavior

Raise `ValueError` if `amount <= 0`.

---

## Helper Function: `validate_positive_quantity`

```python
def validate_positive_quantity(quantity: int) -> None:
    ...
```

### Behavior

Raise `ValueError` if quantity is not an integer or quantity <= 0.

Important: Reject booleans because `bool` is a subclass of `int`.

---

# Backend Formatting Helpers for Frontend

These are optional but recommended because they keep frontend code simple.

## Function: `transaction_to_row`

```python
def transaction_to_row(transaction: Transaction) -> list[str | int | float | None]:
    ...
```

### Returns

A list suitable for Gradio `Dataframe`, for example:

```python
[
    transaction.transaction_id,
    transaction.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
    transaction.transaction_type,
    transaction.symbol or "",
    transaction.quantity or "",
    transaction.price if transaction.price is not None else "",
    transaction.amount,
    transaction.cash_balance_after,
]
```

---

## Function: `holding_to_row`

```python
def holding_to_row(holding: Holding) -> list[str | int | float]:
    ...
```

### Returns

```python
[
    holding.symbol,
    holding.quantity,
    holding.current_price,
    holding.market_value,
]
```

---

## Function: `summary_to_rows`

```python
def summary_to_rows(summary: PortfolioSummary, profit_loss_from_initial: float) -> list[list[str | float]]:
    ...
```

### Returns

Rows suitable for a two-column `Dataframe`.

Example rows:

```python
[
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
```

---

# Frontend Design

## File: `app.py`

### Purpose

Create a Gradio 6 user interface for interacting with one account per browser session.

Use `gr.State` to store the backend `Account` object.

---

# Gradio 6 API Guidance

The frontend engineer should use Gradio 6 APIs as follows.

## Import

```python
import gradio as gr
```

## Blocks

Use:

```python
with gr.Blocks() as demo:
    ...
demo.launch()
```

## Button Event Binding

Use:

```python
button.click(fn=handler_function, inputs=[...], outputs=[...])
```

or for one input/output:

```python
button.click(fn=handler_function, inputs=input_component, outputs=output_component)
```

Do not call the function directly.

## State

Use:

```python
account_state = gr.State(None)
```

State can hold the backend `Account` object.

Handler functions that modify the account must include `account_state` as both an input and output.

Example signature pattern:

```python
def handle_deposit(account: Account | None, amount: float):
    ...
    return account, message, summary_rows, holdings_rows, transaction_rows
```

Event binding:

```python
deposit_button.click(
    fn=handle_deposit,
    inputs=[account_state, deposit_amount],
    outputs=[account_state, status_box, summary_table, holdings_table, transactions_table],
)
```

## Number Component

Gradio 6 `gr.Number` constructor supports:

```python
gr.Number(
    value=None,
    label=None,
    placeholder=None,
    precision=None,
    minimum=None,
    maximum=None,
    step=1,
)
```

Use `minimum=0` for deposit/withdraw amount input and `minimum=1`, `precision=0`, `step=1` for quantity input.

Example:

```python
deposit_amount = gr.Number(label="Deposit Amount", minimum=0, step=100)
quantity = gr.Number(label="Quantity", minimum=1, precision=0, step=1)
```

## Textbox

Use for account ID and status messages.

```python
account_id_box = gr.Textbox(label="Account ID")
status_box = gr.Textbox(label="Status", interactive=False)
```

## Dropdown

Use for share symbols.

```python
symbol_dropdown = gr.Dropdown(
    choices=["AAPL", "TSLA", "GOOGL"],
    label="Symbol",
    value="AAPL",
)
```

## Dataframe

Use `gr.Dataframe` for holdings, transactions, and summary.

Examples:

```python
summary_table = gr.Dataframe(
    headers=["Metric", "Value"],
    label="Portfolio Summary",
    interactive=False,
)

holdings_table = gr.Dataframe(
    headers=["Symbol", "Quantity", "Current Price", "Market Value"],
    label="Holdings",
    interactive=False,
)

transactions_table = gr.Dataframe(
    headers=[
        "ID",
        "Timestamp",
        "Type",
        "Symbol",
        "Quantity",
        "Price",
        "Amount",
        "Cash Balance After",
    ],
    label="Transactions",
    interactive=False,
)
```

Do not rely on Pandas because only Gradio and the standard library are guaranteed. Return lists of lists to `gr.Dataframe`.

## Layout

Use:

```python
with gr.Row():
    ...

with gr.Column():
    ...

with gr.Tab("Tab Name"):
    ...
```

---

# Frontend Functions

All frontend functions should be in `app.py`.

They should call backend methods and convert output to display rows.

---

## Function: `empty_summary_rows`

```python
def empty_summary_rows() -> list[list[str]]:
    ...
```

### Behavior

Return empty summary display, for example:

```python
[]
```

---

## Function: `empty_holdings_rows`

```python
def empty_holdings_rows() -> list[list[str]]:
    ...
```

---

## Function: `empty_transaction_rows`

```python
def empty_transaction_rows() -> list[list[str]]:
    ...
```

---

## Function: `build_display_state`

```python
def build_display_state(account: Account | None) -> tuple[
    list[list[object]],
    list[list[object]],
    list[list[object]],
]:
    ...
```

### Behavior

If account is `None`, return empty tables.

Otherwise return:

```python
summary_rows
holdings_rows
transaction_rows
```

Use backend helper functions where available:

```python
summary_to_rows
holding_to_row
transaction_to_row
```

---

## Function: `handle_create_account`

```python
def handle_create_account(
    account_id: str,
    initial_deposit: float,
) -> tuple[Account | None, str, list[list[object]], list[list[object]], list[list[object]]]:
    ...
```

### Behavior

- Try to create an `Account`.
- On success, return:

```python
account, success_message, summary_rows, holdings_rows, transaction_rows
```

- On validation error, return:

```python
None, error_message, [], [], []
```

### Error Handling

Catch `ValueError` and display the message in status box.

---

## Function: `handle_deposit`

```python
def handle_deposit(
    account: Account | None,
    amount: float,
) -> tuple[Account | None, str, list[list[object]], list[list[object]], list[list[object]]]:
    ...
```

### Behavior

- If account is `None`, return error asking user to create account first.
- Otherwise call:

```python
account.deposit(amount)
```

- Return updated account and refreshed tables.

---

## Function: `handle_withdraw`

```python
def handle_withdraw(
    account: Account | None,
    amount: float,
) -> tuple[Account | None, str, list[list[object]], list[list[object]], list[list[object]]]:
    ...
```

### Behavior

- If account is `None`, return error.
- Otherwise call:

```python
account.withdraw(amount)
```

- Return updated account and refreshed tables.

---

## Function: `handle_buy`

```python
def handle_buy(
    account: Account | None,
    symbol: str,
    quantity: int | float,
) -> tuple[Account | None, str, list[list[object]], list[list[object]], list[list[object]]]:
    ...
```

### Behavior

- If account is `None`, return error.
- Convert `quantity` from Gradio number input to `int`.
- Call:

```python
account.buy(symbol, int(quantity))
```

- Return updated account and refreshed tables.

### Important

Even though the UI uses `precision=0`, Gradio `Number` may still pass numeric values as `float`. Convert carefully.

---

## Function: `handle_sell`

```python
def handle_sell(
    account: Account | None,
    symbol: str,
    quantity: int | float,
) -> tuple[Account | None, str, list[list[object]], list[list[object]], list[list[object]]]:
    ...
```

### Behavior

- If account is `None`, return error.
- Convert quantity to `int`.
- Call:

```python
account.sell(symbol, int(quantity))
```

- Return updated account and refreshed tables.

---

## Function: `handle_refresh`

```python
def handle_refresh(
    account: Account | None,
) -> tuple[str, list[list[object]], list[list[object]], list[list[object]]]:
    ...
```

### Behavior

- If account is `None`, return message and empty tables.
- Otherwise return current status and refreshed tables.

---

## Function: `build_app`

```python
def build_app() -> gr.Blocks:
    ...
```

### Behavior

Build and return the complete Gradio Blocks app.

Suggested UI:

```text
Title
Status

Tab: Account
  Account ID
  Initial Deposit
  Create Account Button

Tab: Cash
  Deposit Amount
  Deposit Button
  Withdraw Amount
  Withdraw Button

Tab: Trade
  Symbol Dropdown
  Quantity
  Buy Button
  Sell Button

Tab: Reports
  Refresh Button
  Portfolio Summary Dataframe
  Holdings Dataframe
  Transactions Dataframe
```

### Event Wiring

Create account:

```python
create_button.click(
    fn=handle_create_account,
    inputs=[account_id_box, initial_deposit_box],
    outputs=[account_state, status_box, summary_table, holdings_table, transactions_table],
)
```

Deposit:

```python
deposit_button.click(
    fn=handle_deposit,
    inputs=[account_state, deposit_amount_box],
    outputs=[account_state, status_box, summary_table, holdings_table, transactions_table],
)
```

Withdraw:

```python
withdraw_button.click(
    fn=handle_withdraw,
    inputs=[account_state, withdraw_amount_box],
    outputs=[account_state, status_box, summary_table, holdings_table, transactions_table],
)
```

Buy:

```python
buy_button.click(
    fn=handle_buy,
    inputs=[account_state, symbol_dropdown, quantity_box],
    outputs=[account_state, status_box, summary_table, holdings_table, transactions_table],
)
```

Sell:

```python
sell_button.click(
    fn=handle_sell,
    inputs=[account_state, symbol_dropdown, quantity_box],
    outputs=[account_state, status_box, summary_table, holdings_table, transactions_table],
)
```

Refresh:

```python
refresh_button.click(
    fn=handle_refresh,
    inputs=[account_state],
    outputs=[status_box, summary_table, holdings_table, transactions_table],
)
```

---

## Main Guard

At bottom of `app.py`:

```python
if __name__ == "__main__":
    demo = build_app()
    demo.launch()
```

---

# Testing Design

## File: `test_backend.py`

### Purpose

Test backend behavior only. Do not test Gradio UI.

Use:

```python
import unittest
```

Run with:

```bash
uv run python test_backend.py
```

---

# Test Cases

## Test Class: `TestSharePrices`

```python
class TestSharePrices(unittest.TestCase):
    ...
```

### Tests

```python
def test_get_share_price_supported_symbols(self) -> None:
    ...
```

Verify fixed prices for:

- AAPL
- TSLA
- GOOGL

```python
def test_get_share_price_normalizes_symbol(self) -> None:
    ...
```

Verify lowercase and whitespace work.

```python
def test_get_share_price_rejects_unknown_symbol(self) -> None:
    ...
```

Verify `ValueError`.

---

## Test Class: `TestAccountCreation`

```python
class TestAccountCreation(unittest.TestCase):
    ...
```

### Tests

```python
def test_create_account_sets_initial_cash_balance(self) -> None:
    ...
```

Expected:

- Cash balance equals initial deposit.
- Total deposits equals initial deposit.
- Initial deposit stored.

```python
def test_create_account_records_transaction(self) -> None:
    ...
```

Expected:

- One transaction exists.
- Type is `"CREATE_ACCOUNT"`.

```python
def test_create_account_rejects_negative_initial_deposit(self) -> None:
    ...
```

```python
def test_create_account_rejects_empty_account_id(self) -> None:
    ...
```

---

## Test Class: `TestDepositsAndWithdrawals`

```python
class TestDepositsAndWithdrawals(unittest.TestCase):
    ...
```

### Tests

```python
def test_deposit_increases_cash_balance(self) -> None:
    ...
```

```python
def test_deposit_records_transaction(self) -> None:
    ...
```

```python
def test_deposit_rejects_zero_or_negative_amount(self) -> None:
    ...
```

```python
def test_withdraw_decreases_cash_balance(self) -> None:
    ...
```

```python
def test_withdraw_records_transaction(self) -> None:
    ...
```

```python
def test_withdraw_rejects_zero_or_negative_amount(self) -> None:
    ...
```

```python
def test_withdraw_rejects_amount_exceeding_cash_balance(self) -> None:
    ...
```

Required validation:

- Attempting to withdraw more than cash should raise `ValueError`.
- Cash balance should remain unchanged after failed withdrawal.

---

## Test Class: `TestBuyingShares`

```python
class TestBuyingShares(unittest.TestCase):
    ...
```

### Tests

```python
def test_buy_decreases_cash_and_increases_holdings(self) -> None:
    ...
```

Example:

- Account starts with `1000`.
- Buy 2 AAPL at 150.
- Cash becomes `700`.
- Holdings AAPL becomes `2`.

```python
def test_buy_records_transaction(self) -> None:
    ...
```

```python
def test_buy_rejects_unsupported_symbol(self) -> None:
    ...
```

```python
def test_buy_rejects_non_positive_quantity(self) -> None:
    ...
```

```python
def test_buy_rejects_quantity_exceeding_cash_balance(self) -> None:
    ...
```

Required validation:

- Failed buy should not change cash or holdings.

---

## Test Class: `TestSellingShares`

```python
class TestSellingShares(unittest.TestCase):
    ...
```

### Tests

```python
def test_sell_increases_cash_and_decreases_holdings(self) -> None:
    ...
```

Example:

- Account starts with `1000`.
- Buy 3 AAPL.
- Sell 1 AAPL.
- Holdings AAPL becomes `2`.
- Cash reflects proceeds.

```python
def test_sell_removes_holding_when_quantity_reaches_zero(self) -> None:
    ...
```

```python
def test_sell_records_transaction(self) -> None:
    ...
```

```python
def test_sell_rejects_quantity_exceeding_holdings(self) -> None:
    ...
```

```python
def test_sell_rejects_symbol_not_held(self) -> None:
    ...
```

```python
def test_sell_rejects_non_positive_quantity(self) -> None:
    ...
```

Required validation:

- Failed sell should not change cash or holdings.

---

## Test Class: `TestReports`

```python
class TestReports(unittest.TestCase):
    ...
```

### Tests

```python
def test_get_holdings_returns_market_values(self) -> None:
    ...
```

Example:

- Buy 2 AAPL.
- Holding market value is `2 * 150`.

```python
def test_get_holdings_sorted_by_symbol(self) -> None:
    ...
```

```python
def test_get_transactions_returns_copy(self) -> None:
    ...
```

Mutating returned transaction list should not mutate internal transaction history.

```python
def test_portfolio_summary_calculates_total_value(self) -> None:
    ...
```

```python
def test_portfolio_summary_calculates_profit_loss(self) -> None:
    ...
```

```python
def test_profit_loss_from_initial_deposit(self) -> None:
    ...
```

---

# Important Backend Invariants

The backend must preserve these invariants after every successful or failed operation:

```python
cash_balance >= 0
all holding quantities > 0
transaction IDs are sequential
failed operations do not mutate state
```

For failed operations:

- Validate before mutating internal state.
- Raise `ValueError`.
- Do not record a transaction.

---

# Example Backend Flow

```python
account = Account("demo", 10000)

account.buy("AAPL", 10)
# Cost: 1500
# Cash: 8500
# Holdings: {"AAPL": 10}

account.sell("AAPL", 4)
# Proceeds: 600
# Cash: 9100
# Holdings: {"AAPL": 6}

account.withdraw(1000)
# Cash: 8100

summary = account.get_portfolio_summary()
# Holdings value: 6 * 150 = 900
# Total portfolio value: 8100 + 900 = 9000
```

---

# Error Message Guidance

Backend error messages should be clear and user-facing enough for the frontend to display.

Examples:

```text
Account ID is required.
Initial deposit cannot be negative.
Amount must be greater than zero.
Insufficient cash balance.
Unsupported symbol: MSFT.
Quantity must be a positive integer.
Insufficient cash to buy 10 shares of AAPL.
Cannot sell 5 shares of AAPL; only 2 held.
```

---

# Assignment Details

## backend_engineer Tasks

Implement `backend.py` with:

```python
SUPPORTED_SYMBOLS
get_share_price(symbol: str) -> float
normalize_symbol(symbol: str) -> str
validate_positive_amount(amount: float, field_name: str = "amount") -> None
validate_positive_quantity(quantity: int) -> None
@dataclass Transaction
@dataclass Holding
@dataclass PortfolioSummary
class Account
transaction_to_row(transaction: Transaction) -> list[str | int | float | None]
holding_to_row(holding: Holding) -> list[str | int | float]
summary_to_rows(summary: PortfolioSummary, profit_loss_from_initial: float) -> list[list[str | float]]
```

Ensure all calculations are deterministic and use fixed prices.

---

## frontend_engineer Tasks

Implement `app.py` with:

```python
empty_summary_rows() -> list[list[str]]
empty_holdings_rows() -> list[list[str]]
empty_transaction_rows() -> list[list[str]]
build_display_state(account: Account | None) -> tuple[list[list[object]], list[list[object]], list[list[object]]]
handle_create_account(account_id: str, initial_deposit: float) -> tuple[Account | None, str, list[list[object]], list[list[object]], list[list[object]]]
handle_deposit(account: Account | None, amount: float) -> tuple[Account | None, str, list[list[object]], list[list[object]], list[list[object]]]
handle_withdraw(account: Account | None, amount: float) -> tuple[Account | None, str, list[list[object]], list[list[object]], list[list[object]]]
handle_buy(account: Account | None, symbol: str, quantity: int | float) -> tuple[Account | None, str, list[list[object]], list[list[object]], list[list[object]]]
handle_sell(account: Account | None, symbol: str, quantity: int | float) -> tuple[Account | None, str, list[list[object]], list[list[object]], list[list[object]]]
handle_refresh(account: Account | None) -> tuple[str, list[list[object]], list[list[object]], list[list[object]]]
build_app() -> gr.Blocks
```

Use `gr.State(None)` for session state.

Use Gradio 6-compatible component constructors and event binding as described above.

---

## test_engineer Tasks

Implement `test_backend.py` using `unittest`.

Cover:

- Price lookup
- Account creation
- Deposits
- Withdrawals
- Buying
- Selling
- Holdings report
- Transaction history
- Portfolio valuation
- Profit/loss calculations
- Failure cases and no-mutation guarantees

End file with:

```python
if __name__ == "__main__":
    unittest.main()
```

Run tests with:

```bash
uv run python test_backend.py
```

---

# Acceptance Criteria

The system is complete when:

1. `backend.py` supports account creation, deposits, withdrawals, buys, sells, holdings reports, transaction reports, and portfolio summary.
2. Invalid withdrawals, unaffordable buys, and invalid sells raise `ValueError` and do not mutate state.
3. `get_share_price(symbol)` returns fixed prices for AAPL, TSLA, and GOOGL.
4. `app.py` launches a working Gradio 6 interface with:

   ```bash
   uv run python app.py
   ```

5. The Gradio app supports one account per user session using `gr.State`.
6. The UI tables refresh after every successful operation.
7. Backend tests pass with:

   ```bash
   uv run python test_backend.py
   ```

8. No third-party packages besides Gradio are used.
9. All files are in the same directory.
10. There are no subdirectories or Python packages.