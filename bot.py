import os
import pandas as pd
from nsepython import nse_optionchain_scrapper
from google import genai
from pyairtable import Api
import datetime

# Setup Clients from environment variables
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
AIRTABLE_TOKEN = os.environ.get("AIRTABLE_TOKEN")
BASE_ID = os.environ.get("AIRTABLE_BASE_ID")

# Initialize Gemini
client = genai.Client(api_key=GEMINI_KEY)

# INITIALIZATION FIX: 
# The 404 error happened because the IDs were likely concatenated.
# We initialize the Api first, then the table separately.
api = Api(AIRTABLE_TOKEN)
table = api.table(BASE_ID, "Table 1")

def main():
    try:
        # 1. Fetch NSE Data
        data = nse_optionchain_scrapper("NIFTY")
        price = data['records']['underlyingValue']
        
        # 2. Extract Strategy Data
        # Flatten the nested CE and PE data
        df = pd.json_normalize(data['filtered']['data'])
        
        # Strategy Logic: Identify Walls and compare CE vs PE
        # We need Open Interest AND Change in OI to see if walls are collapsing
        top_ce = df.nlargest(5, 'CE.openInterest')[['strikePrice', 'CE.openInterest', 'CE.changeinOpenInterest']]
        top_pe = df.nlargest(5, 'PE.openInterest')[['strikePrice', 'PE.openInterest', 'PE.changeinOpenInterest']]
        
        # 3. Gemini Analysis (Strict Formatting: no hyphens, no double quotes)
        prompt = (
            f"Market Price is {price}. "
            f"Call Walls (Resistance): {top_ce.to_string(index=False)}. "
            f"Put Walls (Support): {top_pe.to_string(index=False)}. "
            "Analyze if any wall is collapsing. "
            "Tell me who is selling more at which levels. "
            "Is the ball moving up or down? "
            "Use simple text only less commas no double quotes no hyphens."
        )
        
        # Using 1.5-flash for reliability
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt
        )
        
        # Clean the verdict to follow your formatting rules
        verdict = response.text.replace('"', '').replace('-', '').replace('\n', ' ').strip()

        # 4. Save to Airtable
        # Ensure your Column Names in Airtable are exactly: Time, Price, Verdict
        table.create({
            "Time": datetime.datetime.now().strftime("%H:%M"),
            "Price": float(price),
            "Verdict": verdict
        })
        print(f"Success: Market @ {price} updated at {datetime.datetime.now()}")

    except Exception as e:
        # This will print the exact error in your GitHub Action logs
        print(f"Error encountered: {str(e)}")

if __name__ == "__main__":
    main()
