"""
models.py — структуры данных системы расчёта себестоимости.
Описывают сущности, которые передаются между блоками IDEF0 (A1 → A2 → A3 → A4).
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class Material:
    """Материал изделия (из спецификации/BOM)."""
    name: str                 # наименование детали/заготовки
    grade: str                # марка материала (напр. "Сталь 45")
    mass_billet: float        # масса заготовки, кг
    mass_part: float          # масса готовой детали, кг
    price_per_kg: float = 0.0     # цена материала за кг (подставляется в A2)
    price_waste_per_kg: float = 0.0  # цена возвратных отходов за кг (A2)


@dataclass
class Operation:
    """Технологическая операция (из маршрута)."""
    name: str                 # название операции (токарная, фрезерная...)
    equipment: str            # оборудование
    time_norm: float          # норма времени, нормо-час
    worker_grade: str = ""    # разряд рабочего (для подстановки тарифа в A2)
    rate_machine_hour: float = 0.0  # стоимость машино-часа, руб (A2)
    rate_worker: float = 0.0        # тарифная ставка рабочего, руб/час (A2)


@dataclass
class ProductData:
    """Структурированные данные изделия — результат A1, обогащаются в A2."""
    product_name: str
    materials: List[Material] = field(default_factory=list)
    operations: List[Operation] = field(default_factory=list)
    # нормативы (подставляются в A2 из справочников)
    insurance_rate: float = 0.30      # ставка страховых взносов (доля)
    overhead_rate: float = 0.0        # % накладных расходов (доля от прямых)


@dataclass
class CostResult:
    """Итог расчёта — результат A3, оформляется в A4."""
    product_name: str
    material_cost: float = 0.0        # A31 — материальные затраты
    operations_cost: float = 0.0      # A32 — затраты на операции
    wage_cost: float = 0.0            # в т.ч. зарплата с взносами
    equipment_cost: float = 0.0       # в т.ч. эксплуатация оборудования
    overhead_cost: float = 0.0        # A33 — накладные расходы
    metal_utilization: float = 0.0    # коэффициент металлоёмкости
    direct_cost: float = 0.0          # прямые затраты (материалы + операции)
    total_cost: float = 0.0           # A34 — итоговая себестоимость
