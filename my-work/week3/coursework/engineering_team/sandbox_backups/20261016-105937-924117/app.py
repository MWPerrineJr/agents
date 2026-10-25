"""Gradio UI for the Trading Simulation Account Management system.

Run with: `uv run python app.py`

Color palette (works in light + dark mode):
    #ecad0a  - accent gold (primary action)
    #209dd7  - accent blue (secondary action / headers)
    #753991  - accent purple (highlight)
    neutral grays via Gradio's built-in theme tokens
"""

from __future__ import annotations

import gradio as gr

from backend import (
    AccountService,
    holding_report_row_to_row,
    portfolio_summary_to_rows,
    transaction_to_row,
)
from backend import ValidationError  # re-exported for use in handlers

# ----------------------------------------------------------------------------
# Service (single in-memory user instance)
# ----------------------------------------------------------------------------

service = AccountService()

SUPPORTED_SYMBOLS = ["AAPL", "TSLA", "GOOGL"]

# ----------------------------------------------------------------------------
# Theme: build off Gradio's Soft theme and inject our brand palette.
# The CSS below uses CSS custom properties so colors look great in both
# light and dark mode (Gradio toggles .dark on the root element).
# ----------------------------------------------------------------------------

THEME = gr.themes.Soft(
    primary_hue=gr.themes.Color(
        c50="#fff8e1",
        c100="#ffecb3",
        c200="#ffe082",
        c300="#ffd54f",
        c400="#ffca28",
        c500="#ecad0a",
        c600="#d49a09",
        c700="#a87a07",
        c800="#7a5805",
        c900="#4d3703",
        c950="#2d2002",
    ),
    secondary_hue=gr.themes.Color(
        c50="#e8f6fd",
        c100="#c5e7f8",
        c200="#9ed6f3",
        c300="#73c4ee",
        c400="#4bb3e8",
        c500="#209dd7",
        c600="#1b85b8",
        c700="#146790",
        c800="#0e4a68",
        c900="#082d40",
        c950="#041720",
    ),
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
)

CUSTOM_CSS = """
:root {
    --brand-gold: #ecad0a;
    --brand-blue: #209dd7;
    --brand-purple: #753991;
    --brand-surface: rgba(32, 157, 215, 0.06);
    --brand-border: rgba(32, 157, 215, 0.25);
    --brand-status-success-bg: rgba(236, 173, 10, 0.10);
    --brand-status-success-border: rgba(236, 173, 10, 0.45);
    --brand-status-error-bg: rgba(117, 57, 145, 0.10);
    --brand-status-error-border: rgba(117, 57, 145, 0.50);
}

.dark {
    --brand-surface: rgba(32, 157, 215, 0.12);
    --brand-border: rgba(32, 157, 215, 0.40);
    --brand-status-success-bg: rgba(236, 173, 10, 0.14);
    --brand-status-success-border: rgba(236, 173, 10, 0.55);
    --brand-status-error-bg: rgba(117, 57, 145, 0.20);
    --brand-status-error-border: rgba(117, 57, 145, 0.60);
}

/* App title bar */
#app-header {
    padding: 18px 22px;
    border-radius: 14px;
    background: linear-gradient(
        135deg,
        rgba(32, 157, 215, 0.18) 0%,
        rgba(117, 57, 145, 0.18) 55%,
        rgba(236, 173, 10, 0.18) 100%
    );
    border: 1px solid var(--brand-border);
    margin-bottom: 10px;
}
#app-header h1 {
    margin: 0 0 4px 0 !important;
    font-size: 1.65rem;
    color: var(--brand-blue);
    letter-spacing: -0.01em;
}
.dark #app-header h1 { color: #7dc8ea; }
#app-header p { margin: 0 !important; opacity: 0.85; }

/* Section cards */
.brand-card {
    border: 1px solid var(--brand-border) !important;
    background: var(--brand-surface) !important;
    border-radius: 12px !important;
    padding: 14px !important;
}

/* Section titles */
.section-title {
    color: var(--brand-purple);
    font-weight: 600;
    margin-bottom: 4px !important;
}
.dark .section-title { color: #c192d6; }

/* Status area */
#status-output {
    border-radius: 10px;
    padding: 10px 14px;
    border: 1px solid var(--brand-border);
    background: var(--brand-surface);
    min-height: 44px;
}
#status-output strong { color: var(--brand-purple); }
.dark #status-output strong { color: #d7b2e8; }

/* Dataframes */
.gradio-container table thead th {
    background: rgba(32, 157, 215, 0.12) !important;
    color: var(--brand-blue) !important;
    font-weight: 600 !important;
}
.dark .gradio-container table thead th { color: #7dc8ea !important; }

/* Buttons - secondary variant tinted blue */
button.secondary {
    border-color: var(--brand-blue) !important;
}

/* Tabs */
button.selected { color: var(--brand-gold) !important; }

/* Footer caption */
#footer-caption {
    text-align: center;
    opacity: 0.65;
    font-size: 0.85rem;
    margin-top: 6px;
}
"""


