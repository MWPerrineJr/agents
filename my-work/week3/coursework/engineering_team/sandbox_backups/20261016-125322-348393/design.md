# Design: Simple Account Management System for Trading Simulation

## Overview

Build a small in-memory trading simulation account system with:

- Account creation
- Cash deposits and withdrawals
- Buy/sell share recording
- Holdings reporting
- Transaction history reporting
- Portfolio valuation using `get_share_price(symbol)`
- Profit/loss calculation relative to total deposited capital
- Validation to prevent:
  - Negative cash balance after withdrawal
  - Buying shares without enough cash
  - Selling more shares than owned

All files will live in the same sandbox directory. No packages or subdirectories.

---

# File Structure

```text
backend.py          # Backend models, account service, price provider
app.py              # Gradio frontend app
test_backend.py     # Unit tests for backend.py
README.md           # Optional short usage notes
```

---

# Backend Design

Assigned to: `backend_engineer`

## Module: `backend.py`

### Responsibilities

`backend.py` owns all business logic and data modeling.

It should be completely independent of Gradio so it can be unit tested directly.

The backend should:

- Manage multiple accounts in memory.
- Track cash balance per account.
- Track holdings per account.
- Track all transactions over time.
- Validate deposits, withdrawals, buys, and sells.
- Calculate current portfolio value.
- Calculate profit/loss from deposits.
- Provide fixed test prices for `AAPL`, `TSLA`, and `GOOGL`.

---

## Constants

```python
SUPPORTED_SYMBOLS: tuple[str, ...]
```

Expected value:

```text
("AAPL", "TSLA", "GOOGL")
```

```python
DEFAULT_PRICES: dict[str, float]
```

Suggested fixed test values:

```text
AAPL: 150.00
TSLA: 250.00
GOOGL: 2800.00
```

---

## Exceptions

Use custom exceptions for clear error handling.

```python
class AccountError(Exception):
    """Base exception for account management errors."""
```

```python
class AccountNotFoundError(AccountError):
    """Raised when an account id is not found."""
```

```python
class DuplicateAccountError(AccountError):
    """Raised when trying to create an account that already exists."""
```

```python
class ValidationError(AccountError):
    """Raised when an operation is invalid."""
```

```python
class InsufficientFundsError(AccountError):
    """Raised when cash balance is insufficient."""
```

```python
class InsufficientSharesError(AccountError):
    """Raised when share holdings are insufficient."""
```

```python
class UnknownSymbolError(AccountError):
    """Raised when a share symbol is not supported."""
```

---

## Data Classes

### Class: `Transaction`

Represents one account transaction.

```python
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
```

### Transaction Type Values

Use string constants:

```python
TRANSACTION_DEPOSIT: str
TRANSACTION_WITHDRAW: str
TRANSACTION_BUY: str
TRANSACTION_SELL: str
```

Expected values:

```text
"DEPOSIT"
"WITHDRAW"
"BUY"
"SELL"
```

---

### Class: `Account`

Represents a user trading account.

```python
@dataclass
class Account:
    account_id: str
    cash_balance: float = 0.0
    total_deposited: float = 0.0
    holdings: dict[str, int] = field(default_factory=dict)
    transactions: list[Transaction] = field(default_factory=list)
```

Notes:

- `cash_balance` is available uninvested cash.
- `total_deposited` is cumulative deposits minus nothing. Withdrawals should not reduce `total_deposited`.
- `holdings` maps symbol to quantity.
- `transactions` preserves chronological order.

---

## Price Provider Function

### Function: `get_share_price`

```python
def get_share_price(symbol: str) -> float:
    """
    Return the current fixed share price for a supported symbol.

    Supported symbols:
    - AAPL
    - TSLA
    - GOOGL

    Raises:
        UnknownSymbolError: if symbol is unsupported.
    """
```

Validation:

- Normalize symbol with `symbol.upper().strip()`.
- Raise `UnknownSymbolError` for unsupported symbols.

---

# Account Service

## Class: `AccountService`

Main backend API used by frontend and tests.

