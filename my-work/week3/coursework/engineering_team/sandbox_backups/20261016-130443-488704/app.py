"""Gradio UI for the Trading Simulation Account Manager.

Run with:
    uv run python app.py
"""

from typing import Any, Dict, List, Tuple

import gradio as gr

from account_backend import AccountService, get_share_price


# ---------------------------------------------------------------------------
# Global single-user service instance
# ---------------------------------------------------------------------------
service = AccountService()

SUPPORTED_SYMBOLS = ["AAPL", "TSLA", "GOOGL"]

# Brand palette (chosen to work in both light & dark Gradio themes)
BRAND_GOLD = "#ecad0a"
BRAND_BLUE = "#209dd7"
BRAND_PURPLE = "#753991"


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------
def format_currency(value: float) -> str:
    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value)


def _pl_color(value: float) -> str:
    if value > 0:
        return BRAND_BLUE
    if value < 0:
        return BRAND_PURPLE
    return "var(--body-text-color)"


EMPTY_SUMMARY_MD = f"""
<div class="tsx-summary tsx-empty">
  <div class="tsx-summary-title">No account yet</div>
  <div class="tsx-summary-sub">
    Create an account below to start simulating trades on
    <b>AAPL</b>, <b>TSLA</b> or <b>GOOGL</b>.
  </div>
</div>
"""


def format_summary(summary: Dict[str, Any]) -> str:
    pl = float(summary.get("profit_loss", 0.0))
    pl_color = _pl_color(pl)
    pl_sign = "+" if pl > 0 else ("" if pl == 0 else "-")
    pl_display = f"{pl_sign}{format_currency(abs(pl))}"

    return f"""
<div class="tsx-summary">
  <div class="tsx-summary-header">
    <div>
      <div class="tsx-summary-eyebrow">Account</div>
      <div class="tsx-summary-name">{summary.get("owner_name", "")}</div>
      <div class="tsx-summary-id">{summary.get("account_id", "")}</div>
    </div>
    <div class="tsx-portfolio-value">
      <div class="tsx-summary-eyebrow">Portfolio Value</div>
      <div class="tsx-big-number">{format_currency(summary.get("portfolio_value", 0.0))}</div>
    </div>
  </div>

  <div class="tsx-metrics">
    <div class="tsx-metric">
      <div class="tsx-metric-label">Cash Balance</div>
      <div class="tsx-metric-value">{format_currency(summary.get("cash_balance", 0.0))}</div>
    </div>
    <div class="tsx-metric">
      <div class="tsx-metric-label">Holdings Value</div>
      <div class="tsx-metric-value">{format_currency(summary.get("holdings_value", 0.0))}</div>
    </div>
    <div class="tsx-metric">
      <div class="tsx-metric-label">Total Deposited</div>
      <div class="tsx-metric-value">{format_currency(summary.get("total_deposited", 0.0))}</div>
    </div>
    <div class="tsx-metric">
      <div class="tsx-metric-label">Profit / Loss</div>
      <div class="tsx-metric-value" style="color:{pl_color};">{pl_display}</div>
    </div>
  </div>

  <div class="tsx-summary-footer">Created at {summary.get("created_at", "")}</div>
</div>
"""


def holdings_report_to_rows(report: List[Dict[str, Any]]) -> List[List[Any]]:
    rows: List[List[Any]] = []
    for row in report:
        rows.append(
            [
                row.get("symbol", ""),
                int(row.get("quantity", 0)),
                format_currency(row.get("current_price", 0.0)),
                format_currency(row.get("market_value", 0.0)),
            ]
        )
    return rows


def transactions_report_to_rows(report: List[Dict[str, Any]]) -> List[List[Any]]:
    rows: List[List[Any]] = []
    for row in report:
        qty = row.get("quantity", "")
        price = row.get("price", "")
        rows.append(
            [
                row.get("timestamp", ""),
                row.get("type", ""),
                row.get("symbol", "") or "",
                qty if qty != "" else "",
                format_currency(price) if price != "" else "",
                format_currency(row.get("amount", 0.0)),
                format_currency(row.get("cash_balance_after", 0.0)),
                row.get("description", ""),
            ]
        )
    # Show newest first for readability
    rows.reverse()
    return rows


