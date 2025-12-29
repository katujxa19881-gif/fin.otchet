import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ------------------------
# Данные (как в последнем HTML варианте)
# ------------------------

TOTAL_REVENUE = 620_682_373.59

yearly_expenses = {
    "material": 38_374_083.32,
    "fotpr": 97_689_625.69,
    "prochie_pr": 22_559_651.69,
    "amort_pr": 50_628_156.84,
    "fotopR": 143_704_063.88,
    "amort_opr": 8_527_933.20,
    "ostalnye_opr": 28_015_544.97,
    "fotoxr": 58_189_393.57,
    "amort_oxr": 12_291_689.47,
    "ostalnye_oxr": 67_382_397.10,
    "commersial": 195_860.72,
    "logistika_hub": 959_983.83,
    "logistika_vneshnaya": 19_590_419.54,
    "logistika_barton": 704_202.91,
    "procenty": 106_105_864.26,
}

products_data = [
    # Внутренний заказ
    ("Приемник Триколор Стандарт 2", "Внутренний заказ", 100420, 619.50, 416.37, 24.99),
    ("MB R1N02", "Внутренний заказ", 56500, 409.55, 412.55, 18.98),
    ("Гл.платы", "Внутренний заказ", 1500, 460.50, 369.32, 21.30),
    
    # Внешние заказы
    ("Булат Коммутатор", "Внешние заказы", 600, 15664.14, 16219.99, 507.53),
    ("Qtech (Серв./Коммутатор)", "Внешние заказы", 250, 17007.50, 13191.70, 362.24),
    ("Аквариус (Мат.платы 610T)", "Внешние заказы", 20000, 1749.40, 1451.57, 102.69),
    ("Плата системная (DPH)", "Внешние заказы", 23974.50, 2088.80, 1752.84, 90.12),
    ("IP-камера", "Внешние заказы", 10000, 337.07, 335.56, 4.85),
    ("Модуль оперативной памяти", "Внешние заказы", 5000, 160.70, 304.51, 4.68),
    ("Амур серверная плата", "Внешние заказы", 1000, 13915.00, 11153.99, 572.90),
    ("Депо Серверная плата", "Внешние заказы", 2500, 11277.05, 9526.39, 466.61),
    ("Смартфон Смарт Экосистема", "Внешние заказы", 18000, 3325.64, 2702.01, 88.52),
    ("РДВ Серверная плата", "Внешние заказы", 1000, 13224.56, 10611.45, 355.56),
    ("Процессорный модуль Ядро", "Внешние заказы", 57204, 1928.48, 2112.55, 169.38),
    ("Амур плата системная", "Внешние заказы", 7737, 2858.43, 2404.13, 184.27),
    ("ICL Материнские платы", "Внешние заказы", 4000, 1819.80, 1654.58, 101.30),
    ("ЭмСтор (модули SSD)", "Внешние заказы", 25633, 258.82, 421.17, 13.60),
    ("HTP Радиолинейный модуль", "Внешние заказы", 20000, 1064.47, 1188.05, 141.59),
    ("РДВ Мат.платы", "Внешние заказы", 10500, 2085.00, 1752.84, 88.92),
    ("Qtech Электронные модули", "Внешние заказы", 5377, 3222.41, 2851.41, 286.81),
    ("Delta Computers плата монитора", "Внешние заказы", 10000, 333.31, 484.80, 33.84),
    ("Сбербокс", "Внешние заказы", 52000, 630.55, 291.66, 15.51),
    
    # Вычтех
    ("Блоки питания", "Вычтех", 10100, 2861.04, 2332.23, 179.40),
    ("Плата для ПК", "Вычтех", 1000, 418.50, 534.34, 15.04),
    ("Ноутбук", "Вычтех", 3500, 4340.73, 3682.27, 79.88),
    ("ПК", "Вычтех", 0, 1837.00, 1362.89, 141.59),
    ("Серверная платформа Gen4", "Вычтех", 2100, 15715.58, 13080.77, 668.78),
    ("Серверная платформа ODM", "Вычтех", 0, 24944.20, 16666.67, 1168.94),
    ("Сатро-Палладин (Видеотрон)", "Вычтех", 7750, 1886.11, 1607.58, 40.41),
    ("Модуль КОСВТ", "Вычтех", 6000, 240.40, 202.26, 15.21),
    ("Мат.платы", "Вычтех", 32793, 1992.14, 1809.35, 126.68),
]