```python
class AccountService:
    def __init__(self) -> None:
        ...
```

Internal state:

```python
self._accounts: dict[str, Account]
self._next_transaction_id: int
```

---

## Account Management Methods

### `create_account`

```python
def create_account(self, account_id: str, initial_deposit: float = 0.0) -> Account:
    """
    Create a new account.

    If initial_deposit > 0, record it as a DEPOSIT transaction.

    Raises:
        ValidationError: if account_id is blank.
        ValidationError: if initial_deposit is negative.
        DuplicateAccountError: if account_id already exists.
    """
```

Validation:

- `account_id.strip()` must not be empty.
- `initial_deposit >= 0`.
- Duplicate account ids are not allowed.
- Normalize account ids with `strip()` but do not force uppercase.

---

### `get_account`

```python
def get_account(self, account_id: str) -> Account:
    """
    Return the Account for account_id.

    Raises:
        AccountNotFoundError: if missing.
    """
```

---

### `list_accounts`

```python
def list_accounts(self) -> list[str]:
    """
    Return all account ids sorted alphabetically.
    """
```

---

## Cash Methods

### `deposit`

```python
def deposit(self, account_id: str, amount: float) -> Account:
    """
    Deposit cash into an account.

    Raises:
        AccountNotFoundError
        ValidationError: if amount <= 0.
    """
```

Behavior:

- Increase `cash_balance`.
- Increase `total_deposited`.
- Add `DEPOSIT` transaction.

---

### `withdraw`

```python
def withdraw(self, account_id: str, amount: float) -> Account:
    """
    Withdraw cash from an account.

    Raises:
        AccountNotFoundError
        ValidationError: if amount <= 0.
        InsufficientFundsError: if withdrawal would make cash balance negative.
    """
```

Behavior:

- Decrease `cash_balance`.
- Do not change `total_deposited`.
- Add `WITHDRAW` transaction.

---

## Trading Methods

### `buy_shares`

```python
def buy_shares(self, account_id: str, symbol: str, quantity: int) -> Account:
    """
    Buy quantity shares of symbol at current share price.

    Raises:
        AccountNotFoundError
        UnknownSymbolError
        ValidationError: if quantity <= 0.
        InsufficientFundsError: if cash balance is too low.
    """
```

Behavior:

- Normalize symbol to uppercase.
- Get current price using `get_share_price(symbol)`.
- Compute total cost: `price * quantity`.
- Validate cash balance is sufficient.
- Reduce cash balance by total cost.
- Increase holdings for symbol.
- Add `BUY` transaction.

---

### `sell_shares`

```python
def sell_shares(self, account_id: str, symbol: str, quantity: int) -> Account:
    """
    Sell quantity shares of symbol at current share price.

    Raises:
        AccountNotFoundError
        UnknownSymbolError
        ValidationError: if quantity <= 0.
        InsufficientSharesError: if holdings are too low.
    """
```

Behavior:

- Normalize symbol to uppercase.
- Get current price using `get_share_price(symbol)`.
- Validate user owns at least `quantity`.
- Increase cash balance by `price * quantity`.
- Decrease holdings.
- Remove symbol from holdings if quantity becomes zero.
- Add `SELL` transaction.

---

## Reporting Methods

### `get_cash_balance`

```python
def get_cash_balance(self, account_id: str) -> float:
    """
    Return current cash balance.
    """
```

---

### `get_holdings`

```python
def get_holdings(self, account_id: str) -> dict[str, int]:
    """
    Return a copy of the current holdings dictionary.
    """
```

Important:

- Return a copy, not the internal mutable dictionary.

---

### `get_transactions`

```python
def get_transactions(self, account_id: str) -> list[Transaction]:
    """
    Return a copy of the account transaction list in chronological order.
    """
```

Important:

- Return a shallow copy of the list.

---

### `get_holdings_report`

```python
def get_holdings_report(self, account_id: str) -> list[dict[str, object]]:
    """
    Return holdings as rows suitable for UI display.

    Each row should contain:
    - symbol
    - quantity
    - current_price
    - market_value
    """
```

