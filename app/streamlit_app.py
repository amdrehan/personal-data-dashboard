import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from app.core.load import load_csv, standardize_date

st.set_page_config(
    page_title="Personal Data Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load CSS
css_path = Path(__file__).resolve().parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown("## 📊 Personal Data Dashboard")
st.caption("Personal analytics project • fitness, spending, habits")

st.divider()

# ---------- Load data ----------
fitness = standardize_date(load_csv("fitness_daily.csv"), "date").dropna(subset=["date"])
spend = standardize_date(load_csv("spending_transactions.csv"), "date").dropna(subset=["date"])
habits = standardize_date(load_csv("habits_daily.csv"), "date").dropna(subset=["date"])

fitness["day"] = fitness["date"].dt.date
spend["amount"] = pd.to_numeric(spend["amount"], errors="coerce")
spend = spend.dropna(subset=["amount"])
spend["day"] = spend["date"].dt.date
habits["done"] = pd.to_numeric(habits["done"], errors="coerce").fillna(0).astype(int)

# ---------- Last 30 days ----------
max_day = max(
    fitness["day"].max(),
    spend["day"].max(),
    habits["date"].dt.date.max()
)
start_day = max_day - pd.Timedelta(days=30)

f30 = fitness[fitness["day"] >= start_day]
s30 = spend[spend["day"] >= start_day]
h30 = habits[habits["date"].dt.date >= start_day]

# ---------- KPIs ----------
st.markdown("### Last 30 days overview")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Avg steps", f"{f30['steps'].mean():,.0f}")
k2.metric("Avg sleep (hrs)", f"{f30['sleep_hours'].mean():.1f}")
k3.metric("Total spend", f"{s30['amount'].sum():,.0f} SAR")
k4.metric("Habit completion", f"{(h30['done'].mean()*100):.1f}%")

st.divider()

# ---------- Charts ----------
st.markdown("### Trends")

c1, c2 = st.columns(2)

with c1:
    steps_ts = f30.groupby("day", as_index=False)["steps"].mean()
    fig = px.line(
        steps_ts,
        x="day",
        y="steps",
        title="Steps per day",
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    spend_ts = s30.groupby("day", as_index=False)["amount"].sum()
    fig = px.line(
        spend_ts,
        x="day",
        y="amount",
        title="Daily spending (SAR)",
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)
