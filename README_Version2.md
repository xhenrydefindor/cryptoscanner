# Crypto Market Rapid Change Scanner (CoinMarketCap)

Scan USDT pairs for rapid price/volume changes using CoinMarketCap data.

## Features
- Scan all coins or upload your own list (CSV with `symbol` column).
- Set custom thresholds for rapid price/volume changes.
- View results in browser and download as CSV.

## How to Run Locally

1. Install Python 3.8+ and [pip](https://pip.pypa.io/en/stable/).
2. Clone this repo and navigate to the folder.
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Start the app:
   ```
   streamlit run app.py
   ```

## Deployment

To deploy for free, use [Streamlit Community Cloud](https://streamlit.io/cloud):

1. Push this repo to your GitHub account.
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud), sign in with GitHub, and deploy a new app.
3. Use `app.py` as the main file.

## Notes

- Scanning all coins may take a few minutes due to API rate limits.
- Your CoinMarketCap API key is used securely on the server side.