Example return:

```text
[
  {
    "symbol": "AAPL",
    "quantity": 3,
    "current_price": 150.0,
    "market_value": 450.0
  }
]
```

---

### `get_transactions_report`

```python
def get_transactions_report(self, account_id: str) -> list[dict[str, object]]:
    """
    Return transactions as rows suitable for UI display.

    Each row should contain:
    - transaction_id
    - timestamp
    - transaction_type
    - amount
    - symbol
    - quantity
    - price
    - cash_balance_after
    """
```

---

### `get_portfolio_value`

```python
def get_portfolio_value(self, account_id: str) -> float:
    """
    Return total current portfolio value.

    Formula:
        cash_balance + sum(quantity * get_share_price(symbol) for holdings)
    """
```

---

### `get_profit_loss`

```python
def get_profit_loss(self, account_id: str) -> float:
    """
    Return profit/loss from initial deposits.

    Formula:
        current_portfolio_value - total_deposited
    """
```

---

### `get_account_summary`

```python
def get_account_summary(self, account_id: str) -> dict[str, float | str]:
    """
    Return summary values for UI display.

    Keys:
    - account_id
    - cash_balance
    - holdings_value
    - portfolio_value
    - total_deposited
    - profit_loss
    """
```

---

## Internal Helper Methods

These should be private implementation details.

### `_validate_account_id`

```python
def _validate_account_id(self, account_id: str) -> str:
    """
    Strip and validate account_id.

    Raises:
        ValidationError
    """
```

---

### `_validate_positive_amount`

```python
def _validate_positive_amount(self, amount: float, field_name: str = "amount") -> float:
    """
    Validate a positive money amount.

    Raises:
        ValidationError
    """
```

---

### `_validate_positive_quantity`

```python
def _validate_positive_quantity(self, quantity: int) -> int:
    """
    Validate a positive integer share quantity.

    Raises:
        ValidationError
    """
```

---

### `_normalize_symbol`

```python
def _normalize_symbol(self, symbol: str) -> str:
    """
    Strip and uppercase a symbol.

    Raises:
        ValidationError if blank.
        UnknownSymbolError if unsupported.
    """
```

---

### `_record_transaction`

```python
def _record_transaction(
    self,
    account: Account,
    transaction_type: str,
    amount: float | None = None,
    symbol: str | None = None,
    quantity: int | None = None,
    price: float | None = None,
) -> Transaction:
    """
    Create and append a Transaction to account.transactions.
    """
```

---

# Frontend Design

Assigned to: `frontend_engineer`

## Module: `app.py`

### Responsibilities

Build a Gradio app that allows users to:

- Create/select an account
- Deposit funds
- Withdraw funds
- Buy shares
- Sell shares
- View account summary
- View holdings
- View transaction history

The Gradio frontend should call only public methods on `AccountService`.

---

## Backend Import

```python
from backend import (
    AccountService,
    AccountError,
    SUPPORTED_SYMBOLS,
)
```

---

## Global Service Instance

```python
service = AccountService()
```

This is acceptable for the simple in-memory simulation.

---

# Gradio 6 API Guidance

Use modern Gradio APIs.

## Imports

```python
import gradio as gr
```

## App Shell

Use:

```python
with gr.Blocks(title="Trading Simulation Account Manager") as demo:
    ...
```

Do not use old APIs such as:

```text
gr.Interface with gr.inputs / gr.outputs
gr.inputs.Textbox
gr.outputs.Dataframe
component.style(...)
```

Those older patterns should be avoided.

---

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

Use constructor kwargs like:

```python
gr.Textbox(label="Account ID", placeholder="example: alice")
gr.Number(label="Amount", value=0)
gr.Dropdown(label="Symbol", choices=list(SUPPORTED_SYMBOLS), value="AAPL")
gr.Button("Create Account", variant="primary")
gr.Markdown()
gr.Dataframe(headers=[...], interactive=False)
```

---

## Events

Use event handlers with explicit keyword arguments:

