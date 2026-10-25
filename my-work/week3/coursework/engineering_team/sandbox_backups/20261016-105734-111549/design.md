# Design: Simple Account Management System for Trading Simulation

## 1. Overview

Build a small in-memory trading simulation account system with:

- Account creation
- Deposits and withdrawals
- Buy and sell share transactions
- Current holdings reporting
- Historical holdings reporting
- Transaction history listing
- Portfolio valuation
- Profit/loss calculation
- Business-rule validation:
  - Cannot withdraw more cash than available
  - Cannot buy shares without enough cash
  - Cannot sell more shares than currently held

All files will live in the same directory. No subdirectories or packages.

The system will be split into:

| File | Owner | Purpose |
|---|---|---|
| `backend.py` | `backend_engineer` | Core account/trading logic |
| `app.py` | `frontend_engineer` | Gradio UI |
| `test_backend.py` | `test_engineer` | Unit tests for backend |
| `README.md` | Optional shared | Usage notes if time permits |

No third-party packages are allowed except `gradio`, which is already installed in the uv project.

---

## 2. Backend Design

### File: `backend.py`

Owner: `backend_engineer`

The backend should be fully independent of Gradio. It should expose clean Python classes and functions that can be tested directly.

Use only Python standard library.

Recommended standard-library imports:

```text
dataclasses
datetime
decimal
enum
typing
uuid
```

Do not use floats for money. Use `Decimal`.

Shares should be whole-number quantities for this version.

---

## 3. Backend Domain Model

### 3.1 Supported Symbols and Price Function

The system has access to a function:

```python
def get_share_price(symbol: str) -> Decimal
```

Required behavior:

- Accepts symbols case-insensitively.
- Supports at least:
  - `AAPL`
  - `TSLA`
  - `GOOGL`
- Returns fixed prices for testing/demo.
- Raises `UnknownSymbolError` for unsupported symbols.

Suggested fixed test prices:

| Symbol | Price |
|---|---:|
| `AAPL` | `150.00` |
| `TSLA` | `250.00` |
| `GOOGL` | `2800.00` |

Signature:

```python
def get_share_price(symbol: str) -> Decimal
```

---

### 3.2 Exceptions

Define explicit exception classes so the frontend and tests can handle business-rule failures cleanly.

```python
class AccountError(Exception)
```

Base exception for account system errors.

```python
class AccountNotFoundError(AccountError)
```

Raised when an account ID does not exist.

```python
class ValidationError(AccountError)
```

Raised for invalid inputs such as negative deposits, zero quantity, empty account name, etc.

```python
class InsufficientFundsError(AccountError)
```

Raised when a withdrawal or buy would exceed available cash.

```python
class InsufficientSharesError(AccountError)
```

Raised when selling more shares than currently held.

```python
class UnknownSymbolError(AccountError)
```

Raised when `get_share_price()` receives an unsupported symbol.

---

## 4. Backend Data Structures

### 4.1 `TransactionType`

Use an enum to avoid string mistakes.

```python
class TransactionType(Enum)
```

Members:

```text
CREATE_ACCOUNT
DEPOSIT
WITHDRAW
BUY
SELL
```

---

### 4.2 `Transaction`

Represents one account event.

```python
@dataclass(frozen=True)
class Transaction
```

Fields:

```python
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
```

Field meaning:

| Field | Meaning |
|---|---|
| `transaction_id` | Unique transaction ID |
| `account_id` | Owning account |
| `transaction_type` | Deposit, withdrawal, buy, sell, etc. |
| `timestamp` | UTC timestamp of transaction |
| `symbol` | Share symbol for buy/sell, otherwise `None` |
| `quantity` | Share quantity for buy/sell, otherwise `None` |
| `price` | Per-share execution price for buy/sell, otherwise `None` |
| `cash_amount` | Positive or negative cash movement |
| `cash_balance_after` | Cash balance after transaction |
| `description` | Human-readable detail |

Cash amount convention:

| Transaction | `cash_amount` |
|---|---:|
| Create account with initial deposit | Positive |
| Deposit | Positive |
| Withdraw | Negative |
| Buy | Negative total cost |
| Sell | Positive total proceeds |

---

### 4.3 `Account`

Represents one trading account.

```python
@dataclass
class Account
```

Fields:

```python
account_id: str
owner_name: str
created_at: datetime
initial_deposit: Decimal
cash_balance: Decimal
holdings: dict[str, int]
transactions: list[Transaction]
```

Notes:

- `holdings` maps normalized symbols to integer share quantities.
- Symbols should always be stored uppercase.
- Holdings with zero quantity may either be removed or retained, but reporting should not show zero-quantity holdings unless explicitly requested.

---

### 4.4 Report Structures

Use small dataclasses for report-style return values.

#### `HoldingReportRow`

```python
@dataclass(frozen=True)
class HoldingReportRow
```

Fields:

```python
symbol: str
quantity: int
current_price: Decimal
market_value: Decimal
```

---

#### `PortfolioSummary`

```python
@dataclass(frozen=True)
class PortfolioSummary
```

Fields:

```python
account_id: str
owner_name: str
cash_balance: Decimal
holdings_value: Decimal
total_value: Decimal
initial_deposit: Decimal
net_cash_contributions: Decimal
profit_loss_from_initial_deposit: Decimal
profit_loss_excluding_cash_flows: Decimal
```

Definitions:

| Field | Formula |
|---|---|
| `cash_balance` | Current uninvested cash |
| `holdings_value` | Sum of current market value of all holdings |
| `total_value` | `cash_balance + holdings_value` |
| `initial_deposit` | Amount supplied during account creation |
| `net_cash_contributions` | Initial deposit + later deposits - withdrawals |
| `profit_loss_from_initial_deposit` | `total_value - initial_deposit` |
| `profit_loss_excluding_cash_flows` | `total_value - net_cash_contributions` |

The UI should show both P/L values to avoid ambiguity.

---

## 5. Backend Service Class

### 5.1 `AccountService`

Primary backend API used by both tests and Gradio.

```python
class AccountService
```

Constructor:

```python
def __init__(self, price_lookup: Callable[[str], Decimal] | None = None) -> None
```

Behavior:

- If `price_lookup` is `None`, use default `get_share_price`.
- Store accounts in memory.
- Use account IDs as strings.

Private/internal helper method signatures:

```python
def _normalize_symbol(self, symbol: str) -> str
```

```python
def _normalize_money(self, amount: Decimal | int | float | str) -> Decimal
```

```python
def _validate_positive_money(self, amount: Decimal, field_name: str) -> None
```

```python
def _validate_positive_quantity(self, quantity: int) -> None
```

```python
def _get_account_or_raise(self, account_id: str) -> Account
```

```python
def _new_transaction_id(self) -> str
```

```python
def _utc_now(self) -> datetime
```

```python
def _record_transaction(
    self,
    account: Account,
    transaction_type: TransactionType,
    symbol: str | None,
    quantity: int | None,
    price: Decimal | None,
    cash_amount: Decimal,
    description: str,
) -> Transaction
```

---

## 6. Backend Public API

### 6.1 Create Account

```python
def create_account(self, owner_name: str, initial_deposit: Decimal | int | float | str) -> Account
```

Validation:

- `owner_name` must not be blank.
- `initial_deposit` must be greater than zero.

Behavior:

- Creates an account with:
  - Unique account ID
  - Initial cash balance equal to initial deposit
  - Empty holdings
  - A `CREATE_ACCOUNT` transaction
- Returns the new `Account`.

---

### 6.2 Retrieve Account

```python
def get_account(self, account_id: str) -> Account
```

Validation:

- Raise `AccountNotFoundError` if missing.

---

### 6.3 List Accounts

```python
def list_accounts(self) -> list[Account]
```

Behavior:

- Returns all accounts currently in memory.
- Useful for frontend account selector.

---

### 6.4 Deposit Funds

```python
def deposit(self, account_id: str, amount: Decimal | int | float | str) -> Transaction
```

Validation:

- Account must exist.
- Amount must be greater than zero.

Behavior:

- Increase account cash balance.
- Record a `DEPOSIT` transaction.
- Return the transaction.

---

### 6.5 Withdraw Funds

```python
def withdraw(self, account_id: str, amount: Decimal | int | float | str) -> Transaction
```

Validation:

- Account must exist.
- Amount must be greater than zero.
- Amount must be less than or equal to current cash balance.

Behavior:

- Decrease account cash balance.
- Record a `WITHDRAW` transaction.
- Return the transaction.

Failure:

- Raise `InsufficientFundsError` if withdrawal would make cash negative.

---

### 6.6 Buy Shares

```python
def buy_shares(self, account_id: str, symbol: str, quantity: int) -> Transaction
```

Validation:

- Account must exist.
- Symbol must be known.
- Quantity must be a positive integer.
- Total cost must be less than or equal to current cash balance.

Behavior:

