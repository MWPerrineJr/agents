"""Validation script: ensure app.py's Gradio Blocks construct cleanly.

Does NOT call .launch() (that would block).
"""

import traceback


def main() -> int:
    try:
        import gradio as gr
        import app

        demo = app.build_app()
        assert isinstance(demo, gr.Blocks), f"Expected gr.Blocks, got {type(demo)!r}"

        # Exercise display helpers for extra safety.
        s, h, t = app.build_display_state(None)
        assert s == [] and h == [] and t == []

        # Exercise a happy-path handler to ensure wiring returns the right shape.
        account, msg, s, h, t = app.handle_create_account("demo", 10000)
        assert account is not None, "Account should be created"
        assert "created" in msg.lower()
        assert len(s) > 0 and isinstance(h, list) and len(t) >= 1

        # Exercise a buy and inspect refreshed tables.
        account, msg, s, h, t = app.handle_buy(account, "AAPL", 2)
        assert account is not None
        assert len(h) == 1 and h[0][0] == "AAPL" and h[0][1] == 2

        # Exercise an error path (insufficient cash).
        account, msg, s, h, t = app.handle_buy(account, "GOOGL", 1000)
        assert account is not None
        assert "⚠" in msg or "Insufficient" in msg

        print("OK — app.build_app() constructed a gr.Blocks successfully.")
        print(f"    Blocks title: {demo.title!r}")
        print(f"    Handlers verified (create, buy, buy-error).")
        return 0
    except Exception:
        traceback.print_exc()
        print("FAILED — validation did not complete.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
