"""Функции для отображения истории и отчётов."""


def print_transactions(transactions):
    if not transactions:
        print("Операций не найдено.")
        return

    print("\nИстория операций:")
    print("-" * 86)
    print(f"{'№':<4} {'Дата':<12} {'Тип':<10} {'Сумма':>12} {'Категория':<18} Описание")
    print("-" * 86)
    for number, item in enumerate(transactions, start=1):
        kind = "Доход" if item.kind == "income" else "Расход"
        print(
            f"{number:<4} {item.transaction_date:%d.%m.%Y}  "
            f"{kind:<10} {item.amount:>12.2f} "
            f"{item.category:<18} {item.description}"
        )
    print("-" * 86)


def print_period_report(report):
    print(f"\nОтчёт за период: {report['start_date']:%d.%m.%Y} — {report['end_date']:%d.%m.%Y}")
    print(f"Доходы:  {report['income']:.2f}")
    print(f"Расходы: {report['expenses']:.2f}")
    print(f"Итог:    {report['balance']:.2f}")
    print_transactions(report["transactions"])


def print_category_summary(summary):
    if not summary:
        print("Пока нет операций для статистики.")
        return

    print("\nСтатистика по категориям:")
    print("-" * 66)
    print(f"{'Категория':<20} {'Доходы':>14} {'Расходы':>14} {'Итог':>14}")
    print("-" * 66)
    for category, values in sorted(summary.items()):
        print(
            f"{category:<20} {values['income']:>14.2f} "
            f"{values['expenses']:>14.2f} {values['balance']:>14.2f}"
        )
    print("-" * 66)
