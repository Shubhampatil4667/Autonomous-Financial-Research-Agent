# Tools module
from .tool_registry import ToolRegistry
from .sec_filing_search import sec_filing_search
from .web_search import web_search
from .financial_data_api import financial_data_api
from .earnings_transcript import earnings_transcript
from .news_sentiment import news_sentiment
from .company_profile import company_profile
from .peer_comparison import peer_comparison
from .report_generator import report_generator
from .fact_checker import fact_checker
from .calculation_engine import calculation_engine

# Try to import vector DB tools, skip if ChromaDB unavailable
try:
    from .vector_db_search import vector_db_search
    from .vector_db_store import vector_db_store
    VECTOR_TOOLS_AVAILABLE = True
except (ImportError, ValueError) as e:
    print(f"Vector database tools unavailable: {e}")
    VECTOR_TOOLS_AVAILABLE = False
    vector_db_search = None
    vector_db_store = None

# Global tool registry instance for reuse
_tool_registry = None

def get_tool_registry() -> ToolRegistry:
    """Get or create the global tool registry instance"""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = create_tool_registry()
    return _tool_registry

def create_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()

    # Register all tools
    registry.register_tool(
        name="sec_filing_search",
        description="Search SEC filings for company information",
        input_schema={"company": "str", "filing_type": "str"},
        output_schema={"filings": "list[SECFiling]"},
        function=sec_filing_search
    )

    registry.register_tool(
        name="web_search",
        description="Search the web for information",
        input_schema={"query": "str", "num_results": "int"},
        output_schema={"results": "list[dict]"},
        function=web_search
    )

    registry.register_tool(
        name="financial_data_api",
        description="Get financial data for a stock symbol",
        input_schema={"symbol": "str"},
        output_schema={"data": "FinancialData"},
        function=financial_data_api
    )

    registry.register_tool(
        name="earnings_transcript",
        description="Get earnings call transcripts",
        input_schema={"company": "str", "quarters": "int"},
        output_schema={"transcripts": "list[dict]"},
        function=earnings_transcript
    )

    registry.register_tool(
        name="news_sentiment",
        description="Analyze sentiment of news articles",
        input_schema={"news_articles": "list[str]"},
        output_schema={"sentiment_analysis": "list[NewsItem]"},
        function=news_sentiment
    )

    # Only register vector tools if available
    if VECTOR_TOOLS_AVAILABLE:
        registry.register_tool(
            name="vector_db_search",
            description="Search vector database for similar content",
            input_schema={"query": "str", "n_results": "int"},
            output_schema={"results": "list[str]"},
            function=vector_db_search
        )

        registry.register_tool(
            name="vector_db_store",
            description="Store content in vector database",
            input_schema={"texts": "list[str]", "metadatas": "list[dict]"},
            output_schema={"success": "bool"},
            function=vector_db_store
        )

    registry.register_tool(
        name="company_profile",
        description="Get company profile information",
        input_schema={"symbol": "str"},
        output_schema={"profile": "dict"},
        function=company_profile
    )

    registry.register_tool(
        name="peer_comparison",
        description="Compare company with industry peers",
        input_schema={"symbol": "str", "peers": "list[str]"},
        output_schema={"comparison": "dict"},
        function=peer_comparison
    )

    registry.register_tool(
        name="report_generator",
        description="Generate structured investment report",
        input_schema={"synthesis_data": "dict"},
        output_schema={"report": "InvestmentReport"},
        function=report_generator
    )

    registry.register_tool(
        name="fact_checker",
        description="Verify facts against context",
        input_schema={"statement": "str", "context": "str"},
        output_schema={"verification": "dict"},
        function=fact_checker
    )

    registry.register_tool(
        name="calculation_engine",
        description="Perform financial calculations",
        input_schema={"operation": "str", "data": "list[float]"},
        output_schema={"result": "dict"},
        function=calculation_engine
    )

    return registry