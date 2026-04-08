import streamlit as st
import pandas as pd
import google.generativeai as genai
from bs4 import BeautifulSoup

# Add 'beautifulsoup4' and 'lxml' to your requirements.txt
genai.configure(api_key="YOUR_GEMINI_API_KEY_HERE")
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("📂 HTML Option Chain Analyst")

# File Uploader now accepts HTML
uploaded_file = st.file_uploader("Upload the saved NSE Webpage (HTML)", type="html")

if uploaded_file is not None:
    # 1. Parse the HTML
    soup = BeautifulSoup(uploaded_file, 'html.parser')
    
    # 2. Find the table (NSE usually uses a specific ID or class)
    # This tries to find the main data table automatically
    tables = pd.read_html(str(soup))
    
    if tables:
        df = tables[0] # Usually the first big table
        st.write("Data Extracted Successfully!")
        st.dataframe(df.head())
        
        # 3. Send to Gemini
        csv_text = df.to_csv(index=False)
        prompt = f"Analyze this Nifty Option Chain from the uploaded HTML: {csv_text[:8000]}"
        
        response = model.generate_content(prompt)
        st.markdown(response.text)
