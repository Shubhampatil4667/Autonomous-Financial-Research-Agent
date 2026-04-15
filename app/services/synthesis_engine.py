from typing import List, Dict, Any
from app.models.schemas import SECFiling, FinancialData, NewsItem

class SynthesisEngine:
    def __init__(self):
        self.source_priority = {"sec": 3, "api": 2, "news": 1}

    def combine_sources(self, sec_data: List[SECFiling],
                       financial_data: FinancialData,
                       news: List[NewsItem]) -> Dict[str, Any]:
        """Combine data from multiple sources"""
        combined = {
            "company_info": {},
            "financial_metrics": {},
            "sentiment": 0.0,
            "risks": [],
            "opportunities": []
        }

        # Extract from SEC filings (highest priority)
        for filing in sec_data:
            if "10-K" in filing.type:
                combined["company_info"]["business_description"] = filing.content[:500]
            if "risk" in filing.content.lower():
                combined["risks"].append(f"SEC Risk: {filing.content[:200]}")

        # Add financial data
        combined["financial_metrics"] = {
            "price": financial_data.price,
            "market_cap": financial_data.market_cap,
            "pe_ratio": financial_data.pe_ratio,
            "eps": financial_data.eps
        }

        # Add news sentiment
        sentiments = [n.sentiment for n in news]
        combined["sentiment"] = sum(sentiments) / len(sentiments) if sentiments else 0.0
        combined["recent_news"] = [n.title for n in news[:5]]

        return combined

    def resolve_conflicts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve conflicts based on source priority"""
        # For this mock, assume no conflicts
        return data

    def generate_insights(self, combined_data: Dict[str, Any]) -> str:
        """Generate insights from combined data"""
        insights = []

        metrics = combined_data.get("financial_metrics", {})
        if metrics.get("pe_ratio"):
            if metrics["pe_ratio"] > 25:
                insights.append("Stock appears overvalued based on P/E ratio")
            elif metrics["pe_ratio"] < 15:
                insights.append("Stock appears undervalued based on P/E ratio")

        sentiment = combined_data.get("sentiment", 0)
        if sentiment > 0.1:
            insights.append("Positive market sentiment")
        elif sentiment < -0.1:
            insights.append("Negative market sentiment")

        return " ".join(insights)

    def synthesize(self, sec_data: List[SECFiling],
                  financial_data: FinancialData,
                  news: List[NewsItem]) -> Dict[str, Any]:
        """Full synthesis process"""
        combined = self.combine_sources(sec_data, financial_data, news)
        resolved = self.resolve_conflicts(combined)
        resolved["insights"] = self.generate_insights(resolved)
        return resolved