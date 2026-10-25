# Design: Simple Account Management System for Trading Simulation Platform

## 1. Overview

Build a simple in-memory trading account management application that allows a user to:

- Create an account.
- Deposit funds.
- Withdraw funds.
- Buy shares.
- Sell shares.
- View cash balance.
- View current holdings.
- View transaction history.
- Calculate total portfolio value.
- Calculate profit/loss relative to total deposited capital.
- Prevent invalid operations:
  - Cannot withdraw more cash than available.
  - Cannot buy shares without enough cash.
  - Cannot sell more shares than currently held.

The system will be implemented as a small Python backend plus a Gradio frontend.

All files must live in the same sandbox directory. No packages or subdirectories.

---

## 2. File Structure

The engineers should create the following files in the same directory:

| File | Owner | Purpose |
|---|---|---|
| `account_backend.py` | `backend_engineer` | Core account, transaction, pricing, validation, and portfolio logic |
| `app.py` | `frontend_engineer` | Gradio 6 app for interacting with the backend |
| `test_account_backend.py` | `test_engineer` | Unit tests for backend functionality |
| `README.md` | Shared, optional | Short usage notes if time permits |

---

## 3. Backend Design

### Owner

`backend_engineer`

### File

`account_backend.py`

### Core Requirements

The backend should be framework-independent and fully testable without Gradio.

It should expose a clean API that the frontend can call directly.

The system may store a single user account in memory. Multiple accounts are not required unless the engineer wants to keep the design extensible.

---

## 4. Backend Data Model

Use only the Python standard library.

Recommended imports:

- `dataclasses`
- `datetime`
- `typing`
- `uuid`

No third-party backend dependencies.

---

## 5. Backend Constants

### Supported Test Prices

The backend must include a test implementation of `get_share_price(symbol)` returning fixed prices for:

| Symbol | Price |
|---|---:|
| `AAPL` | `150.00` |
| `TSLA` | `250.00` |
| `GOOGL` | `2800.00` |

Unknown symbols should raise a clear error.

### Required Function Signature

```python
def get_share_price(symbol: str) -> float
```

### Behavior

- Normalize symbol to uppercase.
- Return the fixed price.
- Raise `ValueError` for unsupported symbols.

---

## 6. Backend Classes

### 6.1 `Transaction`

Represents one user action.

#### Class Signature

```python
@dataclass
class Transaction:
    transaction_id: str
    timestamp: datetime
    transaction_type: str
    symbol: str | None
    quantity: int | None
    price: float | None
    amount: float
    cash_balance_after: float
    description: str
```

#### Fields

| Field | Type | Description |
|---|---|---|
| `transaction_id` | `str` | Unique transaction ID |
| `timestamp` | `datetime` | Time of transaction |
| `transaction_type` | `str` | One of `"CREATE_ACCOUNT"`, `"DEPOSIT"`, `"WITHDRAW"`, `"BUY"`, `"SELL"` |
| `symbol` | `str \| None` | Share symbol for trades, otherwise `None` |
| `quantity` | `int \| None` | Share quantity for trades, otherwise `None` |
| `price` | `float \| None` | Per-share price for trades, otherwise `None` |
| `amount` | `float` | Cash value of transaction |
| `cash_balance_after` | `float` | Cash balance after transaction |
| `description` | `str` | Human-readable summary |

---

### 6.2 `Account`

Represents the user’s trading simulation account.

#### Class Signature

```python
@dataclass
class Account:
    account_id: str
    owner_name: str
    cash_balance: float
    total_deposited: float
    holdings: dict[str, int]
    transactions: list[Transaction]
    created_at: datetime
```

#### Fields

| Field | Type | Description |
|---|---|---|
| `account_id` | `str` | Unique account ID |
| `owner_name` | `str` | User display name |
| `cash_balance` | `float` | Available cash |
| `total_deposited` | `float` | Net deposited capital used for profit/loss calculation |
| `holdings` | `dict[str, int]` | Symbol-to-quantity map |
| `transactions` | `list[Transaction]` | Ordered transaction history |
| `created_at` | `datetime` | Account creation timestamp |

