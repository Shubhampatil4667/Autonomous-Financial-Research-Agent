from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class ToolInput(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class ToolOutput(BaseModel):
    name: str
    result: Any
    serialized_result: Any = None
    error: Optional[str] = None

class AgentAction(BaseModel):
    tool_name: str
    tool_input: Dict[str, Any]

class AgentStep(BaseModel):
    thought: str
    action: Optional[AgentAction] = None
    observation: Optional[str] = None

class ResearchQuery(BaseModel):
    query: str
    company: Optional[str] = None

class FinancialData(BaseModel):
    symbol: str
    price: float
    market_cap: float
    pe_ratio: Optional[float] = None
    eps: Optional[float] = None

class NewsItem(BaseModel):
    title: str
    content: str
    sentiment: float
    date: datetime

class SECFiling(BaseModel):
    type: str
    date: datetime
    content: str

class InvestmentReport(BaseModel):
    executive_summary: str
    company_overview: str
    financial_analysis: str
    risk_assessment: str
    competitive_analysis: str
    final_insight: str

class MemoryItem(BaseModel):
    query: str
    actions: List[AgentStep]
    timestamp: datetime