import openai
import os
import re
from typing import List, Dict, Any, Optional
from app.models.schemas import AgentStep, AgentAction
from app.services.memory_service import MemoryService
from app.tools import get_tool_registry
from app.services.logging_service import logger
from app.config import settings

class PlanExecuteAgent:
    def __init__(self):
        self.memory = MemoryService()
        self.tool_registry = get_tool_registry()  # Use global instance

        # Validate API key
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        # Initialize sync client
        from openai import OpenAI
        self.client = OpenAI(api_key=settings.openai_api_key)

        logger.info("PlanExecuteAgent initialized")

    def _extract_company_symbol(self, query: str) -> str:
        """Extract company symbol from query using regex and common patterns"""
        # Look for stock symbols (uppercase letters, 1-5 chars)
        symbol_match = re.search(r'\b[A-Z]{1,5}\b', query.upper())
        if symbol_match:
            return symbol_match.group()

        # Common company name to symbol mapping
        company_mappings = {
            'tesla': 'TSLA',
            'apple': 'AAPL',
            'microsoft': 'MSFT',
            'amazon': 'AMZN',
            'google': 'GOOGL',
            'nvidia': 'NVDA',
            'meta': 'META',
            'netflix': 'NFLX'
        }

        query_lower = query.lower()
        for company, symbol in company_mappings.items():
            if company in query_lower:
                return symbol

        # Default fallback
        return 'TSLA'

    def create_plan(self, query: str) -> List[str]:
        """Create execution plan with optimized parameters"""
        symbol = self._extract_company_symbol(query)

        prompt = f"""
Create a step-by-step plan to analyze: {query}

Extracted company symbol: {symbol}
Available tools: {self.tool_registry.get_tool_descriptions()}

Return a numbered list of steps, each specifying which tool to use and why.
Be specific about parameters, especially the company symbol '{symbol}'.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
                timeout=30  # Add timeout for API calls
            )
            plan_text = response.choices[0].message.content.strip()
            plan = [step.strip() for step in plan_text.split('\n') if step.strip() and step.strip()[0].isdigit()]
            logger.info(f"Created plan with {len(plan)} steps")
            return plan
        except Exception as e:
            logger.error(f"Error creating plan: {e}")
            from openai import APIError, RateLimitError, APITimeoutError
            if isinstance(e, (APITimeoutError, RateLimitError)):
                logger.warning(f"OpenAI API issue ({type(e).__name__}), using fallback plan")
            
            # Improved fallback plan
            return self._get_fallback_plan(symbol)

    def _get_fallback_plan(self, symbol: str) -> List[str]:
        """Fallback plan when API fails"""
        return [
            f"1. Get financial data using financial_data_api for symbol {symbol}",
            f"2. Search SEC filings using sec_filing_search for {symbol}",
            f"3. Analyze news sentiment using web_search for {symbol} news",
            "4. Generate report using report_generator"
        ]

    def execute_plan(self, plan: List[str], symbol: str) -> str:
        """Execute the plan with optimized parameters"""
        results = []

        for step in plan:
            logger.info(f"Executing step: {step}")
            try:
                if "financial_data_api" in step:
                    result = self.tool_registry.call_tool("financial_data_api", symbol=symbol)
                elif "sec_filing_search" in step:
                    result = self.tool_registry.call_tool("sec_filing_search", company=symbol, filing_type="10-K")
                elif "web_search" in step:
                    result = self.tool_registry.call_tool("web_search", query=f"{symbol} stock news", num_results=settings.max_search_results)
                elif "news_sentiment" in step:
                    # Get news first, then analyze sentiment
                    news_result = self.tool_registry.call_tool("web_search", query=f"{symbol} stock news", num_results=settings.max_search_results)
                    if news_result.result:
                        news_texts = [item.get('snippet', '') for item in news_result.result if item.get('snippet')]
                        if news_texts:
                            result = self.tool_registry.call_tool("news_sentiment", news_articles=news_texts)
                        else:
                            result = type('MockResult', (), {'result': []})()
                    else:
                        result = type('MockResult', (), {'result': []})()
                elif "report_generator" in step:
                    # Mock synthesis data - in production this would use gathered data
                    synthesis_data = {
                        "company_info": {"name": f"{symbol} Corporation"},
                        "financial_metrics": {"pe_ratio": 25.0, "market_cap": 100000000000},
                        "sentiment": 0.1,
                        "recent_news": ["Recent developments"],
                        "insights": f"{symbol} shows moderate growth potential"
                    }
                    result = self.tool_registry.call_tool("report_generator", synthesis_data=synthesis_data)
                else:
                    result = self.tool_registry.call_tool("web_search", query=f"{symbol} financial analysis")

                output_data = result.serialized_result if getattr(result, 'serialized_result', None) is not None else result.result
                results.append(f"Step: {step}\nResult: {output_data if output_data else 'No result'}")
                logger.debug(f"Step completed: {step[:50]}...")

            except Exception as e:
                logger.error(f"Error executing step '{step}': {e}")
                results.append(f"Step: {step}\nError: {str(e)}")

        return "\n\n".join(results)

    def run(self, query: str) -> str:
        """Run plan-and-execute"""
        logger.info(f"Starting plan-and-execute analysis for: {query}")
        symbol = self._extract_company_symbol(query)
        plan = self.create_plan(query)
        result = self.execute_plan(plan, symbol)
        self.memory.store_episodic(query, [])  # Store plan
        logger.info("Plan-and-execute analysis completed")
        return result