---

## 7. Backend Service Class

### 7.1 `AccountService`

This should be the primary API used by the Gradio app and tests.

#### Class Signature

```python
class AccountService:
```

### Constructor

```python
def __init__(self) -> None
```

#### Behavior

- Starts with no active account.
- Stores the current account as an instance field, such as `self.account`.

---

## 8. Backend Public Methods

### 8.1 Create Account

```python
def create_account(self, owner_name: str, initial_deposit: float) -> Account
```

#### Behavior

- Validate owner name is non-empty.
- Validate initial deposit is greater than or equal to zero.
- Create a new account.
- Set:
  - `cash_balance = initial_deposit`
  - `total_deposited = initial_deposit`
  - `holdings = {}`
  - `transactions = []`
- Add a `"CREATE_ACCOUNT"` transaction.
- If an account already exists, either:
  - Replace it with the new account, or
  - Raise `ValueError`.
- Recommended behavior: replace the existing account, because this keeps the frontend simple.

#### Validation Errors

- Empty owner name: `ValueError`
- Negative initial deposit: `ValueError`

---

### 8.2 Get Current Account

```python
def get_account(self) -> Account
```

#### Behavior

- Return the active account.
- Raise `ValueError` if no account has been created.

---

### 8.3 Deposit Funds

```python
def deposit(self, amount: float) -> Account
```

#### Behavior

- Require an existing account.
- Validate amount is greater than zero.
- Increase `cash_balance`.
- Increase `total_deposited`.
- Add a `"DEPOSIT"` transaction.

#### Validation Errors

- No account exists: `ValueError`
- Amount is zero or negative: `ValueError`

---

### 8.4 Withdraw Funds

```python
def withdraw(self, amount: float) -> Account
```

#### Behavior

- Require an existing account.
- Validate amount is greater than zero.
- Validate amount is not greater than `cash_balance`.
- Decrease `cash_balance`.
- Decrease `total_deposited` only if using a net-capital model.

#### Profit/Loss Policy

Use this policy for consistency:

```text
Profit/Loss = current total portfolio value - total_deposited
```

Where `total_deposited` means net external capital contributed.

Therefore:

- Deposits increase `total_deposited`.
- Withdrawals decrease `total_deposited`.
- `total_deposited` must not go below zero.

If withdrawal amount is greater than `total_deposited`, set `total_deposited` to zero rather than negative.

#### Validation Errors

- No account exists: `ValueError`
- Amount is zero or negative: `ValueError`
- Amount exceeds cash balance: `ValueError`

---

### 8.5 Buy Shares

```python
def buy(self, symbol: str, quantity: int) -> Account
```

#### Behavior

- Require an existing account.
- Normalize symbol to uppercase.
- Validate quantity is positive.
- Get current price with `get_share_price(symbol)`.
- Calculate total cost: `price * quantity`.
- Validate total cost is less than or equal to `cash_balance`.
- Decrease `cash_balance`.
- Increase holdings for that symbol.
- Add a `"BUY"` transaction.

#### Validation Errors

- No account exists: `ValueError`
- Unsupported symbol: `ValueError`
- Quantity is zero or negative: `ValueError`
- Total cost exceeds cash balance: `ValueError`

---

### 8.6 Sell Shares

```python
def sell(self, symbol: str, quantity: int) -> Account
```

#### Behavior

- Require an existing account.
- Normalize symbol to uppercase.
- Validate quantity is positive.
- Validate user owns the symbol.
- Validate quantity is less than or equal to current holding quantity.
- Get current price with `get_share_price(symbol)`.
- Calculate sale value: `price * quantity`.
- Increase `cash_balance`.
- Decrease holdings for that symbol.
- If quantity becomes zero, remove symbol from holdings or leave it with zero. Recommended: remove zero-quantity symbols.
- Add a `"SELL"` transaction.

