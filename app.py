import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Себестоимость", layout="wide")
st.title("📊 Интерактивный Отчет Себестоимости")
st.markdown("Анализ рентабельности и финансовых показателей по видам продукции")

# =========================
# ИСХОДНЫЕ ДАННЫЕ (31 модель)
# =========================
TOTAL_REVENUE = 620682373.59

yearly_expenses = {
    "material": 38374083.32, "fotpr": 97689625.69, "prochie_pr": 22559651.69,
    "amort_pr": 50628156.84, "fotopR": 143704063.88, "amort_opr": 8527933.20,
    "ostalnye_opr": 28015544.97, "fotoxr": 58189393.57, "amort_oxr": 12291689.47,
    "ostalnye_oxr": 67382397.10, "commersial": 195860.72,
    "logistika_hub": 959983.83, "logistika_vneshnaya": 19590419.54, "logistika_barton": 704202.91,
    "procenty": 106105864.26
}

products_data = [
    # Внутренний заказ
    ["Приемник Триколор Стандарт 2", "Внутренний заказ", 100420, 619.50, 416.37, 24.99],
    ["MB R1N02", "Внутренний заказ", 56500, 409.55, 412.55, 18.98],
    ["Гл.платы", "Внутренний заказ", 1500, 460.50, 369.32, 21.30],
    
    # Внешние заказы (19)
    ["Булат Коммутатор", "Внешние заказы", 600, 15664.14, 16219.99, 507.53],
    ["Qtech (Серв./Коммутатор)", "Внешние заказы", 250, 17007.50, 13191.70, 362.24],
    ["Аквариус (Мат.платы 610T)", "Внешние заказы", 20000, 1749.40, 1451.57, 102.69],
    ["Плата системная (DPH)", "Внешние заказы", 23974.5, 2088.80, 1752.84, 90.12],
    ["IP-камера", "Внешние заказы", 10000, 337.07, 335.56, 4.85],
    ["Модуль оперативной памяти", "Внешние заказы", 5000, 160.70, 304.51, 4.68],
    ["Амур серверная плата", "Внешние заказы", 1000, 13915.00, 11153.99, 572.90],
    ["Депо Серверная плата", "Внешние заказы", 2500, 11277.05, 9526.39, 466.61],
    ["Смартфон Смарт Экосистема", "Внешние заказы", 18000, 3325.64, 2702.01, 88.52],
    ["РДВ Серверная плата", "Внешние заказы", 1000, 13224.56, 10611.45, 355.56],
    ["Процессорный модуль Ядро", "Внешние заказы", 57204, 1928.48, 2112.55, 169.38],
    ["Амур плата системная", "Внешние заказы", 7737, 2858.43, 2404.13, 184.27],
    ["ICL Материнские платы", "Внешние заказы", 4000, 1819.80, 1654.58, 101.30],
    ["ЭмСтор (модули SSD)", "Внешние заказы", 25633, 258.82, 421.17, 13.60],
    ["HTP Радиолинейный модуль", "Внешние заказы", 20000, 1064.47, 1188.05, 141.59],
    ["РДВ Мат.платы", "Внешние заказы", 10500, 2085.00, 1752.84, 88.92],
    ["Qtech Электронные модули", "Внешние заказы", 5377, 3222.41, 2851.41, 286.81],
    ["Delta Computers плата монитора", "Внешние заказы", 10000, 333.31, 484.80, 33.84],
    ["Сбербокс", "Внешние заказы", 52000, 630.55, 291.66, 15.51],
    
    # Вычтех
    ["Блоки питания", "Вычтех", 10100, 2861.04, 2332.23, 179.40],
    ["Плата для ПК", "Вычтех", 1000, 418.50, 534.34, 15.04],
    ["Ноутбук", "Вычтех", 3500, 4340.73, 3682.27, 79.88],
    ["ПК", "Вычтех", 0, 1837.00, 1362.89, 141.59],
    ["Серверная платформа Gen4", "Вычтех", 2100, 15715.58, 13080.77, 668.78],
    ["Серверная платформа ODM", "Вычтех", 0, 24944.20, 16666.67, 1168.94],
    ["Сатро-Палладин (Видеотрон)", "Вычтех", 7750, 1886.11, 1607.58, 40.41],
    ["Модуль КОСВТ", "Вычтех", 6000, 240.40, 202.26, 15.21],
    ["Мат.платы", "Вычтех", 32793, 1992.14, 1809.35, 126.68]
]

df_products = pd.DataFrame(products_data, columns=["name", "category", "quantity_base", "labor_sec", "price_base", "material_per_unit"])
df_products["quantity"] = df_products["quantity_base"].astype(float)

