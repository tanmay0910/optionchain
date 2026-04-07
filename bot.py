import pandas as pd
from nsepython import nse_optionchain_scrapper
from google import genai
import datetime

# Setup Gemini
client = genai.Client(api_key="YOUR_GEMINI_KEY")

def main():
    # 1. Get Data
    data = nse_optionchain_scrapper("NIFTY")
    price = data['records']['underlyingValue']
    df = pd.json_normalize(data['filtered']['data'])
    
    # 2. Get Walls (Top OI)
    top_ce = df.nlargest(3, 'CE.openInterest')
    top_pe = df.nlargest(3, 'PE.openInterest')
    
    # 3. Gemini Analysis (No hyphens, no quotes)
    prompt = f"Price {price}. CE Walls: {top_ce.to_string()}. PE Walls: {top_pe.to_string()}. Any wall collapsing? Simple text only no double quotes no hyphens."
    response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
    verdict = response.text.replace('"', '').replace('-', '').strip()

    # 4. Save to CSV (This acts as your 'Database')
    new_data = {
        "Time": [datetime.datetime.now().strftime("%H:%M")],
        "Price": [price],
        "Verdict": [verdict]
    }
    new_df = pd.DataFrame(new_data)
    
    # Append to the file
    try:
        existing_df = pd.read_csv("market_log.csv")
        final_df = pd.concat([existing_df, new_df]).tail(20) # Keep last 20 entries
    except:
        final_df = new_df
        
    final_df.to_csv("market_log.csv", index=False)
    print("Log updated.")

if __name__ == "__main__":
    main()