#### Validation Errors

- No account exists: `ValueError`
- Unsupported symbol: `ValueError`
- Quantity is zero or negative: `ValueError`
- User does not own symbol: `ValueError`
- Quantity exceeds current holdings: `ValueError`

---

### 8.7 Get Holdings

```python
def get_holdings(self) -> dict[str, int]
```

#### Behavior

- Require an existing account.
- Return a copy of the holdings dictionary.
- Do not expose internal mutable state directly.

---

### 8.8 Get Holdings Report

```python
def get_holdings_report(self) -> list[dict[str, object]]
```

#### Behavior

Return a list of dictionaries suitable for display in Gradio.

Each row should include:

| Key | Type | Description |
|---|---|---|
| `symbol` | `str` | Stock symbol |
| `quantity` | `int` | Number of shares held |
| `current_price` | `float` | Current share price |
| `market_value` | `float` | `quantity * current_price` |

Example structure:

```python
[
    {
        "symbol": "AAPL",
        "quantity": 3,
        "current_price": 150.0,
        "market_value": 450.0,
    }
]
```

If there are no holdings, return an empty list.

---

### 8.9 Get Transactions

```python
def get_transactions(self) -> list[Transaction]
```

#### Behavior

- Require an existing account.
- Return a copy of the transaction list.

---

### 8.10 Get Transactions Report

```python
def get_transactions_report(self) -> list[dict[str, object]]
```

#### Behavior

Return a list of dictionaries suitable for display in Gradio.

Each row should include:

| Key | Type |
|---|---|
| `timestamp` | `str` |
| `type` | `str` |
| `symbol` | `str` |
| `quantity` | `int \| str` |
| `price` | `float \| str` |
| `amount` | `float` |
| `cash_balance_after` | `float` |
| `description` | `str` |

Format timestamp as a readable string.

Use empty string `""` for missing symbol, quantity, or price fields when building the report.

---

### 8.11 Calculate Cash Balance

```python
def get_cash_balance(self) -> float
```

#### Behavior

- Require an existing account.
- Return current cash balance.

---

### 8.12 Calculate Holdings Value

```python
def calculate_holdings_value(self) -> float
```

#### Behavior

- Require an existing account.
- For each symbol in holdings:
  - Get current price.
  - Multiply by quantity.
- Return total market value of all held shares.

---

### 8.13 Calculate Total Portfolio Value

```python
def calculate_portfolio_value(self) -> float
```

#### Behavior

Return:

```text
cash_balance + calculate_holdings_value()
```

---

### 8.14 Calculate Profit/Loss

```python
def calculate_profit_loss(self) -> float
```

#### Behavior

Return:

```text
calculate_portfolio_value() - total_deposited
```

---

### 8.15 Get Account Summary

```python
def get_account_summary(self) -> dict[str, object]
```

#### Behavior

Return a dictionary suitable for frontend display.

Required keys:

| Key | Type |
|---|---|
| `account_id` | `str` |
| `owner_name` | `str` |
| `cash_balance` | `float` |
| `holdings_value` | `float` |
| `portfolio_value` | `float` |
| `total_deposited` | `float` |
| `profit_loss` | `float` |
| `created_at` | `str` |

---

## 9. Backend Helper Functions

The backend may include the following helper functions.

### Generate ID

```python
def generate_id(prefix: str) -> str
```

#### Behavior

- Return a unique string like `"acct_..."` or `"txn_..."`.

---

### Validate Positive Amount

```python
def validate_positive_amount(amount: float, field_name: str = "amount") -> None
```

#### Behavior

- Raise `ValueError` if amount is not greater than zero.

---

### Validate Non-Negative Amount

```python
def validate_non_negative_amount(amount: float, field_name: str = "amount") -> None
```

