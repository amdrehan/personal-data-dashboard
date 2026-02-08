import streamlit as st
import pandas as pd
import plotly.express as px
from app.core.load import load_csv, standardize_date

st.markdown("## ✅ Habits")
st.caption("Completion rate, streaks, and weekly heatmap")

df = load_csv("habits_daily.csv")
df = standardize_date(df, "date").dropna(subset=["date"]).sort_values("date")

df["habit"] = df["habit"].astype(str).str.strip().str.title()
df["done"] = pd.to_numeric(df["done"], errors="coerce").fillna(0).astype(int).clip(0, 1)
df["day"] = df["date"].dt.date

habits = sorted(df["habit"].unique().tolist())
picked = st.multiselect("Habits", habits, default=habits)

f = df[df["habit"].isin(picked)].copy()

k1, k2, k3 = st.columns(3)
k1.metric("Rows", f"{len(f):,}")
k2.metric("Completion", f"{(f['done'].mean()*100):.1f}%")

daily = f.groupby("day", as_index=False)["done"].mean().sort_values("day")
streak = 0
for v in daily["done"].tolist()[::-1]:
    if v >= 1:
        streak += 1
    else:
        break
k3.metric("Current streak (days)", f"{streak}")

st.divider()

by_habit = f.groupby("habit", as_index=False)["done"].mean().sort_values("done", ascending=False)
fig = px.bar(by_habit, x="habit", y="done", title="Completion by habit")
st.plotly_chart(fig, use_container_width=True)

# Heatmap: week x day-of-week
d = f.copy()
d["week"] = pd.to_datetime(d["day"]).astype("datetime64[ns]").dt.isocalendar().week.astype(int)
d["dow"] = pd.to_datetime(d["day"]).astype("datetime64[ns]").dt.day_name()

pivot = d.pivot_table(index="week", columns="dow", values="done", aggfunc="mean").fillna(0)
order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
pivot = pivot[[c for c in order if c in pivot.columns]]

fig = px.imshow(pivot, aspect="auto", title="Weekly heatmap (avg completion)")
st.plotly_chart(fig, use_container_width=True)

with st.expander("Data"):
    st.dataframe(f, use_container_width=True)
