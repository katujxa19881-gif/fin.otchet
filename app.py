import streamlit as st
import pandas as pd
import plotly.express as px


# ------------------------
# 1. Исходные данные
# ------------------------

# Годовая выручка (общая, фиксированная)
TOTAL_REVENUE = 620_682_373.59  # руб

# Годовые расходы (как в файле Excel, лист "Свод")
yearly_expenses = {
    "material":       38_374_083.32,
    "fotpr":          97_689_625.69,
    "prochie_pr":     22_559_651.69,
    "amort_pr":       50_628_156.84,
    "fotopR":        143_704_063.88,
    "amort_opr":      8_527_933.20,
    "ostalnye_opr":  28_015_544.97,
    "fotoxr":        58_189_393.57,
    "amort_oxr":     12_291_689.47,
    "ostalnye_oxr":  67_382_397.10,
    "commersial":        195_860.72,
    "logistika_hub":      959_983.83,
    "logistika_vnesh": 19_590_419.54,
    "logistika_barton":   704_202.91,
    "procenty":      106_105_864.26,
}

# Таблица номенклатуры (31 модель) с параметрами
# Взято из последнего HTML-варианта (категория, количество, трудоёмкость, цена, материалы). [file:3]
products_data = [
    # Внутренний заказ
    ("Приемник Триколор Стандарт 2", "Внутренний заказ", 100_420, 619.50, 416.37, 24.99),
    ("MB R1N02",                      "Внутренний заказ",  56_500, 409.55, 412.55, 18.98),
    ("Гл.платы",                      "Внутренний заказ",   1_500, 460.50, 369.32, 21.30),

    # Внешние заказы
    ("Булат Коммутатор",             "Внешние заказы",       600, 15664.14, 16219.99, 507.53),
    ("Qtech (Серв./Коммутатор)",     "Внешние заказы",       250, 17007.50, 13191.70, 362.24),
    ("Аквариус (Мат.платы 610T)",    "Внешние заказы",     20_000, 1749.40, 1451.57, 102.69),
    ("Плата системная (DPH)",        "Внешние заказы",  23_974.50, 2088.80, 1752.84, 90.12),
    ("IP-камера",                    "Внешние заказы",    10_000, 337.07, 335.56, 4.85),
    ("Модуль оперативной памяти",    "Внешние заказы",     5_000, 160.70, 304.51, 4.68),
    ("Амур серверная плата",         "Внешние заказы",     1_000, 13915.00, 11153.99, 572.90),
    ("Депо Серверная плата",         "Внешние заказы",     2_500, 11277.05, 9526.39, 466.61),
    ("Смартфон Смарт Экосистема",    "Внешние заказы",    18_000, 3325.64, 2702.01, 88.52),
    ("РДВ Серверная плата",          "Внешние заказы",     1_000, 13224.56, 10611.45, 355.56),
    ("Процессорный модуль Ядро",     "Внешние заказы",    57_204, 1928.48, 2112.55, 169.38),
    ("Амур плата системная",         "Внешние заказы",     7_737, 2858.43, 2404.13, 184.27),
    ("ICL Материнские платы",        "Внешние заказы",     4_000, 1819.80, 1654.58, 101.30),
    ("ЭмСтор (модули SSD)",          "Внешние заказы",    25_633, 258.82, 421.17, 13.60),
    ("HTP Радиолинейный модуль",     "Внешние заказы",    20_000, 1064.47, 1188.05, 141.59),
    ("РДВ Мат.платы",                "Внешние заказы",    10_500, 2085.00, 1752.84, 88.92),
    ("Qtech Электронные модули",     "Внешние заказы",     5_377, 3222.41, 2851.41, 286.81),
    ("Delta Computers плата монитора","Внешние заказы",   10_000, 333.31, 484.80, 33.84),
    ("Сбербокс",                     "Внешние заказы",    52_000, 630.55, 291.66, 15.51),

    # Вычтех
    ("Блоки питания",                "Вычтех",            10_100, 2861.04, 2332.23, 179.40),
    ("Плата для ПК",                 "Вычтех",             1_000, 418.50, 534.34, 15.04),
    ("Ноутбук",                      "Вычтех",             3_500, 4340.73, 3682.27, 79.88),
    ("ПК",                           "Вычтех",                 0, 1837.00, 1362.89, 141.59),
    ("Серверная платформа Gen4",     "Вычтех",             2_100, 15715.58, 13080.77, 668.78),
    ("Серверная платформа ODM",      "Вычтех",                 0, 24944.20, 16666.67, 1168.94),
    ("Сатро-Палладин (Видеотрон)",   "Вычтех",             7_750, 1886.11, 1607.58, 40.41),
    ("Модуль КОСВТ",                 "Вычтех",             6_000, 240.40, 202.26, 15.21),
    ("Мат.платы",                    "Вычтех",            32_793, 1992.14, 1809.35, 126.68),
]