#### Behavior

- Raise `ValueError` if amount is negative.

---

### Validate Positive Quantity

```python
def validate_positive_quantity(quantity: int) -> None
```

#### Behavior

- Raise `ValueError` if quantity is not an integer greater than zero.

---

### Normalize Symbol

```python
def normalize_symbol(symbol: str) -> str
```

#### Behavior

- Strip whitespace.
- Convert to uppercase.
- Raise `ValueError` if empty.

---

### Create Transaction

```python
def create_transaction(
    transaction_type: str,
    symbol: str | None,
    quantity: int | None,
    price: float | None,
    amount: float,
    cash_balance_after: float,
    description: str,
) -> Transaction
```

---

## 10. Frontend Design

### Owner

`frontend_engineer`

### File

`app.py`

### Framework

Use Gradio 6.

The app should import and use the backend service from `account_backend.py`.

```python
from account_backend import AccountService
```

Create one global service instance for the running app:

```python
service = AccountService()
```

No authentication or persistence is required.

---

## 11. Frontend User Experience

The Gradio app should provide:

1. Account creation form.
2. Deposit and withdraw controls.
3. Buy and sell controls.
4. Account summary display.
5. Holdings table.
6. Transaction history table.
7. Status/error message output.

Recommended layout:

- Title at top.
- Account management section.
- Funds section.
- Trading section.
- Summary section.
- Holdings section.
- Transactions section.

---

## 12. Gradio 6 API Guidance

The frontend engineer must follow Gradio 6 conventions.

### 12.1 Use `gr.Blocks`

Recommended app structure:

```python
with gr.Blocks() as demo:
    ...
demo.launch()
```

### 12.2 Event Binding

Use named keyword arguments for event handlers:

```python
button.click(fn=handler_function, inputs=[...], outputs=[...])
```

Valid Gradio 6 pattern:

```python
btn.click(fn=update, inputs=inp, outputs=out)
```

For multiple inputs and outputs:

```python
btn.click(fn=handler, inputs=[input_1, input_2], outputs=[output_1, output_2])
```

### 12.3 `gr.State`

Use `gr.State` only if needed. Since the backend service is global and in-memory, state is optional.

If session-level state is preferred, create:

```python
account_state = gr.State(None)
```

But the simpler design should use the global `service`.

### 12.4 `gr.Dataframe` Changes in Gradio 6

Important: Gradio 6 changed `gr.Dataframe` row and column parameters.

Do not use old Gradio 5 style:

```python
row_count=(5, "fixed")
col_count=(3, "fixed")
```

Use Gradio 6 style instead:

```python
gr.Dataframe(
    headers=[...],
    row_count=5,
    row_limits=None,
    column_count=4,
    column_limits=(4, 4),
)
```

Gradio 6 uses:

| Purpose | Gradio 6 Parameter |
|---|---|
| Initial rows | `row_count` |
| Min/max row constraint | `row_limits` |
| Initial columns | `column_count` |
| Min/max column constraint | `column_limits` |

For a fixed number of columns:

```python
column_count=4
column_limits=(4, 4)
```

For dynamic number of rows:

```python
row_limits=None
```

### 12.5 Recommended Component Constructors

Use these Gradio components:

#### Text Input

```python
gr.Textbox(label="Owner Name", placeholder="Enter your name")
```

#### Number Input

```python
gr.Number(label="Initial Deposit", value=10000)
```

#### Dropdown

```python
gr.Dropdown(
    choices=["AAPL", "TSLA", "GOOGL"],
    label="Symbol",
    value="AAPL",
)
```

#### Button

```python
gr.Button("Create Account")
```

#### Markdown

```python
gr.Markdown("# Trading Simulation Account Manager")
```

#### Dataframe

For holdings:

