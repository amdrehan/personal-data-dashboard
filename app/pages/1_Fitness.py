import streamlit as st
import pandas as pd
import plotly.express as px
from app.core.load import load_csv, standardize_date

st.markdown("## 🏃 Fitness")
st.caption("Steps, sleep, and weight trends")

df = load_csv("fitness_daily.csv")
df = standardize_date(df, "date").dropna(subset=["date"]).sort_values("date")
df["day"] = df["date"].dt.date

min_d, max_d = df["day"].min(), df["day"].max()
start, end = st.date_input("Date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)

f = df[(df["day"] >= start) & (df["day"] <= end)].copy()

k1, k2, k3 = st.columns(3)
k1.metric("Avg steps", f"{f['steps'].mean():,.0f}")
k2.metric("Avg sleep (hrs)", f"{f['sleep_hours'].mean():.1f}")
k3.metric("Latest weight (kg)", f"{f['weight_kg'].dropna().iloc[-1]:.1f}" if f["weight_kg"].notna().any() else "—")

st.divider()

c1, c2 = st.columns(2)
with c1:
    fig = px.line(f.groupby("day", as_index=False)["steps"].mean(), x="day", y="steps", markers=True, title="Steps per day")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    fig = px.line(f.groupby("day", as_index=False)["sleep_hours"].mean(), x="day", y="sleep_hours", markers=True, title="Sleep hours per day")
    st.plotly_chart(fig, use_container_width=True)

w = f.dropna(subset=["weight_kg"]).groupby("day", as_index=False)["weight_kg"].mean()
fig = px.line(w, x="day", y="weight_kg", markers=True, title="Weight trend")
st.plotly_chart(fig, use_container_width=True)

with st.expander("Data"):
    st.dataframe(f, use_container_width=True)
