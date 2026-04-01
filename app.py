import streamlit as st 
import pandas as pd    
import    requests   
from worldmap_component import render_world_map  

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Real-Time COVID-19 Tracker", 
    layout="wide",   
    page_icon="🌍"
)

# --------------------------------------------------
# HEADER BANNER
# --------------------------------------------------
def header_bg(image_path):
    st.markdown(
        f"""
        <style>
        .header {{
            background-image: url("{image_path}");
            background-size: cover;
            background-position: center;
            padding: 80px;
            border-radius: 20px;
            text-align: center;
            color: white;
        }}
        </style>
        <div class="header">
            <h1>Real Time Covid-19 Tracker</h1>
            <p>Built using Pandas • Streamlit • Live API</p>
        </div>
        """,
        unsafe_allow_html=True
    )

header_bg("assets/banner.jpg")

# --------------------------------------------------
# FETCH LIVE DATA
# --------------------------------------------------
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

# --------------------------------------------------
# TABS
# --------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌍 Global Summary",
    "🏆 Top Countries",
    "📋 Full Data Table",
    "🔮 Predictions",
    "🗺 World Map (Live)"
])

# --------------------------------------------------
# TAB 1 – GLOBAL SUMMARY
# --------------------------------------------------
with tab1:
    st.subheader("Global COVID-19 Statistics")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Countries", df.shape[0])
    col2.metric("Total Cases", f"{df['Cases'].sum():,}")
    col3.metric("Total Deaths", f"{df['Deaths'].sum():,}")
    col4.metric("Total Recovered", f"{df['Recovered'].sum():,}")

# --------------------------------------------------
# TAB 2 – TOP COUNTRIES
# --------------------------------------------------
with tab2:
    st.subheader("Top 10 Countries by Active Cases")
    top10 = df.sort_values("Active", ascending=False).head(10)
    st.bar_chart(top10.set_index("Country")["Active"])

# --------------------------------------------------
# TAB 3 – FULL TABLE
# --------------------------------------------------
with tab3:
    st.subheader("Country-wise COVID Data")
    st.dataframe(df, use_container_width=True)

# --------------------------------------------------
# TAB 4 – PREDICTIONS
# --------------------------------------------------
with tab4:
    st.info("Prediction module will be added in future versions.")

# --------------------------------------------------
# TAB 5 – WORLD MAP
# --------------------------------------------------
with tab5:
    st.subheader("Live COVID-19 World Map")
    render_world_map()