```python
button.click(
    fn=handler_function,
    inputs=[input_component_1, input_component_2],
    outputs=[output_component_1, output_component_2],
)
```

Avoid relying on positional event arguments.

If a handler has no inputs, use:

```python
inputs=[]
```

If a handler has one input or output, still prefer lists:

```python
inputs=[account_id_box]
outputs=[status_markdown]
```

---

## Updating Component Values

Prefer returning new values directly from event handler functions.

Example design:

```python
def handle_refresh(account_id: str) -> tuple[str, list[list[object]], list[list[object]]]:
    ...
```

Avoid depending on deprecated component update patterns unless necessary.

For dropdown account choices, use a full returned component update only if needed. To keep implementation simple, the frontend may use a plain `gr.Textbox` for account id rather than a dynamic account dropdown.

---

## Dataframe Guidance

Use `gr.Dataframe` for holdings and transactions.

Suggested holdings dataframe:

```python
holdings_table = gr.Dataframe(
    headers=["Symbol", "Quantity", "Current Price", "Market Value"],
    interactive=False,
)
```

Suggested transactions dataframe:

```python
transactions_table = gr.Dataframe(
    headers=[
        "ID",
        "Timestamp",
        "Type",
        "Amount",
        "Symbol",
        "Quantity",
        "Price",
        "Cash Balance After",
    ],
    interactive=False,
)
```

Handlers should return list-of-lists data:

```text
[
  ["AAPL", 3, 150.0, 450.0],
  ["TSLA", 1, 250.0, 250.0],
]
```

Do not return backend objects directly into the dataframe.

---

## Launch

At bottom of `app.py`:

```python
if __name__ == "__main__":
    demo.launch()
```

Do not automatically launch during import.

---

# Frontend Components

## Account Section

Components:

```python
account_id_input: gr.Textbox
initial_deposit_input: gr.Number
create_account_button: gr.Button
refresh_button: gr.Button
status_output: gr.Markdown
summary_output: gr.Markdown
```

Purpose:

- User enters account id.
- User optionally enters initial deposit.
- User creates account.
- User refreshes account summary.

---

## Cash Section

Components:

```python
deposit_amount_input: gr.Number
deposit_button: gr.Button
withdraw_amount_input: gr.Number
withdraw_button: gr.Button
```

Purpose:

- Deposit funds into current account.
- Withdraw funds from current account.

---

## Trading Section

Components:

```python
symbol_dropdown: gr.Dropdown
quantity_input: gr.Number
buy_button: gr.Button
sell_button: gr.Button
```

Notes:

- `quantity_input` should accept numeric values.
- Handler must convert to `int`.
- Backend will validate positive integer quantity.

---

## Reports Section

Components:

```python
holdings_table: gr.Dataframe
transactions_table: gr.Dataframe
```

---

# Frontend Handler Functions

All handlers should live in `app.py`.

They should catch `AccountError` and return an error message instead of crashing.

---

## `format_money`

```python
def format_money(value: float) -> str:
    """
    Format a float as currency text.
    """
```

Example output:

```text
$1,234.56
```

---

## `format_summary`

```python
def format_summary(account_id: str) -> str:
    """
    Return markdown summary for account.

    Uses service.get_account_summary(account_id).
    """
```

Suggested markdown fields:

```text
### Account Summary

- Account ID: alice
- Cash Balance: $500.00
- Holdings Value: $1,200.00
- Portfolio Value: $1,700.00
- Total Deposited: $2,000.00
- Profit/Loss: -$300.00
```

---

## `build_holdings_rows`

```python
def build_holdings_rows(account_id: str) -> list[list[object]]:
    """
    Convert service.get_holdings_report(account_id) to Dataframe rows.
    """
```

Row format:

```text
[symbol, quantity, current_price, market_value]
```

---

## `build_transaction_rows`

```python
def build_transaction_rows(account_id: str) -> list[list[object]]:
    """
    Convert service.get_transactions_report(account_id) to Dataframe rows.
    """
```

Row format:

```text
[
    transaction_id,
    timestamp_as_string,
    transaction_type,
    amount,
    symbol,
    quantity,
    price,
    cash_balance_after,
]
```

