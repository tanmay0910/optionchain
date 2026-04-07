import os
import pandas as pd
from nsepython import nse_optionchain_scrapper
from google import genai
from pyairtable import Api
import datetime

# Setup Clients
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
airtable = Api(os.environ["AIRTABLE_TOKEN"]).table(os.environ["AIRTABLE_BASE_ID"], "Table 1")

def main():
    # 1. Fetch NSE Data
    data = nse_optionchain_scrapper("NIFTY")
    price = data['records']['underlyingValue']
    df = pd.json_normalize(data['filtered']['data'])
    
    # 2. Strategy Logic: Identify "Walls"
    # Filter for top 5 Call and Put OI strikes
    walls = df.nlargest(5, 'CE.openInterest')
    
    # 3. Gemini Analysis (Strict Formatting: no hyphens, no quotes)
    prompt = f"Price {price}. Analyze these walls: {walls.to_string()}. Is a wall collapsing? Tell me who is selling more. Simple text only less commas no double quotes no hyphens."
    
    response = client.models.generate_content(model="gemini-2.5-flash-lite", contents=prompt)
    verdict = response.text.replace('"', '').replace('-', '')

    # 4. Save to Storage
    airtable.create({
        "Time": datetime.datetime.now().strftime("%H:%M"),
        "Price": price,
        "Verdict": verdict
    })

if __name__ == "__main__":
    main()
