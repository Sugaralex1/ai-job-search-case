"""Скоринг вакансій: бал від 0 до 10 за зваженими критеріями.

Працює для різних ролей через профілі: sales, hr, frontend, backend, devops.
Кожен профіль має свої ваги критеріїв і приклад мінімальної зарплати.

Запуск:
    python vacancy_score.py vacancies_example.csv --profile sales
    python vacancy_score.py vacancies_it_example.csv --profile backend --min-salary 80000
    python vacancy_score.py --list

Колонки CSV (значення 0..1, крім зарплати):
    company_name, title  назва компанії і посади
    expected_net         зарплата на руки, грн
    schedule             графік: 5/2 = 1, частково суботи = 0.6, 6/1 = 0
    remote               віддалено = 1, гібрид = 0.5, тільки офіс = 0
    role_fit             наскільки роль збігається з тим, що ви хочете робити
    stack_match          збіг з вашим стеком або інструментами (для IT)
    no_car               авто не потрібне = 1, бажане = 0.5, обов'язкове = 0
    growth               перспектива росту (ваша оцінка)
    company              якість компанії (ваша оцінка)

Потрібні лише колонки, які використовує обраний профіль.
"""
import argparse
import csv
import sys

# Ваги в кожному профілі в сумі дають 1.0.
# min_salary це лише приклад, задайте свій через --min-salary.
PROFILES = {
    "sales": {
        "title": "Продажі (B2B, B2C)",
        "min_salary": 30_000,
        "weights": {"salary": 0.30, "role_fit": 0.20, "schedule": 0.15,
                    "growth": 0.15, "no_car": 0.10, "company": 0.10},
    },
    "hr": {
        "title": "HR, рекрутинг",
        "min_salary": 30_000,
        "weights": {"salary": 0.25, "role_fit": 0.25, "schedule": 0.15,
                    "growth": 0.15, "company": 0.15, "remote": 0.05},
    },
    "frontend": {
        "title": "Frontend",
        "min_salary": 50_000,
        "weights": {"salary": 0.30, "stack_match": 0.25, "remote": 0.15,
                    "growth": 0.15, "company": 0.15},
    },
    "backend": {
        "title": "Backend",
        "min_salary": 60_000,
        "weights": {"salary": 0.30, "stack_match": 0.25, "remote": 0.15,
                    "growth": 0.15, "company": 0.15},
    },
    "devops": {
        "title": "DevOps",
        "min_salary": 70_000,
        "weights": {"salary": 0.30, "stack_match": 0.25, "remote": 0.10,
                    "schedule": 0.10, "growth": 0.15, "company": 0.10},
    },
}


def salary_score(expected_net: float, min_salary: float) -> float:
    """0 нижче мінімуму, 0.5 на мінімумі, 1.0 від подвійного мінімуму."""
    if expected_net < min_salary:
        return 0.0
    return min(1.0, 0.5 + 0.5 * (expected_net - min_salary) / min_salary)


def score(row: dict, weights: dict, min_salary: float) -> float:
    total = 0.0
    salary_ok = True
    for key, weight in weights.items():
        if key == "salary":
            value = salary_score(float(row["expected_net"]), min_salary)
            salary_ok = value > 0
        else:
            value = float(row[key])
        total += weight * value
    if not salary_ok:  # нижче мінімуму вакансія не проходить
        total = min(total, 0.3)
    return round(total * 10, 1)


def check_columns(rows: list, weights: dict) -> None:
    needed = {"company_name", "title"} | {
        "expected_net" if k == "salary" else k for k in weights}
    missing = needed - set(rows[0].keys()) if rows else set()
    if missing:
        sys.exit(f"У файлі бракує колонок: {', '.join(sorted(missing))}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Скоринг вакансій за профілем ролі")
    parser.add_argument("csv", nargs="?", help="файл з вакансіями")
    parser.add_argument("--profile", default="sales", choices=PROFILES)
    parser.add_argument("--min-salary", type=float, help="ваш мінімум на руки, грн")
    parser.add_argument("--list", action="store_true", help="показати профілі")
    args = parser.parse_args()

    if args.list or not args.csv:
        for name, p in PROFILES.items():
            ws = ", ".join(f"{k} {int(v * 100)}%" for k, v in p["weights"].items())
            print(f"{name:<9} {p['title']:<20} {ws}")
        return

    profile = PROFILES[args.profile]
    min_salary = args.min_salary or profile["min_salary"]
    with open(args.csv, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    check_columns(rows, profile["weights"])

    ranked = sorted(rows, key=lambda r: score(r, profile["weights"], min_salary), reverse=True)
    print(f"Профіль: {profile['title']}, мінімум {int(min_salary)} грн")
    print(f"{'Бал':>4}  {'Компанія':<14} Посада")
    print("-" * 50)
    for r in ranked:
        print(f"{score(r, profile['weights'], min_salary):>4}  {r['company_name']:<14} {r['title']}")


if __name__ == "__main__":
    main()