---

## `refresh_view`

```python
def refresh_view(account_id: str) -> tuple[str, str, list[list[object]], list[list[object]]]:
    """
    Refresh status, summary, holdings table, and transactions table.

    Returns:
        status_markdown
        summary_markdown
        holdings_rows
        transaction_rows
    """
```

On success:

```text
"✅ Refreshed account alice"
```

On error:

```text
"❌ Error message"
```

For errors, return empty table rows.

---

## `handle_create_account`

```python
def handle_create_account(
    account_id: str,
    initial_deposit: float,
) -> tuple[str, str, list[list[object]], list[list[object]]]:
    """
    Create account, then return refreshed UI data.
    """
```

---

## `handle_deposit`

```python
def handle_deposit(
    account_id: str,
    amount: float,
) -> tuple[str, str, list[list[object]], list[list[object]]]:
    """
    Deposit funds, then return refreshed UI data.
    """
```

---

## `handle_withdraw`

```python
def handle_withdraw(
    account_id: str,
    amount: float,
) -> tuple[str, str, list[list[object]], list[list[object]]]:
    """
    Withdraw funds, then return refreshed UI data.
    """
```

---

## `handle_buy`

```python
def handle_buy(
    account_id: str,
    symbol: str,
    quantity: float,
) -> tuple[str, str, list[list[object]], list[list[object]]]:
    """
    Buy shares, then return refreshed UI data.

    Convert quantity to int before passing to backend.
    """
```

---

## `handle_sell`

```python
def handle_sell(
    account_id: str,
    symbol: str,
    quantity: float,
) -> tuple[str, str, list[list[object]], list[list[object]]]:
    """
    Sell shares, then return refreshed UI data.

    Convert quantity to int before passing to backend.
    """
```

---

# Suggested Gradio Wiring

Every operation should update the same outputs:

```python
common_outputs = [
    status_output,
    summary_output,
    holdings_table,
    transactions_table,
]
```

Create account:

```python
create_account_button.click(
    fn=handle_create_account,
    inputs=[account_id_input, initial_deposit_input],
    outputs=common_outputs,
)
```

Refresh:

```python
refresh_button.click(
    fn=refresh_view,
    inputs=[account_id_input],
    outputs=common_outputs,
)
```

Deposit:

```python
deposit_button.click(
    fn=handle_deposit,
    inputs=[account_id_input, deposit_amount_input],
    outputs=common_outputs,
)
```

Withdraw:

```python
withdraw_button.click(
    fn=handle_withdraw,
    inputs=[account_id_input, withdraw_amount_input],
    outputs=common_outputs,
)
```

Buy:

```python
buy_button.click(
    fn=handle_buy,
    inputs=[account_id_input, symbol_dropdown, quantity_input],
    outputs=common_outputs,
)
```

Sell:

```python
sell_button.click(
    fn=handle_sell,
    inputs=[account_id_input, symbol_dropdown, quantity_input],
    outputs=common_outputs,
)
```

---

# Testing Design

Assigned to: `test_engineer`

## Module: `test_backend.py`

### Responsibilities

Write unit tests for `backend.py`.

No Gradio tests are required.

Use Python standard library testing only:

```python
import unittest
```

Do not require third-party test packages.

The tests should be runnable with:

```bash
uv run python -m unittest test_backend.py
```

---

# Test Coverage Requirements

## Price Provider Tests

### `test_get_share_price_supported_symbols`

Verify:

- `get_share_price("AAPL") == 150.0`
- `get_share_price("TSLA") == 250.0`
- `get_share_price("GOOGL") == 2800.0`

### `test_get_share_price_normalizes_symbol`

Verify:

- lowercase and whitespace symbols work.

### `test_get_share_price_unknown_symbol`

Verify:

- unsupported symbol raises `UnknownSymbolError`.

---

## Account Creation Tests

### `test_create_account_success_no_initial_deposit`

Verify:

- account exists.
- cash balance is `0.0`.
- total deposited is `0.0`.
- no transactions or a clearly expected transaction count based on implementation.

