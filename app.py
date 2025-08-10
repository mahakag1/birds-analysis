import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------
# Page Setup
# ----------------------
st.set_page_config(page_title="Bird Observation Dashboard", layout="wide")

# Custom CSS for attractive styling
st.markdown(
    """
    <style>
    /* Main app background */
    .stApp {
        background-color: #f4f9f9;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Header title styling */
    h1 {
        background: linear-gradient(90deg, #00b4d8, #48cae4);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }

    /* Sidebar background */
    section[data-testid="stSidebar"] {
        background-color: #e3f2fd;
    }

    /* KPI metrics */
    div[data-testid="metric-container"] {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
    }

    /* Chart titles */
    .plotly-title {
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Dashboard Title
st.title("🦜 Bird Observation Dashboard")

# ----------------------
# Load Data
# ----------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Cleaned_Bird_Observation_Data.csv", low_memory=False)

    # Convert key numeric columns to numeric
    numeric_cols = ["Interval_Length", "Temperature", "Humidity", "Count", "Distance"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

df = load_data()

# ----------------------
# Sidebar Filters
# ----------------------
st.sidebar.header("🔍 Filters")
years = st.sidebar.multiselect("Select Year(s)", options=sorted(df["Year"].dropna().unique()), default=sorted(df["Year"].dropna().unique()))
seasons = st.sidebar.multiselect("Select Season(s)", options=df["Season"].dropna().unique(), default=df["Season"].dropna().unique())
locations = st.sidebar.multiselect("Select Location Type", options=df["Location_Type"].dropna().unique(), default=df["Location_Type"].dropna().unique())

filtered_df = df[df["Year"].isin(years) & df["Season"].isin(seasons) & df["Location_Type"].isin(locations)]

# ----------------------
# KPI Section
# ----------------------
col1, col2, col3 = st.columns(3)
col1.metric("Total Observations", len(filtered_df))
col2.metric("Unique Species", filtered_df["Scientific_Name"].nunique())
col3.metric("Observers", filtered_df["Observer"].nunique())

# Chart color palette
colors = px.colors.qualitative.Bold

# ----------------------
# Temporal Analysis
# ----------------------
st.subheader("📅 Temporal Analysis")
temp_col1, temp_col2 = st.columns(2)

season_counts = filtered_df.groupby("Season")["Scientific_Name"].count().reset_index()
fig1 = px.bar(season_counts, x="Season", y="Scientific_Name", title="Bird Sightings by Season", color="Season", color_discrete_sequence=colors)
temp_col1.plotly_chart(fig1, use_container_width=True)

filtered_df["Start_Hour"] = pd.to_datetime(filtered_df["Start_Time"], errors="coerce").dt.hour
hour_counts = filtered_df.groupby("Start_Hour")["Scientific_Name"].count().reset_index()
fig2 = px.bar(hour_counts, x="Start_Hour", y="Scientific_Name", title="Bird Activity by Hour", labels={"Scientific_Name": "Observations"}, color_discrete_sequence=["#ff6b6b"])
temp_col2.plotly_chart(fig2, use_container_width=True)

# ----------------------
# Spatial Analysis
# ----------------------
st.subheader("📍 Spatial Analysis")
sp_col1, sp_col2 = st.columns(2)

loc_counts = filtered_df.groupby("Location_Type")["Scientific_Name"].nunique().reset_index()
fig3 = px.bar(loc_counts, x="Location_Type", y="Scientific_Name", title="Species Diversity by Location Type", color="Location_Type", color_discrete_sequence=colors)
sp_col1.plotly_chart(fig3, use_container_width=True)

plot_counts = filtered_df.groupby("Plot_Name")["Scientific_Name"].nunique().reset_index().sort_values(by="Scientific_Name", ascending=False).head(10)
fig4 = px.bar(plot_counts, x="Plot_Name", y="Scientific_Name", title="Top 10 Plots by Species Diversity", color_discrete_sequence=["#48cae4"])
sp_col2.plotly_chart(fig4, use_container_width=True)

# ----------------------
# Species Analysis
# ----------------------
st.subheader("🦉 Species Analysis")
spc_col1, spc_col2, spc_col3 = st.columns(3)

top_species = filtered_df["Scientific_Name"].value_counts().head(10).reset_index()
top_species.columns = ["Species", "Count"]
fig5 = px.bar(top_species, x="Species", y="Count", title="Top 10 Observed Species", color_discrete_sequence=["#9b5de5"])
spc_col1.plotly_chart(fig5, use_container_width=True)

id_method_counts = filtered_df["ID_Method"].value_counts().reset_index()
id_method_counts.columns = ["ID_Method", "Count"]
fig6 = px.pie(id_method_counts, names="ID_Method", values="Count", title="ID Methods Used", color_discrete_sequence=colors)
spc_col2.plotly_chart(fig6, use_container_width=True)

sex_counts = filtered_df["Sex"].value_counts().reset_index()
sex_counts.columns = ["Sex", "Count"]
fig7 = px.pie(sex_counts, names="Sex", values="Count", title="Sex Ratio of Birds Observed", color_discrete_sequence=["#ffb703", "#219ebc"])
spc_col3.plotly_chart(fig7, use_container_width=True)

# ----------------------
# Environmental Conditions
# ----------------------
st.subheader("🌦 Environmental Conditions")
env_col1, env_col2 = st.columns(2)

fig8 = px.scatter(
    filtered_df.dropna(subset=["Temperature", "Humidity", "Interval_Length"]),
    x="Temperature", y="Humidity",
    size="Interval_Length", color="Season",
    hover_name="Scientific_Name", title="Temperature vs Humidity by Season",
    color_discrete_sequence=colors
)
env_col1.plotly_chart(fig8, use_container_width=True)

disturb_counts = filtered_df["Disturbance"].value_counts().reset_index()
disturb_counts.columns = ["Disturbance", "Count"]
fig9 = px.bar(disturb_counts, x="Disturbance", y="Count", title="Impact of Disturbance on Observations", color="Disturbance", color_discrete_sequence=colors)
env_col2.plotly_chart(fig9, use_container_width=True)

# ----------------------
# Distance & Behavior
# ----------------------
st.subheader("📏 Distance & Behavior")
db_col1, db_col2 = st.columns(2)

fig10 = px.histogram(filtered_df.dropna(subset=["Distance"]), x="Distance", nbins=20, title="Distribution of Observation Distances", color_discrete_sequence=["#06d6a0"])
db_col1.plotly_chart(fig10, use_container_width=True)

flyover_counts = filtered_df["Flyover_Observed"].value_counts().reset_index()
flyover_counts.columns = ["Flyover_Observed", "Count"]
fig11 = px.pie(flyover_counts, names="Flyover_Observed", values="Count", title="Flyover Observations", color_discrete_sequence=colors)
db_col2.plotly_chart(fig11, use_container_width=True)

# ----------------------
# Observer Trends
# ----------------------
st.subheader("👩‍🔬 Observer Trends")
obs_counts = filtered_df["Observer"].value_counts().head(10).reset_index()
obs_counts.columns = ["Observer", "Count"]
fig12 = px.bar(obs_counts, x="Observer", y="Count", title="Top 10 Observers by Number of Observations", color_discrete_sequence=["#ef476f"])
st.plotly_chart(fig12, use_container_width=True)

# ----------------------
# Conservation Insights
# ----------------------
st.subheader("🛡 Conservation Insights")
cons_col1, cons_col2 = st.columns(2)

watchlist_counts = filtered_df["PIF_Watchlist_Status"].value_counts().reset_index()
watchlist_counts.columns = ["Watchlist Status", "Count"]
fig13 = px.bar(watchlist_counts, x="Watchlist Status", y="Count", title="Watchlist Status Distribution", color_discrete_sequence=colors)
cons_col1.plotly_chart(fig13, use_container_width=True)

aou_counts = filtered_df["AOU_Code"].value_counts().head(10).reset_index()
aou_counts.columns = ["AOU_Code", "Count"]
fig14 = px.bar(aou_counts, x="AOU_Code", y="Count", title="Top 10 AOU Codes", color_discrete_sequence=["#118ab2"])
cons_col2.plotly_chart(fig14, use_container_width=True)

st.markdown("📌 *Dashboard generated using Streamlit & Plotly — Bird Monitoring Data Analysis*")
