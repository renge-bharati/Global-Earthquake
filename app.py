# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

# --- Page setup ---
st.set_page_config(
    page_title="🌍 Global Earthquake & Tsunami Dashboard",
    page_icon="🌊",
    layout="wide",
)

# --- Custom CSS for better look ---
st.markdown("""
    <style>
        .main {
            background-color: #F8FAFC;
        }
        h1, h2, h3 {
            color: #1E3A8A;
        }
        .stMetric {
            background-color: #EFF6FF;
            border-radius: 10px;
            padding: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.title("🌍 Global Earthquake & Tsunami Risk Dashboard")
st.markdown("""
Analyze global earthquake data and visualize tsunami risks in an interactive way.  
**Dataset Source:** [Kaggle - Global Earthquake-Tsunami Risk Assessment](https://www.kaggle.com/datasets/ahmeduzaki/global-earthquake-tsunami-risk-assessment-dataset)
""")

# --- Load data ---
@st.cache_data
def load_data():
    df = pd.read_csv("data/global_earthquake_tsunami_risk.csv")
    return df

df = load_data()

# --- Sidebar filters ---
st.sidebar.header("🔎 Filter Options")
min_mag = st.sidebar.slider("Minimum Magnitude", float(df["Magnitude"].min()), float(df["Magnitude"].max()), 5.0)
max_depth = st.sidebar.slider("Maximum Depth (km)", float(df["Depth"].min()), float(df["Depth"].max()), float(df["Depth"].max()))
countries = st.sidebar.multiselect("Select Country", options=sorted(df["Country"].dropna().unique()), default=[])

filtered = df[(df["Magnitude"] >= min_mag) & (df["Depth"] <= max_depth)]
if countries:
    filtered = filtered[filtered["Country"].isin(countries)]

# --- Top metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Earthquakes", len(filtered))
col2.metric("Average Magnitude", round(filtered["Magnitude"].mean(), 2))
col3.metric("Tsunami Events", filtered["Tsunami"].sum() if "Tsunami" in filtered.columns else "N/A")

# --- Dataset preview ---
with st.expander("📋 Show Dataset Preview"):
    st.dataframe(filtered.head(20))

# --- Chart 1: Magnitude distribution ---
st.subheader("📊 Earthquake Magnitude Distribution")
fig_mag = px.histogram(
    filtered, 
    x="Magnitude", 
    nbins=30, 
    color_discrete_sequence=["#2563EB"], 
    title="Magnitude Distribution"
)
fig_mag.update_layout(bargap=0.05, plot_bgcolor="white")
st.plotly_chart(fig_mag, use_container_width=True)

# --- Chart 2: Depth vs Magnitude Scatter ---
st.subheader("🌊 Depth vs Magnitude (Tsunami Highlighted)")
if "Tsunami" in filtered.columns:
    fig_scatter = px.scatter(
        filtered,
        x="Depth",
        y="Magnitude",
        color="Tsunami",
        color_continuous_scale=["#60A5FA", "#EF4444"],
        title="Depth vs Magnitude (Colored by Tsunami)"
    )
else:
    fig_scatter = px.scatter(filtered, x="Depth", y="Magnitude", color="Magnitude")
st.plotly_chart(fig_scatter, use_container_width=True)

# --- Chart 3: Map visualization ---
st.subheader("🗺️ Global Earthquake Map")
if {"Latitude", "Longitude"}.issubset(filtered.columns):
    fig_map = px.scatter_geo(
        filtered,
        lat="Latitude",
        lon="Longitude",
        color="Magnitude",
        hover_name="Country",
        size="Magnitude",
        projection="natural earth",
        title="Global Earthquake Locations",
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("Latitude/Longitude columns missing in the dataset.")

# --- Chart 4: Country-wise analysis ---
if "Country" in filtered.columns:
    st.subheader("🏳️ Top 10 Countries by Average Magnitude")
    country_stats = (
        filtered.groupby("Country")["Magnitude"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig_bar = px.bar(
        country_stats,
        x="Country",
        y="Magnitude",
        color="Magnitude",
        color_continuous_scale="Blues",
        title="Top 10 Countries by Average Magnitude",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# --- Footer ---
st.markdown("---")
st.markdown("💡 **Tip:** Use the filters on the left sidebar to explore different magnitude and country combinations!")
st.caption("Created by [Your Name] • Data from Kaggle")