# ----------------------------------------------------------------------------
# Utility functions
# ----------------------------------------------------------------------------

def account_choices() -> list[tuple[str, str]]:
    """Return (label, value) pairs for the account dropdown."""
    accounts = service.list_accounts()
    return [
        (f"{acc.owner_name} — {acc.account_id[:8]}", acc.account_id)
        for acc in accounts
    ]


def empty_reports() -> tuple[list[list[str]], list[list[str]], list[list[str]]]:
    return [], [], []


def build_portfolio_summary_rows(account_id: str | None) -> list[list[str]]:
    if not account_id:
        return []
    summary = service.get_portfolio_summary(account_id)
    return portfolio_summary_to_rows(summary)


def build_holdings_rows(account_id: str | None) -> list[list[str]]:
    if not account_id:
        return []
    report = service.get_holdings_report(account_id)
    return [holding_report_row_to_row(r) for r in report]


def build_transaction_rows(account_id: str | None) -> list[list[str]]:
    if not account_id:
        return []
    transactions = service.list_transactions(account_id)
    # Newest first for easier reading in the UI
    return [transaction_to_row(tx) for tx in reversed(transactions)]


def build_all_report_rows(
    account_id: str | None,
) -> tuple[list[list[str]], list[list[str]], list[list[str]]]:
    if not account_id:
        return empty_reports()
    try:
        return (
            build_portfolio_summary_rows(account_id),
            build_holdings_rows(account_id),
            build_transaction_rows(account_id),
        )
    except Exception:
        return empty_reports()


def success_message(message: str) -> str:
    return f"✅ **Success:** {message}"


def info_message(message: str) -> str:
    return f"ℹ️ {message}"


def error_message(error: Exception) -> str:
    return f"⚠️ **Error:** {error}"


# ----------------------------------------------------------------------------
# Handlers
# ----------------------------------------------------------------------------

def handle_create_account(owner_name, initial_deposit):
    try:
        if initial_deposit is None:
            raise ValidationError("Initial deposit is required.")
        account = service.create_account(owner_name, initial_deposit)
        choices = account_choices()
        summary, holdings, txs = build_all_report_rows(account.account_id)
        return (
            gr.update(choices=choices, value=account.account_id),
            success_message(
                f"Account created for '{account.owner_name}' "
                f"with initial deposit of {initial_deposit}."
            ),
            summary,
            holdings,
            txs,
        )
    except Exception as e:
        return gr.update(choices=account_choices()), error_message(e), *empty_reports()


def handle_refresh(account_id):
    choices = account_choices()
    if not account_id:
        return (
            gr.update(choices=choices),
            info_message("Please select or create an account."),
            *empty_reports(),
        )
    try:
        summary, holdings, txs = build_all_report_rows(account_id)
        return (
            gr.update(choices=choices, value=account_id),
            success_message("Reports refreshed."),
            summary,
            holdings,
            txs,
        )
    except Exception as e:
        return gr.update(choices=choices), error_message(e), *empty_reports()


def handle_account_changed(account_id):
    if not account_id:
        return info_message("Please select or create an account."), *empty_reports()
    try:
        summary, holdings, txs = build_all_report_rows(account_id)
        return success_message("Account loaded."), summary, holdings, txs
    except Exception as e:
        return error_message(e), *empty_reports()


def handle_deposit(account_id, amount):
    if not account_id:
        return info_message("Please select an account first."), *empty_reports()
    try:
        if amount is None:
            raise ValidationError("Deposit amount is required.")
        service.deposit(account_id, amount)
        summary, holdings, txs = build_all_report_rows(account_id)
        return success_message(f"Deposited ${amount:,.2f}."), summary, holdings, txs
    except Exception as e:
        summary, holdings, txs = build_all_report_rows(account_id)
        return error_message(e), summary, holdings, txs