Recommended: no transaction if initial deposit is zero.

### `test_create_account_success_with_initial_deposit`

Verify:

- cash balance equals initial deposit.
- total deposited equals initial deposit.
- one `DEPOSIT` transaction exists.

### `test_create_duplicate_account_raises`

Verify:

- creating same account id twice raises `DuplicateAccountError`.

### `test_create_account_blank_id_raises`

Verify:

- blank id raises `ValidationError`.

### `test_create_account_negative_initial_deposit_raises`

Verify:

- negative initial deposit raises `ValidationError`.

---

## Deposit Tests

### `test_deposit_success`

Verify:

- cash balance increases.
- total deposited increases.
- deposit transaction recorded.

### `test_deposit_zero_or_negative_raises`

Verify:

- zero and negative values raise `ValidationError`.

---

## Withdrawal Tests

### `test_withdraw_success`

Verify:

- cash balance decreases.
- total deposited is unchanged.
- withdrawal transaction recorded.

### `test_withdraw_too_much_raises`

Verify:

- `InsufficientFundsError` is raised.
- balance remains unchanged.

### `test_withdraw_zero_or_negative_raises`

Verify:

- zero and negative values raise `ValidationError`.

---

## Buy Tests

### `test_buy_shares_success`

Setup:

- create account with enough cash.
- buy 2 shares of AAPL.

Verify:

- cash reduced by `2 * 150.0`.
- holdings `AAPL == 2`.
- buy transaction recorded with price `150.0`.

### `test_buy_shares_insufficient_funds_raises`

Verify:

- raises `InsufficientFundsError`.
- cash unchanged.
- holdings unchanged.

### `test_buy_shares_invalid_quantity_raises`

Verify:

- zero and negative quantities raise `ValidationError`.

### `test_buy_unknown_symbol_raises`

Verify:

- unsupported symbol raises `UnknownSymbolError`.

---

## Sell Tests

### `test_sell_shares_success`

Setup:

- create account.
- buy shares.
- sell some but not all.

Verify:

- cash increases by sale proceeds.
- holdings decrease.
- sell transaction recorded.

### `test_sell_all_shares_removes_holding`

Verify:

- after selling all shares of a symbol, symbol is removed from holdings or quantity is not present.

### `test_sell_more_than_owned_raises`

Verify:

- raises `InsufficientSharesError`.
- holdings unchanged.
- cash unchanged.

### `test_sell_invalid_quantity_raises`

Verify:

- zero and negative quantities raise `ValidationError`.

---

## Reporting Tests

### `test_get_holdings_returns_copy`

Verify:

- mutating returned holdings does not mutate backend state.

### `test_get_transactions_returns_copy`

Verify:

- mutating returned transaction list does not mutate backend state.

### `test_get_portfolio_value_cash_only`

Verify:

- portfolio value equals cash balance when no holdings.

### `test_get_portfolio_value_with_holdings`

Setup:

- deposit cash.
- buy shares.

Verify:

- portfolio value equals cash plus current market value of holdings.

### `test_get_profit_loss`

Example:

- deposit `1000`.
- buy 2 AAPL at `150`.
- portfolio should remain `1000` immediately after buy if price is fixed.
- profit/loss should be `0`.

Also test after withdrawal:

- deposit `1000`.
- withdraw `100`.
- portfolio value becomes `900`.
- profit/loss becomes `-100`, because total deposited remains `1000`.

### `test_get_account_summary`

Verify returned keys:

```text
account_id
cash_balance
holdings_value
portfolio_value
total_deposited
profit_loss
```

---

## Multi-Account Tests

### `test_multiple_accounts_are_isolated`

Setup:

- create `alice` and `bob`.
- deposit and buy for Alice.
- deposit and sell/buy different for Bob.

Verify:

- balances, holdings, and transactions are independent.

---

# Implementation Notes for Backend Engineer

## Numeric Precision

Use `float` for simplicity.

Round only for display if desired. Avoid rounding internal values except where necessary.

