import streamlit as st
import pandas as pd
import requests
import time

API_KEY = "28b039f1-36e6-48a6-8ad0-bb8ebc22733c"
API_BASE = "https://pro-api.coinmarketcap.com/v1"

st.set_page_config(page_title="Crypto Ticker Scanner", layout="wide")
st.title("Live Crypto Market Rapid Change Ticker (CoinMarketCap)")

st.markdown("""
**Scan USDT pairs for rapid price/volume changes – live ticker style!**  
You can upload a CSV with a `symbol` column or scan all coins.  
""")

uploaded_file = st.file_uploader("Upload coin list (CSV with 'symbol' column):", type=['csv'])
price_thresh = st.number_input("Rapid price change threshold (%)", min_value=1, max_value=100, value=5)
vol_thresh = st.number_input("Rapid volume change threshold (%)", min_value=1, max_value=1000, value=50)
update_interval = st.slider("Update interval (seconds)", 10, 300, 60)

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
                        'percent_change_24h': quote['percent_change_24h'],
                    })
        time.sleep(0.5)
    return pd.DataFrame(results)

def detect_rapid_changes(df, price_thresh=5, vol_thresh=50):
    # Filter for rapid price or volume changes
    rapid = df[
        (df['percent_change_1h'].abs() > price_thresh) |
        (df['percent_change_24h'].abs() > price_thresh)
    ]
    return rapid

if st.button("Start Live Ticker"):
    st.success("Ticker started! Leave this tab open to keep watching live updates.")
    if uploaded_file:
        user_df = pd.read_csv(uploaded_file)
        symbols = user_df['symbol'].dropna().unique().tolist()
    else:
        symbols = get_coin_list()
    if not symbols:
        st.error("No coins found!")
        st.stop()
    ticker_placeholder = st.empty()
    last_update = st.empty()
    while True:
        try:
            with st.spinner("Fetching market data..."):
                df = get_market_data(symbols)
                rapid = detect_rapid_changes(df, price_thresh, vol_thresh)
                if rapid.empty:
                    ticker_placeholder.info("No rapid movers detected at this time.")
                else:
                    # Display as ticker
                    ticker_html = ""
                    for _, row in rapid.iterrows():
                        direction = "🔺" if row['percent_change_1h'] > 0 else "🔻"
                        ticker_html += f"<span style='margin-right:32px; font-size:1.2em'>{direction} <b>{row['symbol']}</b> ${row['price']:.4f} ({row['percent_change_1h']:.2f}%/1h, {row['percent_change_24h']:.2f}%/24h)</span>"
                    ticker_placeholder.markdown(f"<marquee>{ticker_html}</marquee>", unsafe_allow_html=True)
                last_update.markdown(f"Last update: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            time.sleep(update_interval)
        except Exception as e:
            ticker_placeholder.error(f"Error: {e}")
            break