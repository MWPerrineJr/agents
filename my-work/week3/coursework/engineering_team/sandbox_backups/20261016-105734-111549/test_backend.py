import unittest
from decimal import Decimal
from backend import (
    AccountService,
    TransactionType,
    AccountNotFoundError,
    ValidationError,
    InsufficientFundsError,
    InsufficientSharesError,
    UnknownSymbolError,
)

def fixed_price_lookup(symbol: str) -> Decimal:
    prices = {
        "AAPL": Decimal("100.00"),
        "TSLA": Decimal("200.00"),
        "GOOGL": Decimal("1000.00"),
    }
    normalized = symbol.upper()
    if normalized not in prices:
        raise UnknownSymbolError(f"Unsupported symbol: {symbol}")
    return prices[normalized]

class TestAccountService(unittest.TestCase):
    def setUp(self):
        self.service = AccountService(price_lookup=fixed_price_lookup)

    def test_create_account_sets_initial_cash_and_empty_holdings(self):
        acc = self.service.create_account("Jane", "1000.00")
        self.assertEqual(acc.owner_name, "Jane")
        self.assertEqual(acc.cash_balance, Decimal("1000.00"))
        self.assertEqual(acc.initial_deposit, Decimal("1000.00"))
        self.assertEqual(acc.holdings, {})
        self.assertEqual(len(acc.transactions), 1)
        self.assertEqual(acc.transactions[0].transaction_type, TransactionType.CREATE_ACCOUNT)

    def test_create_account_rejects_blank_owner_name(self):
        with self.assertRaises(ValidationError):
            self.service.create_account("   ", "1000.00")

    def test_create_account_rejects_non_positive_initial_deposit(self):
        with self.assertRaises(ValidationError):
            self.service.create_account("Jane", "-100.00")
        with self.assertRaises(ValidationError):
            self.service.create_account("Jane", "0")

    def test_deposit_increases_cash_and_records_transaction(self):
        acc = self.service.create_account("Jane", "1000.00")
        tx = self.service.deposit(acc.account_id, "500.00")
        self.assertEqual(acc.cash_balance, Decimal("1500.00"))
        self.assertEqual(tx.transaction_type, TransactionType.DEPOSIT)
        self.assertEqual(tx.cash_amount, Decimal("500.00"))

    def test_deposit_rejects_non_positive_amount(self):
        acc = self.service.create_account("Jane", "1000.00")
        with self.assertRaises(ValidationError):
            self.service.deposit(acc.account_id, "-50.00")

    def test_withdraw_decreases_cash_and_records_transaction(self):
        acc = self.service.create_account("Jane", "1000.00")
        tx = self.service.withdraw(acc.account_id, "200.00")
        self.assertEqual(acc.cash_balance, Decimal("800.00"))
        self.assertEqual(tx.transaction_type, TransactionType.WITHDRAW)
        self.assertEqual(tx.cash_amount, Decimal("-200.00"))

    def test_withdraw_rejects_amount_greater_than_cash_balance(self):
        acc = self.service.create_account("Jane", "1000.00")
        with self.assertRaises(InsufficientFundsError):
            self.service.withdraw(acc.account_id, "1500.00")

    def test_withdraw_rejects_non_positive_amount(self):
        acc = self.service.create_account("Jane", "1000.00")
        with self.assertRaises(ValidationError):
            self.service.withdraw(acc.account_id, "-50.00")

    def test_buy_shares_decreases_cash_and_increases_holdings(self):
        acc = self.service.create_account("Jane", "1000.00")
        self.service.buy_shares(acc.account_id, "AAPL", 3)
        self.assertEqual(acc.cash_balance, Decimal("700.00"))
        self.assertEqual(acc.holdings, {"AAPL": 3})

    def test_buy_shares_records_transaction_with_price_quantity_and_symbol(self):
        acc = self.service.create_account("Jane", "1000.00")
        tx = self.service.buy_shares(acc.account_id, "AAPL", 3)
        self.assertEqual(tx.transaction_type, TransactionType.BUY)
        self.assertEqual(tx.symbol, "AAPL")
        self.assertEqual(tx.quantity, 3)
        self.assertEqual(tx.price, Decimal("100.00"))
        self.assertEqual(tx.cash_amount, Decimal("-300.00"))

    def test_buy_shares_rejects_insufficient_funds(self):
        acc = self.service.create_account("Jane", "1000.00")
        with self.assertRaises(InsufficientFundsError):
            self.service.buy_shares(acc.account_id, "AAPL", 15)

    def test_buy_shares_rejects_non_positive_quantity(self):
        acc = self.service.create_account("Jane", "1000.00")
        with self.assertRaises(ValidationError):
            self.service.buy_shares(acc.account_id, "AAPL", 0)

    def test_buy_shares_rejects_unknown_symbol(self):
        acc = self.service.create_account("Jane", "1000.00")
        with self.assertRaises(UnknownSymbolError):
            self.service.buy_shares(acc.account_id, "MSFT", 1)

    def test_sell_shares_increases_cash_and_decreases_holdings(self):
        acc = self.service.create_account("Jane", "1000.00")
        self.service.buy_shares(acc.account_id, "AAPL", 5)
        self.service.sell_shares(acc.account_id, "AAPL", 2)
        self.assertEqual(acc.cash_balance, Decimal("700.00"))
        self.assertEqual(acc.holdings, {"AAPL": 3})

    def test_sell_all_shares_removes_or_zeroes_holding(self):
        acc = self.service.create_account("Jane", "1000.00")
        self.service.buy_shares(acc.account_id, "AAPL", 5)
        self.service.sell_shares(acc.account_id, "AAPL", 5)
        self.assertNotIn("AAPL", acc.holdings)
        self.assertEqual(self.service.get_holdings(acc.account_id), {})

    def test_sell_shares_rejects_more_than_owned(self):
        acc = self.service.create_account("Jane", "1000.00")
        self.service.buy_shares(acc.account_id, "AAPL", 5)
        with self.assertRaises(InsufficientSharesError):
            self.service.sell_shares(acc.account_id, "AAPL", 6)

    def test_sell_shares_rejects_non_positive_quantity(self):
        acc = self.service.create_account("Jane", "1000.00")
        self.service.buy_shares(acc.account_id, "AAPL", 5)
        with self.assertRaises(ValidationError):
            self.service.sell_shares(acc.account_id, "AAPL", 0)

    def test_calculate_holdings_value(self):
        acc = self.service.create_account("Jane", "1000.00")
        self.service.buy_shares(acc.account_id, "AAPL", 2)
        self.service.buy_shares(acc.account_id, "TSLA", 1)
        self.assertEqual(self.service.calculate_holdings_value(acc.account_id), Decimal("400.00"))

    def test_calculate_total_value(self):
        acc = self.service.create_account("Jane", "1000.00")
        self.service.buy_shares(acc.account_id, "AAPL", 2)
        # Cash: 800, Holdings: 200, Total: 1000
        self.assertEqual(self.service.calculate_total_value(acc.account_id), Decimal("1000.00"))

    def test_profit_loss_excluding_cash_flows_is_zero_when_prices_unchanged(self):
        acc = self.service.create_account("Jane", "1000.00")
        self.service.buy_shares(acc.account_id, "AAPL", 2)
        self.assertEqual(self.service.calculate_profit_loss_excluding_cash_flows(acc.account_id), Decimal("0"))

    def test_profit_loss_excluding_cash_flows_handles_deposits_and_withdrawals(self):
        acc = self.service.create_account("Jane", "1000.00")
        self.service.deposit(acc.account_id, "500.00")
        self.service.withdraw(acc.account_id, "200.00")
        self.assertEqual(self.service.calculate_profit_loss_excluding_cash_flows(acc.account_id), Decimal("0"))

    def test_get_holdings_returns_copy(self):
        acc = self.service.create_account("Jane", "1000.00")
        self.service.buy_shares(acc.account_id, "AAPL", 2)
        holdings = self.service.get_holdings(acc.account_id)
        holdings["AAPL"] = 100
        self.assertEqual(self.service.get_holdings(acc.account_id)["AAPL"], 2)

    def test_get_holdings_report_includes_market_value(self):
        acc = self.service.create_account("Jane", "1000.00")
        self.service.buy_shares(acc.account_id, "AAPL", 2)
        report = self.service.get_holdings_report(acc.account_id)
        self.assertEqual(len(report), 1)
        row = report[0]
        self.assertEqual(row.symbol, "AAPL")
        self.assertEqual(row.quantity, 2)
        self.assertEqual(row.current_price, Decimal("100.00"))
        self.assertEqual(row.market_value, Decimal("200.00"))

    def test_get_holdings_at_transaction_id(self):
        acc = self.service.create_account("Jane", "1000.00")
        tx1 = self.service.buy_shares(acc.account_id, "AAPL", 5)
        self.service.buy_shares(acc.account_id, "TSLA", 2)
        holdings_at = self.service.get_holdings_at(acc.account_id, transaction_id=tx1.transaction_id)
        self.assertEqual(holdings_at, {"AAPL": 5})

    def test_get_holdings_at_rejects_unknown_transaction_id(self):
        acc = self.service.create_account("Jane", "1000.00")
        with self.assertRaises(ValidationError):
            self.service.get_holdings_at(acc.account_id, transaction_id="unknown")

    def test_get_holdings_at_rejects_both_as_of_and_transaction_id(self):
        acc = self.service.create_account("Jane", "1000.00")
        tx1 = self.service.buy_shares(acc.account_id, "AAPL", 5)
        with self.assertRaises(ValidationError):
            self.service.get_holdings_at(acc.account_id, as_of=tx1.timestamp, transaction_id=tx1.transaction_id)

    def test_list_transactions_returns_chronological_transactions(self):
        acc = self.service.create_account("Jane", "1000.00")
        tx1 = self.service.buy_shares(acc.account_id, "AAPL", 5)
        tx2 = self.service.sell_shares(acc.account_id, "AAPL", 2)
        transactions = self.service.list_transactions(acc.account_id)
        self.assertEqual(transactions[0].transaction_type, TransactionType.CREATE_ACCOUNT)
        self.assertEqual(transactions[1].transaction_id, tx1.transaction_id)
        self.assertEqual(transactions[2].transaction_id, tx2.transaction_id)

    def test_list_transactions_returns_copy(self):
        acc = self.service.create_account("Jane", "1000.00")
        transactions = self.service.list_transactions(acc.account_id)
        transactions.clear()
        self.assertEqual(len(self.service.list_transactions(acc.account_id)), 1)

    def test_get_missing_account_raises_account_not_found(self):
        with self.assertRaises(AccountNotFoundError):
            self.service.get_account("missing")

if __name__ == "__main__":
    unittest.main()
