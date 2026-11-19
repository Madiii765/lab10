"""Точка входа консольного приложения «Финансовый учёт»."""

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from finance import FinanceManager
from reports import (
    print_category_summary,
    print_period_report,
    print_transactions,
)
from storage import load_transactions, save_transactions


# Файл данных всегда находится рядом с main.py, а не в текущей папке терминала.
DATA_FILE = Path(__file__).resolve().parent / "transactions.csv"


def read_date(prompt):
    """Запрашивает дату в формате ДД.ММ.ГГГГ."""
    value = input(prompt).strip()
    try:
        return datetime.strptime(value, "%d.%m.%Y").date()
    except ValueError as exc:
        raise ValueError("Введите существующую дату в формате ДД.ММ.ГГГГ.") from exc


def read_amount():
    """Запрашивает положительную денежную сумму."""
    value = input("Сумма: ").strip().replace(",", ".")
    try:
        amount = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("Введите корректное число.") from exc
    if not amount.is_finite() or amount <= 0:
        raise ValueError("Сумма должна быть конечным числом больше нуля.")
    return amount


def add_operation(manager, kind):
    """Собирает данные у пользователя и добавляет операцию."""
    amount = read_amount()
    category = input("Категория: ").strip()
    if not category:
        raise ValueError("Категория не может быть пустой.")

    description = input("Описание (необязательно): ").strip()
    date_text = input("Дата (ДД.ММ.ГГГГ, Enter — сегодня): ").strip()
    if date_text:
        try:
            operation_date = datetime.strptime(date_text, "%d.%m.%Y").date()
        except ValueError as exc:
            raise ValueError("Введите существующую дату в формате ДД.ММ.ГГГГ.") from exc
    else:
        operation_date = date.today()

    manager.add_transaction(kind, amount, category, operation_date, description)
    save_transactions(manager, DATA_FILE)
    print("Операция успешно добавлена.")


def delete_operation(manager):
    """Показывает историю и удаляет выбранную операцию."""
    transactions = manager.get_transactions()
    if not transactions:
        print("Нет операций для удаления.")
        return

    print_transactions(transactions)
    value = input("Введите номер операции для удаления (0 — отмена): ").strip()
    if not value.isdigit():
        raise ValueError("Введите номер операции цифрами.")

    number = int(value)
    if number == 0:
        print("Удаление отменено.")
        return
    if number < 1 or number > len(transactions):
        raise ValueError("Операции с таким номером нет.")

    if manager.remove_transaction(transactions[number - 1]):
        save_transactions(manager, DATA_FILE)
        print("Операция удалена.")


def main():
    manager = load_transactions(DATA_FILE)

    while True:
        print("\n=== ФИНАНСОВЫЙ УЧЁТ ===")
        print("1. Добавить доход")
        print("2. Добавить расход")
        print("3. Показать историю операций")
        print("4. Показать баланс")
        print("5. Отчёт за период")
        print("6. Удалить операцию")
        print("7. Статистика по категориям")
        print("0. Выход")

        choice = input("Выберите действие: ").strip()
        try:
            if choice == "1":
                add_operation(manager, "income")
            elif choice == "2":
                add_operation(manager, "expense")
            elif choice == "3":
                print_transactions(manager.get_transactions())
            elif choice == "4":
                print(f"Текущий баланс: {manager.get_balance():.2f}")
            elif choice == "5":
                start = read_date("Начальная дата (ДД.ММ.ГГГГ): ")
                end = read_date("Конечная дата (ДД.ММ.ГГГГ): ")
                print_period_report(manager.get_period_report(start, end))
            elif choice == "6":
                delete_operation(manager)
            elif choice == "7":
                print_category_summary(manager.get_category_summary())
            elif choice == "0":
                save_transactions(manager, DATA_FILE)
                print("Данные сохранены. До свидания!")
                break
            else:
                print("Неизвестная команда. Попробуйте ещё раз.")
        except (ValueError, OSError) as error:
            print(f"Ошибка: {error}")


if __name__ == "__main__":
    main()
