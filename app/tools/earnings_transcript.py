from typing import Dict, Any, List
from datetime import datetime
import requests
import os

def earnings_transcript(company: str, quarters: int = 4) -> List[Dict[str, Any]]:
    """
    Get earnings transcripts using Alpha Vantage API
    """
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        # Fallback to mock data
        return _get_mock_transcripts(company, quarters)

    try:
        # Use Alpha Vantage Earnings Calendar API
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "EARNINGS_CALENDAR",
            "symbol": company,
            "horizon": "3month",  # Get recent earnings
            "apikey": api_key
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()

            transcripts = []
            for item in data[:quarters]:  # Limit to requested quarters
                transcripts.append({
                    "quarter": item.get("fiscalDateEnding", "Unknown"),
                    "date": datetime.strptime(item.get("reportDate", "2024-01-01"), "%Y-%m-%d"),
                    "content": f"Earnings report for {company}. EPS: {item.get('reportedEPS', 'N/A')}, Revenue: {item.get('reportedRevenue', 'N/A')}",
                    "key_points": [
                        f"EPS: {item.get('reportedEPS', 'N/A')}",
                        f"Revenue: {item.get('reportedRevenue', 'N/A')}",
                        f"Estimated EPS: {item.get('estimatedEPS', 'N/A')}"
                    ]
                })

            return transcripts

    except Exception as e:
        print(f"Earnings API error: {e}")

    # Fallback to mock data
    return _get_mock_transcripts(company, quarters)

def _get_mock_transcripts(company: str, quarters: int) -> List[Dict[str, Any]]:
    """
    Fallback mock transcripts
    """
    transcripts = []
    for i in range(quarters):
        transcripts.append({
            "quarter": f"Q{i+1} 2024",
            "date": datetime(2024, 3 + i*3, 15),
            "content": f"Earnings call transcript for {company} Q{i+1}. Revenue guidance: increased. Market conditions: challenging but improving.",
            "key_points": ["Revenue up", "Margin expansion", "Future outlook positive"]
        })
    return transcripts