- Normalize symbol to uppercase.
- Look up current share price.
- Calculate total cost as `price * quantity`.
- Decrease cash balance by total cost.
- Increase holdings for symbol.
- Record a `BUY` transaction.
- Return the transaction.

Failure:

- Raise `InsufficientFundsError` if buying would make cash negative.
- Raise `UnknownSymbolError` if symbol unsupported.

---

### 6.7 Sell Shares

```python
def sell_shares(self, account_id: str, symbol: str, quantity: int) -> Transaction
```

Validation:

- Account must exist.
- Symbol must be known.
- Quantity must be a positive integer.
- Quantity must be less than or equal to currently held quantity.

Behavior:

- Normalize symbol to uppercase.
- Look up current share price.
- Calculate proceeds as `price * quantity`.
- Increase cash balance by proceeds.
- Decrease holdings for symbol.
- Remove holding from dictionary if quantity reaches zero.
- Record a `SELL` transaction.
- Return the transaction.

Failure:

- Raise `InsufficientSharesError` if selling more than held.
- Raise `UnknownSymbolError` if symbol unsupported.

---

### 6.8 Current Holdings

```python
def get_holdings(self, account_id: str) -> dict[str, int]
```

Behavior:

- Return a copy of current holdings.
- Do not expose internal mutable dictionary.

---

### 6.9 Holdings Report

```python
def get_holdings_report(self, account_id: str) -> list[HoldingReportRow]
```

Behavior:

- Return one row per currently held symbol.
- Include current price and current market value.
- Exclude zero-quantity holdings.

---

### 6.10 Historical Holdings

```python
def get_holdings_at(
    self,
    account_id: str,
    as_of: datetime | None = None,
    transaction_id: str | None = None,
) -> dict[str, int]
```

Behavior:

- Reconstruct holdings by replaying transactions from account creation.
- If `as_of` is provided, include transactions with `timestamp <= as_of`.
- If `transaction_id` is provided, include transactions up to and including that transaction.
- If neither is provided, return current holdings.
- If both `as_of` and `transaction_id` are provided, raise `ValidationError`.

Only `BUY` and `SELL` transactions affect holdings.

Validation:

- Account must exist.
- If `transaction_id` is provided, it must belong to the account.

---

### 6.11 Transaction History

```python
def list_transactions(self, account_id: str) -> list[Transaction]
```

Behavior:

- Return account transactions in chronological order.
- Return a copy of the transaction list.

Optional filtering method:

```python
def list_transactions_by_type(
    self,
    account_id: str,
    transaction_type: TransactionType,
) -> list[Transaction]
```

---

### 6.12 Portfolio Valuation

```python
def calculate_holdings_value(self, account_id: str) -> Decimal
```

Behavior:

- Sum `quantity * current_price` for all current holdings.

---

```python
def calculate_total_value(self, account_id: str) -> Decimal
```

Behavior:

- Return `cash_balance + calculate_holdings_value(account_id)`.

---

```python
def calculate_net_cash_contributions(self, account_id: str) -> Decimal
```

Behavior:

- Sum cash movements from:
  - `CREATE_ACCOUNT`
  - `DEPOSIT`
  - `WITHDRAW`
- Exclude:
  - `BUY`
  - `SELL`

Formula:

```text
initial deposit + deposits - withdrawals
```

---

```python
def calculate_profit_loss_from_initial_deposit(self, account_id: str) -> Decimal
```

Behavior:

- Return current total account value minus initial deposit.

---

```python
def calculate_profit_loss_excluding_cash_flows(self, account_id: str) -> Decimal
```

Behavior:

- Return current total account value minus net cash contributions.

---

```python
def get_portfolio_summary(self, account_id: str) -> PortfolioSummary
```

Behavior:

- Return all key valuation fields in one object.

---

## 7. Formatting Helpers for Frontend

Backend can include pure helper functions that convert values to UI-friendly strings. These should be simple and deterministic.

```python
def format_money(amount: Decimal) -> str
```

Expected output examples:

```text
$1,000.00
-$250.00
```

```python
def transaction_to_row(transaction: Transaction) -> list[str]
```

Suggested columns:

```text
Timestamp
Type
Symbol
Quantity
Price
Cash Amount
Cash Balance After
Description
Transaction ID
```

```python
def holding_report_row_to_row(row: HoldingReportRow) -> list[str]
```

Suggested columns:

```text
Symbol
Quantity
Current Price
Market Value
```

```python
def portfolio_summary_to_rows(summary: PortfolioSummary) -> list[list[str]]
```

Suggested rows:

