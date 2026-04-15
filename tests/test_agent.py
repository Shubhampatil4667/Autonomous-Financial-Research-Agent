import pytest
from app.agent.react_agent import ReActAgent
from app.agent.plan_execute_agent import PlanExecuteAgent
from app.tools import create_tool_registry

def test_tool_registry():
    registry = create_tool_registry()
    tools = registry.list_tools()
    assert len(tools) >= 10
    assert "financial_data_api" in tools

def test_react_agent_initialization():
    agent = ReActAgent()
    assert agent.max_iterations == 10

def test_plan_execute_agent():
    agent = PlanExecuteAgent()
    plan = agent.create_plan("Analyze Tesla")
    assert len(plan) > 0

def test_financial_data_tool():
    registry = create_tool_registry()
    result = registry.call_tool("financial_data_api", symbol="TSLA")
    assert result.name == "financial_data_api"
    assert result.result is not None