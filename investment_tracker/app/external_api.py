import requests
import config

from functools import lru_cache

# Get API key
EXCHANGE_RATE_API_KEY = config.EXCHANGE_RATE_API_KEY
BASE_URL = "https://v6.exchangerate-api.com/v6"

@lru_cache(maxsize=32)
def get_exchange_rate(base_currency: str):
    """
    Fetches all exchange rates for a given base currency
    from ExchangeRate-API.
    """
    
    base_currency = base_currency.upper()

    url = f"{BASE_URL}/{EXCHANGE_RATE_API_KEY}/latest/{base_currency}"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status() # Check if request was successful
        
        data = response.json()
        
        # The data looks like: {"result": "success", "conversion_rates": {"USD": 1, "DKK": 6.95, ...}}
        if data.get("result") == "success":
            return data.get("conversion_rates")
        else:
            print(f"Error: API call for exchange rates was not successful: {data.get('error-type', 'Unknown error')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching exchange rates for {base_currency}: {e}")
        return None
    except (KeyError, TypeError, ValueError):
        print("Error parsing exchange rate API response.")
        return None