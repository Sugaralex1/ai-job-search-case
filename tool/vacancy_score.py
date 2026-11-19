"""Скоринг вакансій для пошуку роботи в продажах.

Кожна вакансія отримує бал від 0 до 10 за зваженими критеріями.
Ваги і мінімальна зарплата налаштовуються нижче.

Запуск:
    python vacancy_score.py vacancies_example.csv
"""
import csv
import sys

MIN_NET_SALARY = 40_000  # грн на руки, мінімум

# Ваги критеріїв (сума = 1.0)
WEIGHTS = {
    "salary": 0.30,     # дохід відносно мінімуму
    "schedule": 0.15,   # 5/2 = 1, 5/2 з суботами за вихідний = 0.6, 6/1 = 0
    "b2b_it": 0.20,     # B2B/IT/CRM = 1, B2B інше = 0.6, B2C = 0.2
    "no_car": 0.10,     # авто не обов'язкове = 1, бажане = 0.5, обов'язкове = 0
    "growth": 0.15,     # перспектива росту, 0..1 (моя оцінка)
    "company": 0.10,    # якість компанії, 0..1 (моя оцінка)
}


def salary_score(expected_net: float) -> float:
    """0 нижче мінімуму, 0.5 на мінімумі, 1.0 від подвійного мінімуму."""
    if expected_net < MIN_NET_SALARY:
        return 0.0
    ratio = (expected_net - MIN_NET_SALARY) / MIN_NET_SALARY
    return min(1.0, 0.5 + 0.5 * ratio)


def score(row: dict) -> float:
    parts = {
        "salary": salary_score(float(row["expected_net"])),
        "schedule": float(row["schedule"]),
        "b2b_it": float(row["b2b_it"]),
        "no_car": float(row["no_car"]),
        "growth": float(row["growth"]),
        "company": float(row["company"]),
    }
    total = sum(WEIGHTS[k] * v for k, v in parts.items())
    # Жорсткий фільтр: нижче мінімуму вакансія не проходить
    if parts["salary"] == 0:
        total = min(total, 0.3)
    return round(total * 10, 1)


def main(path: str) -> None:
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    ranked = sorted(rows, key=score, reverse=True)
    print(f"{'Бал':>4}  {'Компанія':<14} Посада")
    print("-" * 50)
    for r in ranked:
        print(f"{score(r):>4}  {r['company_name']:<14} {r['title']}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Використання: python vacancy_score.py <файл.csv>")
        sys.exit(1)
    main(sys.argv[1])
