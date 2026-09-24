"""
calculator.py — БЛОК A3 «Расчёт себестоимости».

Реализует декомпозицию A3 на четыре подфункции:
    A31 — расчёт материальных затрат
    A32 — расчёт затрат на операции
    A33 — расчёт накладных расходов
    A34 — формирование статей калькуляции (агрегация)
"""
from models import ProductData, CostResult


def a31_material_cost(product: ProductData):
    """A31 — Материальные затраты.
    Стоимость заготовки за вычетом возвратных отходов.
    Дополнительно — коэффициент металлоёмкости.
    """
    total = 0.0
    mass_billet_sum = 0.0
    mass_part_sum = 0.0
    for m in product.materials:
        billet_cost = m.mass_billet * m.price_per_kg
        waste_mass = max(m.mass_billet - m.mass_part, 0.0)
        waste_return = waste_mass * m.price_waste_per_kg
        total += billet_cost - waste_return
        mass_billet_sum += m.mass_billet
        mass_part_sum += m.mass_part

    metal_utilization = (mass_part_sum / mass_billet_sum) if mass_billet_sum else 0.0
    return total, metal_utilization


def a32_operations_cost(product: ProductData):
    """A32 — Затраты на операции.
    По каждой операции: оплата труда (с страховыми взносами) + эксплуатация оборудования.
    """
    wage_total = 0.0
    equipment_total = 0.0
    for op in product.operations:
        wage = op.time_norm * op.rate_worker * (1 + product.insurance_rate)
        equipment = op.time_norm * op.rate_machine_hour
        wage_total += wage
        equipment_total += equipment
    operations_total = wage_total + equipment_total
    return operations_total, wage_total, equipment_total


def a33_overhead_cost(direct_cost: float, product: ProductData):
    """A33 — Накладные расходы. Процент от прямых затрат."""
    return direct_cost * product.overhead_rate


def a34_aggregate(product: ProductData) -> CostResult:
    """A34 — Формирование статей калькуляции. Сводит A31, A32, A33 в итог."""
    material_cost, metal_util = a31_material_cost(product)
    operations_cost, wage, equipment = a32_operations_cost(product)
    direct_cost = material_cost + operations_cost
    overhead_cost = a33_overhead_cost(direct_cost, product)
    total = direct_cost + overhead_cost

    return CostResult(
        product_name=product.product_name,
        material_cost=round(material_cost, 2),
        operations_cost=round(operations_cost, 2),
        wage_cost=round(wage, 2),
        equipment_cost=round(equipment, 2),
        overhead_cost=round(overhead_cost, 2),
        metal_utilization=round(metal_util, 3),
        direct_cost=round(direct_cost, 2),
        total_cost=round(total, 2),
    )


def calculate(product: ProductData) -> CostResult:
    """Основная функция блока A3: полный расчёт себестоимости."""
    return a34_aggregate(product)
