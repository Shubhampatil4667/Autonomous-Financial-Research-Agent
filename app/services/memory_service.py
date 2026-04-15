from typing import List, Dict, Any
from datetime import datetime
from app.models.schemas import MemoryItem, AgentStep
from vector_db.vector_store import VectorStore
from .logging_service import logger
from .cache_service import CacheService

class MemoryService:
    def __init__(self):
        self.vector_store = VectorStore()
        self.short_term_memory: List[AgentStep] = []
        self.episodic_memory: List[MemoryItem] = []
        self.cache = CacheService()
        logger.info("MemoryService initialized")

    def add_to_short_term(self, step: AgentStep):
        """Add step to short-term memory"""
        self.short_term_memory.append(step)
        # Keep only last 10 steps
        if len(self.short_term_memory) > 10:
            self.short_term_memory.pop(0)
        logger.debug(f"Added step to short-term memory. Total steps: {len(self.short_term_memory)}")

    def get_short_term_context(self) -> str:
        """Get short-term context as string"""
        context = "\n".join([f"Thought: {s.thought}\nAction: {s.action.tool_name if s.action else 'None'}\nObservation: {s.observation or 'None'}" for s in self.short_term_memory])
        logger.debug(f"Retrieved short-term context with {len(self.short_term_memory)} steps")
        return context

    def store_episodic(self, query: str, actions: List[AgentStep]):
        """Store in episodic memory"""
        memory_item = MemoryItem(
            query=query,
            actions=actions,
            timestamp=datetime.now()
        )
        self.episodic_memory.append(memory_item)
        # Store in vector DB for retrieval
        text = f"Query: {query}\nActions: {[a.thought for a in actions]}"
        self.vector_store.store([text], [{"type": "episodic", "timestamp": str(memory_item.timestamp)}])
        logger.info(f"Stored episodic memory for query: {query}")

    def retrieve_episodic(self, query: str) -> List[MemoryItem]:
        """Retrieve similar past experiences"""
        # Check cache first
        cache_key = f"episodic_{query}"
        cached = self.cache.get(cache_key)
        if cached:
            logger.debug("Retrieved episodic memory from cache")
            return cached

        results = self.vector_store.search(query, n_results=3)
        # For simplicity, return recent episodic memories
        result = self.episodic_memory[-3:] if self.episodic_memory else []
        self.cache.set(cache_key, result)
        logger.debug(f"Retrieved {len(result)} episodic memories")
        return result

    def store_long_term(self, content: str, metadata: Dict[str, Any]):
        """Store in long-term memory (vector DB)"""
        self.vector_store.store([content], [metadata])
        logger.info("Stored content in long-term memory")

    def retrieve_long_term(self, query: str, n_results: int = 5) -> List[str]:
        """Retrieve from long-term memory"""
        cache_key = f"long_term_{query}_{n_results}"
        cached = self.cache.get(cache_key)
        if cached:
            logger.debug("Retrieved long-term memory from cache")
            return cached

        results = self.vector_store.search(query, n_results)
        result = [r["document"] for r in results]
        self.cache.set(cache_key, result)
        logger.debug(f"Retrieved {len(result)} long-term memories")
        return result