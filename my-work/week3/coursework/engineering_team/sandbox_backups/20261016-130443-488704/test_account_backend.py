import unittest
from datetime import datetime

from account_backend import (
    Account,
    AccountService,
    Transaction,
    generate_id,
    get_share_price,
    normalize_symbol,
)


class TestAccountBackend(unittest.TestCase):
    def setUp(self) -> None:
        self.service = AccountService()

    def snapshot_state(self):
        account = self.service.get_account()
        return {
            "cash_balance": account.cash_balance,
            "total_deposited": account.total_deposited,
            "holdings": dict(account.holdings),
            "transaction_count": len(account.transactions),
        }

    def assert_state_unchanged(self, before) -> None:
        self.assertEqual(self.snapshot_state(), before)

    def test_get_share_price_known_symbols(self) -> None:
        self.assertEqual(get_share_price("AAPL"), 150.0)
        self.assertEqual(get_share_price("TSLA"), 250.0)
        self.assertEqual(get_share_price("GOOGL"), 2800.0)
        self.assertEqual(get_share_price("aapl"), 150.0)
        self.assertEqual(get_share_price("  tsla  "), 250.0)

    def test_get_share_price_unknown_symbol_raises(self) -> None:
        with self.assertRaises(ValueError):
            get_share_price("MSFT")

    def test_generate_id_uses_prefix_and_is_unique(self) -> None:
        first = generate_id("acct")
        second = generate_id("acct")
        self.assertTrue(first.startswith("acct_"))
        self.assertTrue(second.startswith("acct_"))
        self.assertNotEqual(first, second)

    def test_normalize_symbol_strips_and_uppercases(self) -> None:
        self.assertEqual(normalize_symbol(" aapl "), "AAPL")
        self.assertEqual(normalize_symbol("tsla"), "TSLA")

    def test_normalize_symbol_rejects_empty_symbol(self) -> None:
        with self.assertRaises(ValueError):
            normalize_symbol("")
        with self.assertRaises(ValueError):
            normalize_symbol("   ")

    def test_create_account_success(self) -> None:
        account = self.service.create_account("Alice", 1000.0)

        self.assertIsInstance(account, Account)
        self.assertTrue(account.account_id.startswith("acct_"))
        self.assertEqual(account.owner_name, "Alice")
        self.assertEqual(account.cash_balance, 1000.0)
        self.assertEqual(account.total_deposited, 1000.0)
        self.assertEqual(account.holdings, {})
        self.assertIsInstance(account.created_at, datetime)
        self.assertEqual(len(account.transactions), 1)

        txn = account.transactions[0]
        self.assertIsInstance(txn, Transaction)
        self.assertTrue(txn.transaction_id.startswith("txn_"))
        self.assertIsInstance(txn.timestamp, datetime)
        self.assertEqual(txn.transaction_type, "CREATE_ACCOUNT")
        self.assertIsNone(txn.symbol)
        self.assertIsNone(txn.quantity)
        self.assertIsNone(txn.price)
        self.assertEqual(txn.amount, 1000.0)
        self.assertEqual(txn.cash_balance_after, 1000.0)

    def test_create_account_strips_owner_name_and_allows_zero_deposit(self) -> None:
        account = self.service.create_account("  Alice  ", 0.0)
        self.assertEqual(account.owner_name, "Alice")
        self.assertEqual(account.cash_balance, 0.0)
        self.assertEqual(account.total_deposited, 0.0)

    def test_create_account_replaces_existing_account(self) -> None:
        first = self.service.create_account("Alice", 1000.0)
        self.service.buy("AAPL", 1)
        second = self.service.create_account("Bob", 250.0)

        self.assertIsNot(first, second)
        self.assertEqual(second.owner_name, "Bob")
        self.assertEqual(second.cash_balance, 250.0)
        self.assertEqual(second.total_deposited, 250.0)
        self.assertEqual(second.holdings, {})
        self.assertEqual(len(second.transactions), 1)
        self.assertEqual(second.transactions[0].transaction_type, "CREATE_ACCOUNT")

    def test_create_account_rejects_empty_owner_name(self) -> None:
        with self.assertRaises(ValueError):
            self.service.create_account("", 1000.0)
        with self.assertRaises(ValueError):
            self.service.create_account("   ", 1000.0)

    def test_create_account_rejects_negative_initial_deposit(self) -> None:
        with self.assertRaises(ValueError):
            self.service.create_account("Alice", -100.0)

    def test_get_account_requires_account(self) -> None:
        with self.assertRaises(ValueError):
            self.service.get_account()

    def test_deposit_success(self) -> None:
        self.service.create_account("Alice", 1000.0)
        account = self.service.deposit(500.0)

        self.assertEqual(account.cash_balance, 1500.0)
        self.assertEqual(account.total_deposited, 1500.0)
        self.assertEqual(len(account.transactions), 2)
        self.assertEqual(account.transactions[1].transaction_type, "DEPOSIT")
        self.assertEqual(account.transactions[1].amount, 500.0)
        self.assertEqual(account.transactions[1].cash_balance_after, 1500.0)

    def test_deposit_rejects_non_positive_amount_and_does_not_mutate(self) -> None:
        self.service.create_account("Alice", 1000.0)
        before = self.snapshot_state()

        with self.assertRaises(ValueError):
            self.service.deposit(0)
        self.assert_state_unchanged(before)

        with self.assertRaises(ValueError):
            self.service.deposit(-100.0)
        self.assert_state_unchanged(before)

    def test_deposit_requires_account(self) -> None:
        with self.assertRaises(ValueError):
            self.service.deposit(500.0)

    def test_withdraw_success(self) -> None:
        self.service.create_account("Alice", 1000.0)
        account = self.service.withdraw(200.0)

        self.assertEqual(account.cash_balance, 800.0)
        self.assertEqual(account.total_deposited, 800.0)
        self.assertEqual(len(account.transactions), 2)
        self.assertEqual(account.transactions[1].transaction_type, "WITHDRAW")
        self.assertEqual(account.transactions[1].amount, 200.0)
        self.assertEqual(account.transactions[1].cash_balance_after, 800.0)

    def test_withdraw_can_reduce_total_deposited_to_zero(self) -> None:
        self.service.create_account("Alice", 100.0)
        self.service.withdraw(75.0)
        self.service.deposit(25.0)
        account = self.service.withdraw(50.0)

        self.assertEqual(account.cash_balance, 0.0)
        self.assertEqual(account.total_deposited, 0.0)

    def test_withdraw_rejects_non_positive_amount_and_does_not_mutate(self) -> None:
        self.service.create_account("Alice", 1000.0)
        before = self.snapshot_state()

        with self.assertRaises(ValueError):
            self.service.withdraw(0)
        self.assert_state_unchanged(before)

        with self.assertRaises(ValueError):
            self.service.withdraw(-100.0)
        self.assert_state_unchanged(before)

    def test_withdraw_rejects_amount_greater_than_cash_balance_and_does_not_mutate(self) -> None:
        self.service.create_account("Alice", 1000.0)
        before = self.snapshot_state()

        with self.assertRaises(ValueError):
            self.service.withdraw(1200.0)
        self.assert_state_unchanged(before)

    def test_withdraw_requires_account(self) -> None:
        with self.assertRaises(ValueError):
            self.service.withdraw(200.0)

    def test_buy_success(self) -> None:
        self.service.create_account("Alice", 1000.0)
        account = self.service.buy("aapl", 2)

        self.assertEqual(account.cash_balance, 700.0)
        self.assertEqual(account.holdings, {"AAPL": 2})
        self.assertEqual(len(account.transactions), 2)
        self.assertEqual(account.transactions[1].transaction_type, "BUY")
        self.assertEqual(account.transactions[1].symbol, "AAPL")
        self.assertEqual(account.transactions[1].quantity, 2)
        self.assertEqual(account.transactions[1].price, 150.0)
        self.assertEqual(account.transactions[1].amount, 300.0)
        self.assertEqual(account.transactions[1].cash_balance_after, 700.0)

    def test_buy_accumulates_existing_holding(self) -> None:
        self.service.create_account("Alice", 1000.0)
        self.service.buy("AAPL", 1)
        account = self.service.buy(" aapl ", 2)

        self.assertEqual(account.cash_balance, 550.0)
        self.assertEqual(account.holdings, {"AAPL": 3})
        self.assertEqual(len(account.transactions), 3)

    def test_buy_rejects_when_insufficient_cash_and_does_not_mutate(self) -> None:
        self.service.create_account("Alice", 100.0)
        before = self.snapshot_state()

        with self.assertRaises(ValueError):
            self.service.buy("AAPL", 1)
        self.assert_state_unchanged(before)

    def test_buy_rejects_non_positive_quantity_and_does_not_mutate(self) -> None:
        self.service.create_account("Alice", 1000.0)
        before = self.snapshot_state()

        with self.assertRaises(ValueError):
            self.service.buy("AAPL", 0)
        self.assert_state_unchanged(before)

        with self.assertRaises(ValueError):
            self.service.buy("AAPL", -1)
        self.assert_state_unchanged(before)

    def test_buy_rejects_non_integer_quantity_and_does_not_mutate(self) -> None:
        self.service.create_account("Alice", 1000.0)
        before = self.snapshot_state()

        with self.assertRaises(ValueError):
            self.service.buy("AAPL", 1.5)
        self.assert_state_unchanged(before)

    def test_buy_rejects_unknown_symbol_and_does_not_mutate(self) -> None:
        self.service.create_account("Alice", 1000.0)
        before = self.snapshot_state()

        with self.assertRaises(ValueError):
            self.service.buy("MSFT", 1)
        self.assert_state_unchanged(before)

    def test_buy_rejects_empty_symbol_and_does_not_mutate(self) -> None:
        self.service.create_account("Alice", 1000.0)
        before = self.snapshot_state()

        with self.assertRaises(ValueError):
            self.service.buy("   ", 1)
        self.assert_state_unchanged(before)

    def test_buy_requires_account(self) -> None:
        with self.assertRaises(ValueError):
            self.service.buy("AAPL", 1)

    def test_sell_success(self) -> None:
        self.service.create_account("Alice", 1000.0)
        self.service.buy("AAPL", 2)
        account = self.service.sell("aapl", 1)

        self.assertEqual(account.cash_balance, 850.0)
        self.assertEqual(account.holdings, {"AAPL": 1})
        self.assertEqual(len(account.transactions), 3)
        self.assertEqual(account.transactions[2].transaction_type, "SELL")
        self.assertEqual(account.transactions[2].symbol, "AAPL")
        self.assertEqual(account.transactions[2].quantity, 1)
        self.assertEqual(account.transactions[2].price, 150.0)
        self.assertEqual(account.transactions[2].amount, 150.0)
        self.assertEqual(account.transactions[2].cash_balance_after, 850.0)

    def test_sell_all_removes_symbol_from_holdings(self) -> None:
        self.service.create_account("Alice", 1000.0)
        self.service.buy("AAPL", 2)
        account = self.service.sell("AAPL", 2)
        self.assertEqual(account.holdings, {})

    def test_sell_rejects_when_no_holdings_for_symbol_and_does_not_mutate(self) -> None:
        self.service.create_account("Alice", 1000.0)
        before = self.snapshot_state()

        with self.assertRaises(ValueError):
            self.service.sell("AAPL", 1)
        self.assert_state_unchanged(before)

    def test_sell_rejects_quantity_greater_than_holdings_and_does_not_mutate(self) -> None:
        self.service.create_account("Alice", 1000.0)
        self.service.buy("AAPL", 1)
        before = self.snapshot_state()

        with self.assertRaises(ValueError):
            self.service.sell("AAPL", 2)
        self.assert_state_unchanged(before)

    def test_sell_rejects_non_positive_quantity_and_does_not_mutate(self) -> None:
        self.service.create_account("Alice", 1000.0)
        self.service.buy("AAPL", 1)
        before = self.snapshot_state()

        with self.assertRaises(ValueError):
            self.service.sell("AAPL", 0)
        self.assert_state_unchanged(before)

        with self.assertRaises(ValueError):
            self.service.sell("AAPL", -1)
        self.assert_state_unchanged(before)

    def test_sell_rejects_non_integer_quantity_and_does_not_mutate(self) -> None:
        self.service.create_account("Alice", 1000.0)
        self.service.buy("AAPL", 1)
        before = self.snapshot_state()

        with self.assertRaises(ValueError):
            self.service.sell("AAPL", 1.5)
        self.assert_state_unchanged(before)

    def test_sell_rejects_empty_symbol_and_does_not_mutate(self) -> None:
        self.service.create_account("Alice", 1000.0)
        self.service.buy("AAPL", 1)
        before = self.snapshot_state()

        with self.assertRaises(ValueError):
            self.service.sell("   ", 1)
        self.assert_state_unchanged(before)

    def test_sell_requires_account(self) -> None:
        with self.assertRaises(ValueError):
            self.service.sell("AAPL", 1)

    def test_get_holdings_returns_copy(self) -> None:
        self.service.create_account("Alice", 1000.0)
        self.service.buy("AAPL", 2)

        holdings = self.service.get_holdings()
        holdings["AAPL"] = 999
        holdings["TSLA"] = 1

        self.assertEqual(self.service.get_holdings(), {"AAPL": 2})

    def test_get_transactions_returns_copy(self) -> None:
        self.service.create_account("Alice", 1000.0)
        transactions = self.service.get_transactions()
        transactions.clear()

        self.assertEqual(len(self.service.get_transactions()), 1)
        self.assertEqual(self.service.get_transactions()[0].transaction_type, "CREATE_ACCOUNT")

    def test_calculate_holdings_value(self) -> None:
        self.service.create_account("Alice", 2000.0)
        self.service.buy("AAPL", 2)
        self.service.buy("TSLA", 3)
        self.assertEqual(self.service.calculate_holdings_value(), 1050.0)

    def test_calculate_portfolio_value(self) -> None:
        self.service.create_account("Alice", 1000.0)
        self.service.buy("AAPL", 2)
        self.assertEqual(self.service.calculate_portfolio_value(), 1000.0)

    def test_calculate_profit_loss(self) -> None:
        self.service.create_account("Alice", 1000.0)
        self.service.buy("AAPL", 2)
        self.assertEqual(self.service.calculate_profit_loss(), 0.0)

        self.service.withdraw(200.0)
        self.assertEqual(self.service.calculate_profit_loss(), 0.0)

    def test_calculation_methods_require_account(self) -> None:
        with self.assertRaises(ValueError):
            self.service.get_cash_balance()
        with self.assertRaises(ValueError):
            self.service.calculate_holdings_value()
        with self.assertRaises(ValueError):
            self.service.calculate_portfolio_value()
        with self.assertRaises(ValueError):
            self.service.calculate_profit_loss()

    def test_get_holdings_report(self) -> None:
        self.service.create_account("Alice", 1000.0)
        self.service.buy("AAPL", 2)
        report = self.service.get_holdings_report()

        self.assertEqual(
            report,
            [
                {
                    "symbol": "AAPL",
                    "quantity": 2,
                    "current_price": 150.0,
                    "market_value": 300.0,
                }
            ],
        )

    def test_get_holdings_report_empty_when_no_holdings(self) -> None:
        self.service.create_account("Alice", 1000.0)
        self.assertEqual(self.service.get_holdings_report(), [])

    def test_get_transactions_report(self) -> None:
        self.service.create_account("Alice", 1000.0)
        self.service.deposit(100.0)
        self.service.buy("AAPL", 1)
        report = self.service.get_transactions_report()

        self.assertEqual(len(report), 3)
        self.assertEqual([row["type"] for row in report], ["CREATE_ACCOUNT", "DEPOSIT", "BUY"])
        self.assertIn("timestamp", report[0])
        self.assertEqual(report[0]["symbol"], "")
        self.assertEqual(report[0]["quantity"], "")
        self.assertEqual(report[0]["price"], "")
        self.assertEqual(report[0]["amount"], 1000.0)
        self.assertEqual(report[2]["symbol"], "AAPL")
        self.assertEqual(report[2]["quantity"], 1)
        self.assertEqual(report[2]["price"], 150.0)
        self.assertEqual(report[2]["amount"], 150.0)

    def test_get_account_summary(self) -> None:
        self.service.create_account("Alice", 1000.0)
        self.service.buy("AAPL", 2)
        summary = self.service.get_account_summary()

        expected_keys = {
            "account_id",
            "owner_name",
            "cash_balance",
            "holdings_value",
            "portfolio_value",
            "total_deposited",
            "profit_loss",
            "created_at",
        }
        self.assertEqual(set(summary), expected_keys)
        self.assertTrue(str(summary["account_id"]).startswith("acct_"))
        self.assertEqual(summary["owner_name"], "Alice")
        self.assertEqual(summary["cash_balance"], 700.0)
        self.assertEqual(summary["holdings_value"], 300.0)
        self.assertEqual(summary["portfolio_value"], 1000.0)
        self.assertEqual(summary["total_deposited"], 1000.0)
        self.assertEqual(summary["profit_loss"], 0.0)
        self.assertIsInstance(summary["created_at"], str)
        self.assertGreater(len(summary["created_at"]), 0)

    def test_report_and_summary_methods_require_account(self) -> None:
        with self.assertRaises(ValueError):
            self.service.get_holdings()
        with self.assertRaises(ValueError):
            self.service.get_holdings_report()
        with self.assertRaises(ValueError):
            self.service.get_transactions()
        with self.assertRaises(ValueError):
            self.service.get_transactions_report()
        with self.assertRaises(ValueError):
            self.service.get_account_summary()


if __name__ == "__main__":
    unittest.main()
