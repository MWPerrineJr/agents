import unittest
from backend import (
    SUPPORTED_SYMBOLS,
    get_share_price,
    normalize_symbol,
    validate_positive_amount,
    validate_positive_quantity,
    Account,
    Transaction,
    Holding,
    PortfolioSummary
)

class TestSharePrices(unittest.TestCase):
    def test_get_share_price_supported_symbols(self) -> None:
        self.assertEqual(get_share_price("AAPL"), 150.00)
        self.assertEqual(get_share_price("TSLA"), 250.00)
        self.assertEqual(get_share_price("GOOGL"), 2800.00)

    def test_get_share_price_normalizes_symbol(self) -> None:
        self.assertEqual(get_share_price(" aapl "), 150.00)

    def test_get_share_price_rejects_unknown_symbol(self) -> None:
        with self.assertRaises(ValueError):
            get_share_price("MSFT")


class TestAccountCreation(unittest.TestCase):
    def test_create_account_sets_initial_cash_balance(self) -> None:
        acc = Account("acc1", 1000.0)
        self.assertEqual(acc.get_cash_balance(), 1000.0)
        self.assertEqual(acc.total_deposits, 1000.0)
        self.assertEqual(acc.initial_deposit, 1000.0)

    def test_create_account_records_transaction(self) -> None:
        acc = Account("acc1", 1000.0)
        txs = acc.get_transactions()
        self.assertEqual(len(txs), 1)
        self.assertEqual(txs[0].transaction_type, "CREATE_ACCOUNT")
        self.assertEqual(txs[0].amount, 1000.0)

    def test_create_account_rejects_negative_initial_deposit(self) -> None:
        with self.assertRaises(ValueError):
            Account("acc1", -10.0)

    def test_create_account_rejects_empty_account_id(self) -> None:
        with self.assertRaises(ValueError):
            Account("", 1000.0)