cols = [
    "name", "category", "quantity_base",
    "labor_sec", "price_base", "material_per_unit"
]

df_products = pd.DataFrame(products_data, columns=cols)

# Рентабельность по категориям (в процентах)
profitability_by_category = {
    "Внутренний заказ": 30.0,
    "Внешние заказы": 30.0,
    "Вычтех": 30.0
}

# Можно также завести общий множитель на количестве (для имитации ползунков количества)
df_products["quantity"] = df_products["quantity_base"].astype(float)

# ------------------------
# 2. Вспомогательные функции
# ------------------------

def calculate_total_labor(df: pd.DataFrame) -> float:
    """Общая трудоёмкость по текущим количествам."""
    return float((df["labor_sec"] * df["quantity"]).sum())


def allocate_costs_by_labor(df: pd.DataFrame, expenses: dict) -> pd.DataFrame:
    """
    Распределяет расходы по трудоёмкости между продуктами.
    Возвращает DF с добавленными колонками:
    material_total, fotpr_alloc, logistics_alloc, overhead_alloc, depreciation_alloc, procenty_alloc.
    """
    df = df.copy()
    total_labor = calculate_total_labor(df)
    # Доля трудоёмкости
    df["labor_share"] = (df["labor_sec"] * df["quantity"]) / total_labor

    # Материалы — по нормативу на штуку * qty
    df["material_total"] = df["material_per_unit"] * df["quantity"]

    # Прямые расходы
    logistics_sum = (
        expenses["logistika_hub"] +
        expenses["logistika_vnesh"] +
        expenses["logistika_barton"]
    )

    df["fotpr_alloc"] = expenses["fotpr"] * df["labor_share"]
    df["logistics_alloc"] = logistics_sum * df["labor_share"]

    # Накладные
    overhead_sum = (
        expenses["fotopR"] +
        expenses["ostalnye_opr"] +
        expenses["fotoxr"] +
        expenses["ostalnye_oxr"] +
        expenses["commersial"]
    )
    df["overhead_alloc"] = overhead_sum * df["labor_share"]

    # Амортизация (ПР + ОПР + ОХР)
    amort_sum = expenses["amort_pr"] + expenses["amort_opr"] + expenses["amort_oxr"]
    df["depr_alloc"] = amort_sum * df["labor_share"]

    # Проценты
    df["procenty_alloc"] = expenses["procenty"] * df["labor_share"]

    return df


def calc_price_with_profitability(price_base: float, profitability_pct: float) -> float:
    """
    В HTML используется логика:
    basePriceWithoutProfit = price_base / 1.3  (где 30% - изначальная маржа)
    newPrice = basePriceWithoutProfit * (1 + profitability/100)
    """
    base_price_wo_profit = price_base / 1.3
    return base_price_wo_profit * (1.0 + profitability_pct / 100.0)