Recommended helper for reports:

```python
round(value, 2)
```

Use consistently in frontend formatting.

---

## Quantity Validation

The backend should require actual integer quantities.

If frontend passes a float, frontend must convert to int before calling backend.

Backend validation should reject:

- `0`
- negative values
- non-integer values if they reach backend

Suggested validation behavior:

```text
quantity must be an int and quantity > 0
```

---

## Transaction Timestamps

Use:

```python
datetime.now()
```

or:

```python
datetime.utcnow()
```

Either is acceptable. Tests should not assert exact timestamp values.

---

## Transaction IDs

Use sequential transaction ids starting at `1`.

Every recorded transaction should increment the service-level counter.

---

## Error Messages

Keep error messages human-readable because frontend will display them directly.

Examples:

```text
Account 'alice' already exists.
Account 'bob' was not found.
Amount must be greater than zero.
Insufficient funds.
Insufficient shares.
Unsupported symbol: MSFT.
```

---

# Implementation Notes for Frontend Engineer

## UI Behavior

Each successful operation should:

1. Perform backend action.
2. Refresh summary.
3. Refresh holdings table.
4. Refresh transactions table.
5. Show success message.

Each failed operation should:

1. Catch `AccountError`.
2. Show error message.
3. Preserve or clear report tables.

Recommended: call `refresh_view(account_id)` after successful operations.

---

## Suggested UI Layout

```text
# Trading Simulation Account Manager

Account
- Account ID
- Initial Deposit
- Create Account
- Refresh

Cash
- Deposit Amount
- Deposit
- Withdraw Amount
- Withdraw

Trading
- Symbol
- Quantity
- Buy
- Sell

Summary
- Markdown summary

Holdings
- Dataframe

Transactions
- Dataframe
```

---

# Work Assignments

## `backend_engineer`

Deliverable: `backend.py`

Build:

- Constants
- Exceptions
- `Transaction` dataclass
- `Account` dataclass
- `get_share_price(symbol)`
- `AccountService`
- All public and private methods listed above

Acceptance criteria:

- All backend unit tests pass.
- Backend has no Gradio dependency.
- Invalid operations raise the correct custom exceptions.
- Transactions are recorded in chronological order.
- Multi-account state is isolated.

---

## `frontend_engineer`

Deliverable: `app.py`

Build:

- Gradio Blocks app
- Account creation UI
- Deposit/withdraw UI
- Buy/sell UI
- Account summary
- Holdings table
- Transaction table
- Handler functions listed above
- Error handling for `AccountError`

Acceptance criteria:

- App launches with `uv run python app.py`.
- User can create an account with initial deposit.
- User can deposit and withdraw.
- User can buy and sell supported symbols.
- Invalid operations display errors instead of crashing.
- Summary, holdings, and transaction history update after each operation.
- Uses modern Gradio component APIs and event wiring.

---

## `test_engineer`

Deliverable: `test_backend.py`

Build:

- Unit tests using `unittest`
- Coverage for account creation, deposits, withdrawals, buying, selling, reports, errors, and multi-account isolation

Acceptance criteria:

- Tests run with:

```bash
uv run python -m unittest test_backend.py
```

- Tests do not require third-party packages.
- Tests do not import or depend on Gradio.
- Tests verify both success paths and failure paths.
- Tests verify invalid operations do not mutate backend state.

---

# Final Acceptance Criteria

The system is complete when:

1. `backend.py` implements the complete backend API.
2. `test_backend.py` passes all unit tests.
3. `app.py` launches successfully as a Gradio app.
4. A user can:
   - Create an account.
   - Deposit funds.
   - Withdraw available funds.
   - Buy affordable shares.
   - Sell owned shares.
   - View current holdings.
   - View full transaction history.
   - View current portfolio value.
   - View profit/loss from total deposits.
5. The system prevents:
   - Withdrawal beyond cash balance.
   - Buying beyond cash balance.
   - Selling shares not owned.
   - Using unsupported symbols.
   - Creating duplicate accounts.
   - Invalid zero or negative amounts/quantities.