# ---------------------------------------------------------------------------
# UI state assembly
# ---------------------------------------------------------------------------
def build_ui_state(
    status_message: str,
) -> Tuple[str, List[List[Any]], List[List[Any]], str]:
    try:
        summary = service.get_account_summary()
        holdings = service.get_holdings_report()
        transactions = service.get_transactions_report()
        return (
            format_summary(summary),
            holdings_report_to_rows(holdings),
            transactions_report_to_rows(transactions),
            status_message,
        )
    except ValueError:
        return (EMPTY_SUMMARY_MD, [], [], status_message)


# ---------------------------------------------------------------------------
# Event handlers
# ---------------------------------------------------------------------------
def handle_create_account(
    owner_name: str, initial_deposit: float
) -> Tuple[str, List[List[Any]], List[List[Any]], str]:
    try:
        account = service.create_account(owner_name, float(initial_deposit or 0))
        msg = f"✓ Account created for {account.owner_name} with {format_currency(initial_deposit or 0)}."
    except ValueError as e:
        return build_ui_state(f"✗ {e}")
    return build_ui_state(msg)


def handle_deposit(
    amount: float,
) -> Tuple[str, List[List[Any]], List[List[Any]], str]:
    try:
        service.deposit(float(amount or 0))
        msg = f"✓ Deposited {format_currency(amount or 0)}."
    except ValueError as e:
        return build_ui_state(f"✗ {e}")
    return build_ui_state(msg)


def handle_withdraw(
    amount: float,
) -> Tuple[str, List[List[Any]], List[List[Any]], str]:
    try:
        service.withdraw(float(amount or 0))
        msg = f"✓ Withdrew {format_currency(amount or 0)}."
    except ValueError as e:
        return build_ui_state(f"✗ {e}")
    return build_ui_state(msg)


def handle_buy(
    symbol: str, quantity: float
) -> Tuple[str, List[List[Any]], List[List[Any]], str]:
    try:
        qty = int(quantity or 0)
        service.buy(symbol, qty)
        msg = f"✓ Bought {qty} share(s) of {symbol}."
    except ValueError as e:
        return build_ui_state(f"✗ {e}")
    return build_ui_state(msg)


def handle_sell(
    symbol: str, quantity: float
) -> Tuple[str, List[List[Any]], List[List[Any]], str]:
    try:
        qty = int(quantity or 0)
        service.sell(symbol, qty)
        msg = f"✓ Sold {qty} share(s) of {symbol}."
    except ValueError as e:
        return build_ui_state(f"✗ {e}")
    return build_ui_state(msg)


def handle_refresh() -> Tuple[str, List[List[Any]], List[List[Any]], str]:
    return build_ui_state("↻ Refreshed.")


def handle_price_lookup(symbol: str) -> str:
    try:
        price = get_share_price(symbol)
        return f"**{symbol.upper()}** — current price: **{format_currency(price)}**"
    except ValueError as e:
        return f"✗ {e}"


