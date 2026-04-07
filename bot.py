import os
import pandas as pd
from nsepython import nse_optionchain_scrapper
from google import genai
import datetime

# Configuration
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_KEY)

def main():
    try:
        # 1. Fetch NSE Data
        data = nse_optionchain_scrapper("NIFTY")
        price = data['records']['underlyingValue']
        df = pd.json_normalize(data['filtered']['data'])
        
        # 2. Strategy: Filter Top 3 Call & Put Walls
        top_ce = df.nlargest(3, 'CE.openInterest')[['strikePrice', 'CE.openInterest']]
        top_pe = df.nlargest(3, 'PE.openInterest')[['strikePrice', 'PE.openInterest']]
        
        # 3. Gemini Analysis
        prompt = (
            f"Price {price}. CE Walls: {top_ce.to_string(index=False)}. "
            f"PE Walls: {top_pe.to_string(index=False)}. "
            "Is a wall collapsing? Who is selling more? "
            "Simple text only less commas no double quotes no hyphens."
        )
        
        response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
        verdict = response.text.replace('"', '').replace('-', '').replace('\n', ' ').strip()

        # 4. Save to Local CSV
        new_row = pd.DataFrame([[datetime.datetime.now().strftime("%H:%M"), price, verdict]], 
                               columns=["Time", "Price", "Verdict"])
        
        if os.path.exists("market_data.csv"):
            old_df = pd.read_csv("market_data.csv")
            final_df = pd.concat([old_df, new_row]).tail(50)
        else:
            final_df = new_row
            
        final_df.to_csv("market_data.csv", index=False)
        print(f"Update Success: {price}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
