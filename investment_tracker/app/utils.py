from .api import get_exchange_rate

# This cache will store entire rate dictionaries, e.g., {"EUR": {"USD": 1.08, "DKK": 7.45}}
EXCHANGE_RATE_CACHE = {}

def convert_currency(amount: float, from_currency: str, to_currency: str):
    """
    Converts an amount from one currency to another using a cached exchange rate.
    """
    global EXCHANGE_RATE_CACHE
    
    # Check if rates for from_currency are already cached
    if from_currency not in EXCHANGE_RATE_CACHE:
        print(f"Fetching exchange rates for base currency: {from_currency}...")
        rates = get_exchange_rate(from_currency)
        
        if rates is None:
            # If API fails, return None to show an error
            return None 
            
        EXCHANGE_RATE_CACHE[from_currency] = rates
        print(f"Cached all rates for {from_currency}.")
    
    # Get the specific rate from the cache
    rates = EXCHANGE_RATE_CACHE[from_currency]
    rate = rates.get(to_currency.upper())
    
    if rate is None:
        print(f"Error: Could not find target currency '{to_currency}' in rates for {from_currency}.")
        return None
    
    # Perform the conversion
    converted_amount = amount * rate
    return converted_amount