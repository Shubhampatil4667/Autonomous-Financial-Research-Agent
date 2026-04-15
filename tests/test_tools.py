import pytest
from app.tools import create_tool_registry

def test_tool_registry_creation():
    registry = create_tool_registry()
    tools = registry.list_tools()
    assert len(tools) == 12
    assert "financial_data_api" in tools
    assert "report_generator" in tools

def test_financial_data_tool():
    registry = create_tool_registry()
    result = registry.call_tool("financial_data_api", symbol="AAPL")
    assert result.name == "financial_data_api"
    assert result.result is not None
    assert hasattr(result.result, 'symbol')

def test_calculation_engine():
    registry = create_tool_registry()
    result = registry.call_tool("calculation_engine", operation="mean", data=[1, 2, 3, 4, 5])
    assert result.name == "calculation_engine"
    assert result.result["result"] == 3.0

def test_fact_checker():
    registry = create_tool_registry()
    result = registry.call_tool("fact_checker", statement="Tesla makes cars", context="Tesla is an electric vehicle company")
    assert result.name == "fact_checker"
    assert "verified" in result.result

def test_vector_db_tools():
    registry = create_tool_registry()

    # Test store
    result = registry.call_tool("vector_db_store", texts=["test content"], metadatas=[{"type": "test"}])
    assert result.name == "vector_db_store"
    assert result.result == True

    # Test search
    result = registry.call_tool("vector_db_search", query="test", n_results=1)
    assert result.name == "vector_db_search"
    assert isinstance(result.result, list)