```python
gr.Dataframe(
    headers=["Symbol", "Quantity", "Current Price", "Market Value"],
    row_count=0,
    row_limits=None,
    column_count=4,
    column_limits=(4, 4),
    interactive=False,
    label="Holdings",
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
        "Amount",
        "Cash Balance After",
        "Description",
    ],
    row_count=0,
    row_limits=None,
    column_count=8,
    column_limits=(8, 8),
    interactive=False,
    label="Transactions",
)
```

### 12.6 Launch

Use:

```python
demo.launch()
```

No custom server settings are required.

---

## 13. Frontend Functions

The frontend should contain thin wrapper functions that call backend service methods and format outputs for Gradio.

### 13.1 Format Currency

```python
def format_currency(value: float) -> str
```

#### Behavior

Return a string like:

```text
$10,000.00
```

---

### 13.2 Format Summary Markdown

```python
def format_summary(summary: dict[str, object]) -> str
```

#### Behavior

Return a Markdown string showing:

- Account owner
- Account ID
- Cash balance
- Holdings value
- Total portfolio value
- Total deposited
- Profit/loss
- Created timestamp

Example display:

```markdown
### Account Summary

- **Owner:** Alice
- **Cash Balance:** $8,500.00
- **Holdings Value:** $1,500.00
- **Portfolio Value:** $10,000.00
- **Total Deposited:** $10,000.00
- **Profit/Loss:** $0.00
```

---

### 13.3 Convert Holdings Report to Rows

```python
def holdings_report_to_rows(report: list[dict[str, object]]) -> list[list[object]]
```

#### Behavior

Convert backend holdings dictionaries into Gradio Dataframe row lists:

```python
[
    ["AAPL", 3, 150.0, 450.0]
]
```

---

### 13.4 Convert Transactions Report to Rows

```python
def transactions_report_to_rows(report: list[dict[str, object]]) -> list[list[object]]
```

#### Behavior

Convert backend transaction dictionaries into Gradio Dataframe row lists.

---

### 13.5 Build Full UI State

```python
def build_ui_state(status_message: str) -> tuple[str, list[list[object]], list[list[object]], str]
```

#### Return Order

The return order should match the common frontend outputs:

1. Summary Markdown
2. Holdings table rows
3. Transactions table rows
4. Status message

#### Behavior

- Get account summary.
- Get holdings report.
- Get transactions report.
- Format all outputs.
- If account does not exist, return:
  - Empty or placeholder summary.
  - Empty holdings rows.
  - Empty transactions rows.
  - Status message.

---

## 14. Frontend Event Handler Functions

All handlers should catch `ValueError` and return friendly status messages instead of crashing the UI.

Each handler should return the same output tuple:

```python
tuple[str, list[list[object]], list[list[object]], str]
```

Where the outputs are:

1. Summary Markdown
2. Holdings table data
3. Transactions table data
4. Status message

---

### 14.1 Handle Create Account

```python
def handle_create_account(owner_name: str, initial_deposit: float) -> tuple[str, list[list[object]], list[list[object]], str]
```

#### Behavior

- Call `service.create_account(owner_name, initial_deposit)`.
- Return refreshed UI state with success message.

---

### 14.2 Handle Deposit

```python
def handle_deposit(amount: float) -> tuple[str, list[list[object]], list[list[object]], str]
```

#### Behavior

- Call `service.deposit(amount)`.
- Return refreshed UI state.

---

### 14.3 Handle Withdraw

```python
def handle_withdraw(amount: float) -> tuple[str, list[list[object]], list[list[object]], str]
```

#### Behavior

- Call `service.withdraw(amount)`.
- Return refreshed UI state.

---

### 14.4 Handle Buy

```python
def handle_buy(symbol: str, quantity: int | float) -> tuple[str, list[list[object]], list[list[object]], str]
```

#### Behavior

- Convert quantity to `int`.
- Call `service.buy(symbol, quantity)`.
- Return refreshed UI state.

---

### 14.5 Handle Sell

```python
def handle_sell(symbol: str, quantity: int | float) -> tuple[str, list[list[object]], list[list[object]], str]
```

