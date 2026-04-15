import yfinance as yf
from typing import Dict, Any
from app.models.schemas import FinancialData

def financial_data_api(symbol: str) -> FinancialData:
    """
    Get financial data using yfinance
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        history = ticker.history(period="1d")

        return FinancialData(
            symbol=symbol,
            price=history['Close'].iloc[-1] if not history.empty else 0.0,
            market_cap=info.get('marketCap', 0),
            pe_ratio=info.get('trailingPE'),
            eps=info.get('trailingEps')
        )
    except Exception as e:
        # Mock data if API fails
        return FinancialData(
            symbol=symbol,
            price=250.0,
            market_cap=500000000000,
            pe_ratio=30.0,
            eps=8.0
        )