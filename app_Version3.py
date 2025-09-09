import streamlit as st
import pandas as pd
import requests
import time

API_KEY = "28b039f1-36e6-48a6-8ad0-bb8ebc22733c"
API_BASE = "https://pro-api.coinmarketcap.com/v1"

st.title("Crypto Market Rapid Change Scanner (CoinMarketCap)")

st.markdown("""
Scan USDT pairs for rapid price/volume changes using CoinMarketCap data.<br>
You can upload a CSV with a `symbol` column or scan all coins.
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload your coin list (CSV with 'symbol' column):", type=['csv'])
price_thresh = st.number_input("Rapid price change threshold (%)", min_value=1, max_value=100, value=5)
vol_thresh = st.number_input("Rapid volume change threshold (%)", min_value=1, max_value=1000, value=50)

def get_coin_list():
    url = f"{API_BASE}/cryptocurrency/listings/latest"
    headers = {'X-CMC_PRO_API_KEY': API_KEY}
    params = {'limit': 5000}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    coins = response.json()['data']
    return [coin['symbol'] for coin in coins]

def get_market_data(symbols):
    url = f"{API_BASE}/cryptocurrency/quotes/latest"
    headers = {'X-CMC_PRO_API_KEY': API_KEY}
    results = []
    batch_size = 100
    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i+batch_size]
        params = {'symbol': ','.join(batch), 'convert': 'USDT'}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()['data']
            for symbol in batch:
                coin_data = data.get(symbol)
                if coin_data and 'USDT' in coin_data.get('quote', {}):
                    quote = coin_data['quote']['USDT']
                    results.append({
                        'symbol': symbol,
                        'price': quote['price'],
                        'volume_24h': quote['volume_24h'],
                        'percent_change_1h': quote['percent_change_1h'],
                        'percent_change_24h': quote['percent_change_24h']
                    })
        else:
            st.warning(f"Error fetching batch {i//batch_size+1}: {response.text}")
        time.sleep(0.5)
    return pd.DataFrame(results)

def detect_rapid_changes(df, price_thresh=5, vol_thresh=50):
    rapid = df[
        (df['percent_change_1h'].abs() > price_thresh) |
        (df['percent_change_24h'].abs() > price_thresh)
    ]
    return rapid

if st.button("Run Scan"):
    with st.spinner("Scanning..."):
        if uploaded_file:
            user_df = pd.read_csv(uploaded_file)
            symbols = user_df['symbol'].dropna().unique().tolist()
        else:
            symbols = get_coin_list()
        if not symbols:
            st.error("No coins found!")
            st.stop()
        df = get_market_data(symbols)
        if df.empty:
            st.error("No market data found.")
            st.stop()
        rapid = detect_rapid_changes(df, price_thresh, vol_thresh)
        st.subheader("Coins with rapid changes")
        st.dataframe(rapid)
        st.download_button("Download results as CSV", rapid.to_csv(index=False), "rapid_changes.csv")

st.markdown("""
---
**Note:** For large scans, this may take a few minutes due to API rate limits.  
Your CoinMarketCap API key is used server-side and not exposed to users.
""")