```text
Cash Balance
Holdings Value
Total Account Value
Initial Deposit
Net Cash Contributions
P/L From Initial Deposit
P/L Excluding Cash Flows
```

---

## 8. Frontend Design

### File: `app.py`

Owner: `frontend_engineer`

Build a Gradio app using `gradio`.

The frontend should import only from `backend.py`.

Use one global in-memory service instance:

```python
service = AccountService()
```

The app does not need persistent storage.

---

## 9. Gradio 6 API Guidance

The frontend engineer should use the current Gradio `Blocks` style.

### 9.1 Recommended App Structure

Use:

```python
with gr.Blocks(title="Trading Simulation Account Manager") as demo:
```

Then finish with:

```python
demo.launch()
```

Do not use old `gr.Interface` unless the UI is extremely simple. This app is stateful and multi-action, so `Blocks` is preferred.

---

### 9.2 Components to Use

Recommended components:

| UI Need | Gradio Component |
|---|---|
| Text input | `gr.Textbox` |
| Number input | `gr.Number` |
| Dropdown account selector | `gr.Dropdown` |
| Button | `gr.Button` |
| Status messages | `gr.Markdown` or `gr.Textbox` |
| Tables | `gr.Dataframe` |
| Static section headers | `gr.Markdown` |
| Layout | `gr.Row`, `gr.Column`, `gr.Tab`, `gr.Tabs` |

Example component signatures to follow conceptually:

```python
gr.Textbox(label="Owner Name", placeholder="Jane Doe")
```

```python
gr.Number(label="Initial Deposit", precision=2)
```

```python
gr.Dropdown(label="Account", choices=[], value=None, interactive=True)
```

```python
gr.Button("Create Account", variant="primary")
```

```python
gr.Dataframe(headers=[...], value=[], interactive=False)
```

```python
gr.Markdown("...")
```

Important:

- In modern Gradio, component updates should be returned using `gr.update(...)`.
- To update dropdown choices, return:

```python
gr.update(choices=new_choices, value=selected_value)
```

- Prefer `interactive=False` for output-only tables.
- Use `precision=0` for integer-like `gr.Number` quantity inputs if needed.
- Gradio inputs may return `float`, `int`, `str`, or `None`; wrapper functions must validate and convert before calling backend methods.

---

### 9.3 Button Event Binding

Use `.click(...)` on buttons.

Conceptual event signature:

```python
button.click(
    fn=handler_function,
    inputs=[component_a, component_b],
    outputs=[component_x, component_y],
)
```

For multiple outputs, the handler must return the same number of values as listed in `outputs`.

Do not rely on deprecated patterns like directly mutating component objects after launch.

---

### 9.4 State

This app can use a module-level `service = AccountService()` and does not strictly need `gr.State`.

If using `gr.State`, use it only for simple values such as selected account ID. Do not put unnecessary duplicated account data in state because the backend service already owns source-of-truth state.

Recommended:

- Use `gr.Dropdown` to hold selected account ID.
- Refresh all reports from backend after each action.

---

### 9.5 Dataframe Guidance

Use Dataframes for holdings, transactions, and portfolio summary.

Recommended construction:

```python
gr.Dataframe(
    headers=["Symbol", "Quantity", "Current Price", "Market Value"],
    value=[],
    interactive=False,
)
```

For portfolio summary:

```python
gr.Dataframe(
    headers=["Metric", "Value"],
    value=[],
    interactive=False,
)
```

For transactions:

```python
gr.Dataframe(
    headers=[
        "Timestamp",
        "Type",
        "Symbol",
        "Quantity",
        "Price",
        "Cash Amount",
        "Cash Balance After",
        "Description",
        "Transaction ID",
    ],
    value=[],
    interactive=False,
)
```

Return plain Python lists of lists to `gr.Dataframe`.

---

## 10. Frontend Layout

### 10.1 Page Header

At the top:

```text
Trading Simulation Account Manager
```

Show a short description:

```text
Create an account, deposit or withdraw funds, buy and sell shares, and view your simulated portfolio.
```

---

### 10.2 Account Section

Components:

```python
owner_name_input: gr.Textbox
initial_deposit_input: gr.Number
create_account_button: gr.Button
account_dropdown: gr.Dropdown
refresh_button: gr.Button
status_output: gr.Markdown
```

Expected behavior:

- User enters owner name and initial deposit.
- Clicking create account:
  - Calls backend `create_account`.
  - Updates account dropdown choices.
  - Selects the new account.
  - Refreshes portfolio summary, holdings, and transactions.
  - Shows success or error message.

