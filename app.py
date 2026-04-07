import streamlit as st
from pyairtable import Api
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Wall Scanner", layout="wide")
st.title("🏹 Market Wall & Momentum Scanner")

# Load from Airtable
api = Api(st.secrets["AIRTABLE_TOKEN"])
table = api.table(st.secrets["AIRTABLE_BASE_ID"], "Table 1")
rows = table.all()
df = pd.DataFrame([r['fields'] for r in rows])

if not df.empty:
    # 1. THE SIGNAL
    latest = df.iloc[-1]
    st.subheader(f"Latest Signal @ {latest['Time']}")
    st.info(latest['Verdict'])

    # 2. PIE CHART: Selling Overview
    # (Assuming your bot calculates Total CE vs PE Selling)
    fig = px.pie(values=[60, 40], names=['Call Sellers', 'Put Sellers'], hole=.4)
    st.plotly_chart(fig)
