"""
Currency Exchange Rate Endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
import httpx
import logging
from datetime import datetime, timedelta
from core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Cache for exchange rates (in production, use Redis)
_rate_cache: Dict[str, Dict[str, Any]] = {}
CACHE_DURATION_MINUTES = 60

@router.get("/exchange-rate")
async def get_exchange_rate(
    from_currency: str = Query(..., description="Source currency code"),
    to_currency: str = Query(..., description="Target currency code")
):
    """Get exchange rate between two currencies"""
    
    if from_currency == to_currency:
        return {"rate": 1.0, "from": from_currency, "to": to_currency}
    
    cache_key = f"{from_currency}-{to_currency}"
    
    # Check cache first
    if cache_key in _rate_cache:
        cached_data = _rate_cache[cache_key]
        cache_time = datetime.fromisoformat(cached_data["timestamp"])
        if datetime.now(UTC) - cache_time < timedelta(minutes=CACHE_DURATION_MINUTES):
            return cached_data
    
    try:
        # Try to get real exchange rates from an API
        # Using exchangerate-api.com as an example (free tier available)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.exchangerate-api.com/v4/latest/{from_currency}",
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                rates = data.get("rates", {})
                
                if to_currency in rates:
                    rate = rates[to_currency]
                    result = {
                        "rate": rate,
                        "from": from_currency,
                        "to": to_currency,
                        "timestamp": datetime.now(UTC).isoformat(),
                        "source": "exchangerate-api.com"
                    }
                    
                    # Cache the result
                    _rate_cache[cache_key] = result
                    return result
    
    except Exception as e:
        logger.warning(f"Failed to fetch real exchange rate: {e}")
    
    # Fallback to mock rates
    mock_rates = get_mock_exchange_rates()
    
    if from_currency in mock_rates and to_currency in mock_rates[from_currency]:
        rate = mock_rates[from_currency][to_currency]
    elif to_currency in mock_rates and from_currency in mock_rates[to_currency]:
        rate = 1 / mock_rates[to_currency][from_currency]
    else:
        rate = 1.0  # Default fallback
    
    result = {
        "rate": rate,
        "from": from_currency,
        "to": to_currency,
        "timestamp": datetime.now(UTC).isoformat(),
        "source": "mock_data"
    }
    
    # Cache the mock result
    _rate_cache[cache_key] = result
    return result

@router.get("/supported-currencies")
async def get_supported_currencies():
    """Get list of supported currencies"""
    return {
        "currencies": [
            {"code": "USD", "name": "US Dollar", "symbol": "$"},
            {"code": "EUR", "name": "Euro", "symbol": "€"},
            {"code": "GBP", "name": "British Pound", "symbol": "£"},
            {"code": "JPY", "name": "Japanese Yen", "symbol": "¥"},
            {"code": "CNY", "name": "Chinese Yuan", "symbol": "¥"},
            {"code": "CAD", "name": "Canadian Dollar", "symbol": "C$"},
            {"code": "AUD", "name": "Australian Dollar", "symbol": "A$"},
            {"code": "CHF", "name": "Swiss Franc", "symbol": "CHF"},
            {"code": "SEK", "name": "Swedish Krona", "symbol": "kr"},
            {"code": "NOK", "name": "Norwegian Krone", "symbol": "kr"},
            {"code": "INR", "name": "Indian Rupee", "symbol": "₹"},
            {"code": "BRL", "name": "Brazilian Real", "symbol": "R$"},
            {"code": "MXN", "name": "Mexican Peso", "symbol": "$"},
            {"code": "KRW", "name": "South Korean Won", "symbol": "₩"},
            {"code": "SGD", "name": "Singapore Dollar", "symbol": "S$"}
        ]
    }

def get_mock_exchange_rates() -> Dict[str, Dict[str, float]]:
    """Mock exchange rates for demo purposes"""
    return {
        "USD": {
            "EUR": 0.85, "GBP": 0.73, "JPY": 110.0, "CNY": 6.45, "CAD": 1.25, 
            "AUD": 1.35, "CHF": 0.92, "SEK": 8.50, "NOK": 8.75, "INR": 74.5,
            "BRL": 5.2, "MXN": 20.1, "KRW": 1180.0, "SGD": 1.35
        },
        "EUR": {
            "USD": 1.18, "GBP": 0.86, "JPY": 129.0, "CNY": 7.59, "CAD": 1.47,
            "AUD": 1.59, "CHF": 1.08, "SEK": 10.0, "NOK": 10.3, "INR": 87.8,
            "BRL": 6.1, "MXN": 23.7, "KRW": 1390.0, "SGD": 1.59
        },
        "GBP": {
            "USD": 1.37, "EUR": 1.16, "JPY": 150.0, "CNY": 8.83, "CAD": 1.71,
            "AUD": 1.85, "CHF": 1.26, "SEK": 11.6, "NOK": 12.0, "INR": 102.0,
            "BRL": 7.1, "MXN": 27.5, "KRW": 1615.0, "SGD": 1.85
        }
    }


