import requests
import config

# Get API key
EXCHANGE_RATE_API_KEY = config.EXCHANGE_RATE_API_KEY
BASE_URL = "https://api.twelvedata.com"

def get_exchange_rate(base_currency: str):
    """
    Fetches all exchange rates for a given base currency
    from ExchangeRate-API.
    """
    
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/latest/{base_currency.upper()}"
    
    try:
        response = requests.get(url)
        response.raise_for_status() # Check if request was successful
        
        data = response.json()
        
        # The data looks like: {"result": "success", "conversion_rates": {"USD": 1, "DKK": 6.95, ...}}
        if data.get("result") == "success":
            return data.get("conversion_rates")
        else:
            print(f"Error: API call for exchange rates was not successful. Response: {data}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching exchange rate data: {e}")
        return None
    except (KeyError, TypeError, ValueError):
        print("Error parsing exchange rate data.")
        return None