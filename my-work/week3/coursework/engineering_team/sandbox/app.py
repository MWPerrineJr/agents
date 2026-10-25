"""Gradio UI for the Trading Simulation Account Management backend.

Run with:  uv run python app.py
"""

from __future__ import annotations

import gradio as gr

from backend import (
    Account,
    holding_to_row,
    summary_to_rows,
    transaction_to_row,
)

# -----------------------------------------------------------------------------
# Color palette
# -----------------------------------------------------------------------------
# Primary brand colors (work in both light and dark mode):
#   #ecad0a  (gold)
#   #209dd7  (blue)
#   #753991  (purple)
# plus neutral grays.
GOLD = "#ecad0a"
BLUE = "#209dd7"
PURPLE = "#753991"

# -----------------------------------------------------------------------------
# Table headers
# -----------------------------------------------------------------------------
SUMMARY_HEADERS = ["Metric", "Value"]
HOLDINGS_HEADERS = ["Symbol", "Quantity", "Current Price", "Market Value"]
TRANSACTION_HEADERS = [
    "ID",
    "Timestamp",
    "Type",
    "Symbol",
    "Quantity",
    "Price",
    "Amount",
    "Cash Balance After",
]


# -----------------------------------------------------------------------------
# Display helpers
# -----------------------------------------------------------------------------
def empty_summary_rows() -> list[list[str]]:
    return []


def empty_holdings_rows() -> list[list[str]]:
    return []


def empty_transaction_rows() -> list[list[str]]:
    return []


def build_display_state(
    account: Account | None,
) -> tuple[list[list[object]], list[list[object]], list[list[object]]]:
    if account is None:
        return (
            empty_summary_rows(),
            empty_holdings_rows(),
            empty_transaction_rows(),
        )

    summary = account.get_portfolio_summary()
    profit_loss_from_initial = account.get_profit_loss_from_initial_deposit()
    summary_rows = summary_to_rows(summary, profit_loss_from_initial)
    holdings_rows = [holding_to_row(h) for h in account.get_holdings()]
    transaction_rows = [transaction_to_row(t) for t in account.get_transactions()]
    return summary_rows, holdings_rows, transaction_rows


# -----------------------------------------------------------------------------
# Event handlers
# -----------------------------------------------------------------------------
def handle_create_account(
    account_id: str,
    initial_deposit: float,
) -> tuple[Account | None, str, list[list[object]], list[list[object]], list[list[object]]]:
    try:
        account = Account(account_id or "", float(initial_deposit or 0))
        s, h, t = build_display_state(account)
        return (
            account,
            f"✅ Account '{account.account_id}' created with initial deposit ${account.initial_deposit:,.2f}.",
            s,
            h,
            t,
        )
    except ValueError as e:
        return None, f"⚠ {e}", [], [], []


def handle_deposit(
    account: Account | None,
    amount: float,
) -> tuple[Account | None, str, list[list[object]], list[list[object]], list[list[object]]]:
    if account is None:
        return None, "⚠ Please create an account first.", [], [], []
    try:
        account.deposit(float(amount or 0))
        s, h, t = build_display_state(account)
        return account, f"✅ Deposited ${float(amount):,.2f}.", s, h, t
    except ValueError as e:
        s, h, t = build_display_state(account)
        return account, f"⚠ {e}", s, h, t


def handle_withdraw(
    account: Account | None,
    amount: float,
) -> tuple[Account | None, str, list[list[object]], list[list[object]], list[list[object]]]:
    if account is None:
        return None, "⚠ Please create an account first.", [], [], []
    try:
        account.withdraw(float(amount or 0))
        s, h, t = build_display_state(account)
        return account, f"✅ Withdrew ${float(amount):,.2f}.", s, h, t
    except ValueError as e:
        s, h, t = build_display_state(account)
        return account, f"⚠ {e}", s, h, t


def handle_buy(
    account: Account | None,
    symbol: str,
    quantity: int | float,
) -> tuple[Account | None, str, list[list[object]], list[list[object]], list[list[object]]]:
    if account is None:
        return None, "⚠ Please create an account first.", [], [], []
    try:
        qty = int(quantity or 0)
        account.buy(symbol, qty)
        s, h, t = build_display_state(account)
        return account, f"✅ Bought {qty} share(s) of {symbol}.", s, h, t
    except ValueError as e:
        s, h, t = build_display_state(account)
        return account, f"⚠ {e}", s, h, t


def handle_sell(
    account: Account | None,
    symbol: str,
    quantity: int | float,
) -> tuple[Account | None, str, list[list[object]], list[list[object]], list[list[object]]]:
    if account is None:
        return None, "⚠ Please create an account first.", [], [], []
    try:
        qty = int(quantity or 0)
        account.sell(symbol, qty)
        s, h, t = build_display_state(account)
        return account, f"✅ Sold {qty} share(s) of {symbol}.", s, h, t
    except ValueError as e:
        s, h, t = build_display_state(account)
        return account, f"⚠ {e}", s, h, t


