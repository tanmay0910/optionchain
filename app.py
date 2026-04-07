import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Market Pulse", layout="wide")
st.title("🏹 Market Wall Scanner")

try:
    # Read the file directly from your GitHub folder
    df = pd.read_csv("market_log.csv")
    
    if not df.empty:
        # Latest Signal
        latest = df.iloc[-1]
        st.metric("Nifty Price", latest['Price'])
        st.info(f"Verdict: {latest['Verdict']}")
        
        # Historical View
        st.write("### Momentum Log")
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
        
        # Simple Chart
        fig = px.line(df, x="Time", y="Price", title="Price Movement")
        st.plotly_chart(fig, use_container_width=True)
except:
    st.warning("Waiting for the first data update from the bot...")
