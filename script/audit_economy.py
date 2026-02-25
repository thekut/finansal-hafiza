import requests
import re
import sys
import time
import traceback

def fetch_data():
    data = {}
    print("Starting data fetch...")

    # 1. Currency (USD, EUR)
    r = None
    try:
        print("Fetching Currencies...")
        for _ in range(3):
            try:
                r = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=10)
                if r.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                time.sleep(2)
                continue

        if r is None or r.status_code != 200:
             raise Exception(f"API Error or Unreachable. Status: {r.status_code if r else 'None'}")

        rates = r.json().get('rates', {})
        usd_try = rates.get('TRY', 0)
        eur_try = usd_try / rates.get('EUR', 1)

        if usd_try > 0:
            data['dolar'] = round(usd_try, 2)
            data['euro'] = round(eur_try, 2)
            print(f"USD: {data['dolar']}, EUR: {data['euro']}")
    except Exception as e:
        print(f"Failed to fetch Currency: {e}")
        traceback.print_exc()

    # 2. Crypto (BTC, NST) & Gold (via PAXG)
    r = None
    try:
        print("Fetching Crypto & Gold (via PAXG)...")
        # Added retry logic
        for _ in range(3):
            try:
                r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ninja-squad,pax-gold&vs_currencies=try", timeout=10)
                if r.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                time.sleep(2)
                continue
            time.sleep(2)

        if r is None or r.status_code != 200:
             raise Exception(f"Crypto API Error. Status: {r.status_code if r else 'None'}")

        c = r.json()

        if 'bitcoin' in c:
            data['btc'] = int(c['bitcoin']['try'])
            print(f"BTC: {data['btc']}")

        if 'ninja-squad' in c:
            data['nst'] = round(c['ninja-squad']['try'], 2)
            print(f"NST: {data['nst']}")

        if 'pax-gold' in c:
            paxg_try = c['pax-gold']['try']
            # 1 Troy Ounce = 31.1034768 Grams
            gram_spot = paxg_try / 31.1035

            # Physical Market Premium (Turkey specific)
            # Spot usually lower than physical market (Kapalıçarşı)
            # Adding ~3% spread
            gram_market = gram_spot * 1.03

            data['gram'] = int(gram_market)

            # Quarter Gold Calculation
            # Theoretical: 1.754g total, 22k (0.916)
            # Market Price usually follows: Gram Price * 1.63 to 1.67 depending on workmanship
            # Using 1.65 multiplier
            data['ceyrek'] = int(gram_market * 1.65)

            print(f"Gram Gold: {data['gram']}, Quarter Gold: {data['ceyrek']}")

    except Exception as e:
        print(f"Failed to fetch Crypto/Gold: {e}")
        traceback.print_exc()

    return data

def update_index(data):
    filepath = "index.html"
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"{filepath} not found.")
        return

    # Strategy: Locate the "2026" items block using regex
    # We look for "2026": { ... items: { ... } }

    # 1. Find the start of 2026 items
    # Matches: "2026": { ... items: {
    pattern_start = r'("2026"\s*:\s*\{.*?items\s*:\s*\{)'
    match = re.search(pattern_start, content, re.DOTALL)
    
    if match:
        start_idx = match.end()
        # Find the closing brace of the items object
        # We need to be careful about nested braces, but items usually contains simple key-values
        # Just searching for the next '}' might be safe enough for this structure
        end_idx = content.find("}", start_idx)

        if end_idx == -1:
            print("Could not find end of items block.")
            return

        items_block = content[start_idx:end_idx]
        original_block = items_block

        # Helper to replace key value
        def replace_val(key, val, text):
            # Matches key: number, or key: number.decimal
            return re.sub(r'(\b' + key + r'\b\s*:\s*)([\d.]+)', f'\\g<1>{val}', text)

        if 'dolar' in data: items_block = replace_val('dolar', data['dolar'], items_block)
        if 'euro' in data: items_block = replace_val('euro', data['euro'], items_block)
        if 'gram' in data: items_block = replace_val('gram', data['gram'], items_block)
        if 'ceyrek' in data: items_block = replace_val('ceyrek', data['ceyrek'], items_block)
        if 'btc' in data: items_block = replace_val('btc', data['btc'], items_block)
        if 'nst' in data: items_block = replace_val('nst', data['nst'], items_block)

        if items_block != original_block:
            new_content = content[:start_idx] + items_block + content[end_idx:]
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("index.html updated successfully.")
        else:
            print("No changes made to index.html (Data might be same).")

    else:
        print("Could not find 2026 items block structure.")

if __name__ == "__main__":
    data = fetch_data()
    if data:
        update_index(data)
    else:
        print("No data fetched.")
        sys.exit(1)