cols = ["name", "category", "quantity_base", "labor_sec", "price_base", "material_per_unit"]
df_products = pd.DataFrame(products_data, columns=cols)
df_products["quantity"] = df_products["quantity_base"].astype(float)

# ------------------------
# Функции расчета (как в HTML)
# ------------------------

def calculate_total_labor(df):
    return float((df["labor_sec"] * df["quantity"]).sum())

def allocate_costs_by_labor(df, expenses):
    df = df.copy()
    total_labor = calculate_total_labor(df)
    df["labor_share"] = (df["labor_sec"] * df["quantity"]) / total_labor

    df["material_total"] = df["material_per_unit"] * df["quantity"]

    logistics_sum = (expenses["logistika_hub"] + expenses["logistika_vneshnaya"] + expenses["logistika_barton"])
    df["fotpr_alloc"] = expenses["fotpr"] * df["labor_share"]
    df["logistics_alloc"] = logistics_sum * df["labor_share"]

    overhead_sum = (expenses["fotopR"] + expenses["ostalnye_opr"] + expenses["fotoxr"] + 
                    expenses["ostalnye_oxr"] + expenses["commersial"])
    df["overhead_alloc"] = overhead_sum * df["labor_share"]

    amort_sum = expenses["amort_pr"] + expenses["amort_opr"] + expenses["amort_oxr"]
    df["depr_alloc"] = amort_sum * df["labor_share"]

    df["procenty_alloc"] = expenses["procenty"] * df["labor_share"]
    return df

def calc_price_with_profitability(price_base, profitability_pct):
    base_price_wo_profit = price_base / 1.3
    return base_price_wo_profit * (1.0 + profitability_pct / 100.0)

def compute_metrics(df, profitability_by_cat):
    df = allocate_costs_by_labor(df, yearly_expenses)
    df["profitability_pct"] = df["category"].map(profitability_by_cat)
    
    df["price_new"] = df.apply(lambda r: calc_price_with_profitability(r["price_base"], r["profitability_pct"]), axis=1)
    df["revenue"] = df["price_new"] * df["quantity"]
    
    df["direct_costs"] = df["material_total"] + df["fotpr_alloc"] + df["logistics_alloc"]
    df["margin_income"] = df["revenue"] - df["direct_costs"]
    df["ebitda"] = df["revenue"] - (df["material_total"] + df["fotpr_alloc"] + df["logistics_alloc"] + df["overhead_alloc"])
    
    df["margin_per_unit"] = df["margin_income"] / df["quantity"].replace(0, np.nan)
    df["ebitda_per_unit"] = df["ebitda"] / df["quantity"].replace(0, np.nan)
    return df

def aggregate_kpi(df_metrics):
    total_margin = df_metrics["margin_income"].sum()
    total_ebitda = df_metrics["ebitda"].sum()
    total_revenue = TOTAL_REVENUE
    profitability_pct = (total_margin / total_revenue * 100) if total_revenue != 0 else 0
    return {
        "total_revenue": total_revenue,
        "total_margin_income": total_margin,
        "total_ebitda": total_ebitda,
        "profitability_pct": profitability_pct
    }

# ------------------------
# Streamlit интерфейс
# ------------------------

st.set_page_config(page_title="Интерактивный Отчет Себестоимости", layout="wide")
st.title("📊 Интерактивный Отчет Себестоимости")
st.markdown("Анализ рентабельности и финансовых показателей по видам продукции")

# Сайдбар для управления
st.sidebar.header("⚙ Управление параметрами")

