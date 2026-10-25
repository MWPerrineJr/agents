import unittest
from backend import (
    AccountService,
    get_share_price,
    AccountNotFoundError,
    DuplicateAccountError,
    ValidationError,
    InsufficientFundsError,
    InsufficientSharesError,
    UnknownSymbolError,
    TRANSACTION_DEPOSIT,
    TRANSACTION_WITHDRAW,
    TRANSACTION_BUY,
    TRANSACTION_SELL,
)

class TestPriceProvider(unittest.TestCase):
    def test_get_share_price_supported_symbols(self):
        self.assertEqual(get_share_price("AAPL"), 150.0)
        self.assertEqual(get_share_price("TSLA"), 250.0)
        self.assertEqual(get_share_price("GOOGL"), 2800.0)

    def test_get_share_price_normalizes_symbol(self):
        self.assertEqual(get_share_price(" aapl "), 150.0)
        self.assertEqual(get_share_price("tsla"), 250.0)

    def test_get_share_price_unknown_symbol(self):
        with self.assertRaises(UnknownSymbolError):
            get_share_price("MSFT")

class TestAccountCreation(unittest.TestCase):
    def setUp(self):
        self.service = AccountService()

    def test_create_account_success_no_initial_deposit(self):
        acc = self.service.create_account("alice")
        self.assertEqual(acc.account_id, "alice")
        self.assertEqual(acc.cash_balance, 0.0)
        self.assertEqual(acc.total_deposited, 0.0)
        self.assertEqual(len(acc.transactions), 0)

    def test_create_account_success_with_initial_deposit(self):
        acc = self.service.create_account("bob", 1000.0)
        self.assertEqual(acc.cash_balance, 1000.0)
        self.assertEqual(acc.total_deposited, 1000.0)
        self.assertEqual(len(acc.transactions), 1)
        self.assertEqual(acc.transactions[0].transaction_type, TRANSACTION_DEPOSIT)

    def test_create_duplicate_account_raises(self):
        self.service.create_account("charlie")
        with self.assertRaises(DuplicateAccountError):
            self.service.create_account("charlie")

    def test_create_account_blank_id_raises(self):
        with self.assertRaises(ValidationError):
            self.service.create_account("")
        with self.assertRaises(ValidationError):
            self.service.create_account("   ")

    def test_create_account_negative_initial_deposit_raises(self):
        with self.assertRaises(ValidationError):
            self.service.create_account("dave", -50.0)

class TestDeposit(unittest.TestCase):
    def setUp(self):
        self.service = AccountService()
        self.service.create_account("alice")

    def test_deposit_success(self):
        acc = self.service.deposit("alice", 500.0)
        self.assertEqual(acc.cash_balance, 500.0)
        self.assertEqual(acc.total_deposited, 500.0)
        self.assertEqual(len(acc.transactions), 1)
        self.assertEqual(acc.transactions[0].transaction_type, TRANSACTION_DEPOSIT)

    def test_deposit_zero_or_negative_raises(self):
        with self.assertRaises(ValidationError):
            self.service.deposit("alice", 0)
        with self.assertRaises(ValidationError):
            self.service.deposit("alice", -10)

class TestWithdrawal(unittest.TestCase):
    def setUp(self):
        self.service = AccountService()
        self.service.create_account("alice", 1000.0)

    def test_withdraw_success(self):
        acc = self.service.withdraw("alice", 200.0)
        self.assertEqual(acc.cash_balance, 800.0)
        self.assertEqual(acc.total_deposited, 1000.0)
        self.assertEqual(len(acc.transactions), 2)
        self.assertEqual(acc.transactions[1].transaction_type, TRANSACTION_WITHDRAW)

    def test_withdraw_too_much_raises(self):
        with self.assertRaises(InsufficientFundsError):
            self.service.withdraw("alice", 1200.0)
        self.assertEqual(self.service.get_account("alice").cash_balance, 1000.0)

    def test_withdraw_zero_or_negative_raises(self):
        with self.assertRaises(ValidationError):
            self.service.withdraw("alice", 0)
        with self.assertRaises(ValidationError):
            self.service.withdraw("alice", -10)

