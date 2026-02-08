import streamlit as st
import pandas as pd
import plotly.express as px
from app.core.load import load_csv, standardize_date

st.markdown("## 💳 Spending")
st.caption("Daily spend, category breakdown, top merchants")

df = load_csv("spending_transactions.csv")
df = standardize_date(df, "date").dropna(subset=["date"]).sort_values("date")
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
df = df.dropna(subset=["amount"])

df["day"] = df["date"].dt.date
df["category"] = df["category"].astype(str).str.strip().str.title()

min_d, max_d = df["day"].min(), df["day"].max()
start, end = st.date_input("Date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)

cats = sorted(df["category"].unique().tolist())
picked = st.multiselect("Categories", cats, default=cats)

f = df[(df["day"] >= start) & (df["day"] <= end) & (df["category"].isin(picked))].copy()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total spend", f"{f['amount'].sum():,.0f} SAR")
k2.metric("Transactions", f"{len(f):,}")
k3.metric("Avg / day", f"{f.groupby('day')['amount'].sum().mean():,.0f} SAR" if len(f) else "0 SAR")
k4.metric("Refunds", f"{f.loc[f['amount']<0,'amount'].sum():,.0f} SAR")

st.divider()

c1, c2 = st.columns(2)
daily = f.groupby("day", as_index=False)["amount"].sum()

with c1:
    fig = px.line(daily, x="day", y="amount", markers=True, title="Daily spend (SAR)")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    by_cat = f.groupby("category", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
    fig = px.bar(by_cat, x="category", y="amount", title="Spend by category")
    st.plotly_chart(fig, use_container_width=True)

if "merchant" in f.columns:
    top = f.groupby("merchant", as_index=False)["amount"].sum().sort_values("amount", ascending=False).head(10)
    fig = px.bar(top, x="merchant", y="amount", title="Top merchants")
    st.plotly_chart(fig, use_container_width=True)

with st.expander("Data"):
    st.dataframe(f, use_container_width=True)