# Ползунки рентабельности по группам
profitability_internal = st.sidebar.slider("Внутренний заказ (%)", 5.0, 60.0, 30.0, 0.5)
profitability_external = st.sidebar.slider("Внешние заказы (%)", 5.0, 60.0, 30.0, 0.5)
profitability_tech = st.sidebar.slider("Вычтех (%)", 5.0, 60.0, 30.0, 0.5)

profitability_by_category = {
    "Внутренний заказ": profitability_internal,
    "Внешние заказы": profitability_external,
    "Вычтех": profitability_tech
}

# Кнопка сброса
if st.sidebar.button("🔄 Сброс значений"):
    st.rerun()

# Расчет метрик
df_metrics = compute_metrics(df_products, profitability_by_category)
kpi = aggregate_kpi(df_metrics)

# ------------------------
# KPI Dashboard
# ------------------------
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Выручка", f"{kpi['total_revenue']:,.0f} ₽", delta=None)
with col2:
    st.metric("EBITDA", f"{kpi['total_ebitda']:,.0f} ₽", delta=None)
with col3:
    st.metric("Маржинальный доход", f"{kpi['total_margin_income']:,.0f} ₽", delta=None)
with col4:
    st.metric("Рентабельность", f"{kpi['profitability_pct']:.1f}%", delta=None)

# ------------------------
# Выбор категории
# ------------------------
category = st.selectbox("Фильтр по категории:", ["all"] + df_products["category"].unique().tolist())

if category != "all":
    df_filtered = df_metrics[df_metrics["category"] == category]
else:
    df_filtered = df_metrics

# ------------------------
# Таблица продуктов
# ------------------------
st.subheader("📦 Анализ по продуктам")
st.dataframe(
    df_filtered[["name", "quantity", "price_new", "revenue", "margin_per_unit", "ebitda_per_unit"]]
    .round(2)
    .style.format({
        "quantity": "{:,.0f}",
        "price_new": "{:,.0f}",
        "revenue": "{:,.0f}",
        "margin_per_unit": "{:,.0f}",
        "ebitda_per_unit": "{:,.0f}"
    }),
    use_container_width=True
)

# ------------------------
# Сводка по категориям
# ------------------------
st.subheader("📈 Сводка по категориям")
cat_summary = df_metrics.groupby("category").agg({
    "revenue": "sum",
    "margin_income": "sum", 
    "ebitda": "sum"
}).round(0)
cat_summary["margin_pct"] = (cat_summary["margin_income"] / cat_summary["revenue"] * 100).round(1)
cat_summary["ebitda_pct"] = (cat_summary["ebitda"] / cat_summary["revenue"] * 100).round(1)

st.dataframe(cat_summary.style.format({
    "revenue": "{:,.0f}",
    "margin_income": "{:,.0f}",
    "ebitda": "{:,.0f}"
}))

# ------------------------
# Графики
# ------------------------
col1, col2 = st.columns(2)

with col1:
    fig_pie = px.pie(
        cat_summary.reset_index(),
        values="revenue", 
        names="category",
        title="Доля выручки по категориям"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    fig_bar = px.bar(
        cat_summary.reset_index(),
        x="category",
        y=["revenue", "margin_income", "ebitda"],
        title="Выручка, Маржа, EBITDA по категориям",
        barmode="group"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ------------------------
# Экспорт
# ------------------------
st.subheader("💾 Экспорт данных")
col1, col2, col3 = st.columns(3)
with col1:
    csv = df_metrics.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Скачать таблицу продуктов",
        csv,
        "sebestoimost_products.csv",
        "text/csv"
    )
with col2:
    csv_kpi = pd.DataFrame([kpi]).to_csv(index=False).encode('utf-8')
    st.download_button(
        "Скачать KPI",
        csv_kpi,
        "sebestoimost_kpi.csv",
        "text/csv"
    )
with col3:
    csv_cat = cat_summary.to_csv().encode('utf-8')
    st.download_button(
        "Скачать сводку по категориям",
        csv_cat,
        "sebestoimost_categories.csv",
        "text/csv"
    )

st.markdown("---")
st.caption("Интерактивный отчет себестоимости © 2025 | Данные актуальны на момент расчета")