def handle_refresh(
    account: Account | None,
) -> tuple[str, list[list[object]], list[list[object]], list[list[object]]]:
    if account is None:
        return "⚠ Please create an account first.", [], [], []
    s, h, t = build_display_state(account)
    return "🔄 Refreshed.", s, h, t


# -----------------------------------------------------------------------------
# Theme & CSS
# -----------------------------------------------------------------------------
def build_theme() -> gr.themes.Base:
    """Theme that uses our palette as the primary hue and plays nicely in
    both light and dark mode."""
    return gr.themes.Soft(
        primary_hue=gr.themes.Color(
            c50="#fef7e0",
            c100="#fdecb3",
            c200="#fbdd80",
            c300="#f8cd4d",
            c400="#f5be26",
            c500=GOLD,   # #ecad0a
            c600="#c99408",
            c700="#a67a06",
            c800="#835f04",
            c900="#5f4603",
            c950="#3c2c02",
        ),
        secondary_hue=gr.themes.Color(
            c50="#e6f4fb",
            c100="#c0e3f5",
            c200="#96d1ef",
            c300="#6bbee8",
            c400="#48afe0",
            c500=BLUE,   # #209dd7
            c600="#1b85b7",
            c700="#166c95",
            c800="#115374",
            c900="#0b3a52",
            c950="#062231",
        ),
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
    )


# Custom CSS — uses CSS variables where possible so it adapts to the active
# theme (light / dark). Accent colors are kept as explicit hex values from the
# requested palette.
CUSTOM_CSS = f"""
:root {{
    --brand-gold: {GOLD};
    --brand-blue: {BLUE};
    --brand-purple: {PURPLE};
}}

/* App container */
.gradio-container {{
    max-width: 1180px !important;
    margin: 0 auto !important;
}}

/* Header banner */
#app-header {{
    background: linear-gradient(
        135deg,
        var(--brand-purple) 0%,
        var(--brand-blue) 55%,
        var(--brand-gold) 100%
    );
    color: #ffffff;
    padding: 22px 28px;
    border-radius: 14px;
    margin-bottom: 18px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.18);
}}
#app-header h1 {{
    margin: 0 0 4px 0;
    font-size: 1.75rem;
    font-weight: 700;
    letter-spacing: 0.2px;
    color: #ffffff !important;
}}
#app-header p {{
    margin: 0;
    opacity: 0.95;
    color: #f5f5f5 !important;
    font-size: 0.95rem;
}}

/* Status bar */
/* Pin the status message so feedback is visible after any button click */
#status-box {{
    position: sticky;
    top: 0;
    z-index: 100;
}}
#status-box textarea {{
    font-weight: 600;
    border-left: 4px solid var(--brand-blue) !important;
    background: var(--background-fill-secondary) !important;
    color: var(--body-text-color) !important;
}}

/* Tabs: accent color for the selected tab underline */
button.selected[role="tab"] {{
    color: var(--brand-blue) !important;
    border-bottom-color: var(--brand-blue) !important;
}}

/* Buttons — distinct colors per action, legible in both modes */
#btn-create button, #btn-create {{
    background: var(--brand-purple) !important;
    color: #ffffff !important;
    border: none !important;
}}
#btn-deposit button, #btn-deposit {{
    background: var(--brand-blue) !important;
    color: #ffffff !important;
    border: none !important;
}}
#btn-withdraw button, #btn-withdraw {{
    background: #6b7280 !important;  /* neutral gray */
    color: #ffffff !important;
    border: none !important;
}}
#btn-buy button, #btn-buy {{
    background: var(--brand-gold) !important;
    color: #1f2937 !important;       /* dark text for contrast on gold */
    border: none !important;
    font-weight: 600 !important;
}}
#btn-sell button, #btn-sell {{
    background: var(--brand-purple) !important;
    color: #ffffff !important;
    border: none !important;
}}
#btn-refresh button, #btn-refresh {{
    background: var(--brand-blue) !important;
    color: #ffffff !important;
    border: none !important;
}}

/* Dataframe polish */
.gr-dataframe table thead th {{
    background: var(--background-fill-secondary) !important;
    color: var(--body-text-color) !important;
    border-bottom: 2px solid var(--brand-blue) !important;
}}

/* Footer */
#app-footer {{
    text-align: center;
    padding: 14px 10px 6px 10px;
    color: var(--body-text-color-subdued);
    font-size: 0.85rem;
    opacity: 0.8;
}}
"""


