import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Market Pulse", layout="wide")
st.title("🏹 Market Momentum Scanner")

try:
    # Read the data file
    df = pd.read_csv("market_data.csv")
    
    # 1. Broad Status Section
    latest = df.iloc[-1]
    col1, col2 = st.columns(2)
    col1.metric("Nifty Price", latest['Price'])
    st.info(f"Verdict: {latest['Verdict']}")
    
    # 2. Visual Chart: The 'Ball' Movement
    st.subheader("Price Movement Trend")
    fig = px.line(df, x="Time", y="Price", markers=True)
    st.plotly_chart(fig, use_container_width=True)
    
    # 3. History Table
    st.subheader("5-Min Market Log")
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)

except Exception:
    st.warning("Waiting for the first data update from the bot. Ensure bot.py has run successfully.")
