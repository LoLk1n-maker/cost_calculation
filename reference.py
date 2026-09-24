"""
reference.py — БЛОК A2 «Сопоставление со справочниками».

Задача блока: подставить к структурированным данным (из A1) цены материалов,
тарифы рабочих, стоимость машино-часа и нормативы из справочников предприятия.
На выходе — «обогащённые данные», готовые к расчёту.
"""
import json
from models import ProductData


class Reference:
    """Справочники цен и ставок предприятия."""

    def __init__(self, path: str):
        with open(path, encoding="utf-8") as f:
            self.data = json.load(f)

    def material_price(self, grade: str) -> float:
        return self.data["materials_price_per_kg"].get(grade, 0.0)

    def waste_price(self, grade: str) -> float:
        return self.data["waste_price_per_kg"].get(grade, 0.0)

    def machine_rate(self, equipment: str) -> float:
        return self.data["machine_hour_rate"].get(equipment, 0.0)

    def worker_rate(self, grade: str) -> float:
        return self.data["worker_rate_by_grade"].get(grade, 0.0)

    @property
    def insurance_rate(self) -> float:
        return self.data.get("insurance_rate", 0.30)

    @property
    def overhead_rate(self) -> float:
        return self.data.get("overhead_rate", 0.0)


def enrich(product: ProductData, ref: Reference) -> ProductData:
    """Основная функция блока A2: обогащает данные ценами и ставками."""
    missing = []

    for m in product.materials:
        m.price_per_kg = ref.material_price(m.grade)
        m.price_waste_per_kg = ref.waste_price(m.grade)
        if m.price_per_kg == 0.0:
            missing.append(f"нет цены материала «{m.grade}»")

    for op in product.operations:
        op.rate_machine_hour = ref.machine_rate(op.equipment)
        op.rate_worker = ref.worker_rate(op.worker_grade)
        if op.rate_machine_hour == 0.0:
            missing.append(f"нет ставки машино-часа «{op.equipment}»")
        if op.rate_worker == 0.0:
            missing.append(f"нет тарифа «{op.worker_grade}»")

    product.insurance_rate = ref.insurance_rate
    product.overhead_rate = ref.overhead_rate

    if missing:
        print("[A2] Предупреждения по справочникам:")
        for w in dict.fromkeys(missing):  # уникальные, с порядком
            print("   -", w)

    return product