# -----------------------------------------------------------------------------
# App builder
# -----------------------------------------------------------------------------
def build_app() -> gr.Blocks:
    # In Gradio 6, theme/css are passed to .launch(), not Blocks().
    with gr.Blocks(title="Trading Sim Account") as demo:
        # Header
        gr.HTML(
            """
            <div id="app-header">
                <h1>📈 Trading Simulation — Account Management</h1>
                <p>Create an account, manage cash, trade shares, and track your portfolio.</p>
            </div>
            """
        )

        account_state = gr.State(None)

        status_box = gr.Textbox(
            label="Status",
            value="Welcome! Start by creating an account in the Account tab.",
            interactive=False,
            elem_id="status-box",
            lines=1,
        )

        with gr.Tabs():
            # ---- Account tab ---------------------------------------------
            with gr.Tab("👤 Account"):
                gr.Markdown("### Create a new trading account")
                with gr.Row():
                    with gr.Column(scale=2):
                        account_id_box = gr.Textbox(
                            label="Account ID",
                            placeholder="e.g. demo-user",
                        )
                    with gr.Column(scale=2):
                        initial_deposit_box = gr.Number(
                            label="Initial Deposit ($)",
                            minimum=0,
                            value=10000,
                            step=100,
                        )
                    with gr.Column(scale=1, min_width=160):
                        create_button = gr.Button(
                            "Create Account",
                            variant="primary",
                            elem_id="btn-create",
                        )

            # ---- Cash tab ------------------------------------------------
            with gr.Tab("💵 Cash"):
                gr.Markdown("### Deposit or withdraw cash")
                with gr.Row():
                    with gr.Column():
                        deposit_amount = gr.Number(
                            label="Deposit Amount ($)",
                            minimum=0,
                            step=100,
                            value=1000,
                        )
                        deposit_button = gr.Button(
                            "Deposit",
                            variant="primary",
                            elem_id="btn-deposit",
                        )
                    with gr.Column():
                        withdraw_amount = gr.Number(
                            label="Withdraw Amount ($)",
                            minimum=0,
                            step=100,
                            value=500,
                        )
                        withdraw_button = gr.Button(
                            "Withdraw",
                            elem_id="btn-withdraw",
                        )

            # ---- Trade tab ----------------------------------------------
            with gr.Tab("📊 Trade"):
                gr.Markdown("### Buy or sell shares")
                with gr.Row():
                    symbol_dropdown = gr.Dropdown(
                        choices=["AAPL", "TSLA", "GOOGL"],
                        label="Symbol",
                        value="AAPL",
                    )
                    quantity = gr.Number(
                        label="Quantity",
                        minimum=1,
                        precision=0,
                        step=1,
                        value=1,
                    )
                with gr.Row():
                    buy_button = gr.Button(
                        "Buy",
                        variant="primary",
                        elem_id="btn-buy",
                    )
                    sell_button = gr.Button(
                        "Sell",
                        elem_id="btn-sell",
                    )
                gr.Markdown(
                    "_Fixed demo prices: **AAPL $150.00**, **TSLA $250.00**, **GOOGL $2,800.00**._"
                )

            # ---- Reports tab --------------------------------------------
            with gr.Tab("📑 Reports"):
                with gr.Row():
                    refresh_button = gr.Button(
                        "🔄 Refresh Reports",
                        variant="primary",
                        elem_id="btn-refresh",
                    )

                gr.Markdown("#### Portfolio Summary")
                summary_table = gr.Dataframe(
                    headers=SUMMARY_HEADERS,
                    datatype=["str", "str"],
                    value=[],
                    interactive=False,
                    wrap=True,
                )

                gr.Markdown("#### Current Holdings")
                holdings_table = gr.Dataframe(
                    headers=HOLDINGS_HEADERS,
                    datatype=["str", "number", "number", "number"],
                    value=[],
                    interactive=False,
                    wrap=True,
                )

                gr.Markdown("#### Transaction History")
                transactions_table = gr.Dataframe(
                    headers=TRANSACTION_HEADERS,
                    datatype=[
                        "number", "str", "str", "str",
                        "str", "str", "number", "number",
                    ],
                    value=[],
                    interactive=False,
                    wrap=True,
                )

        gr.HTML(
            '<div id="app-footer">Trading Simulation Platform · Demo · '
            'Single-user session · Powered by Gradio</div>'
        )

        # ---- Event wiring --------------------------------------------------
        report_outputs = [summary_table, holdings_table, transactions_table]
        state_outputs = [account_state, status_box, *report_outputs]

        create_button.click(
            fn=handle_create_account,
            inputs=[account_id_box, initial_deposit_box],
            outputs=state_outputs,
        )
        deposit_button.click(
            fn=handle_deposit,
            inputs=[account_state, deposit_amount],
            outputs=state_outputs,
        )
        withdraw_button.click(
            fn=handle_withdraw,
            inputs=[account_state, withdraw_amount],
            outputs=state_outputs,
        )
        buy_button.click(
            fn=handle_buy,
            inputs=[account_state, symbol_dropdown, quantity],
            outputs=state_outputs,
        )
        sell_button.click(
            fn=handle_sell,
            inputs=[account_state, symbol_dropdown, quantity],
            outputs=state_outputs,
        )
        refresh_button.click(
            fn=handle_refresh,
            inputs=[account_state],
            outputs=[status_box, *report_outputs],
        )

    return demo


if __name__ == "__main__":
    # In Gradio 6, theme and css are launch-time parameters.
    build_app().launch(theme=build_theme(), css=CUSTOM_CSS)