---

### 10.3 Cash Management Tab

Components:

```python
cash_amount_input: gr.Number
deposit_button: gr.Button
withdraw_button: gr.Button
```

Expected behavior:

- Deposit button calls backend `deposit`.
- Withdraw button calls backend `withdraw`.
- Both refresh all reports.
- Errors are shown in status area.

---

### 10.4 Trading Tab

Components:

```python
symbol_input: gr.Textbox
quantity_input: gr.Number
buy_button: gr.Button
sell_button: gr.Button
```

Expected behavior:

- Buy button calls backend `buy_shares`.
- Sell button calls backend `sell_shares`.
- Both refresh all reports.
- Errors are shown in status area.

Suggested UI hint:

```text
Supported symbols: AAPL, TSLA, GOOGL
```

---

### 10.5 Reports Tab

Components:

```python
portfolio_summary_df: gr.Dataframe
holdings_df: gr.Dataframe
transactions_df: gr.Dataframe
```

Also include a historical holdings section:

```python
historical_transaction_id_input: gr.Textbox
historical_holdings_button: gr.Button
historical_holdings_df: gr.Dataframe
```

Historical holdings behavior:

- User enters a transaction ID.
- Backend calls `get_holdings_at(account_id, transaction_id=entered_id)`.
- Display resulting holdings as rows with columns:
  - `Symbol`
  - `Quantity`

---

## 11. Frontend Handler Function Signatures

All frontend handlers live in `app.py`.

### 11.1 Utility Functions

```python
def account_choices() -> list[tuple[str, str]]
```

Behavior:

- Return dropdown choices for all accounts.
- Recommended label format:
  - `"Jane Doe - abc123"`
- Recommended value:
  - account ID

---

```python
def empty_reports() -> tuple[list[list[str]], list[list[str]], list[list[str]]]
```

Returns empty values for:

```text
portfolio summary rows
holdings rows
transaction rows
```

---

```python
def build_portfolio_summary_rows(account_id: str | None) -> list[list[str]]
```

---

```python
def build_holdings_rows(account_id: str | None) -> list[list[str]]
```

---

```python
def build_transaction_rows(account_id: str | None) -> list[list[str]]
```

---

```python
def build_all_report_rows(
    account_id: str | None,
) -> tuple[list[list[str]], list[list[str]], list[list[str]]]
```

Returns:

```text
portfolio_summary_rows
holdings_rows
transaction_rows
```

---

```python
def success_message(message: str) -> str
```

Returns Markdown-formatted success text.

---

```python
def error_message(error: Exception) -> str
```

Returns Markdown-formatted error text.

---

### 11.2 Account Handlers

```python
def handle_create_account(
    owner_name: str,
    initial_deposit: float | int | None,
) -> tuple[
    object,
    str,
    list[list[str]],
    list[list[str]],
    list[list[str]],
]
```

Outputs:

```text
account_dropdown update
status markdown
portfolio summary rows
holdings rows
transaction rows
```

Behavior:

- Calls `service.create_account`.
- Updates dropdown choices with `gr.update(...)`.
- Selects newly created account.
- Refreshes reports.
- On error, keep dropdown selection unchanged if possible and return empty or current reports.

---

```python
def handle_refresh(
    account_id: str | None,
) -> tuple[
    object,
    str,
    list[list[str]],
    list[list[str]],
    list[list[str]],
]
```

Outputs:

```text
account_dropdown update
status markdown
portfolio summary rows
holdings rows
transaction rows
```

Behavior:

- Refresh dropdown choices and reports.
- If no account selected, show helpful message.

---

```python
def handle_account_changed(
    account_id: str | None,
) -> tuple[
    str,
    list[list[str]],
    list[list[str]],
    list[list[str]],
]
```

Outputs:

```text
status markdown
portfolio summary rows
holdings rows
transaction rows
```

---

### 11.3 Cash Handlers

```python
def handle_deposit(
    account_id: str | None,
    amount: float | int | None,
) -> tuple[str, list[list[str]], list[list[str]], list[list[str]]]
```

Outputs:

```text
status markdown
portfolio summary rows
holdings rows
transaction rows
```

---

```python
def handle_withdraw(
    account_id: str | None,
    amount: float | int | None,
) -> tuple[str, list[list[str]], list[list[str]], list[list[str]]]
```

Outputs:

```text
status markdown
portfolio summary rows
holdings rows
transaction rows
```

---

### 11.4 Trading Handlers

