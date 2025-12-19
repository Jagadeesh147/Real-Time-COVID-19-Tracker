import streamlit as st
import pandas as pd
import plotly.express as px
import pycountry
import requests


# --------------------------------------------------------------
# SAFE ISO3 CONVERSION
# --------------------------------------------------------------
def safe_iso(name: str):
    try:
        return pycountry.countries.lookup(name).alpha_3
    except Exception:
        return None


# --------------------------------------------------------------
# LOAD LIVE DATA (cached for 5 minutes)
# --------------------------------------------------------------
@st.cache_data(ttl=300)
def load_live_data():
    url = "https://disease.sh/v3/covid-19/countries"
    raw = requests.get(url).json()

    rows = []
    for c in raw:
        country = c.get("country")
        if not country:
            continue

        deaths = c.get("deaths", 0)
        cases = c.get("cases", 0)
        recovered = c.get("recovered", 0)
        active = c.get("active", 0)

        iso = safe_iso(country)
        if iso is None:
            continue

        death_rate = (deaths / cases * 100) if cases > 0 else 0.0

        rows.append(
            {
                "Country": country,
                "ISO3": iso,
                "Cases": cases,
                "Deaths": deaths,
                "Recovered": recovered,
                "Active": active,
                "DeathRate": round(death_rate, 2),
            }
        )

    df = pd.DataFrame(rows)
    return df


# --------------------------------------------------------------
# MAIN RENDER FUNCTION
# --------------------------------------------------------------
def render_world_map():
    df = load_live_data()

    # --- Search Box ---
    st.markdown(
        """
        <div class="main-card">
            <h3 style="margin-top:0;">🌍 Global Map & Country Highlighter</h3>
            <p style="margin-bottom:8px; color:#555;">
                👉 Leave search empty to view global death rate intensity.<br>
                👉 Type a country name (e.g., <b>India</b>) to highlight it in red and see KPIs.
            </p>
        """,
        unsafe_allow_html=True,
    )

    search = st.text_input("Search Country", value="", placeholder="India, United States, Brazil ...")
    st.markdown("</div><br/>", unsafe_allow_html=True)

    # --- CASE 1: No search → Choropleth by death rate ---
    if not search.strip():
        fig = px.choropleth(
            df,
            locations="ISO3",
            color="DeathRate",
            hover_name="Country",
            color_continuous_scale="Reds",
            labels={"DeathRate": "Death Rate (%)"},
            title="Global COVID-19 Death Rate (%) – Higher = Darker Red",
        )
        fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))

        st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            """
            <div class="main-card">
                <b>Note:</b> Death rate = (Total deaths ÷ Total cases) × 100.
                Type any country above to focus on that region.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # --- CASE 2: Search → highlight one country in red ---
    search_lower = search.strip().lower()
    mask = df["Country"].str.lower().str.contains(search_lower)

    if not mask.any():
        st.warning(f"No country found for search: '{search}'. Please check spelling.")
        fig = px.choropleth(
            df,
            locations="ISO3",
            color="DeathRate",
            hover_name="Country",
            color_continuous_scale="Reds",
            labels={"DeathRate": "Death Rate (%)"},
            title="Global COVID-19 Death Rate (%)",
        )
        fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig, use_container_width=True)
        return

    selected_row = df[mask].iloc[0]
    selected_country = selected_row["Country"]

    df["Selection"] = df["Country"].apply(
        lambda c: "Selected" if c == selected_country else "Other"
    )

    fig = px.choropleth(
        df,
        locations="ISO3",
        color="Selection",
        hover_name="Country",
        title=f"{selected_country} highlighted in RED",
        color_discrete_map={"Selected": "red", "Other": "lightgrey"},
    )
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), showlegend=False)

    st.plotly_chart(fig, use_container_width=True)

    # --- KPI METRICS ---
    st.markdown(
        f"""
        <div class="main-card">
            <h3 style="margin-top:0;">📊 Key Metrics – {selected_country}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Cases", f"{selected_row['Cases']:,}")
    c2.metric("Total Deaths", f"{selected_row['Deaths']:,}")
    c3.metric("Recovered", f"{selected_row['Recovered']:,}")
    c4.metric("Active", f"{selected_row['Active']:,}")
    c5.metric("Death Rate (%)", f"{selected_row['DeathRate']:.2f}")