def compute_metrics(df: pd.DataFrame, profitability_by_cat: dict) -> pd.DataFrame:
    """
    Рассчитать выручку, маржинальный доход и EBITDA по каждой позиции с учётом
    индивидуальной рентабельности для категорий.
    """
    df = df.copy()

    # Распределяем расходы
    df = allocate_costs_by_labor(df, yearly_expenses)

    # Рентабельность в разрезе категорий
    df["profitability_pct"] = df["category"].map(
        lambda c: profitability_by_cat.get(c, 30.0)
    )

    # Новая цена и выручка
    df["price_new"] = df.apply(
        lambda r: calc_price_with_profitability(r["price_base"], r["profitability_pct"]),
        axis=1
    )
    df["revenue"] = df["price_new"] * df["quantity"]

    # Прямые расходы = материалы + ФОТ ПР + логистика
    df["direct_costs"] = df["material_total"] + df["fotpr_alloc"] + df["logistics_alloc"]

    # Маржинальный доход
    df["margin_income"] = df["revenue"] - df["direct_costs"]

    # EBITDA = Выручка - материалы - ФОТ ПР - логистика - накладные
    df["ebitda"] = df["revenue"] - (
        df["material_total"] +
        df["fotpr_alloc"] +
        df["logistics_alloc"] +
        df["overhead_alloc"]
    )

    # Дополнительно: метрики на единицу
    df["margin_per_unit"] = df["margin_income"] / df["quantity"].replace(0, np.nan)
    df["ebitda_per_unit"] = df["ebitda"] / df["quantity"].replace(0, np.nan)

    return df


def aggregate_kpi(df_metrics: pd.DataFrame) -> dict:
    """Агрегированные показатели (как на панели KPI)."""
    total_margin = df_metrics["margin_income"].sum()
    total_ebitda = df_metrics["ebitda"].sum()
    # Выручка остаётся базовой 620 млн, как в HTML
    total_revenue = TOTAL_REVENUE

    # Средняя "виртуальная" рентабельность как маржа / выручка * 100
    profitability_pct = (total_margin / total_revenue * 100) if total_revenue != 0 else 0

    return {
        "total_revenue": total_revenue,
        "total_margin_income": total_margin,
        "total_ebitda": total_ebitda,
        "profitability_pct": profitability_pct
    }


def aggregate_by_category(df_metrics: pd.DataFrame) -> pd.DataFrame:
    """
    Сводка по категориям: выручка, маржа, EBITDA по Внутренний заказ / Внешние заказы / Вычтех.
    """
    grp = df_metrics.groupby("category").agg(
        revenue=("revenue", "sum"),
        margin_income=("margin_income", "sum"),
        ebitda=("ebitda", "sum")
    )
    grp["margin_pct_of_revenue"] = grp["margin_income"] / grp["revenue"].replace(0, np.nan) * 100
    grp["ebitda_pct_of_revenue"] = grp["ebitda"] / grp["revenue"].replace(0, np.nan) * 100
    return grp


# ------------------------
# 3. Пример использования
# ------------------------

if __name__ == "__main__":
    # Можно менять рентабельность по группам, как ползунками в HTML
    profitability_by_category = {
        "Внутренний заказ": 25.0,   # например, 25%
        "Внешние заказы":   35.0,   # 35%
        "Вычтех":           40.0    # 40%
    }

    # Можно также менять количество (имитация слайдеров количества)
    # Пример: увеличим выпуск "Сбербокс" в 1.5 раза
    df_products.loc[df_products["name"] == "Сбербокс", "quantity"] *= 1.5

    # Расчёт метрик по продуктам
    df_metrics = compute_metrics(df_products, profitability_by_category)

    # Общие KPI
    kpi = aggregate_kpi(df_metrics)
    print("KPI:")
    for k, v in kpi.items():
        print(f"  {k}: {v:,.2f}")

    # Сводка по категориям
    print("
Сводка по категориям:")
    print(aggregate_by_category(df_metrics))

    # Топ-10 продуктов по EBITDA
    print("
Топ-10 по EBITDA:")
    print(df_metrics[["name", "category", "quantity", "price_new", "revenue", "margin_income", "ebitda"]]
          .sort_values("ebitda", ascending=False)
          .head(10))
