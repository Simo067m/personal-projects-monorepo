import requests
import config

from cachetools import TTLCache, cached
from threading import RLock

# Get API key
EXCHANGE_RATE_API_KEY = config.EXCHANGE_RATE_API_KEY
BASE_URL = "https://v6.exchangerate-api.com/v6"

# Cache up to 32 currencies, each entry expires after 1 hour.
# lru_cache never expires, so rates would go stale if the server
# runs for days without a restart.
# The RLock makes the cache safe for concurrent WSGI threads.
_exchange_rate_cache = TTLCache(maxsize=32, ttl=3600)
_exchange_rate_lock = RLock()

@cached(_exchange_rate_cache, lock=_exchange_rate_lock)
def _get_exchange_rate_cached(base_currency: str):
    """Internal cached implementation. Expects base_currency already uppercased."""

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


def get_exchange_rate(base_currency: str):
    """
    Fetches all exchange rates for a given base currency
    from ExchangeRate-API. Results are cached for 1 hour.

    Normalizes base_currency to uppercase before the cache
    key is computed, so 'usd' and 'USD' share the same entry.
    """
    return _get_exchange_rate_cached(base_currency.upper())