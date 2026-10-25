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
    AccountError,
    SUPPORTED_SYMBOLS,
)

# ----------------------------------------------------------------------------
# Service (single in-memory user instance)
# ----------------------------------------------------------------------------

service = AccountService()

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
}

.dark {
    --brand-surface: rgba(32, 157, 215, 0.12);
    --brand-border: rgba(32, 157, 215, 0.40);
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

/* Summary area */
#summary-output {
    border-radius: 10px;
    padding: 12px 16px;
    border: 1px solid var(--brand-border);
    background: var(--brand-surface);
}
#summary-output h3 { color: var(--brand-blue); margin-top: 0 !important; }
.dark #summary-output h3 { color: #7dc8ea; }

/* Dataframes */
.gradio-container table thead th {
    background: rgba(32, 157, 215, 0.12) !important;
    color: var(--brand-blue) !important;
    font-weight: 600 !important;
}
.dark .gradio-container table thead th { color: #7dc8ea !important; }

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
# Formatting helpers
# ----------------------------------------------------------------------------

def format_money(value: float) -> str:
    """Format a float as currency text, handling negatives nicely."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "—"
    if v < 0:
        return f"-${abs(v):,.2f}"
    return f"${v:,.2f}"


def format_summary(account_id: str) -> str:
    """Return markdown summary for account using service.get_account_summary."""
    summary = service.get_account_summary(account_id)
    pl = summary["profit_loss"]
    pl_emoji = "🟢" if pl > 0 else ("🔴" if pl < 0 else "⚪")
    return (
        "### Account Summary\n\n"
        f"- **Account ID:** `{summary['account_id']}`\n"
        f"- **Cash Balance:** {format_money(summary['cash_balance'])}\n"
        f"- **Holdings Value:** {format_money(summary['holdings_value'])}\n"
        f"- **Portfolio Value:** {format_money(summary['portfolio_value'])}\n"
        f"- **Total Deposited:** {format_money(summary['total_deposited'])}\n"
        f"- **Profit / Loss:** {pl_emoji} {format_money(pl)}"
    )


def build_holdings_rows(account_id: str) -> list[list[object]]:
    report = service.get_holdings_report(account_id)
    return [
        [
            row["symbol"],
            row["quantity"],
            format_money(row["current_price"]),
            format_money(row["market_value"]),
        ]
        for row in report
    ]


def build_transaction_rows(account_id: str) -> list[list[object]]:
    report = service.get_transactions_report(account_id)
    rows: list[list[object]] = []
    for t in report:
        rows.append(
            [
                t["transaction_id"],
                t["timestamp"],
                t["transaction_type"],
                format_money(t["amount"]) if t["amount"] is not None else "—",
                t["symbol"] if t["symbol"] is not None else "—",
                t["quantity"] if t["quantity"] is not None else "—",
                format_money(t["price"]) if t["price"] is not None else "—",
                format_money(t["cash_balance_after"]),
            ]
        )
    return rows


def empty_tables() -> tuple[list[list[object]], list[list[object]]]:
    return [], []


def info_message(message: str) -> str:
    return f"ℹ️ {message}"


def success_message(message: str) -> str:
    return f"✅ **Success:** {message}"


def error_message(error: Exception) -> str:
    return f"⚠️ **Error:** {error}"


# ----------------------------------------------------------------------------
# Core refresh handler
# ----------------------------------------------------------------------------

def refresh_view(
    account_id: str,
) -> tuple[str, str, list[list[object]], list[list[object]]]:
    """Refresh status, summary, holdings table, and transactions table."""
    if not account_id or not account_id.strip():
        return (
            info_message("Enter an account ID and create or refresh an account."),
            "",
            *empty_tables(),
        )
    try:
        summary_md = format_summary(account_id)
        holdings = build_holdings_rows(account_id)
        transactions = build_transaction_rows(account_id)
        return (
            success_message(f"Refreshed account '{account_id.strip()}'."),
            summary_md,
            holdings,
            transactions,
        )
    except AccountError as e:
        return error_message(e), "", *empty_tables()


# ----------------------------------------------------------------------------
# Operation handlers
# ----------------------------------------------------------------------------

def handle_create_account(
    account_id: str,
    initial_deposit: float,
) -> tuple[str, str, list[list[object]], list[list[object]]]:
    try:
        deposit = float(initial_deposit) if initial_deposit is not None else 0.0
        service.create_account(account_id, deposit)
        _status, summary, holdings, txs = refresh_view(account_id)
        return (
            success_message(
                f"Account '{account_id.strip()}' created"
                + (f" with initial deposit of {format_money(deposit)}." if deposit > 0 else ".")
            ),
            summary,
            holdings,
            txs,
        )
    except AccountError as e:
        return error_message(e), "", *empty_tables()


def handle_deposit(
    account_id: str,
    amount: float,
) -> tuple[str, str, list[list[object]], list[list[object]]]:
    try:
        amt = float(amount) if amount is not None else 0.0
        service.deposit(account_id, amt)
        _status, summary, holdings, txs = refresh_view(account_id)
        return (
            success_message(f"Deposited {format_money(amt)}."),
            summary,
            holdings,
            txs,
        )
    except AccountError as e:
        # Preserve existing tables when possible
        _s, summary, holdings, txs = refresh_view(account_id) if account_id else ("", "", [], [])
        return error_message(e), summary, holdings, txs


def handle_withdraw(
    account_id: str,
    amount: float,
) -> tuple[str, str, list[list[object]], list[list[object]]]:
    try:
        amt = float(amount) if amount is not None else 0.0
        service.withdraw(account_id, amt)
        _status, summary, holdings, txs = refresh_view(account_id)
        return (
            success_message(f"Withdrew {format_money(amt)}."),
            summary,
            holdings,
            txs,
        )
    except AccountError as e:
        _s, summary, holdings, txs = refresh_view(account_id) if account_id else ("", "", [], [])
        return error_message(e), summary, holdings, txs


def _coerce_quantity(quantity: float) -> int:
    if quantity is None:
        raise AccountError("Quantity is required.")
    q_float = float(quantity)
    q_int = int(q_float)
    if q_int != q_float:
        raise AccountError("Quantity must be a whole number.")
    return q_int


def handle_buy(
    account_id: str,
    symbol: str,
    quantity: float,
) -> tuple[str, str, list[list[object]], list[list[object]]]:
    try:
        qty = _coerce_quantity(quantity)
        service.buy_shares(account_id, symbol, qty)
        _status, summary, holdings, txs = refresh_view(account_id)
        return (
            success_message(f"Bought {qty} share(s) of {str(symbol).upper().strip()}."),
            summary,
            holdings,
            txs,
        )
    except AccountError as e:
        _s, summary, holdings, txs = refresh_view(account_id) if account_id else ("", "", [], [])
        return error_message(e), summary, holdings, txs


def handle_sell(
    account_id: str,
    symbol: str,
    quantity: float,
) -> tuple[str, str, list[list[object]], list[list[object]]]:
    try:
        qty = _coerce_quantity(quantity)
        service.sell_shares(account_id, symbol, qty)
        _status, summary, holdings, txs = refresh_view(account_id)
        return (
            success_message(f"Sold {qty} share(s) of {str(symbol).upper().strip()}."),
            summary,
            holdings,
            txs,
        )
    except AccountError as e:
        _s, summary, holdings, txs = refresh_view(account_id) if account_id else ("", "", [], [])
        return error_message(e), summary, holdings, txs


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
                    gr.Markdown("### Account", elem_classes=["section-title"])
                    account_id_input = gr.Textbox(
                        label="Account ID",
                        placeholder="example: alice",
                    )
                    initial_deposit_input = gr.Number(
                        label="Initial Deposit ($)",
                        value=10000,
                        precision=2,
                        minimum=0,
                    )
                    with gr.Row():
                        create_account_button = gr.Button(
                            "Create Account", variant="primary"
                        )
                        refresh_button = gr.Button("🔄 Refresh", variant="secondary")

            with gr.Column(scale=1):
                with gr.Group(elem_classes=["brand-card"]):
                    gr.Markdown("### Status", elem_classes=["section-title"])
                    status_output = gr.Markdown(
                        info_message("Create an account to get started."),
                        elem_id="status-output",
                    )

        with gr.Tabs():
            # ---- Cash Management -------------------------------------------
            with gr.Tab("💵 Cash"):
                gr.Markdown(
                    "Deposit funds into or withdraw funds from the account above. "
                    "Withdrawals cannot exceed the current cash balance."
                )
                with gr.Row():
                    with gr.Column():
                        deposit_amount_input = gr.Number(
                            label="Deposit Amount ($)",
                            value=100,
                            precision=2,
                            minimum=0,
                        )
                        deposit_button = gr.Button("Deposit", variant="primary")
                    with gr.Column():
                        withdraw_amount_input = gr.Number(
                            label="Withdraw Amount ($)",
                            value=100,
                            precision=2,
                            minimum=0,
                        )
                        withdraw_button = gr.Button("Withdraw", variant="secondary")

            # ---- Trading ---------------------------------------------------
            with gr.Tab("📊 Trading"):
                gr.Markdown(
                    f"**Supported symbols:** `{'` · `'.join(SUPPORTED_SYMBOLS)}` "
                    "— prices are fixed for this simulation."
                )
                with gr.Row():
                    symbol_dropdown = gr.Dropdown(
                        label="Symbol",
                        choices=list(SUPPORTED_SYMBOLS),
                        value="AAPL",
                    )
                    quantity_input = gr.Number(
                        label="Quantity (whole shares)",
                        value=1,
                        precision=0,
                        minimum=0,
                    )
                with gr.Row():
                    buy_button = gr.Button("Buy", variant="primary")
                    sell_button = gr.Button("Sell", variant="secondary")

            # ---- Reports ---------------------------------------------------
            with gr.Tab("📋 Reports"):
                summary_output = gr.Markdown(
                    "_Create or refresh an account to see its summary._",
                    elem_id="summary-output",
                )

                gr.Markdown("### Current Holdings", elem_classes=["section-title"])
                holdings_table = gr.Dataframe(
                    headers=["Symbol", "Quantity", "Current Price", "Market Value"],
                    value=[],
                    interactive=False,
                    wrap=True,
                )

                gr.Markdown("### Transactions", elem_classes=["section-title"])
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
                    value=[],
                    interactive=False,
                    wrap=True,
                )

        gr.Markdown(
            "Fixed simulation prices — AAPL $150 · TSLA $250 · GOOGL $2,800",
            elem_id="footer-caption",
        )

        # ---------------- Event wiring --------------------------------------
        common_outputs = [
            status_output,
            summary_output,
            holdings_table,
            transactions_table,
        ]

        create_account_button.click(
            fn=handle_create_account,
            inputs=[account_id_input, initial_deposit_input],
            outputs=common_outputs,
        )

        refresh_button.click(
            fn=refresh_view,
            inputs=[account_id_input],
            outputs=common_outputs,
        )

        deposit_button.click(
            fn=handle_deposit,
            inputs=[account_id_input, deposit_amount_input],
            outputs=common_outputs,
        )

        withdraw_button.click(
            fn=handle_withdraw,
            inputs=[account_id_input, withdraw_amount_input],
            outputs=common_outputs,
        )

        buy_button.click(
            fn=handle_buy,
            inputs=[account_id_input, symbol_dropdown, quantity_input],
            outputs=common_outputs,
        )

        sell_button.click(
            fn=handle_sell,
            inputs=[account_id_input, symbol_dropdown, quantity_input],
            outputs=common_outputs,
        )

    return demo


demo = build_demo()


if __name__ == "__main__":
    demo.launch()