```python
def handle_buy(
    account_id: str | None,
    symbol: str,
    quantity: float | int | None,
) -> tuple[str, list[list[str]], list[list[str]], list[list[str]]]
```

Behavior:

- Convert Gradio number value to integer.
- Reject missing or non-integer quantity before backend call.

---

```python
def handle_sell(
    account_id: str | None,
    symbol: str,
    quantity: float | int | None,
) -> tuple[str, list[list[str]], list[list[str]], list[list[str]]]
```

---

### 11.5 Historical Holdings Handler

```python
def handle_historical_holdings(
    account_id: str | None,
    transaction_id: str,
) -> tuple[str, list[list[str]]]
```

Outputs:

```text
status markdown
historical holdings rows
```

Behavior:

- Calls backend `get_holdings_at(account_id, transaction_id=transaction_id)`.
- Displays rows:
  - `Symbol`
  - `Quantity`

---

## 12. Frontend Event Wiring

### 12.1 Create Account Button

```python
create_account_button.click(
    fn=handle_create_account,
    inputs=[owner_name_input, initial_deposit_input],
    outputs=[
        account_dropdown,
        status_output,
        portfolio_summary_df,
        holdings_df,
        transactions_df,
    ],
)
```

---

### 12.2 Account Dropdown Change

```python
account_dropdown.change(
    fn=handle_account_changed,
    inputs=[account_dropdown],
    outputs=[
        status_output,
        portfolio_summary_df,
        holdings_df,
        transactions_df,
    ],
)
```

---

### 12.3 Refresh Button

```python
refresh_button.click(
    fn=handle_refresh,
    inputs=[account_dropdown],
    outputs=[
        account_dropdown,
        status_output,
        portfolio_summary_df,
        holdings_df,
        transactions_df,
    ],
)
```

---

### 12.4 Deposit Button

```python
deposit_button.click(
    fn=handle_deposit,
    inputs=[account_dropdown, cash_amount_input],
    outputs=[
        status_output,
        portfolio_summary_df,
        holdings_df,
        transactions_df,
    ],
)
```

---

### 12.5 Withdraw Button

```python
withdraw_button.click(
    fn=handle_withdraw,
    inputs=[account_dropdown, cash_amount_input],
    outputs=[
        status_output,
        portfolio_summary_df,
        holdings_df,
        transactions_df,
    ],
)
```

---

### 12.6 Buy Button

```python
buy_button.click(
    fn=handle_buy,
    inputs=[account_dropdown, symbol_input, quantity_input],
    outputs=[
        status_output,
        portfolio_summary_df,
        holdings_df,
        transactions_df,
    ],
)
```

---

### 12.7 Sell Button

```python
sell_button.click(
    fn=handle_sell,
    inputs=[account_dropdown, symbol_input, quantity_input],
    outputs=[
        status_output,
        portfolio_summary_df,
        holdings_df,
        transactions_df,
    ],
)
```

---

### 12.8 Historical Holdings Button

```python
historical_holdings_button.click(
    fn=handle_historical_holdings,
    inputs=[account_dropdown, historical_transaction_id_input],
    outputs=[
        status_output,
        historical_holdings_df,
    ],
)
```

---

## 13. Test Design

### File: `test_backend.py`

Owner: `test_engineer`

Use Python standard-library `unittest`.

Do not test Gradio.

Test only `backend.py`.

---

## 14. Test Setup

Each test should create a fresh `AccountService`.

Use deterministic prices.

Either use default `get_share_price` or inject a test lookup function.

Recommended injected function signature:

```python
def fixed_price_lookup(symbol: str) -> Decimal
```

Suggested test prices:

| Symbol | Price |
|---|---:|
| `AAPL` | `100.00` |
| `TSLA` | `200.00` |
| `GOOGL` | `1000.00` |

---

## 15. Required Unit Tests

### 15.1 Account Creation

```python
def test_create_account_sets_initial_cash_and_empty_holdings(self) -> None
```

Verify:

- Account has owner name.
- Cash balance equals initial deposit.
- Initial deposit stored correctly.
- Holdings are empty.
- One transaction exists.
- Transaction type is `CREATE_ACCOUNT`.

---

```python
def test_create_account_rejects_blank_owner_name(self) -> None
```

Expect:

- `ValidationError`

---

```python
def test_create_account_rejects_non_positive_initial_deposit(self) -> None
```

Expect:

- `ValidationError`

---

### 15.2 Deposits

```python
def test_deposit_increases_cash_and_records_transaction(self) -> None
```

