"""
main.py — точка входа. Связывает блоки IDEF0 в единую цепочку:
    A1 (парсинг) → A2 (справочники) → A3 (расчёт) → A4 (отчёт)

Запуск:
    python main.py
"""
import os
from parser_ai import analyze_inputs
from reference import Reference, enrich
from calculator import calculate
from report import to_excel, to_json

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
OUT = os.path.join(BASE, "output")


def run(product_name="Вал-шестерня 12.34.567"):
    os.makedirs(OUT, exist_ok=True)

    # --- A1: Анализ входных данных -------------------------------------
    product = analyze_inputs(
        spec_path=os.path.join(DATA, "specification.xlsx"),
        route_path=os.path.join(DATA, "route.xlsx"),
        product_name=product_name,
    )
    print(f"[A1] Распознано: {len(product.materials)} материалов, "
          f"{len(product.operations)} операций")

    # --- A2: Сопоставление со справочниками -----------------------------
    ref = Reference(os.path.join(DATA, "spravochniki.json"))
    product = enrich(product, ref)
    print("[A2] Цены и ставки подставлены")

    # --- A3: Расчёт себестоимости ---------------------------------------
    result = calculate(product)
    print("[A3] Расчёт выполнен")

    # --- A4: Формирование калькуляции и отчёта --------------------------
    xlsx_path = os.path.join(OUT, "kalkulyaciya.xlsx")
    json_path = os.path.join(OUT, "kalkulyaciya.json")
    to_excel(result, product, xlsx_path)
    to_json(result, json_path)
    print(f"[A4] Калькуляция сохранена: {xlsx_path}")

    _print_summary(result)
    return result


def _print_summary(r):
    print("\n" + "=" * 52)
    print(f"  ПЛАНОВАЯ КАЛЬКУЛЯЦИЯ: {r.product_name}")
    print("=" * 52)
    print(f"  1. Материальные затраты      {r.material_cost:>12,.2f} руб.")
    print(f"  2. Затраты на операции       {r.operations_cost:>12,.2f} руб.")
    print(f"       - зарплата с взносами   {r.wage_cost:>12,.2f} руб.")
    print(f"       - оборудование          {r.equipment_cost:>12,.2f} руб.")
    print(f"  3. Прямые затраты            {r.direct_cost:>12,.2f} руб.")
    print(f"  4. Накладные расходы         {r.overhead_cost:>12,.2f} руб.")
    print("-" * 52)
    print(f"  ИТОГО себестоимость          {r.total_cost:>12,.2f} руб.")
    print(f"  Коэффициент металлоёмкости   {r.metal_utilization:>12.3f}")
    print("=" * 52)


if __name__ == "__main__":
    run()