# ---------------------------------------------------------------------------
# Theme & CSS
# ---------------------------------------------------------------------------
CUSTOM_CSS = f"""
:root {{
  --tsx-gold: {BRAND_GOLD};
  --tsx-blue: {BRAND_BLUE};
  --tsx-purple: {BRAND_PURPLE};
}}

/* ---------- Header ---------- */
.tsx-header {{
  background: linear-gradient(135deg, {BRAND_PURPLE} 0%, {BRAND_BLUE} 100%);
  color: #ffffff !important;
  border-radius: 14px;
  padding: 22px 28px;
  margin-bottom: 10px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.12);
}}
.tsx-header h1 {{
  margin: 0 0 4px 0;
  font-size: 1.8rem;
  color: #ffffff !important;
  letter-spacing: 0.2px;
}}
.tsx-header .tsx-subtitle {{
  color: rgba(255,255,255,0.9) !important;
  font-size: 0.95rem;
  margin: 0;
}}
.tsx-header .tsx-accent {{
  color: {BRAND_GOLD} !important;
  font-weight: 700;
}}

/* ---------- Summary card ---------- */
.tsx-summary {{
  border: 1px solid var(--border-color-primary);
  border-radius: 14px;
  padding: 20px 22px;
  background: var(--background-fill-secondary);
}}
.tsx-summary.tsx-empty {{
  text-align: center;
  padding: 32px 22px;
  border-style: dashed;
}}
.tsx-summary-title {{
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--body-text-color);
}}
.tsx-summary-sub {{
  margin-top: 6px;
  color: var(--body-text-color-subdued);
  font-size: 0.95rem;
}}
.tsx-summary-header {{
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  flex-wrap: wrap;
}}
.tsx-summary-eyebrow {{
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.72rem;
  color: var(--body-text-color-subdued);
  margin-bottom: 2px;
}}
.tsx-summary-name {{
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--body-text-color);
}}
.tsx-summary-id {{
  font-family: var(--font-mono);
  font-size: 0.78rem;
  color: var(--body-text-color-subdued);
  margin-top: 2px;
}}
.tsx-portfolio-value {{
  text-align: right;
}}
.tsx-big-number {{
  font-size: 1.9rem;
  font-weight: 700;
  color: {BRAND_BLUE};
}}

.tsx-metrics {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  margin-top: 18px;
}}
.tsx-metric {{
  background: var(--background-fill-primary);
  border: 1px solid var(--border-color-primary);
  border-radius: 10px;
  padding: 12px 14px;
}}
.tsx-metric-label {{
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--body-text-color-subdued);
  margin-bottom: 4px;
}}
.tsx-metric-value {{
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--body-text-color);
}}
.tsx-summary-footer {{
  margin-top: 16px;
  font-size: 0.78rem;
  color: var(--body-text-color-subdued);
}}

/* ---------- Section headers ---------- */
.tsx-section-title {{
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--body-text-color);
  border-left: 4px solid {BRAND_GOLD};
  padding-left: 10px;
  margin: 4px 0 8px 0;
}}

/* ---------- Buttons ---------- */
.tsx-btn-primary button {{
  background: {BRAND_BLUE} !important;
  color: #ffffff !important;
  border: none !important;
}}
.tsx-btn-primary button:hover {{
  background: #1b86b8 !important;
}}
.tsx-btn-gold button {{
  background: {BRAND_GOLD} !important;
  color: #202020 !important;
  border: none !important;
}}
.tsx-btn-gold button:hover {{
  background: #d49a08 !important;
}}
.tsx-btn-purple button {{
  background: {BRAND_PURPLE} !important;
  color: #ffffff !important;
  border: none !important;
}}
.tsx-btn-purple button:hover {{
  background: #633079 !important;
}}

/* ---------- Status pill ---------- */
.tsx-status textarea {{
  background: var(--background-fill-secondary) !important;
  border: 1px solid var(--border-color-primary) !important;
  color: var(--body-text-color) !important;
  font-weight: 500;
}}

/* ---------- Price badge ---------- */
.tsx-price-badge {{
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px dashed {BRAND_GOLD};
  background: var(--background-fill-secondary);
  color: var(--body-text-color);
}}
"""

THEME = gr.themes.Soft(
    primary_hue=gr.themes.colors.sky,
    secondary_hue=gr.themes.colors.purple,
    neutral_hue=gr.themes.colors.slate,
)