# =========================
# ФУНКЦИИ РАСЧЕТА
# =========================
def calculate_total_labor(df):
    return float((df["labor_sec"] * df["quantity"]).sum())

def allocate_costs(df, expenses):
    df = df.copy()
    total_labor = calculate_total_labor(df)
    df["labor_share"] = (df["labor_sec"] * df["quantity"]) / total_labor
    
    # Материалы
    df["material_total"] = df["material_per_unit"] * df["quantity"]
    
    # Прямые расходы
    logistics = expenses["logistika_hub"] + expenses["logistika_vneshnaya"] + expenses["logistika_barton"]
    df["fotpr_total"] = expenses["fotpr"] * df["labor_share"]
    df["logistics_total"] = logistics * df["labor_share"]
    df["direct_costs"] = df["material_total"] + df["fotpr_total"] + df["logistics_total"]
    
    # Накладные
    overhead = (expenses["fotopR"] + expenses["ostalnye_opr"] + expenses["fotoxr"] + 
                expenses["ostalnye_oxr"] + expenses["commersial"])
    df["overhead_total"] = overhead * df["labor_share"]
    
    return df

def compute_all_metrics(df_products, profitability_by_category):
    df = allocate_costs(df_products, yearly_expenses)
    df["profitability"] = df["category"].map(profitability_by_category)
    
    # Новая цена (как в HTML)
    df["price_new"] = (df["price_base"] / 1.3) * (1 + df["profitability"] / 100)
    df["revenue"] = df["price_new"] * df["quantity"]
    
    # Маржинальный доход и EBITDA
    df["margin_income"] = df["revenue"] - df["direct_costs"]
    df["ebitda"] = df["revenue"] - (df["direct_costs"] + df["overhead_total"])
    
    df["margin_unit"] = df["margin_income"] / df["quantity"].replace(0, np.nan)
    df["ebitda_unit"] = df["ebitda"] / df["quantity"].replace(0, np.nan)
    
    return df

# =========================
# ИНТЕРФЕЙС
# =========================

# Ползунки рентабельности
col1, col2, col3 = st.columns(3)
r_internal = col1.slider("Внутренний заказ %", 5.0, 60.0, 30.0, 0.5)
r_external = col2.slider("Внешние заказы %", 5.0, 60.0, 30.0, 0.5)
r_tech = col3.slider("Вычтех %", 5.0, 60.0, 30.0, 0.5)

profitability = {
    "Внутренний заказ": r_internal,
    "Внешние заказы": r_external,
    "Вычтех": r_tech
}

if st.button("🔄 Сброс"):
    st.rerun()

# Расчет
df_metrics = compute_all_metrics(df_products, profitability)

# KPI Dashboard
kpi_rev = df_metrics["revenue"].sum()
kpi_margin = df_metrics["margin_income"].sum()
kpi_ebitda = df_metrics["ebitda"].sum()
kpi_profit = (kpi_margin / TOTAL_REVENUE * 100)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Выручка", str(int(kpi_rev)))
col2.metric("EBITDA", str(int(kpi_ebitda)))
col3.metric("Маржинальный доход", str(int(kpi_margin)))
col4.metric("Рентабельность", str(round(kpi_profit, 1)) + "%")

# Выбор категории
category = st.selectbox("Категория:", ["Все"] + sorted(df_products["category"].unique()))
if category != "Все":
    df_show = df_metrics[df_metrics["category"] == category]
else:
    df_show = df_metrics

# Таблица продуктов
st.subheader("📦 Анализ по продуктам")
show_cols = ["name", "quantity", "price_new", "revenue", "margin_unit", "ebitda_unit"]
df_show[show_cols] = df_show[show_cols].round(0)
st.dataframe(df_show[show_cols], use_container_width=True)

# Сводка по категориям
st.subheader("📊 Сводка по категориям")
cat_summary = df_metrics.groupby("category").agg({
    "revenue": "sum", "margin_income": "sum", "ebitda": "sum"
}).round(0)
st.dataframe(cat_summary)

# Графики
col1, col2 = st.columns(2)
with col1:
    st.subheader("Доля выручки")
    cat_rev = cat_summary["revenue"].reset_index()
    st.bar_chart(cat_rev.set_index("category"))

with col2:
    st.subheader("Маржа vs EBITDA")
    st.bar_chart(cat_summary[["margin_income", "ebitda"]])

# Экспорт
st.subheader("💾 Экспорт")
csv_data = df_metrics.to_csv(index=False).encode('utf-8')
st.download_button("Скачать полный отчет", csv_data, "sebestoimost.csv", "text/csv")

st.markdown("---")
st.caption("Интерактивный отчет себестоимости © 2025")