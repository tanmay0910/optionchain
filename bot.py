import os
import pandas as pd
from nsepython import nse_optionchain_scrapper
from google import genai
from pyairtable import Api
import datetime

# Setup Clients
# Note: Ensure these environment variables are set in your GitHub Secrets/Environment
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
AIRTABLE_TOKEN = os.environ.get("AIRTABLE_TOKEN")
BASE_ID = os.environ.get("AIRTABLE_BASE_ID")

# Initialize Gemini
client = genai.Client(api_key=GEMINI_KEY)

# CORRECT INITIALIZATION: Only Base ID and Table Name
# Do NOT include the tbl... or viw... IDs in your Secrets
api = Api(AIRTABLE_TOKEN)
table = api.table(BASE_ID, "Table 1")

def main():
    try:
        # 1. Fetch NSE Data
        data = nse_optionchain_scrapper("NIFTY")
        price = data['records']['underlyingValue']
        
        # We need both CE and PE data for a "Wall" comparison
        df = pd.json_normalize(data['filtered']['data'])
        
        # 2. Strategy Logic: Identify "Walls"
        # We look at Top 5 Call OI and Top 5 Put OI to see who is selling more
        top_ce = df.nlargest(5, 'CE.openInterest')[['strikePrice', 'CE.openInterest', 'CE.changeinOpenInterest']]
        top_pe = df.nlargest(5, 'PE.openInterest')[['strikePrice', 'PE.openInterest', 'PE.changeinOpenInterest']]
        
        # 3. Gemini Analysis (Following your strict formatting rules)
        prompt = (
            f"Market Price is {price}. "
            f"Call Walls: {top_ce.to_string()}. "
            f"Put Walls: {top_pe.to_string()}. "
            "Analyze if any wall is collapsing. "
            "Tell me who is selling more at which levels. "
            "Use simple text only less commas no double quotes no hyphens."
        )
        
        # Using 1.5-flash as it is the most stable free-tier model for this logic
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt
        )
        
        # Clean the response to match your preference
        verdict = response.text.replace('"', '').replace('-', '').replace('\n', ' ')

        # 4. Save to Storage
        # Ensure your Airtable column names match these EXACTLY
        table.create({
            "Time": datetime.datetime.now().strftime("%H:%M"),
            "Price": float(price),
            "Verdict": verdict
        })
        print(f"Success: Market @ {price} updated.")

    except Exception as e:
        print(f"Error encountered: {e}")

if __name__ == "__main__":
    main()