# ---------------------------------------------------------------------------
# Build the Blocks UI
# ---------------------------------------------------------------------------
def build_demo() -> gr.Blocks:
    with gr.Blocks(theme=THEME, css=CUSTOM_CSS, title="Trading Simulation") as demo:
        gr.HTML(
            """
            <div class="tsx-header">
              <h1>📈 Trading Simulation <span class="tsx-accent">Account Manager</span></h1>
              <p class="tsx-subtitle">
                Create an account, manage funds, and trade AAPL, TSLA, and GOOGL in a safe sandbox.
              </p>
            </div>
            """
        )

        # ---- Summary (always visible) ----
        summary_output = gr.HTML(value=EMPTY_SUMMARY_MD)

        # ---- Status / messages ----
        status_output = gr.Textbox(
            label="Status",
            value="Welcome! Start by creating an account below.",
            interactive=False,
            lines=1,
            elem_classes=["tsx-status"],
        )

        with gr.Row():
            # LEFT column: action panels
            with gr.Column(scale=1):
                # Account creation
                gr.HTML('<div class="tsx-section-title">1. Create Account</div>')
                with gr.Group():
                    owner_name_input = gr.Textbox(
                        label="Owner Name",
                        placeholder="e.g. Alice Johnson",
                    )
                    initial_deposit_input = gr.Number(
                        label="Initial Deposit ($)",
                        value=10000,
                        minimum=0,
                        precision=2,
                    )
                    create_account_button = gr.Button(
                        "Create Account",
                        elem_classes=["tsx-btn-primary"],
                    )

                # Funds
                gr.HTML('<div class="tsx-section-title">2. Manage Funds</div>')
                with gr.Group():
                    with gr.Row():
                        deposit_amount_input = gr.Number(
                            label="Deposit ($)", value=1000, minimum=0, precision=2
                        )
                        withdraw_amount_input = gr.Number(
                            label="Withdraw ($)", value=500, minimum=0, precision=2
                        )
                    with gr.Row():
                        deposit_button = gr.Button(
                            "Deposit", elem_classes=["tsx-btn-gold"]
                        )
                        withdraw_button = gr.Button(
                            "Withdraw", elem_classes=["tsx-btn-purple"]
                        )

                # Trading
                gr.HTML('<div class="tsx-section-title">3. Trade Shares</div>')
                with gr.Group():
                    trade_symbol_input = gr.Dropdown(
                        choices=SUPPORTED_SYMBOLS,
                        value="AAPL",
                        label="Symbol",
                    )
                    trade_quantity_input = gr.Number(
                        label="Quantity",
                        value=1,
                        minimum=1,
                        step=1,
                        precision=0,
                    )
                    price_badge = gr.Markdown(
                        value="**AAPL** — current price: **$150.00**",
                        elem_classes=["tsx-price-badge"],
                    )
                    with gr.Row():
                        buy_button = gr.Button(
                            "Buy", elem_classes=["tsx-btn-primary"]
                        )
                        sell_button = gr.Button(
                            "Sell", elem_classes=["tsx-btn-purple"]
                        )

                refresh_button = gr.Button(
                    "↻ Refresh View", elem_classes=["tsx-btn-gold"]
                )

            # RIGHT column: tables
            with gr.Column(scale=2):
                gr.HTML('<div class="tsx-section-title">Holdings</div>')
                holdings_output = gr.Dataframe(
                    headers=["Symbol", "Quantity", "Current Price", "Market Value"],
                    row_count=0,
                    row_limits=None,
                    column_count=4,
                    column_limits=(4, 4),
                    interactive=False,
                    wrap=True,
                )

                gr.HTML('<div class="tsx-section-title">Transaction History</div>')
                transactions_output = gr.Dataframe(
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
                    wrap=True,
                )

        # Common output tuple
        common_outputs = [
            summary_output,
            holdings_output,
            transactions_output,
            status_output,
        ]

        # ---- Event wiring ----
        create_account_button.click(
            fn=handle_create_account,
            inputs=[owner_name_input, initial_deposit_input],
            outputs=common_outputs,
        )
        deposit_button.click(
            fn=handle_deposit,
            inputs=[deposit_amount_input],
            outputs=common_outputs,
        )
        withdraw_button.click(
            fn=handle_withdraw,
            inputs=[withdraw_amount_input],
            outputs=common_outputs,
        )
        buy_button.click(
            fn=handle_buy,
            inputs=[trade_symbol_input, trade_quantity_input],
            outputs=common_outputs,
        )
        sell_button.click(
            fn=handle_sell,
            inputs=[trade_symbol_input, trade_quantity_input],
            outputs=common_outputs,
        )
        refresh_button.click(
            fn=handle_refresh,
            inputs=[],
            outputs=common_outputs,
        )

        # Live price badge update when the symbol changes
        trade_symbol_input.change(
            fn=handle_price_lookup,
            inputs=[trade_symbol_input],
            outputs=[price_badge],
        )

    return demo


demo = build_demo()


if __name__ == "__main__":
    demo.launch()
