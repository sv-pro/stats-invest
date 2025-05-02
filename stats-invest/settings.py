import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Cryptocurrency settings
# Common cryptocurrency symbols and IDs
AVAILABLE_CRYPTOCURRENCIES = {
    "BTC": {"id": 1, "name": "Bitcoin", "symbol": "BTC"},
    "ETH": {"id": 1027, "name": "Ethereum", "symbol": "ETH"},
    "SOL": {"id": 5426, "name": "Solana", "symbol": "SOL"},
    "ADA": {"id": 2010, "name": "Cardano", "symbol": "ADA"},
    "BNB": {"id": 1839, "name": "Binance Coin", "symbol": "BNB"},
    "XRP": {"id": 52, "name": "XRP", "symbol": "XRP"},
    "DOGE": {"id": 74, "name": "Dogecoin", "symbol": "DOGE"},
    "DOT": {"id": 6636, "name": "Polkadot", "symbol": "DOT"},
}

# Selected cryptocurrency - change this to use a different cryptocurrency
CRYPTO_SYMBOL = "BTC"
CRYPTO_NAME = AVAILABLE_CRYPTOCURRENCIES[CRYPTO_SYMBOL]["name"]
CRYPTO_ID = AVAILABLE_CRYPTOCURRENCIES[CRYPTO_SYMBOL]["id"]

# Investment strategy parameters
WEEKLY_INVESTMENT = int(os.getenv("WEEKLY_INVESTMENT", 100))
WINDOW_SIZE = int(os.getenv("WINDOW_SIZE", 13))

# Z-score investment thresholds
# Format: (percentage_to_invest, z_score_threshold)
# Example: (0.8, 2.0) means "Invest 80% of available cash if z-score magnitude >= 2.0"
Z_SCORE_THRESHOLDS = [
    (0.8, 2.0),  # Invest 80% if |z| >= 2.0 (strongly undervalued)
    (0.6, 1.5),  # Invest 60% if |z| >= 1.5
    (0.4, 1.0),  # Invest 40% if |z| >= 1.0
    (0.2, 0.5),  # Invest 20% if |z| >= 0.5
    (0.1, 0.0)   # Invest 10% if |z| >= 0.0 (slightly undervalued)
]

# Historical data fetching
HISTORICAL_DAYS = int(os.getenv("HISTORICAL_DAYS", 1825))  # ~5 years of data

# CoinMarketCap API settings
CMC_API_KEY = os.getenv("CMC_API_KEY", "")
CMC_API_URL = "https://pro-api.coinmarketcap.com/v2"
CMC_QUOTE_CURRENCY = "USD"

# Data fetch interval - CoinMarketCap API has limitations on historical data granularity
# Available intervals: daily, hourly, etc.
FETCH_INTERVAL = "weekly"