#### Behavior

- Convert quantity to `int`.
- Call `service.sell(symbol, quantity)`.
- Return refreshed UI state.

---

### 14.6 Handle Refresh

```python
def handle_refresh() -> tuple[str, list[list[object]], list[list[object]], str]
```

#### Behavior

- Return refreshed UI state.

---

## 15. Frontend Component Layout

### 15.1 Suggested UI Components

#### Account Creation

Inputs:

- `owner_name_input = gr.Textbox(...)`
- `initial_deposit_input = gr.Number(...)`
- `create_account_button = gr.Button(...)`

#### Funds

Inputs:

- `deposit_amount_input = gr.Number(...)`
- `deposit_button = gr.Button(...)`
- `withdraw_amount_input = gr.Number(...)`
- `withdraw_button = gr.Button(...)`

#### Trading

Inputs:

- `trade_symbol_input = gr.Dropdown(...)`
- `trade_quantity_input = gr.Number(...)`
- `buy_button = gr.Button(...)`
- `sell_button = gr.Button(...)`

#### Outputs

- `summary_output = gr.Markdown(...)`
- `holdings_output = gr.Dataframe(...)`
- `transactions_output = gr.Dataframe(...)`
- `status_output = gr.Textbox(...)`

#### Refresh

- `refresh_button = gr.Button("Refresh")`

---

### 15.2 Event Wiring

Wire all operation buttons to the common outputs.

#### Create Account

```python
create_account_button.click(
    fn=handle_create_account,
    inputs=[owner_name_input, initial_deposit_input],
    outputs=[summary_output, holdings_output, transactions_output, status_output],
)
```

#### Deposit

```python
deposit_button.click(
    fn=handle_deposit,
    inputs=[deposit_amount_input],
    outputs=[summary_output, holdings_output, transactions_output, status_output],
)
```

#### Withdraw

```python
withdraw_button.click(
    fn=handle_withdraw,
    inputs=[withdraw_amount_input],
    outputs=[summary_output, holdings_output, transactions_output, status_output],
)
```

#### Buy

```python
buy_button.click(
    fn=handle_buy,
    inputs=[trade_symbol_input, trade_quantity_input],
    outputs=[summary_output, holdings_output, transactions_output, status_output],
)
```

#### Sell

```python
sell_button.click(
    fn=handle_sell,
    inputs=[trade_symbol_input, trade_quantity_input],
    outputs=[summary_output, holdings_output, transactions_output, status_output],
)
```

#### Refresh

```python
refresh_button.click(
    fn=handle_refresh,
    inputs=[],
    outputs=[summary_output, holdings_output, transactions_output, status_output],
)
```

---

## 16. Testing Design

### Owner

`test_engineer`

### File

`test_account_backend.py`

### Framework

Use Python standard library `unittest`.

Do not use `pytest` because no extra packages are guaranteed.

The tests should import from `account_backend.py`.

---

## 17. Required Unit Test Coverage

### 17.1 Price Function Tests

#### Test Function Signatures

```python
def test_get_share_price_known_symbols(self) -> None
```

Verify:

- `get_share_price("AAPL") == 150.0`
- `get_share_price("TSLA") == 250.0`
- `get_share_price("GOOGL") == 2800.0`
- Lowercase input works, e.g. `"aapl"`

```python
def test_get_share_price_unknown_symbol_raises(self) -> None
```

Verify:

- Unsupported symbol raises `ValueError`.

---

### 17.2 Account Creation Tests

```python
def test_create_account_success(self) -> None
```

Verify:

- Owner name is set.
- Cash balance equals initial deposit.
- Total deposited equals initial deposit.
- Holdings are empty.
- Transactions include a create account transaction.

```python
def test_create_account_rejects_empty_owner_name(self) -> None
```

```python
def test_create_account_rejects_negative_initial_deposit(self) -> None
```