def handle_withdraw(account_id, amount):
    if not account_id:
        return info_message("Please select an account first."), *empty_reports()
    try:
        if amount is None:
            raise ValidationError("Withdrawal amount is required.")
        service.withdraw(account_id, amount)
        summary, holdings, txs = build_all_report_rows(account_id)
        return success_message(f"Withdrew ${amount:,.2f}."), summary, holdings, txs
    except Exception as e:
        summary, holdings, txs = build_all_report_rows(account_id)
        return error_message(e), summary, holdings, txs


def handle_buy(account_id, symbol, quantity):
    if not account_id:
        return info_message("Please select an account first."), *empty_reports()
    try:
        if quantity is None:
            raise ValidationError("Quantity is required.")
        qty_int = int(quantity)
        if qty_int != float(quantity):
            raise ValidationError("Quantity must be a whole number.")
        if not symbol or not symbol.strip():
            raise ValidationError("Symbol is required.")
        service.buy_shares(account_id, symbol, qty_int)
        summary, holdings, txs = build_all_report_rows(account_id)
        return (
            success_message(f"Bought {qty_int} share(s) of {symbol.upper()}."),
            summary,
            holdings,
            txs,
        )
    except Exception as e:
        summary, holdings, txs = build_all_report_rows(account_id)
        return error_message(e), summary, holdings, txs


def handle_sell(account_id, symbol, quantity):
    if not account_id:
        return info_message("Please select an account first."), *empty_reports()
    try:
        if quantity is None:
            raise ValidationError("Quantity is required.")
        qty_int = int(quantity)
        if qty_int != float(quantity):
            raise ValidationError("Quantity must be a whole number.")
        if not symbol or not symbol.strip():
            raise ValidationError("Symbol is required.")
        service.sell_shares(account_id, symbol, qty_int)
        summary, holdings, txs = build_all_report_rows(account_id)
        return (
            success_message(f"Sold {qty_int} share(s) of {symbol.upper()}."),
            summary,
            holdings,
            txs,
        )
    except Exception as e:
        summary, holdings, txs = build_all_report_rows(account_id)
        return error_message(e), summary, holdings, txs


def handle_historical_holdings(account_id, transaction_id):
    if not account_id:
        return info_message("Please select an account first."), []
    try:
        if not transaction_id or not transaction_id.strip():
            raise ValidationError("Transaction ID is required.")
        holdings = service.get_holdings_at(
            account_id, transaction_id=transaction_id.strip()
        )
        rows = [[sym, str(qty)] for sym, qty in holdings.items()]
        return (
            success_message(
                f"Holdings as of transaction {transaction_id.strip()[:8]}…"
            ),
            rows,
        )
    except Exception as e:
        return error_message(e), []


# ----------------------------------------------------------------------------
# UI
# ----------------------------------------------------------------------------