Verify:

- Cash balance increased.
- Transaction type is `DEPOSIT`.
- Transaction cash amount is positive.

---

```python
def test_deposit_rejects_non_positive_amount(self) -> None
```

Expect:

- `ValidationError`

---

### 15.3 Withdrawals

```python
def test_withdraw_decreases_cash_and_records_transaction(self) -> None
```

Verify:

- Cash balance decreased.
- Transaction type is `WITHDRAW`.
- Transaction cash amount is negative.

---

```python
def test_withdraw_rejects_amount_greater_than_cash_balance(self) -> None
```

Expect:

- `InsufficientFundsError`

---

```python
def test_withdraw_rejects_non_positive_amount(self) -> None
```

Expect:

- `ValidationError`

---

### 15.4 Buying Shares

```python
def test_buy_shares_decreases_cash_and_increases_holdings(self) -> None
```

Example:

- Initial deposit: `1000.00`
- Buy 3 AAPL at `100.00`
- Expected cash: `700.00`
- Expected holdings: `{"AAPL": 3}`

---

```python
def test_buy_shares_records_transaction_with_price_quantity_and_symbol(self) -> None
```

Verify:

- Transaction type is `BUY`
- Symbol is normalized uppercase
- Quantity is correct
- Price is correct
- Cash amount is negative total cost

---

```python
def test_buy_shares_rejects_insufficient_funds(self) -> None
```

Expect:

- `InsufficientFundsError`

---

```python
def test_buy_shares_rejects_non_positive_quantity(self) -> None
```

Expect:

- `ValidationError`

---

```python
def test_buy_shares_rejects_unknown_symbol(self) -> None
```

Expect:

- `UnknownSymbolError`

---

### 15.5 Selling Shares

```python
def test_sell_shares_increases_cash_and_decreases_holdings(self) -> None
```

Example:

- Initial deposit: `1000.00`
- Buy 5 AAPL at `100.00`
- Sell 2 AAPL at `100.00`
- Expected cash: `700.00`
- Expected holdings: `{"AAPL": 3}`

---

```python
def test_sell_all_shares_removes_or_zeroes_holding(self) -> None
```

Verify:

- Selling all shares leaves no positive holding.
- `get_holdings()` should not include zero-quantity rows.

---

```python
def test_sell_shares_rejects_more_than_owned(self) -> None
```

Expect:

- `InsufficientSharesError`

---

```python
def test_sell_shares_rejects_non_positive_quantity(self) -> None
```

Expect:

- `ValidationError`

---

### 15.6 Portfolio Valuation

```python
def test_calculate_holdings_value(self) -> None
```

Example:

- Buy 2 AAPL at `100.00`
- Buy 1 TSLA at `200.00`
- Holdings value should be `400.00`.

---

```python
def test_calculate_total_value(self) -> None
```

Verify:

- Total value equals cash plus current holdings value.

---

```python
def test_profit_loss_excluding_cash_flows_is_zero_when_prices_unchanged(self) -> None
```

Because fixed buy and valuation prices are equal, expected P/L excluding cash flows is zero after buying.

---

```python
def test_profit_loss_excluding_cash_flows_handles_deposits_and_withdrawals(self) -> None
```

Verify:

- Deposits and withdrawals do not incorrectly appear as trading profit.

---

### 15.7 Holdings Reports

```python
def test_get_holdings_returns_copy(self) -> None
```

Verify:

- Mutating returned holdings does not mutate internal service/account state.

---

```python
def test_get_holdings_report_includes_market_value(self) -> None
```

Verify:

- Row has symbol, quantity, current price, and market value.

---

### 15.8 Historical Holdings

```python
def test_get_holdings_at_transaction_id(self) -> None
```

Example:

- Create account.
- Buy 5 AAPL.
- Save buy transaction ID.
- Buy 2 TSLA.
- Get holdings at first buy transaction.
- Expected holdings: `{"AAPL": 5}`.

---

```python
def test_get_holdings_at_rejects_unknown_transaction_id(self) -> None
```

Expect:

- `ValidationError`

---

```python
def test_get_holdings_at_rejects_both_as_of_and_transaction_id(self) -> None
```

Expect:

- `ValidationError`

---

### 15.9 Transaction History

```python
def test_list_transactions_returns_chronological_transactions(self) -> None
```

Verify:

- Transactions are returned in order created.

---

```python
def test_list_transactions_returns_copy(self) -> None
```

Verify:

- Mutating returned list does not mutate internal transaction history.

---

### 15.10 Account Lookup

