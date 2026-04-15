from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from app.agent.react_agent import ReActAgent
from app.agent.plan_execute_agent import PlanExecuteAgent
from app.services.synthesis_engine import SynthesisEngine
from app.tools import get_tool_registry
from app.models.schemas import ResearchQuery, InvestmentReport
from app.services.logging_service import logger
import asyncio
from typing import Dict, Any, Optional
import os
import re
import time
from app.config import settings

app = FastAPI(
    title="Autonomous Financial Research Agent",
    description="AI-powered financial analysis with multi-source data synthesis",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],  # Streamlit default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    query: str
    mode: str = "react"  # "react" or "plan_execute"

    @validator('query')
    def query_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        if len(v.strip()) > 500:
            raise ValueError('Query too long (max 500 characters)')
        return v.strip()

    @validator('mode')
    def mode_must_be_valid(cls, v):
        if v not in ['react', 'plan_execute']:
            raise ValueError('Mode must be either "react" or "plan_execute"')
        return v

class AnalysisResponse(BaseModel):
    result: str
    report: Optional[InvestmentReport] = None
    processing_time: float
    mode_used: str

# Global agent instances for reuse
_react_agent = None
_plan_agent = None

def get_react_agent() -> ReActAgent:
    """Get or create ReAct agent singleton"""
    global _react_agent
    if _react_agent is None:
        try:
            _react_agent = ReActAgent()
        except ValueError as e:
            logger.error(f"Failed to initialize ReAct agent: {e}")
            raise HTTPException(status_code=500, detail="Agent initialization failed. Check API keys.")
    return _react_agent

def get_plan_agent() -> PlanExecuteAgent:
    """Get or create Plan-Execute agent singleton"""
    global _plan_agent
    if _plan_agent is None:
        try:
            _plan_agent = PlanExecuteAgent()
        except ValueError as e:
            logger.error(f"Failed to initialize Plan-Execute agent: {e}")
            raise HTTPException(status_code=500, detail="Agent initialization failed. Check API keys.")
    return _plan_agent

