"""Основная бизнес-логика финансового учёта."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation


@dataclass
class Transaction:
    """Одна операция: доход или расход."""

    transaction_date: date
    kind: str
    amount: Decimal
    category: str
    description: str = ""

    def __post_init__(self):
        if self.kind not in ("income", "expense"):
            raise ValueError("Тип операции должен быть income или expense.")
        if not isinstance(self.transaction_date, date):
            raise ValueError("Дата операции указана некорректно.")
        if not isinstance(self.amount, Decimal) or not self.amount.is_finite():
            raise ValueError("Сумма должна быть корректным конечным числом.")
        if self.amount <= 0:
            raise ValueError("Сумма должна быть больше нуля.")
        if not isinstance(self.category, str) or not self.category.strip():
            raise ValueError("Категория не может быть пустой.")
        if not isinstance(self.description, str):
            raise ValueError("Описание должно быть текстом.")


class FinanceManager:
    """Управляет списком операций и выполняет финансовые расчёты."""

    def __init__(self):
        self.transactions = []

    def add_transaction(self, kind, amount, category, transaction_date=None, description=""):
        """Проверяет данные и добавляет новую операцию."""
        if transaction_date is None:
            transaction_date = date.today()

        if not isinstance(amount, Decimal):
            try:
                amount = Decimal(str(amount).replace(",", "."))
            except (InvalidOperation, ValueError) as exc:
                raise ValueError("Некорректная сумма.") from exc

        if not amount.is_finite():
            raise ValueError("Сумма должна быть конечным числом.")

        transaction = Transaction(
            transaction_date=transaction_date,
            kind=kind,
            amount=amount,
            category=category.strip() if isinstance(category, str) else category,
            description=description.strip() if isinstance(description, str) else description,
        )
        self.transactions.append(transaction)
        return transaction

    def remove_transaction(self, transaction):
        """Удаляет конкретную операцию. Возвращает True, если она найдена."""
        for index, item in enumerate(self.transactions):
            if item is transaction:
                del self.transactions[index]
                return True
        return False

    def get_balance(self):
        """Возвращает общий баланс: доходы минус расходы."""
        income = sum(
            (item.amount for item in self.transactions if item.kind == "income"),
            Decimal("0"),
        )
        expenses = sum(
            (item.amount for item in self.transactions if item.kind == "expense"),
            Decimal("0"),
        )
        return income - expenses

    def get_transactions(self, start_date=None, end_date=None):
        """Возвращает операции за период, отсортированные по дате."""
        if start_date is not None and end_date is not None and start_date > end_date:
            raise ValueError("Начальная дата не может быть позже конечной.")

        result = self.transactions
        if start_date is not None:
            result = [item for item in result if item.transaction_date >= start_date]
        if end_date is not None:
            result = [item for item in result if item.transaction_date <= end_date]
        return sorted(result, key=lambda item: item.transaction_date)

    def get_period_report(self, start_date, end_date):
        """Формирует сводные суммы и список операций за период."""
        if start_date > end_date:
            raise ValueError("Начальная дата не может быть позже конечной.")

        period_transactions = self.get_transactions(start_date, end_date)
        income = sum(
            (item.amount for item in period_transactions if item.kind == "income"),
            Decimal("0"),
        )
        expenses = sum(
            (item.amount for item in period_transactions if item.kind == "expense"),
            Decimal("0"),
        )
        return {
            "start_date": start_date,
            "end_date": end_date,
            "income": income,
            "expenses": expenses,
            "balance": income - expenses,
            "transactions": period_transactions,
        }

    def get_category_summary(self):
        """Возвращает суммы доходов и расходов отдельно по каждой категории."""
        summary = {}
        for item in self.transactions:
            if item.category not in summary:
                summary[item.category] = {
                    "income": Decimal("0"),
                    "expenses": Decimal("0"),
                }
            key = "income" if item.kind == "income" else "expenses"
            summary[item.category][key] += item.amount

        for values in summary.values():
            values["balance"] = values["income"] - values["expenses"]
        return summary
