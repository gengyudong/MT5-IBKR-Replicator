symbols = {
    "GBPUSD": {
        "conid": 230949810,
        "symbol": "GBP.USD",
        "currency": "USD",
    }
}

def get_ibkr_symbol(mt5_symbol: str) -> str:
    """
    Convert MT5 symbol to IBKR symbol.
    
    Args:
        mt5_symbol (str): The symbol in MT5 format.
        
    Returns:
        str: The corresponding IBKR symbol.
    """
    return symbols.get(mt5_symbol, {}).get("symbol", "")


def get_ibkr_conid(mt5_symbol: str) -> int:
    """
    Get the IBKR conid for a given MT5 symbol.
    
    Args:
        mt5_symbol (str): The symbol in MT5 format.
        
    Returns:
        int: The corresponding IBKR conid, or None if not found.
    """
    return symbols.get(mt5_symbol, {}).get("conid", 0)


def get_ibkr_currency(mt5_symbol: str) -> str:
    """
    Get the IBKR currency for a given MT5 symbol.
    
    Args:
        mt5_symbol (str): The symbol in MT5 format.
        
    Returns:
        str: The corresponding IBKR currency, or None if not found.
    """
    return symbols.get(mt5_symbol, {}).get("currency", "")