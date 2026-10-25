"""Validation script: imports app.py and verifies the Blocks object constructs."""

import sys


def main() -> int:
    print("Importing app.py ...")
    import app

    print("✓ app imported successfully.")

    import gradio as gr

    assert isinstance(app.demo, gr.Blocks), "app.demo must be a gr.Blocks instance"
    print(f"✓ app.demo is a gr.Blocks instance: {type(app.demo).__name__}")

    # Smoke-test a few handlers using the global service.
    print("\nSmoke-testing handlers:")

    s1 = app.handle_create_account("Alice", 10000)
    assert len(s1) == 4, "handler must return 4 outputs"
    print("  ✓ handle_create_account OK")

    s2 = app.handle_deposit(500)
    assert len(s2) == 4
    print("  ✓ handle_deposit OK")

    s3 = app.handle_buy("AAPL", 2)
    assert len(s3) == 4
    print("  ✓ handle_buy OK")

    s4 = app.handle_sell("AAPL", 1)
    assert len(s4) == 4
    print("  ✓ handle_sell OK")

    s5 = app.handle_withdraw(100)
    assert len(s5) == 4
    print("  ✓ handle_withdraw OK")

    # Validate error branch (friendly message, no raise)
    s6 = app.handle_withdraw(10_000_000)
    assert "✗" in s6[3], "expected a friendly error in status"
    print("  ✓ handle_withdraw error path returns friendly message")

    s7 = app.handle_refresh()
    assert len(s7) == 4
    print("  ✓ handle_refresh OK")

    price_md = app.handle_price_lookup("TSLA")
    assert "TSLA" in price_md
    print("  ✓ handle_price_lookup OK")

    print("\nAll checks passed. (Did NOT call .launch().)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
