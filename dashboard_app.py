# ===============================================================
# IMPORTS
# ===============================================================
import streamlit as st
import pandas as pd
import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from worldmap_component import render_world_map

# ===============================================================
# PAGE CONFIG
# ===============================================================
st.set_page_config(
    page_title="Real-Time COVID-19 Dashboard",
    layout="wide",
    page_icon="🌍"
)

# ===============================================================
# SPARK SESSION
# ===============================================================
spark = SparkSession.builder.appName("CovidDashboard").getOrCreate()

# ===============================================================
# HEADER / BANNER
# ===============================================================
def header_bg(image_path):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{image_path}");
            background-size: cover;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

header_bg("asset/banner.jpg")

st.title("🌍 Real-Time COVID-19 Dashboard")
st.markdown("Built using **PySpark + Streamlit + Live API**")

# ===============================================================
# FETCH LIVE DATA
# ===============================================================
@st.cache_data(ttl=300)
def get_live_data():
    url = "https://disease.sh/v3/covid-19/countries"
    data = requests.get(url).json()

    rows = []
    for c in data:
        rows.append({
            "Country": c["country"],
            "Cases": c["cases"],
            "Deaths": c["deaths"],
            "Recovered": c["recovered"],
            "Active": c["active"]
        })

    return pd.DataFrame(rows)

df = get_live_data()
spark_df = spark.createDataFrame(df)

# ===============================================================
# TABS
# ===============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Global Summary",
    "📈 Charts",
    "📋 Full Data Table",
    "🤖 Predictions",
    "🌍 World Map"
])

# ===============================================================
# TAB 1 – GLOBAL SUMMARY
# ===============================================================
with tab1:
    st.subheader("🌐 Global COVID Summary")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🌍 Countries", len(df))
    col2.metric("🦠 Total Cases", f"{df['Cases'].sum():,}")
    col3.metric("☠️ Deaths", f"{df['Deaths'].sum():,}")
    col4.metric("💚 Recovered", f"{df['Recovered'].sum():,}")

# ===============================================================
# TAB 2 – CHART VISUALIZATION
# ===============================================================
with tab2:
    st.subheader("📈 Top 10 Countries by Active Cases")

    top10 = (
        spark_df
        .orderBy(col("Active").desc())
        .limit(10)
        .toPandas()
    )

    st.bar_chart(
        top10.set_index("Country")["Active"],
        height=400
    )

# ===============================================================
# TAB 3 – FULL DATA TABLE
# ===============================================================
with tab3:
    st.subheader("📋 COVID-19 Data for All Countries")
    st.dataframe(df, width="stretch")

# ===============================================================
# TAB 4 – PREDICTIONS
# ===============================================================
with tab4:
    st.info("🤖 Prediction module coming soon...")

# ===============================================================
# TAB 5 – WORLD MAP
# ===============================================================
with tab5:
    st.subheader("🌍 Live COVID-19 World Map")
    render_world_map()