class TestDepositsAndWithdrawals(unittest.TestCase):
    def test_deposit_increases_cash_balance(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.deposit(500.0)
        self.assertEqual(acc.get_cash_balance(), 1500.0)

    def test_deposit_records_transaction(self) -> None:
        acc = Account("acc1", 1000.0)
        tx = acc.deposit(500.0)
        self.assertEqual(tx.transaction_type, "DEPOSIT")
        self.assertEqual(tx.amount, 500.0)
        self.assertEqual(len(acc.get_transactions()), 2)

    def test_deposit_rejects_zero_or_negative_amount(self) -> None:
        acc = Account("acc1", 1000.0)
        with self.assertRaises(ValueError):
            acc.deposit(0)
        with self.assertRaises(ValueError):
            acc.deposit(-100)

    def test_withdraw_decreases_cash_balance(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.withdraw(400.0)
        self.assertEqual(acc.get_cash_balance(), 600.0)

    def test_withdraw_records_transaction(self) -> None:
        acc = Account("acc1", 1000.0)
        tx = acc.withdraw(400.0)
        self.assertEqual(tx.transaction_type, "WITHDRAW")
        self.assertEqual(tx.amount, 400.0)

    def test_withdraw_rejects_zero_or_negative_amount(self) -> None:
        acc = Account("acc1", 1000.0)
        with self.assertRaises(ValueError):
            acc.withdraw(0)
        with self.assertRaises(ValueError):
            acc.withdraw(-50)

    def test_withdraw_rejects_amount_exceeding_cash_balance(self) -> None:
        acc = Account("acc1", 1000.0)
        with self.assertRaises(ValueError):
            acc.withdraw(1500.0)
        self.assertEqual(acc.get_cash_balance(), 1000.0)


class TestBuyingShares(unittest.TestCase):
    def test_buy_decreases_cash_and_increases_holdings(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.buy("AAPL", 2) # Cost 300
        self.assertEqual(acc.get_cash_balance(), 700.0)
        holdings = acc.get_holdings()
        self.assertEqual(len(holdings), 1)
        self.assertEqual(holdings[0].symbol, "AAPL")
        self.assertEqual(holdings[0].quantity, 2)

    def test_buy_records_transaction(self) -> None:
        acc = Account("acc1", 1000.0)
        tx = acc.buy("AAPL", 2)
        self.assertEqual(tx.transaction_type, "BUY")
        self.assertEqual(tx.symbol, "AAPL")
        self.assertEqual(tx.quantity, 2)
        self.assertEqual(tx.price, 150.0)
        self.assertEqual(tx.amount, 300.0)

    def test_buy_rejects_unsupported_symbol(self) -> None:
        acc = Account("acc1", 1000.0)
        with self.assertRaises(ValueError):
            acc.buy("MSFT", 2)

    def test_buy_rejects_non_positive_quantity(self) -> None:
        acc = Account("acc1", 1000.0)
        with self.assertRaises(ValueError):
            acc.buy("AAPL", 0)

    def test_buy_rejects_quantity_exceeding_cash_balance(self) -> None:
        acc = Account("acc1", 1000.0)
        with self.assertRaises(ValueError):
            acc.buy("AAPL", 10) # Cost 1500
        self.assertEqual(acc.get_cash_balance(), 1000.0)


class TestSellingShares(unittest.TestCase):
    def test_sell_increases_cash_and_decreases_holdings(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.buy("AAPL", 3)
        acc.sell("AAPL", 1)
        self.assertEqual(acc.get_cash_balance(), 1000.0 - 450 + 150)
        holdings = acc.get_holdings()
        self.assertEqual(len(holdings), 1)
        self.assertEqual(holdings[0].quantity, 2)

    def test_sell_removes_holding_when_quantity_reaches_zero(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.buy("AAPL", 3)
        acc.sell("AAPL", 3)
        self.assertEqual(len(acc.get_holdings()), 0)

    def test_sell_records_transaction(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.buy("AAPL", 3)
        tx = acc.sell("AAPL", 1)
        self.assertEqual(tx.transaction_type, "SELL")
        self.assertEqual(tx.symbol, "AAPL")
        self.assertEqual(tx.quantity, 1)

    def test_sell_rejects_quantity_exceeding_holdings(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.buy("AAPL", 3)
        with self.assertRaises(ValueError):
            acc.sell("AAPL", 4)

    def test_sell_rejects_symbol_not_held(self) -> None:
        acc = Account("acc1", 1000.0)
        with self.assertRaises(ValueError):
            acc.sell("AAPL", 1)

    def test_sell_rejects_non_positive_quantity(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.buy("AAPL", 3)
        with self.assertRaises(ValueError):
            acc.sell("AAPL", -1)


class TestReports(unittest.TestCase):
    def test_get_holdings_returns_market_values(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.buy("AAPL", 2)
        holdings = acc.get_holdings()
        self.assertEqual(holdings[0].market_value, 300.0)

    def test_get_holdings_sorted_by_symbol(self) -> None:
        acc = Account("acc1", 10000.0)
        acc.buy("TSLA", 1)
        acc.buy("AAPL", 1)
        holdings = acc.get_holdings()
        self.assertEqual(holdings[0].symbol, "AAPL")
        self.assertEqual(holdings[1].symbol, "TSLA")

    def test_get_transactions_returns_copy(self) -> None:
        acc = Account("acc1", 1000.0)
        txs = acc.get_transactions()
        txs.clear()
        self.assertEqual(len(acc.get_transactions()), 1)

    def test_portfolio_summary_calculates_total_value(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.buy("AAPL", 2)
        summary = acc.get_portfolio_summary()
        self.assertEqual(summary.cash_balance, 700.0)
        self.assertEqual(summary.holdings_value, 300.0)
        self.assertEqual(summary.total_portfolio_value, 1000.0)

    def test_portfolio_summary_calculates_profit_loss(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.buy("AAPL", 2)
        summary = acc.get_portfolio_summary()
        self.assertEqual(summary.net_contributions, 1000.0)
        self.assertEqual(summary.profit_loss, 0.0)

    def test_profit_loss_from_initial_deposit(self) -> None:
        acc = Account("acc1", 1000.0)
        self.assertEqual(acc.get_profit_loss_from_initial_deposit(), 0.0)

if __name__ == "__main__":
    unittest.main()
