from .external_api import get_exchange_rate

def convert_currency(amount: float, from_currency: str, to_currency: str):
    """
    Converts an amount from one currency to another using a cached exchange rate.
    """

    if from_currency == to_currency:
        return amount
    
    rates = get_exchange_rate(from_currency)
    
    if rates is None:
        return None 
        
    rate = rates.get(to_currency.upper())
    
    if rate is None:
        print(f"Error: Target currency '{to_currency}' ont found.")
        return None
    
    return amount * rate