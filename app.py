import streamlit as st
import requests
import pandas as pd
import google.generativeai as genai
import io

# 1. Setup Gemini API
genai.configure(api_key="YOUR_GEMINI_API_KEY_HERE")
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. NSE Fetcher Function
def get_nse_data():
    url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/103.0.0.0 Safari/537.36',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9'
    }
    session = requests.Session()
    session.get("https://www.nseindia.com/option-chain", headers=headers, timeout=10)
    response = session.get(url, headers=headers, timeout=10)
    data = response.json()
    df = pd.json_normalize(data['records']['data'])
    return df

# 3. Website UI
st.title("NSE Option Chain AI Summarizer")

if st.button("Download & Summarize Now"):
    with st.spinner("Fetching market data..."):
        # Fetch data
        df = get_nse_data()
        
        # Prepare data for Gemini (Take the most important columns to save tokens)
        csv_data = df.to_csv(index=False)
        
        st.success("Data Downloaded!")
        
    with st.spinner("Gemini is analyzing..."):
        # Ask Gemini for the summary
        prompt = f"Analyze this NSE Nifty Option Chain data and give me a brief summary. Tell me the PCR, support/resistance, and if there is more call writing or put writing:\n\n{csv_data[:5000]}" # Limit size
        response = model.generate_content(prompt)
        
        st.subheader("Market Summary")
        st.write(response.text)
        
        # Option to download the raw file too
        st.download_button("Download CSV File", csv_data, "nifty_data.csv", "text/csv")
