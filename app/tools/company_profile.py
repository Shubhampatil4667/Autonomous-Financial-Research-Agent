from typing import Dict, Any
import yfinance as yf

def company_profile(symbol: str) -> Dict[str, Any]:
    """
    Get company profile information
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return {
            "name": info.get("longName", ""),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "description": info.get("longBusinessSummary", ""),
            "employees": info.get("fullTimeEmployees"),
            "headquarters": info.get("city", "") + ", " + info.get("state", "") + ", " + info.get("country", "")
        }
    except:
        # Mock data
        return {
            "name": f"{symbol} Corporation",
            "sector": "Technology",
            "industry": "Electric Vehicles",
            "description": f"Leading company in {symbol} industry",
            "employees": 100000,
            "headquarters": "Austin, TX, USA"
        }