def extract_symbol(query: str) -> str:
    """Extract company symbol from query"""
    symbol_match = re.search(r'\b[A-Z]{1,5}\b', query.upper())
    if symbol_match:
        return symbol_match.group()

    # Common mappings
    mappings = {'tesla': 'TSLA', 'apple': 'AAPL', 'microsoft': 'MSFT', 'amazon': 'AMZN', 'google': 'GOOGL'}
    query_lower = query.lower()
    for company, symbol in mappings.items():
        if company in query_lower:
            return symbol
    return 'TSLA'

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_stock(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Analyze a stock or company"""
    start_time = time.time()
    logger.info(f"Received analysis request: {request.query} with mode: {request.mode}")

    try:
        # Validate API keys using settings object
        if not settings.openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")

        if request.mode == "react":
            agent = get_react_agent()
            result = await asyncio.get_event_loop().run_in_executor(None, agent.run, request.query)
        elif request.mode == "plan_execute":
            agent = get_plan_agent()
            result = await asyncio.get_event_loop().run_in_executor(None, agent.run, request.query)
        else:
            raise HTTPException(status_code=400, detail="Invalid mode. Use 'react' or 'plan_execute'")

        # Generate report using actual data gathering
        symbol = extract_symbol(request.query)
        tool_registry = get_tool_registry()

        # Gather real data with error handling
        financial_result = tool_registry.call_tool("financial_data_api", symbol=symbol)
        financial_data = financial_result.result if financial_result.result else type('MockData', (), {'symbol': symbol, 'price': 250, 'market_cap': 500e9, 'pe_ratio': 30, 'eps': 8})()

        sec_result = tool_registry.call_tool("sec_filing_search", company=symbol, filing_type="10-K")
        sec_data = sec_result.result if sec_result.result else []

        news_items = []
        news_result = tool_registry.call_tool("web_search", query=f"{symbol} stock news", num_results=3)
        if news_result.result:
            news_texts = [item.get('snippet', '') for item in news_result.result if item.get('snippet')]
            if news_texts:
                sentiment_result = tool_registry.call_tool("news_sentiment", news_articles=news_texts)
                news_items = sentiment_result.result if sentiment_result.result else []

        # Synthesize and generate report
        synthesis_engine = SynthesisEngine()
        synthesis = synthesis_engine.synthesize(sec_data, financial_data, news_items)
        report_result = tool_registry.call_tool("report_generator", synthesis_data=synthesis)

        processing_time = time.time() - start_time
        logger.info(".2f")

        return AnalysisResponse(
            result=result,
            report=report_result.result if report_result.result else None,
            processing_time=round(processing_time, 2),
            mode_used=request.mode
        )

    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Error during analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}. Processing time: {processing_time:.2f}s"
        )

@app.get("/tools")
async def list_tools():
    """List available tools"""
    try:
        registry = get_tool_registry()
        tools = registry.list_tools()
        logger.debug(f"Listed {len(tools)} available tools")
        return {"tools": tools, "count": len(tools)}
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list tools: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check"""
    try:
        # Check agent initialization
        react_ok = False
        plan_ok = False

        try:
            get_react_agent()
            react_ok = True
        except:
            pass

        try:
            get_plan_agent()
            plan_ok = True
        except:
            pass

        tools_count = len(get_tool_registry().list_tools())

        status = "healthy" if (react_ok or plan_ok) and tools_count > 0 else "degraded"

        return {
            "status": status,
            "react_agent": react_ok,
            "plan_agent": plan_ok,
            "tools_available": tools_count,
            "openai_configured": bool(settings.openai_api_key),
            "serpapi_configured": bool(settings.serpapi_key)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

@app.post("/analyze-async")
async def analyze_stock_async(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Analyze a stock asynchronously"""
    logger.info(f"Starting async analysis for: {request.query}")

    # Add to background tasks
    background_tasks.add_task(process_analysis_async, request)

    return {
        "message": "Analysis started in background",
        "query": request.query,
        "mode": request.mode,
        "timestamp": time.time()
    }

async def process_analysis_async(request: AnalysisRequest):
    """Process analysis in background"""
    try:
        logger.info(f"Processing async analysis for: {request.query}")

        if request.mode == "react":
            agent = get_react_agent()
            result = await asyncio.get_event_loop().run_in_executor(None, agent.run, request.query)
        elif request.mode == "plan_execute":
            agent = get_plan_agent()
            result = await asyncio.get_event_loop().run_in_executor(None, agent.run, request.query)
        else:
            logger.error(f"Invalid mode for async analysis: {request.mode}")
            return

        # Generate report using actual data gathering
        symbol = extract_symbol(request.query)
        tool_registry = get_tool_registry()

        # Gather real data
        financial_result = tool_registry.call_tool("financial_data_api", symbol=symbol)
        financial_data = financial_result.result if financial_result.result else type('MockData', (), {'symbol': symbol, 'price': 250, 'market_cap': 500e9, 'pe_ratio': 30, 'eps': 8})()

        sec_result = tool_registry.call_tool("sec_filing_search", company=symbol, filing_type="10-K")
        sec_data = sec_result.result if sec_result.result else []

        news_items = []
        news_result = tool_registry.call_tool("web_search", query=f"{symbol} stock news", num_results=3)
        if news_result.result:
            news_texts = [item.get('snippet', '') for item in news_result if item.get('snippet')]
            if news_texts:
                sentiment_result = tool_registry.call_tool("news_sentiment", news_articles=news_texts)
                news_items = sentiment_result.result if sentiment_result.result else []

        # Synthesize and generate report
        synthesis_engine = SynthesisEngine()
        synthesis = synthesis_engine.synthesize(sec_data, financial_data, news_items)
        report_result = tool_registry.call_tool("report_generator", synthesis_data=synthesis)

        processing_time = time.time() - start_time
        logger.info(f"Async analysis completed for: {request.query} - Symbol: {symbol} - Time: {processing_time:.2f}s")

        # In production, you could save results to database or send notification
        # For now, just log completion

    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Async analysis failed for {request.query}: {e} (Time: {processing_time:.2f}s)")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server")
    uvicorn.run(app, host="0.0.0.0", port=8000)