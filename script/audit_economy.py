import requests
import re
import os
import sys

def fetch_data():
    print("Fetching data from API...")
    data = {}
    try:
        # Fetch USD and EUR
        r = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=10)
        if r.status_code == 200:
            rates = r.json().get('rates', {})
            usd_try = rates.get('TRY', 0)
            eur_try = usd_try / rates.get('EUR', 1)

            data['dolar'] = round(usd_try, 2)
            data['euro'] = round(eur_try, 2)

            # Estimate Gold
            # Spot gold ~2650 USD/oz (Approximate current market value)
            spot_gold_usd = 2650
            gram_gold_usd = spot_gold_usd / 31.1035
            gram_gold_try = gram_gold_usd * usd_try

            data['gram'] = int(gram_gold_try)
            data['ceyrek'] = int(gram_gold_try * 1.605 * 1.05) # 1.605g + 5% margin

            print(f"Data fetched: {data}")
        else:
            print(f"API request failed with status code {r.status_code}")

    except Exception as e:
        print(f"Error fetching data: {e}")

    return data

def update_index(data):
    # Determine path to index.html relative to this script
    # This script is in script/ directory, so index.html is in ../index.html
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Check if we are running from root or script dir
    if os.path.exists("index.html"):
        filepath = "index.html"
    elif os.path.exists(os.path.join(script_dir, "../index.html")):
        filepath = os.path.join(script_dir, "../index.html")
    else:
        print("Error: index.html not found.")
        sys.exit(1)

    print(f"Updating {filepath}...")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Locate 2026 items block
    pattern_start = r'("2026"\s*:\s*\{.*?items\s*:\s*\{)'
    match = re.search(pattern_start, content, re.DOTALL)
    
    if match:
        start_idx = match.end()
        # Find the closing brace of items
        end_idx = content.find("}", start_idx)

        if end_idx == -1:
            print("Could not find end of items block.")
            return

        items_block = content[start_idx:end_idx]

        # Replace values
        if 'dolar' in data:
            items_block = re.sub(r'(dolar\s*:\s*)[\d.]+', f'\\g<1>{data["dolar"]}', items_block)
        if 'euro' in data:
            items_block = re.sub(r'(euro\s*:\s*)[\d.]+', f'\\g<1>{data["euro"]}', items_block)
        if 'gram' in data:
            items_block = re.sub(r'(gram\s*:\s*)[\d.]+', f'\\g<1>{data["gram"]}', items_block)
        if 'ceyrek' in data:
            items_block = re.sub(r'(ceyrek\s*:\s*)[\d.]+', f'\\g<1>{data["ceyrek"]}', items_block)

        new_content = content[:start_idx] + items_block + content[end_idx:]

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("index.html updated successfully.")

    else:
        print("Could not find 2026 items block in index.html.")

if __name__ == "__main__":
    try:
        data = fetch_data()
        if data:
            update_index(data)
        else:
            print("No data to update.")
    except Exception as e:
        print(f"Critical error in main: {e}")
        sys.exit(1)
