import pandas as pd
import plotly.express as px
import streamlit as st
from io import BytesIO
import base64

st.set_page_config(page_title="📊 Online Retail Dashboard", layout="wide")

# === HEADER ===
st.markdown(
    """
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <h1 style="font-size: 2.5rem;">📦 Online Retail Dashboard</h1>
        <img src="https://upload.wikimedia.org/wikipedia/commons/1/1e/Streamlit_logo_horizontal.svg" height="60">
    </div>
    """, unsafe_allow_html=True
)

# === LOAD DATA ===
@st.cache_data
def load_data():
    df = pd.read_excel("online_retail.xlsx")
    df.dropna(subset=["Customer ID"], inplace=True)
    df = df[df["Quantity"] > 0]
    df = df[df["Price"] > 0]
    df["totalprice"] = df["Quantity"] * df["Price"]
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    return df

df = load_data()

# === KPI BLOCK ===
total_revenue = df['totalprice'].sum()
unique_customers = df['customer_id'].nunique()
total_orders = df['invoice'].nunique()

st.metric("💰 Общий доход", f"${total_revenue:,.0f}")
st.metric("🧑‍🤝‍🧑 Уникальные клиенты", unique_customers)
st.metric("🧾 Количество заказов", total_orders)

# === TABS ===
tab1, tab2, tab3 = st.tabs(["📦 Топ-продукты", "🌍 Доход по странам", "🧩 RFM-анализ"])

with tab1:
    st.subheader("📦 Топ-10 продуктов по выручке")
    top_products = df.groupby('description')['totalprice'].sum().sort_values(ascending=False).head(10).reset_index()
    fig1 = px.bar(top_products, x='totalprice', y='description', orientation='h', title='ТОП-10 товаров')
    st.plotly_chart(fig1, use_container_width=True)

    # Кнопка для скачивания CSV
    csv_data = top_products.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Скачать CSV", data=csv_data, file_name="top_products.csv", mime='text/csv')

with tab2:
    st.subheader("🌍 Доход по странам")
    top_countries = df.groupby('country')['totalprice'].sum().sort_values(ascending=False).head(10).reset_index()
    fig2 = px.bar(top_countries, x='country', y='totalprice', title='Доход по странам')
    st.plotly_chart(fig2, use_container_width=True)

    # Кнопка для скачивания CSV
    csv_countries = top_countries.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Скачать CSV по странам", data=csv_countries, file_name="revenue_by_country.csv", mime='text/csv')

with tab3:
    st.subheader("🧩 RFM-анализ")
    latest_date = df['invoicedate'].max() + pd.Timedelta(days=1)
    rfm = df.groupby('customer_id').agg({
        'invoicedate': lambda x: (latest_date - x.max()).days,
        'invoice': 'nunique',
        'totalprice': 'sum'
    }).reset_index()
    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    rfm['RFM_Score'] = rfm[['recency', 'frequency', 'monetary']].rank(method='first').sum(axis=1)
    fig3 = px.histogram(rfm, x='RFM_Score', nbins=30, title='Распределение RFM-оценок')
    st.plotly_chart(fig3, use_container_width=True)

    # Кнопка для скачивания RFM-таблицы
    rfm_csv = rfm.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Скачать RFM CSV", data=rfm_csv, file_name="rfm_analysis.csv", mime='text/csv')

# === FOOTER ===
st.markdown("---")
st.markdown("💼 Проект создал **Науатбек Санжар** — Data Analyst")
st.markdown("🔗 [GitHub проекта](https://github.com/SanzharNauatbek7")

