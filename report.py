"""
report.py — БЛОК A4 «Формирование калькуляции и отчёта».

Задача блока: оформить рассчитанные затраты (из A3) в итоговые документы —
плановую калькуляцию по статьям (Excel) и структурированный JSON.
"""
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from models import CostResult, ProductData

FONT = "Times New Roman"
HEAD_FILL = PatternFill("solid", start_color="D6E4F0")
TOTAL_FILL = PatternFill("solid", start_color="FCE8B2")
THIN = Side(style="thin", color="999999")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def _style_header(cell):
    cell.font = Font(name=FONT, bold=True, size=11)
    cell.fill = HEAD_FILL
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = BORDER


def to_excel(result: CostResult, product: ProductData, path: str):
    """Формирует плановую калькуляцию по статьям в Excel."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Калькуляция"

    ws["A1"] = f"Плановая калькуляция себестоимости: {result.product_name}"
    ws["A1"].font = Font(name=FONT, bold=True, size=13)
    ws.merge_cells("A1:C1")

    # шапка таблицы
    r = 3
    for col, title in zip("ABC", ["№", "Статья калькуляции", "Сумма, руб."]):
        c = ws[f"{col}{r}"]
        c.value = title
        _style_header(c)

    # статьи (значения как формулы, где это агрегаты)
    rows = [
        ("1", "Материальные затраты", result.material_cost),
        ("2", "Затраты на технологические операции", result.operations_cost),
        ("2.1", "   в т.ч. основная зарплата с взносами", result.wage_cost),
        ("2.2", "   в т.ч. содержание оборудования", result.equipment_cost),
        ("3", "Прямые затраты (стр. 1 + стр. 2)", None),      # формула
        ("4", "Накладные расходы", result.overhead_cost),
        ("5", "Итого плановая себестоимость (стр. 3 + стр. 4)", None),  # формула
    ]
    start = r + 1
    for i, (num, article, value) in enumerate(rows):
        rr = start + i
        ws[f"A{rr}"] = num
        ws[f"B{rr}"] = article
        cell = ws[f"C{rr}"]
        if num == "3":
            cell.value = f"=C{start}+C{start+1}"        # материалы + операции
        elif num == "5":
            cell.value = f"=C{start+4}+C{start+5}"       # прямые + накладные
        else:
            cell.value = value
        cell.number_format = '#,##0.00'
        for col in "ABC":
            ws[f"{col}{rr}"].font = Font(name=FONT, size=11)
            ws[f"{col}{rr}"].border = BORDER
        if num in ("3", "5"):
            for col in "ABC":
                ws[f"{col}{rr}"].fill = TOTAL_FILL
                ws[f"{col}{rr}"].font = Font(name=FONT, size=11, bold=True)

    # доп. показатель
    extra = start + len(rows) + 1
    ws[f"A{extra}"] = "Коэффициент металлоёмкости:"
    ws[f"A{extra}"].font = Font(name=FONT, italic=True, size=11)
    ws.merge_cells(f"A{extra}:B{extra}")
    ws[f"C{extra}"] = result.metal_utilization
    ws[f"C{extra}"].number_format = '0.000'
    ws[f"C{extra}"].font = Font(name=FONT, italic=True, size=11)

    ws.column_dimensions["A"].width = 6
    ws.column_dimensions["B"].width = 46
    ws.column_dimensions["C"].width = 16

    wb.save(path)


def to_json(result: CostResult, path: str):
    """Экспорт результата в JSON (для смежных блоков системы и 1С)."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result.__dict__, f, ensure_ascii=False, indent=2)