class TestBuy(unittest.TestCase):
    def setUp(self):
        self.service = AccountService()
        self.service.create_account("alice", 1000.0)

    def test_buy_shares_success(self):
        self.service.buy_shares("alice", "AAPL", 2)
        acc = self.service.get_account("alice")
        self.assertEqual(acc.cash_balance, 700.0)
        self.assertEqual(acc.holdings.get("AAPL"), 2)
        txs = acc.transactions
        self.assertEqual(txs[-1].transaction_type, TRANSACTION_BUY)
        self.assertEqual(txs[-1].price, 150.0)

    def test_buy_shares_insufficient_funds_raises(self):
        with self.assertRaises(InsufficientFundsError):
            self.service.buy_shares("alice", "GOOGL", 1)
        acc = self.service.get_account("alice")
        self.assertEqual(acc.cash_balance, 1000.0)
        self.assertNotIn("GOOGL", acc.holdings)

    def test_buy_shares_invalid_quantity_raises(self):
        with self.assertRaises(ValidationError):
            self.service.buy_shares("alice", "AAPL", 0)
        with self.assertRaises(ValidationError):
            self.service.buy_shares("alice", "AAPL", -2)

    def test_buy_unknown_symbol_raises(self):
        with self.assertRaises(UnknownSymbolError):
            self.service.buy_shares("alice", "MSFT", 1)

class TestSell(unittest.TestCase):
    def setUp(self):
        self.service = AccountService()
        self.service.create_account("alice", 1000.0)
        self.service.buy_shares("alice", "AAPL", 4)

    def test_sell_shares_success(self):
        self.service.sell_shares("alice", "AAPL", 2)
        acc = self.service.get_account("alice")
        self.assertEqual(acc.cash_balance, 700.0)
        self.assertEqual(acc.holdings.get("AAPL"), 2)
        self.assertEqual(acc.transactions[-1].transaction_type, TRANSACTION_SELL)

    def test_sell_all_shares_removes_holding(self):
        self.service.sell_shares("alice", "AAPL", 4)
        acc = self.service.get_account("alice")
        self.assertNotIn("AAPL", acc.holdings)

    def test_sell_more_than_owned_raises(self):
        with self.assertRaises(InsufficientSharesError):
            self.service.sell_shares("alice", "AAPL", 5)
        acc = self.service.get_account("alice")
        self.assertEqual(acc.holdings.get("AAPL"), 4)

    def test_sell_invalid_quantity_raises(self):
        with self.assertRaises(ValidationError):
            self.service.sell_shares("alice", "AAPL", 0)
        with self.assertRaises(ValidationError):
            self.service.sell_shares("alice", "AAPL", -1)

class TestReporting(unittest.TestCase):
    def setUp(self):
        self.service = AccountService()
        self.service.create_account("alice", 1000.0)

    def test_get_holdings_returns_copy(self):
        self.service.buy_shares("alice", "AAPL", 1)
        holdings = self.service.get_holdings("alice")
        holdings["AAPL"] = 5
        self.assertEqual(self.service.get_holdings("alice")["AAPL"], 1)

    def test_get_transactions_returns_copy(self):
        txs = self.service.get_transactions("alice")
        txs.clear()
        self.assertEqual(len(self.service.get_transactions("alice")), 1)

    def test_get_portfolio_value_cash_only(self):
        self.assertEqual(self.service.get_portfolio_value("alice"), 1000.0)

    def test_get_portfolio_value_with_holdings(self):
        self.service.buy_shares("alice", "AAPL", 2)
        self.assertEqual(self.service.get_portfolio_value("alice"), 1000.0)

    def test_get_profit_loss(self):
        self.service.buy_shares("alice", "AAPL", 2)
        self.assertEqual(self.service.get_profit_loss("alice"), 0.0)

        self.service.withdraw("alice", 100.0)
        self.assertEqual(self.service.get_profit_loss("alice"), -100.0)

    def test_get_account_summary(self):
        self.service.buy_shares("alice", "AAPL", 2)
        summary = self.service.get_account_summary("alice")
        self.assertEqual(summary["account_id"], "alice")
        self.assertEqual(summary["cash_balance"], 700.0)
        self.assertEqual(summary["holdings_value"], 300.0)
        self.assertEqual(summary["portfolio_value"], 1000.0)
        self.assertEqual(summary["total_deposited"], 1000.0)
        self.assertEqual(summary["profit_loss"], 0.0)

class TestMultiAccount(unittest.TestCase):
    def test_multiple_accounts_are_isolated(self):
        service = AccountService()
        service.create_account("alice", 1000.0)
        service.create_account("bob", 2000.0)

        service.buy_shares("alice", "AAPL", 1)
        service.buy_shares("bob", "TSLA", 1)

        alice_acc = service.get_account("alice")
        bob_acc = service.get_account("bob")

        self.assertEqual(alice_acc.cash_balance, 850.0)
        self.assertEqual(bob_acc.cash_balance, 1750.0)
        self.assertEqual(alice_acc.holdings, {"AAPL": 1})
        self.assertEqual(bob_acc.holdings, {"TSLA": 1})

if __name__ == "__main__":
    unittest.main()