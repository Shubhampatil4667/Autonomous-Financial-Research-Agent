import pytest
from app.services.memory_service import MemoryService
from app.services.synthesis_engine import SynthesisEngine
from app.services.rag_pipeline import RAGPipeline
from app.services.cache_service import CacheService
from app.models.schemas import SECFiling, FinancialData, NewsItem
from datetime import datetime

def test_memory_service():
    memory = MemoryService()

    # Test short-term memory
    assert len(memory.short_term_memory) == 0
    memory.add_to_short_term(type('MockStep', (), {'thought': 'test', 'action': None, 'observation': None})())
    assert len(memory.short_term_memory) == 1

    # Test episodic memory
    memory.store_episodic("test query", [])
    assert len(memory.episodic_memory) == 1

def test_synthesis_engine():
    engine = SynthesisEngine()

    sec_data = [SECFiling(type="10-K", date=datetime.now(), content="Revenue $100B")]
    financial_data = FinancialData(symbol="TSLA", price=250, market_cap=500e9, pe_ratio=30, eps=8)
    news = [NewsItem(title="Good news", content="Positive", sentiment=0.8, date=datetime.now())]

    result = engine.synthesize(sec_data, financial_data, news)
    assert "company_info" in result
    assert "financial_metrics" in result
    assert "insights" in result

def test_rag_pipeline():
    memory = MemoryService()
    rag = RAGPipeline(memory)

    # Test query transformation
    transformed = rag.transform_query("Tesla stock")
    assert "financial analysis" in transformed

    # Test pipeline run (mock)
    result = rag.run_pipeline("Tesla analysis")
    assert isinstance(result, str)

def test_cache_service():
    cache = CacheService(cache_dir="./test_cache", ttl_hours=1)

    # Test set and get
    cache.set("test_key", {"data": "value"})
    result = cache.get("test_key")
    assert result == {"data": "value"}

    # Test cache miss
    result = cache.get("nonexistent")
    assert result is None

    # Cleanup
    cache.clear()