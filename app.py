import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Финансовый дашборд", layout="wide")
st.title("💰 Финансовый дашборд ПЭО")

st.sidebar.header("Загрузка данных")
uploaded_file = st.sidebar.file_uploader(
    "Загрузите Excel с планом/фактом", type=["xlsx"]
)

if uploaded_file is None:
    st.info("Загрузите файл Excel, чтобы увидеть отчёт.")
else:
    df = pd.read_excel(uploaded_file)

    filial_col = "Филиал"
    month_col = "Месяц"
    plan_col = "План"
    fact_col = "Факт"

    st.sidebar.subheader("Фильтры")
    filial_list = ["Все"] + sorted(df[filial_col].dropna().unique().tolist())
    selected_filial = st.sidebar.selectbox("Филиал", filial_list)

    if selected_filial != "Все":
        df = df[df[filial_col] == selected_filial]

    st.subheader("Данные")
    st.dataframe(df)

    total_plan = df[plan_col].sum()
    total_fact = df[fact_col].sum()
    delta = total_fact - total_plan
    delta_pct = (delta / total_plan * 100) if total_plan != 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("План", f"{total_plan:,.0f}")
    col2.metric("Факт", f"{total_fact:,.0f}")
    col3.metric("Отклонение, %", f"{delta_pct:.1f}%")

    st.subheader("План‑факт по месяцам")
    fig = px.line(
        df,
        x=month_col,
        y=[plan_col, fact_col],
        markers=True,
        title="План‑факт динамика",
    )
    st.plotly_chart(fig, use_container_width=True)