```python
def test_get_missing_account_raises_account_not_found(self) -> None
```

Expect:

- `AccountNotFoundError`

---

## 16. Engineer Assignments

## 16.1 `backend_engineer`

Create `backend.py`.

Responsibilities:

1. Implement all backend exceptions.
2. Implement `TransactionType`.
3. Implement dataclasses:
   - `Transaction`
   - `Account`
   - `HoldingReportRow`
   - `PortfolioSummary`
4. Implement `get_share_price(symbol)`.
5. Implement `AccountService`.
6. Implement formatting helper functions:
   - `format_money`
   - `transaction_to_row`
   - `holding_report_row_to_row`
   - `portfolio_summary_to_rows`
7. Ensure all backend methods raise explicit exceptions rather than returning error strings.
8. Ensure all money values use `Decimal`.
9. Ensure all returned mutable collections are defensive copies.
10. Ensure transaction history is complete and ordered.

Acceptance criteria:

- Unit tests in `test_backend.py` pass.
- Backend can be imported by `app.py`.
- No Gradio dependency in `backend.py`.

---

## 16.2 `frontend_engineer`

Create `app.py`.

Responsibilities:

1. Import backend service and helper functions.
2. Create global service instance:
   - `service = AccountService()`
3. Build Gradio `Blocks` app.
4. Implement all frontend handler functions listed in this design.
5. Use `gr.update(...)` for dropdown updates.
6. Use `gr.Dataframe` for:
   - Portfolio summary
   - Holdings
   - Transactions
   - Historical holdings
7. Catch backend exceptions and display clear error messages.
8. Refresh reports after every successful backend mutation.
9. Provide helpful empty-state messages when no account is selected.
10. Include supported symbol hint:
    - `AAPL`
    - `TSLA`
    - `GOOGL`

Acceptance criteria:

- Running `uv run python app.py` starts the Gradio app.
- User can create account.
- User can deposit and withdraw.
- User can buy and sell shares.
- UI prevents invalid operations by surfacing backend errors.
- Portfolio summary, holdings, and transaction tables update after actions.
- Historical holdings lookup by transaction ID works.

---

## 16.3 `test_engineer`

Create `test_backend.py`.

Responsibilities:

1. Use standard-library `unittest`.
2. Test backend only.
3. Cover success cases and validation failures.
4. Use fresh `AccountService` for each test.
5. Use deterministic injected price lookup.
6. Verify transaction details.
7. Verify holdings and cash balances.
8. Verify portfolio valuation and P/L calculations.
9. Verify historical holdings.
10. Verify returned collections are copies.

Acceptance criteria:

- Running `uv run python -m unittest test_backend.py` passes.
- Tests are deterministic.
- Tests do not require Gradio.
- Tests do not depend on execution order.

---

## 17. Shared Integration Expectations

The completed system should support this scenario end-to-end:

1. Create account:
   - Owner: `Jane`
   - Initial deposit: `$10,000`
2. Buy:
   - `10` shares of `AAPL`
3. Buy:
   - `2` shares of `TSLA`
4. View holdings:
   - `AAPL: 10`
   - `TSLA: 2`
5. View transaction list:
   - Account creation
   - Buy AAPL
   - Buy TSLA
6. View portfolio summary:
   - Cash balance
   - Holdings value
   - Total value
   - P/L values
7. Attempt invalid withdrawal larger than cash:
   - Should fail with clear error.
8. Attempt invalid sale of `GOOGL` when none owned:
   - Should fail with clear error.
9. Sell some AAPL:
   - Cash increases.
   - AAPL holdings decrease.
   - Transaction list updates.
10. Historical holdings lookup using earlier transaction ID:
   - Shows holdings as of that transaction.

---

## 18. Non-Goals

Do not implement:

- Authentication
- Persistent database storage
- Real market data APIs
- Fractional shares
- Transaction fees
- Short selling
- Margin
- Multiple currencies
- Concurrent multi-user server persistence
- Passwords or personally identifiable user profiles beyond display owner name

---

## 19. Success Criteria

The project is complete when:

1. `backend.py` provides a clean tested account/trading backend.
2. `test_backend.py` passes with `unittest`.
3. `app.py` launches a working Gradio app.
4. Users can:
   - Create accounts
   - Deposit funds
   - Withdraw funds
   - Buy shares
   - Sell shares
   - View current holdings
   - View historical holdings by transaction ID
   - View all transactions
   - View portfolio value and profit/loss
5. Invalid actions are prevented with explicit, user-readable errors.