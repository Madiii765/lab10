"""Модульные тесты финансового менеджера и CSV-хранилища."""

import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from finance import FinanceManager
from storage import load_transactions, save_transactions


class TestFinanceManager(unittest.TestCase):
    def setUp(self):
        self.manager = FinanceManager()

    def test_add_income(self):
        self.manager.add_transaction("income", "1000", "Зарплата")
        self.assertEqual(len(self.manager.transactions), 1)

    def test_add_expense(self):
        self.manager.add_transaction("expense", "250", "Еда")
        self.assertEqual(self.manager.transactions[0].kind, "expense")

    def test_income_amount_is_decimal(self):
        item = self.manager.add_transaction("income", "125.50", "Подработка")
        self.assertEqual(item.amount, Decimal("125.50"))

    def test_accept_comma_decimal_separator(self):
        item = self.manager.add_transaction("income", "12,50", "Подарок")
        self.assertEqual(item.amount, Decimal("12.50"))

    def test_reject_zero_amount(self):
        with self.assertRaises(ValueError):
            self.manager.add_transaction("income", "0", "Подарок")

    def test_reject_negative_amount(self):
        with self.assertRaises(ValueError):
            self.manager.add_transaction("expense", "-10", "Еда")

    def test_reject_non_numeric_amount(self):
        with self.assertRaises(ValueError):
            self.manager.add_transaction("income", "abc", "Работа")

    def test_reject_infinite_amount(self):
        with self.assertRaises(ValueError):
            self.manager.add_transaction("income", "Infinity", "Работа")

    def test_reject_unknown_kind(self):
        with self.assertRaises(ValueError):
            self.manager.add_transaction("transfer", "10", "Другое")

    def test_reject_empty_category(self):
        with self.assertRaises(ValueError):
            self.manager.add_transaction("income", "10", " ")

    def test_reject_invalid_date_type(self):
        with self.assertRaises(ValueError):
            self.manager.add_transaction("income", "10", "Работа", "01.01.2026")

    def test_balance_income_only(self):
        self.manager.add_transaction("income", "500", "Зарплата")
        self.assertEqual(self.manager.get_balance(), Decimal("500"))

    def test_balance_expenses_only(self):
        self.manager.add_transaction("expense", "120", "Еда")
        self.assertEqual(self.manager.get_balance(), Decimal("-120"))

    def test_balance_income_minus_expenses(self):
        self.manager.add_transaction("income", "1000", "Зарплата")
        self.manager.add_transaction("expense", "350", "Покупки")
        self.assertEqual(self.manager.get_balance(), Decimal("650"))

    def test_filter_transactions_by_period(self):
        self.manager.add_transaction("income", "100", "A", date(2026, 1, 1))
        self.manager.add_transaction("expense", "20", "B", date(2026, 1, 10))
        self.manager.add_transaction("income", "50", "C", date(2026, 2, 1))
        result = self.manager.get_transactions(date(2026, 1, 1), date(2026, 1, 31))
        self.assertEqual(len(result), 2)

    def test_transactions_are_sorted_by_date(self):
        self.manager.add_transaction("income", "10", "Позже", date(2026, 2, 1))
        self.manager.add_transaction("income", "20", "Раньше", date(2026, 1, 1))
        result = self.manager.get_transactions()
        self.assertEqual(result[0].category, "Раньше")

    def test_period_report_totals(self):
        self.manager.add_transaction("income", "1000", "Зарплата", date(2026, 3, 1))
        self.manager.add_transaction("expense", "200", "Еда", date(2026, 3, 2))
        report = self.manager.get_period_report(date(2026, 3, 1), date(2026, 3, 31))
        self.assertEqual(report["income"], Decimal("1000"))
        self.assertEqual(report["expenses"], Decimal("200"))
        self.assertEqual(report["balance"], Decimal("800"))

    def test_period_report_rejects_reversed_dates(self):
        with self.assertRaises(ValueError):
            self.manager.get_period_report(date(2026, 4, 2), date(2026, 4, 1))

    def test_empty_period_report(self):
        report = self.manager.get_period_report(date(2026, 1, 1), date(2026, 1, 31))
        self.assertEqual(report["income"], Decimal("0"))
        self.assertEqual(report["expenses"], Decimal("0"))
        self.assertEqual(report["transactions"], [])

    def test_remove_transaction(self):
        item = self.manager.add_transaction("income", "100", "Зарплата")
        self.assertTrue(self.manager.remove_transaction(item))
        self.assertEqual(len(self.manager.transactions), 0)

    def test_remove_unknown_transaction(self):
        item = FinanceManager().add_transaction("income", "100", "Зарплата")
        self.assertFalse(self.manager.remove_transaction(item))

    def test_category_summary(self):
        self.manager.add_transaction("income", "1000", "Зарплата")
        self.manager.add_transaction("expense", "200", "Зарплата")
        summary = self.manager.get_category_summary()
        self.assertEqual(summary["Зарплата"]["income"], Decimal("1000"))
        self.assertEqual(summary["Зарплата"]["expenses"], Decimal("200"))
        self.assertEqual(summary["Зарплата"]["balance"], Decimal("800"))

    def test_save_and_load_csv(self):
        self.manager.add_transaction("income", "750.25", "Работа", date(2026, 5, 5), "Аванс")
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "data.csv"
            save_transactions(self.manager, path)
            loaded = load_transactions(path)
        self.assertEqual(len(loaded.transactions), 1)
        self.assertEqual(loaded.transactions[0].amount, Decimal("750.25"))
        self.assertEqual(loaded.transactions[0].description, "Аванс")

    def test_load_missing_file_returns_empty_manager(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "missing.csv"
            loaded = load_transactions(path)
        self.assertEqual(len(loaded.transactions), 0)


if __name__ == "__main__":
    unittest.main()
