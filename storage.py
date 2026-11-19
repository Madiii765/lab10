"""Сохранение и загрузка финансовых операций в формате CSV."""

import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from finance import FinanceManager


FIELDS = ["transaction_date", "kind", "amount", "category", "description"]


def save_transactions(manager, filename="transactions.csv"):
    """Сохраняет все операции в CSV-файл."""
    path = Path(filename)
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        for transaction in manager.transactions:
            writer.writerow({
                "transaction_date": transaction.transaction_date.isoformat(),
                "kind": transaction.kind,
                "amount": str(transaction.amount),
                "category": transaction.category,
                "description": transaction.description,
            })


def load_transactions(filename="transactions.csv"):
    """Загружает операции; некорректные строки пропускаются."""
    manager = FinanceManager()
    path = Path(filename)
    if not path.exists():
        return manager

    with path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                manager.add_transaction(
                    kind=row["kind"],
                    amount=Decimal(row["amount"]),
                    category=row["category"],
                    transaction_date=date.fromisoformat(row["transaction_date"]),
                    description=row.get("description") or "",
                )
            except (ValueError, KeyError, TypeError, InvalidOperation):
                # Одна повреждённая строка не мешает загрузке остальных операций.
                continue
    return manager
