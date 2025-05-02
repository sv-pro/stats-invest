import os
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv
import settings

# Load environment variables
load_dotenv()

def fetch_cmc_historical_data(crypto_id, days=settings.HISTORICAL_DAYS):
    """
    Fetch historical cryptocurrency data from CoinMarketCap API.
    
    Parameters:
    - crypto_id: ID of the cryptocurrency on CoinMarketCap
    - days: Number of days of historical data to fetch
    
    Returns:
    - DataFrame with historical price data (date, price)
    """
    print(f"Fetching historical data for {settings.CRYPTO_NAME} (ID: {crypto_id})...")
    
    # Calculate time range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Convert to timestamps for API
    end_timestamp = int(end_date.timestamp())
    start_timestamp = int(start_date.timestamp())
    
    # CoinMarketCap API endpoint
    url = f"{settings.CMC_API_URL}/cryptocurrency/quotes/historical"
    
    # Headers with API key
    headers = {
        'X-CMC_PRO_API_KEY': settings.CMC_API_KEY,
        'Accept': 'application/json'
    }
    
    # Parameters for the API request
    params = {
        'id': crypto_id,
        'time_start': start_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'time_end': end_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'interval': settings.FETCH_INTERVAL,
        'convert': settings.CMC_QUOTE_CURRENCY
    }
    
    try:
        # Make API request
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise exception for error status codes
        
        # Parse response
        data = response.json()
        
        if 'data' not in data or 'quotes' not in data['data']:
            print("Error: Invalid API response format")
            print(f"Response: {data}")
            return generate_sample_data(days)
        
        # Extract quotes
        quotes = data['data']['quotes']
        
        if not quotes:
            print("No data returned from CMC API")
            return generate_sample_data(days)
        
        # Convert to DataFrame
        records = []
        for quote in quotes:
            timestamp = quote['timestamp']
            price = quote['quote'][settings.CMC_QUOTE_CURRENCY]['price']
            
            records.append({
                'date': timestamp,
                'price': price
            })
        
        df = pd.DataFrame(records)
        
        # Convert timestamp strings to datetime objects
        df['date'] = pd.to_datetime(df['date'])
        
        # Sort by date
        df = df.sort_values('date')
        
        return df
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from CoinMarketCap API: {e}")
        
        # If API key is missing, suggest adding it
        if settings.CMC_API_KEY == "":
            print("No API key found. Add your CoinMarketCap API key to the .env file.")
        
        # If we get a 429 response (rate limit), wait and retry
        if hasattr(e, 'response') and e.response and e.response.status_code == 429:
            print("Rate limit exceeded. Waiting 60 seconds to retry...")
            time.sleep(60)
            return fetch_cmc_historical_data(crypto_id, days)
        
        # If the paid plan features are required
        if hasattr(e, 'response') and e.response and e.response.status_code == 401:
            print("Error: This endpoint requires a paid CMC API plan.")
        
        # Fall back to sample data
        return generate_sample_data(days)

def fetch_cmc_latest_price(crypto_id):
    """
    Fetch the latest price data from CoinMarketCap.
    
    Parameters:
    - crypto_id: ID of the cryptocurrency on CoinMarketCap
    
    Returns:
    - Current price or None if request fails
    """
    url = f"{settings.CMC_API_URL.replace('/v2', '/v1')}/cryptocurrency/quotes/latest"
    
    headers = {
        'X-CMC_PRO_API_KEY': settings.CMC_API_KEY,
        'Accept': 'application/json'
    }
    
    params = {
        'id': crypto_id,
        'convert': settings.CMC_QUOTE_CURRENCY
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if 'data' in data and str(crypto_id) in data['data']:
            price = data['data'][str(crypto_id)]['quote'][settings.CMC_QUOTE_CURRENCY]['price']
            return price
        else:
            print("Error parsing price data from CMC API")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching latest price: {e}")
        return None

def generate_sample_data(days=settings.HISTORICAL_DAYS):
    """
    Generate sample price data when API calls fail.
    Used for testing or when API is not available.
    
    Parameters:
    - days: Number of days to generate
    
    Returns:
    - DataFrame with sample price data
    """
    print("Generating sample data for testing...")
    
    # Generate dates (weekly)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Generate weekly dates
    num_weeks = days // 7
    dates = [start_date + timedelta(weeks=i) for i in range(num_weeks)]
    
    # Generate simulated price with trend and volatility (similar to BTC price pattern)
    np.random.seed(42)  # For reproducibility
    
    # Base trend (upward)
    base = np.linspace(5000, 50000, num_weeks)
    
    # Add noise
    noise = np.random.normal(0, 5000, num_weeks)
    
    # Add cyclical component
    cycle = 10000 * np.sin(np.linspace(0, 6*np.pi, num_weeks))
    
    # Combine components
    prices = base + noise + cycle
    
    # Create DataFrame
    df = pd.DataFrame({
        'date': dates,
        'price': prices
    })
    
    return df

def save_to_csv(df, crypto_symbol=settings.CRYPTO_SYMBOL):
    """
    Save DataFrame to CSV file.
    
    Parameters:
    - df: DataFrame to save
    - crypto_symbol: Symbol of the cryptocurrency
    
    Returns:
    - Path to the saved file
    """
    if df is None or df.empty:
        print("No data to save.")
        return None
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Filename with current date
    today = datetime.now().strftime('%Y%m%d')
    filename = f"data/{crypto_symbol}_weekly_{today}.csv"
    
    # Save to CSV
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")
    return filename

def get_weekly_data():
    """
    Get weekly data for the configured cryptocurrency.
    Tries to load from a recent file if available, otherwise fetches new data.
    
    Returns:
    - Path to the data file
    """
    crypto_symbol = settings.CRYPTO_SYMBOL
    crypto_id = settings.CRYPTO_ID
    
    # Check if there's already a recent file
    data_dir = 'data'
    if os.path.exists(data_dir):
        files = [f for f in os.listdir(data_dir) if f.startswith(f"{crypto_symbol}_weekly_") and f.endswith('.csv')]
        if files:
            # Sort by date (newest first)
            files.sort(reverse=True)
            newest_file = os.path.join(data_dir, files[0])
            
            # Check if file is recent (less than 1 day old)
            file_mtime = os.path.getmtime(newest_file)
            file_date = datetime.fromtimestamp(file_mtime)
            if (datetime.now() - file_date).days < 1:
                print(f"Using recent data file: {newest_file}")
                return newest_file
    
    # Fetch new data
    df = fetch_cmc_historical_data(crypto_id)
    
    if df is not None:
        # Save to CSV
        filename = save_to_csv(df, crypto_symbol)
        return filename
    
    return None

if __name__ == "__main__":
    filename = get_weekly_data()
    if filename:
        # Show preview of the data
        df = pd.read_csv(filename)
        print("\nData Preview:")
        print(df.head())
        print(f"\nTotal records: {len(df)}")
        
        # Add latest price if available
        latest_price = fetch_cmc_latest_price(settings.CRYPTO_ID)
        if latest_price:
            print(f"\nLatest {settings.CRYPTO_SYMBOL} price: ${latest_price:.2f}")
    else:
        print("Failed to retrieve data.")