```python
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
    def test_supported_symbols_constant(self) -> None:
        self.assertEqual(SUPPORTED_SYMBOLS, ("AAPL", "TSLA", "GOOGL"))

    def test_get_share_price_supported_symbols(self) -> None:
        self.assertEqual(get_share_price("AAPL"), 150.00)
        self.assertEqual(get_share_price("TSLA"), 250.00)
        self.assertEqual(get_share_price("GOOGL"), 2800.00)

    def test_get_share_price_normalizes_symbol(self) -> None:
        self.assertEqual(get_share_price(" aapl "), 150.00)

    def test_get_share_price_rejects_unknown_symbol(self) -> None:
        with self.assertRaises(ValueError):
            get_share_price("MSFT")


class TestValidationHelpers(unittest.TestCase):
    def test_normalize_symbol_strips_and_uppercases(self) -> None:
        self.assertEqual(normalize_symbol(" tsla "), "TSLA")

    def test_normalize_symbol_rejects_non_string(self) -> None:
        with self.assertRaises(ValueError):
            normalize_symbol(123)  # type: ignore[arg-type]

    def test_normalize_symbol_rejects_empty_string(self) -> None:
        with self.assertRaises(ValueError):
            normalize_symbol("   ")

    def test_validate_positive_amount_accepts_positive_amount(self) -> None:
        self.assertIsNone(validate_positive_amount(1.0))

    def test_validate_positive_amount_rejects_zero_or_negative(self) -> None:
        with self.assertRaises(ValueError):
            validate_positive_amount(0)
        with self.assertRaises(ValueError):
            validate_positive_amount(-1)

    def test_validate_positive_quantity_accepts_positive_integer(self) -> None:
        self.assertIsNone(validate_positive_quantity(1))

    def test_validate_positive_quantity_rejects_non_positive_values(self) -> None:
        with self.assertRaises(ValueError):
            validate_positive_quantity(0)
        with self.assertRaises(ValueError):
            validate_positive_quantity(-1)

    def test_validate_positive_quantity_rejects_non_integers_and_bool(self) -> None:
        with self.assertRaises(ValueError):
            validate_positive_quantity(1.5)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            validate_positive_quantity("1")  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            validate_positive_quantity(True)  # type: ignore[arg-type]


class TestAccountCreation(unittest.TestCase):
    def test_create_account_sets_initial_cash_balance(self) -> None:
        acc = Account("acc1", 1000.0)
        self.assertEqual(acc.account_id, "acc1")
        self.assertEqual(acc.get_cash_balance(), 1000.0)
        self.assertEqual(acc.total_deposits, 1000.0)
        self.assertEqual(acc.initial_deposit, 1000.0)
        self.assertEqual(acc.total_withdrawals, 0.0)
        self.assertEqual(acc.holdings, {})

    def test_create_account_strips_account_id(self) -> None:
        acc = Account("  acc1  ", 1000.0)
        self.assertEqual(acc.account_id, "acc1")

    def test_create_account_accepts_zero_initial_deposit(self) -> None:
        acc = Account("acc1", 0.0)
        self.assertEqual(acc.get_cash_balance(), 0.0)
        self.assertEqual(acc.total_deposits, 0.0)

    def test_create_account_records_transaction(self) -> None:
        acc = Account("acc1", 1000.0)
        txs = acc.get_transactions()
        self.assertEqual(len(txs), 1)
        self.assertIsInstance(txs[0], Transaction)
        self.assertEqual(txs[0].transaction_id, 1)
        self.assertEqual(txs[0].transaction_type, "CREATE_ACCOUNT")
        self.assertIsNone(txs[0].symbol)
        self.assertIsNone(txs[0].quantity)
        self.assertIsNone(txs[0].price)
        self.assertEqual(txs[0].amount, 1000.0)
        self.assertEqual(txs[0].cash_balance_after, 1000.0)

    def test_create_account_rejects_negative_initial_deposit(self) -> None:
        with self.assertRaises(ValueError):
            Account("acc1", -10.0)

    def test_create_account_rejects_empty_account_id(self) -> None:
        with self.assertRaises(ValueError):
            Account("", 1000.0)
        with self.assertRaises(ValueError):
            Account("   ", 1000.0)

    def test_create_account_rejects_non_string_account_id(self) -> None:
        with self.assertRaises(ValueError):
            Account(123, 1000.0)  # type: ignore[arg-type]


class TestDepositsAndWithdrawals(unittest.TestCase):
    def test_deposit_increases_cash_balance_and_total_deposits(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.deposit(500.0)
        self.assertEqual(acc.get_cash_balance(), 1500.0)
        self.assertEqual(acc.total_deposits, 1500.0)

    def test_deposit_records_transaction(self) -> None:
        acc = Account("acc1", 1000.0)
        tx = acc.deposit(500.0)
        self.assertEqual(tx.transaction_id, 2)
        self.assertEqual(tx.transaction_type, "DEPOSIT")
        self.assertEqual(tx.amount, 500.0)
        self.assertEqual(tx.cash_balance_after, 1500.0)
        self.assertEqual(len(acc.get_transactions()), 2)

    def test_deposit_rejects_zero_or_negative_amount_without_mutation(self) -> None:
        acc = Account("acc1", 1000.0)
        before_cash = acc.get_cash_balance()
        before_total_deposits = acc.total_deposits
        before_transactions = len(acc.get_transactions())

        with self.assertRaises(ValueError):
            acc.deposit(0)
        with self.assertRaises(ValueError):
            acc.deposit(-100)

        self.assertEqual(acc.get_cash_balance(), before_cash)
        self.assertEqual(acc.total_deposits, before_total_deposits)
        self.assertEqual(len(acc.get_transactions()), before_transactions)

    def test_withdraw_decreases_cash_balance_and_increases_total_withdrawals(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.withdraw(400.0)
        self.assertEqual(acc.get_cash_balance(), 600.0)
        self.assertEqual(acc.total_withdrawals, 400.0)

    def test_withdraw_records_transaction(self) -> None:
        acc = Account("acc1", 1000.0)
        tx = acc.withdraw(400.0)
        self.assertEqual(tx.transaction_id, 2)
        self.assertEqual(tx.transaction_type, "WITHDRAW")
        self.assertEqual(tx.amount, 400.0)
        self.assertEqual(tx.cash_balance_after, 600.0)

    def test_withdraw_rejects_zero_or_negative_amount_without_mutation(self) -> None:
        acc = Account("acc1", 1000.0)
        before_cash = acc.get_cash_balance()
        before_total_withdrawals = acc.total_withdrawals
        before_transactions = len(acc.get_transactions())

        with self.assertRaises(ValueError):
            acc.withdraw(0)
        with self.assertRaises(ValueError):
            acc.withdraw(-50)

        self.assertEqual(acc.get_cash_balance(), before_cash)
        self.assertEqual(acc.total_withdrawals, before_total_withdrawals)
        self.assertEqual(len(acc.get_transactions()), before_transactions)

    def test_withdraw_rejects_amount_exceeding_cash_balance_without_mutation(self) -> None:
        acc = Account("acc1", 1000.0)
        before_transactions = len(acc.get_transactions())

        with self.assertRaises(ValueError):
            acc.withdraw(1500.0)

        self.assertEqual(acc.get_cash_balance(), 1000.0)
        self.assertEqual(acc.total_withdrawals, 0.0)
        self.assertEqual(len(acc.get_transactions()), before_transactions)


class TestBuyingShares(unittest.TestCase):
    def test_buy_decreases_cash_and_increases_holdings(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.buy("AAPL", 2)
        self.assertEqual(acc.get_cash_balance(), 700.0)
        holdings = acc.get_holdings()
        self.assertEqual(len(holdings), 1)
        self.assertIsInstance(holdings[0], Holding)
        self.assertEqual(holdings[0].symbol, "AAPL")
        self.assertEqual(holdings[0].quantity, 2)
        self.assertEqual(holdings[0].current_price, 150.0)
        self.assertEqual(holdings[0].market_value, 300.0)

    def test_buy_normalizes_symbol(self) -> None:
        acc = Account("acc1", 1000.0)
        tx = acc.buy(" aapl ", 1)
        self.assertEqual(tx.symbol, "AAPL")
        self.assertEqual(acc.get_holdings()[0].symbol, "AAPL")

    def test_multiple_buys_accumulate_holdings(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.buy("AAPL", 1)
        acc.buy("AAPL", 2)
        self.assertEqual(acc.get_cash_balance(), 550.0)
        self.assertEqual(acc.get_holdings()[0].quantity, 3)

    def test_buy_records_transaction(self) -> None:
        acc = Account("acc1", 1000.0)
        tx = acc.buy("AAPL", 2)
        self.assertEqual(tx.transaction_id, 2)
        self.assertEqual(tx.transaction_type, "BUY")
        self.assertEqual(tx.symbol, "AAPL")
        self.assertEqual(tx.quantity, 2)
        self.assertEqual(tx.price, 150.0)
        self.assertEqual(tx.amount, 300.0)
        self.assertEqual(tx.cash_balance_after, 700.0)

    def test_buy_rejects_unsupported_symbol_without_mutation(self) -> None:
        acc = Account("acc1", 1000.0)
        before_transactions = len(acc.get_transactions())

        with self.assertRaises(ValueError):
            acc.buy("MSFT", 2)

        self.assertEqual(acc.get_cash_balance(), 1000.0)
        self.assertEqual(acc.get_holdings(), [])
        self.assertEqual(len(acc.get_transactions()), before_transactions)

    def test_buy_rejects_non_positive_quantity_without_mutation(self) -> None:
        acc = Account("acc1", 1000.0)
        before_transactions = len(acc.get_transactions())

        with self.assertRaises(ValueError):
            acc.buy("AAPL", 0)
        with self.assertRaises(ValueError):
            acc.buy("AAPL", -1)

        self.assertEqual(acc.get_cash_balance(), 1000.0)
        self.assertEqual(acc.get_holdings(), [])
        self.assertEqual(len(acc.get_transactions()), before_transactions)

    def test_buy_rejects_non_integer_quantity_without_mutation(self) -> None:
        acc = Account("acc1", 1000.0)
        before_transactions = len(acc.get_transactions())

        with self.assertRaises(ValueError):
            acc.buy("AAPL", 1.5)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            acc.buy("AAPL", True)  # type: ignore[arg-type]

        self.assertEqual(acc.get_cash_balance(), 1000.0)
        self.assertEqual(acc.get_holdings(), [])
        self.assertEqual(len(acc.get_transactions()), before_transactions)

    def test_buy_rejects_quantity_exceeding_cash_balance_without_mutation(self) -> None:
        acc = Account("acc1", 1000.0)
        before_transactions = len(acc.get_transactions())

        with self.assertRaises(ValueError):
            acc.buy("AAPL", 10)

        self.assertEqual(acc.get_cash_balance(), 1000.0)
        self.assertEqual(acc.get_holdings(), [])
        self.assertEqual(len(acc.get_transactions()), before_transactions)


class TestSellingShares(unittest.TestCase):
    def test_sell_increases_cash_and_decreases_holdings(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.buy("AAPL", 3)
        acc.sell("AAPL", 1)
        self.assertEqual(acc.get_cash_balance(), 1000.0 - 450.0 + 150.0)
        holdings = acc.get_holdings()
        self.assertEqual(len(holdings), 1)
        self.assertEqual(holdings[0].quantity, 2)

    def test_sell_normalizes_symbol(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.buy("AAPL", 2)
        tx = acc.sell(" aapl ", 1)
        self.assertEqual(tx.symbol, "AAPL")
        self.assertEqual(acc.get_holdings()[0].quantity, 1)

    def test_sell_removes_holding_when_quantity_reaches_zero(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.buy("AAPL", 3)
        acc.sell("AAPL", 3)
        self.assertEqual(len(acc.get_holdings()), 0)
        self.assertEqual(acc.holdings, {})

    def test_sell_records_transaction(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.buy("AAPL", 3)
        tx = acc.sell("AAPL", 1)
        self.assertEqual(tx.transaction_id, 3)
        self.assertEqual(tx.transaction_type, "SELL")
        self.assertEqual(tx.symbol, "AAPL")
        self.assertEqual(tx.quantity, 1)
        self.assertEqual(tx.price, 150.0)
        self.assertEqual(tx.amount, 150.0)
        self.assertEqual(tx.cash_balance_after, 700.0)

    def test_sell_rejects_quantity_exceeding_holdings_without_mutation(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.buy("AAPL", 3)
        before_cash = acc.get_cash_balance()
        before_holdings = [(h.symbol, h.quantity) for h in acc.get_holdings()]
        before_transactions = len(acc.get_transactions())

        with self.assertRaises(ValueError):
            acc.sell("AAPL", 4)

        self.assertEqual(acc.get_cash_balance(), before_cash)
        self.assertEqual([(h.symbol, h.quantity) for h in acc.get_holdings()], before_holdings)
        self.assertEqual(len(acc.get_transactions()), before_transactions)

    def test_sell_rejects_symbol_not_held_without_mutation(self) -> None:
        acc = Account("acc1", 1000.0)
        before_transactions = len(acc.get_transactions())

        with self.assertRaises(ValueError):
            acc.sell("AAPL", 1)

        self.assertEqual(acc.get_cash_balance(), 1000.0)
        self.assertEqual(acc.get_holdings(), [])
        self.assertEqual(len(acc.get_transactions()), before_transactions)

    def test_sell_rejects_unsupported_symbol_without_mutation(self) -> None:
        acc = Account("acc1", 1000.0)
        before_transactions = len(acc.get_transactions())

        with self.assertRaises(ValueError):
            acc.sell("MSFT", 1)

        self.assertEqual(acc.get_cash_balance(), 1000.0)
        self.assertEqual(acc.get_holdings(), [])
        self.assertEqual(len(acc.get_transactions()), before_transactions)

    def test_sell_rejects_non_positive_quantity_without_mutation(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.buy("AAPL", 3)
        before_cash = acc.get_cash_balance()
        before_quantity = acc.get_holdings()[0].quantity
        before_transactions = len(acc.get_transactions())

        with self.assertRaises(ValueError):
            acc.sell("AAPL", 0)
        with self.assertRaises(ValueError):
            acc.sell("AAPL", -1)

        self.assertEqual(acc.get_cash_balance(), before_cash)
        self.assertEqual(acc.get_holdings()[0].quantity, before_quantity)
        self.assertEqual(len(acc.get_transactions()), before_transactions)

    def test_sell_rejects_non_integer_quantity_without_mutation(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.buy("AAPL", 3)
        before_cash = acc.get_cash_balance()
        before_quantity = acc.get_holdings()[0].quantity
        before_transactions = len(acc.get_transactions())

        with self.assertRaises(ValueError):
            acc.sell("AAPL", 1.5)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            acc.sell("AAPL", False)  # type: ignore[arg-type]

        self.assertEqual(acc.get_cash_balance(), before_cash)
        self.assertEqual(acc.get_holdings()[0].quantity, before_quantity)
        self.assertEqual(len(acc.get_transactions()), before_transactions)


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

    def test_transaction_ids_are_sequential(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.deposit(100.0)
        acc.buy("AAPL", 1)
        acc.sell("AAPL", 1)
        acc.withdraw(50.0)
        ids = [tx.transaction_id for tx in acc.get_transactions()]
        self.assertEqual(ids, [1, 2, 3, 4, 5])

    def test_portfolio_summary_calculates_total_value(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.buy("AAPL", 2)
        summary = acc.get_portfolio_summary()
        self.assertIsInstance(summary, PortfolioSummary)
        self.assertEqual(summary.account_id, "acc1")
        self.assertEqual(summary.cash_balance, 700.0)
        self.assertEqual(summary.holdings_value, 300.0)
        self.assertEqual(summary.total_portfolio_value, 1000.0)

    def test_portfolio_summary_calculates_deposits_withdrawals_and_profit_loss(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.deposit(500.0)
        acc.buy("AAPL", 2)
        acc.withdraw(200.0)
        summary = acc.get_portfolio_summary()

        self.assertEqual(summary.cash_balance, 1000.0)
        self.assertEqual(summary.holdings_value, 300.0)
        self.assertEqual(summary.total_portfolio_value, 1300.0)
        self.assertEqual(summary.total_deposits, 1500.0)
        self.assertEqual(summary.total_withdrawals, 200.0)
        self.assertEqual(summary.net_contributions, 1300.0)
        self.assertEqual(summary.profit_loss, 0.0)

    def test_profit_loss_from_initial_deposit(self) -> None:
        acc = Account("acc1", 1000.0)
        acc.deposit(500.0)
        self.assertEqual(acc.get_profit_loss_from_initial_deposit(), 500.0)


if __name__ == "__main__":
    unittest.main()
```

Unit test run summary:

```text
Ran 31 tests in 0.001s

OK
```