---

### 17.3 Deposit Tests

```python
def test_deposit_success(self) -> None
```

Verify:

- Cash balance increases.
- Total deposited increases.
- Transaction is recorded.

```python
def test_deposit_rejects_non_positive_amount(self) -> None
```

```python
def test_deposit_requires_account(self) -> None
```

---

### 17.4 Withdraw Tests

```python
def test_withdraw_success(self) -> None
```

Verify:

- Cash balance decreases.
- Transaction is recorded.

```python
def test_withdraw_rejects_non_positive_amount(self) -> None
```

```python
def test_withdraw_rejects_amount_greater_than_cash_balance(self) -> None
```

```python
def test_withdraw_requires_account(self) -> None
```

---

### 17.5 Buy Tests

```python
def test_buy_success(self) -> None
```

Example:

- Create account with `1000`.
- Buy `2` AAPL at `150`.
- Verify cash balance is `700`.
- Verify holdings `{"AAPL": 2}`.
- Verify transaction is recorded.

```python
def test_buy_rejects_when_insufficient_cash(self) -> None
```

```python
def test_buy_rejects_non_positive_quantity(self) -> None
```

```python
def test_buy_rejects_unknown_symbol(self) -> None
```

```python
def test_buy_requires_account(self) -> None
```

---

### 17.6 Sell Tests

```python
def test_sell_success(self) -> None
```

Example:

- Create account with `1000`.
- Buy `2` AAPL.
- Sell `1` AAPL.
- Verify cash balance reflects sale.
- Verify holdings now contain `1` AAPL.
- Verify transaction is recorded.

```python
def test_sell_all_removes_symbol_from_holdings(self) -> None
```

```python
def test_sell_rejects_when_no_holdings_for_symbol(self) -> None
```

```python
def test_sell_rejects_quantity_greater_than_holdings(self) -> None
```

```python
def test_sell_rejects_non_positive_quantity(self) -> None
```

```python
def test_sell_requires_account(self) -> None
```

---

### 17.7 Portfolio Calculation Tests

```python
def test_calculate_holdings_value(self) -> None
```

Example:

- Buy `2` AAPL.
- Holdings value should be `300`.

```python
def test_calculate_portfolio_value(self) -> None
```

Example:

- Create account with `1000`.
- Buy `2` AAPL.
- Cash is `700`.
- Holdings value is `300`.
- Portfolio value is `1000`.

```python
def test_calculate_profit_loss(self) -> None
```

With fixed prices and no price movement, after buying shares, profit/loss should generally be `0`.

If withdrawals reduce `total_deposited`, verify the expected net capital behavior.

---

### 17.8 Report Tests

```python
def test_get_holdings_report(self) -> None
```

Verify:

- Report contains symbol, quantity, current price, and market value.

```python
def test_get_transactions_report(self) -> None
```

Verify:

- Transactions are returned in chronological insertion order.
- Expected transaction types are present.

```python
def test_get_account_summary(self) -> None
```

Verify:

- Summary includes all required keys.
- Values are correct.

---

## 18. Backend Error Handling Policy

The backend should raise `ValueError` for all user-correctable validation problems.

Examples:

- `"No account has been created."`
- `"Amount must be greater than zero."`
- `"Initial deposit cannot be negative."`
- `"Insufficient cash balance."`
- `"Insufficient shares to sell."`
- `"Unsupported symbol: MSFT"`

The frontend should catch these and show them in the status message.

---

## 19. Numeric Handling Policy

Use `float` for money in this simple simulation.

Round only for display. Keep raw calculations as floats.

Recommended display rounding:

- Currency: 2 decimal places.
- Prices: 2 decimal places.
- Market values: 2 decimal places.

Tests should use `assertAlmostEqual` for float comparisons.

---

## 20. Transaction Recording Rules

Every successful state-changing action must create exactly one transaction.

Actions that must create transactions:

- Create account.
- Deposit.
- Withdraw.
- Buy.
- Sell.

Failed actions must not create transactions.

---

## 21. Expected User Flow

1. User opens Gradio app.
2. User enters name and initial deposit.
3. User clicks **Create Account**.
4. Summary shows account details.
5. User deposits or withdraws funds.
6. User selects symbol and quantity.
7. User clicks **Buy** or **Sell**.
8. Holdings table updates.
9. Transaction table updates.
10. Portfolio value and profit/loss update.

---

## 22. Engineer Assignments

## `backend_engineer`

### Primary File

`account_backend.py`

### Responsibilities

Implement the full backend domain model and business logic.

### Required Deliverables

- `get_share_price(symbol: str) -> float`
- `Transaction` dataclass
- `Account` dataclass
- `AccountService` class
- All validation helpers
- All report/summary methods
- Clear `ValueError` messages
- No Gradio imports in backend

### Backend Acceptance Criteria

The backend is complete when:

- Accounts can be created.
- Deposits and withdrawals work.
- Invalid withdrawals are blocked.
- Buys and sells work.
- Invalid buys and sells are blocked.
- Holdings are accurate.
- Transactions are recorded in order.
- Portfolio value is calculated correctly.
- Profit/loss is calculated correctly.
- Backend tests pass.

---

## `frontend_engineer`

### Primary File

`app.py`

### Responsibilities

Build the Gradio 6 interface using the backend service.

### Required Deliverables

- Gradio Blocks app.
- Account creation controls.
- Deposit and withdrawal controls.
- Buy and sell controls.
- Account summary display.
- Holdings dataframe.
- Transactions dataframe.
- Status/error output.
- Event handlers that call backend service.
- Friendly error handling.

### Gradio 6 Reminders

- Use `gr.Blocks`.
- Use `button.click(fn=..., inputs=[...], outputs=[...])`.
- Use `column_count`, not old `col_count`.
- Use `row_limits` and `column_limits`, not old tuple-style `row_count=(..., "fixed")`.
- Use `demo.launch()`.

### Frontend Acceptance Criteria

The frontend is complete when:

- Running `uv run python app.py` launches the app.
- User can create an account.
- User can deposit funds.
- User can withdraw valid amounts.
- Invalid withdrawals show a friendly error.
- User can buy supported symbols.
- Invalid buys show a friendly error.
- User can sell shares they own.
- Invalid sells show a friendly error.
- Summary, holdings, and transaction tables update after each action.

---

## `test_engineer`

### Primary File

`test_account_backend.py`

### Responsibilities

Write unit tests for backend behavior using `unittest`.

### Required Deliverables

- Tests for pricing.
- Tests for account creation.
- Tests for deposits.
- Tests for withdrawals.
- Tests for buys.
- Tests for sells.
- Tests for portfolio calculations.
- Tests for holdings report.
- Tests for transaction report.
- Tests for account summary.
- Tests for invalid operation handling.

### Test Acceptance Criteria

The tests are complete when:

- They can be run with:

```bash
uv run python -m unittest test_account_backend.py
```

- They pass against the backend implementation.
- They verify both success paths and failure paths.
- They confirm failed operations do not incorrectly mutate state.

---

## 23. Integration Acceptance Criteria

The full system is successful when:

1. `uv run python -m unittest test_account_backend.py` passes.
2. `uv run python app.py` launches the Gradio app.
3. The app supports the complete user flow:
   - Create account.
   - Deposit funds.
   - Withdraw funds.
   - Buy shares.
   - Sell shares.
   - View holdings.
   - View transaction history.
   - View portfolio value.
   - View profit/loss.
4. Invalid actions are blocked:
   - Cannot withdraw more than cash balance.
   - Cannot buy more shares than cash can cover.
   - Cannot sell shares not owned.
   - Cannot trade unsupported symbols.
5. Backend code is independent from frontend code.
6. All files are in the same directory.