def build_demo() -> gr.Blocks:
    with gr.Blocks(
        title="Trading Simulation Account Manager",
        theme=THEME,
        css=CUSTOM_CSS,
    ) as demo:
        with gr.Group(elem_id="app-header"):
            gr.Markdown(
                "# 📈 Trading Simulation Account Manager\n"
                "Create an account, deposit or withdraw funds, buy and sell "
                "shares, and view your simulated portfolio in real time."
            )

        with gr.Row(equal_height=True):
            with gr.Column(scale=1):
                with gr.Group(elem_classes=["brand-card"]):
                    gr.Markdown(
                        "### Create a new account", elem_classes=["section-title"]
                    )
                    owner_name_input = gr.Textbox(
                        label="Owner Name", placeholder="Jane Doe"
                    )
                    initial_deposit_input = gr.Number(
                        label="Initial Deposit ($)",
                        precision=2,
                        value=10000,
                        minimum=0,
                    )
                    create_account_button = gr.Button(
                        "Create Account", variant="primary"
                    )

            with gr.Column(scale=1):
                with gr.Group(elem_classes=["brand-card"]):
                    gr.Markdown(
                        "### Active account", elem_classes=["section-title"]
                    )
                    account_dropdown = gr.Dropdown(
                        label="Account",
                        choices=[],
                        value=None,
                        interactive=True,
                    )
                    refresh_button = gr.Button("🔄 Refresh Reports")
                    status_output = gr.Markdown(
                        info_message("Create an account to get started."),
                        elem_id="status-output",
                    )

        with gr.Tabs():
            # ---- Cash Management -------------------------------------------
            with gr.Tab("💵 Cash Management"):
                gr.Markdown(
                    "Deposit funds into or withdraw funds from the selected "
                    "account. Withdrawals cannot exceed the current cash balance."
                )
                with gr.Row():
                    cash_amount_input = gr.Number(
                        label="Amount ($)", precision=2, value=100, minimum=0
                    )
                with gr.Row():
                    deposit_button = gr.Button("Deposit", variant="primary")
                    withdraw_button = gr.Button("Withdraw", variant="secondary")

            # ---- Trading ---------------------------------------------------
            with gr.Tab("📊 Trading"):
                gr.Markdown(
                    f"**Supported symbols:** `{'` · `'.join(SUPPORTED_SYMBOLS)}`"
                )
                with gr.Row():
                    symbol_input = gr.Dropdown(
                        label="Symbol",
                        choices=SUPPORTED_SYMBOLS,
                        value="AAPL",
                        allow_custom_value=True,
                    )
                    quantity_input = gr.Number(
                        label="Quantity (whole shares)",
                        precision=0,
                        value=1,
                        minimum=0,
                    )
                with gr.Row():
                    buy_button = gr.Button("Buy", variant="primary")
                    sell_button = gr.Button("Sell", variant="secondary")

            # ---- Reports ---------------------------------------------------
            with gr.Tab("📋 Reports"):
                gr.Markdown(
                    "### Portfolio Summary", elem_classes=["section-title"]
                )
                portfolio_summary_df = gr.Dataframe(
                    headers=["Metric", "Value"],
                    value=[],
                    interactive=False,
                    wrap=True,
                )

                gr.Markdown(
                    "### Current Holdings", elem_classes=["section-title"]
                )
                holdings_df = gr.Dataframe(
                    headers=[
                        "Symbol",
                        "Quantity",
                        "Current Price",
                        "Market Value",
                    ],
                    value=[],
                    interactive=False,
                    wrap=True,
                )

                gr.Markdown(
                    "### Transactions (newest first)",
                    elem_classes=["section-title"],
                )
                transactions_df = gr.Dataframe(
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
                    wrap=True,
                )

            # ---- Historical Holdings --------------------------------------
            with gr.Tab("🕰️ Historical Holdings"):
                gr.Markdown(
                    "View holdings as they were immediately after a specific "
                    "transaction. Copy a Transaction ID from the Reports tab."
                )
                historical_transaction_id_input = gr.Textbox(
                    label="Transaction ID",
                    placeholder="e.g. 1b2c3d4e-...",
                )
                historical_holdings_button = gr.Button(
                    "View Historical Holdings", variant="primary"
                )
                historical_holdings_df = gr.Dataframe(
                    headers=["Symbol", "Quantity"],
                    value=[],
                    interactive=False,
                    wrap=True,
                )

        gr.Markdown(
            "Prices are fixed for this simulation: "
            "AAPL $150 · TSLA $250 · GOOGL $2,800",
            elem_id="footer-caption",
        )

        # ---------------- Event wiring --------------------------------------
        report_outputs = [
            status_output,
            portfolio_summary_df,
            holdings_df,
            transactions_df,
        ]

        create_account_button.click(
            fn=handle_create_account,
            inputs=[owner_name_input, initial_deposit_input],
            outputs=[account_dropdown, *report_outputs],
        )

        account_dropdown.change(
            fn=handle_account_changed,
            inputs=[account_dropdown],
            outputs=report_outputs,
        )

        refresh_button.click(
            fn=handle_refresh,
            inputs=[account_dropdown],
            outputs=[account_dropdown, *report_outputs],
        )

        deposit_button.click(
            fn=handle_deposit,
            inputs=[account_dropdown, cash_amount_input],
            outputs=report_outputs,
        )

        withdraw_button.click(
            fn=handle_withdraw,
            inputs=[account_dropdown, cash_amount_input],
            outputs=report_outputs,
        )

        buy_button.click(
            fn=handle_buy,
            inputs=[account_dropdown, symbol_input, quantity_input],
            outputs=report_outputs,
        )

        sell_button.click(
            fn=handle_sell,
            inputs=[account_dropdown, symbol_input, quantity_input],
            outputs=report_outputs,
        )

        historical_holdings_button.click(
            fn=handle_historical_holdings,
            inputs=[account_dropdown, historical_transaction_id_input],
            outputs=[status_output, historical_holdings_df],
        )

    return demo


demo = build_demo()


if __name__ == "__main__":
    demo.launch()
