from typing import Dict, Any
from app.models.schemas import InvestmentReport

def report_generator(synthesis_data: Dict[str, Any]) -> InvestmentReport:
    """
    Generate structured investment report
    """
    return InvestmentReport(
        executive_summary=f"Analysis of {synthesis_data.get('company_info', {}).get('name', 'Company')}. Key metrics: P/E {synthesis_data.get('financial_metrics', {}).get('pe_ratio', 'N/A')}",
        company_overview=synthesis_data.get('company_info', {}).get('business_description', 'Company overview not available'),
        financial_analysis=f"Financial metrics: Market Cap ${synthesis_data.get('financial_metrics', {}).get('market_cap', 0):,.0f}, EPS ${synthesis_data.get('financial_metrics', {}).get('eps', 0):.2f}",
        risk_assessment="; ".join(synthesis_data.get('risks', ['No major risks identified'])),
        competitive_analysis=f"Market sentiment: {synthesis_data.get('sentiment', 0):.2f}. Recent news: {'; '.join(synthesis_data.get('recent_news', []))}",
        final_insight=synthesis_data.get('insights', 'Further analysis recommended')
    )