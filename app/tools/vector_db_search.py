from typing import List, Dict, Any

# Try to import vector store, fallback to mock if unavailable
try:
    from vector_db.vector_store import VectorStore
    VECTOR_STORE_AVAILABLE = True
except (ImportError, ValueError) as e:
    print(f"Vector store unavailable: {e}")
    VECTOR_STORE_AVAILABLE = False

def vector_db_search(query: str, n_results: int = 5) -> List[str]:
    """
    Search vector database
    """
    if not VECTOR_STORE_AVAILABLE:
        return [f"Mock result for query: {query}"] * min(n_results, 3)

    try:
        store = VectorStore()
        results = store.search(query, n_results)
        return [r["document"] for r in results]
    except Exception as e:
        print(f"Vector search failed: {e}")
        return [f"Fallback result for query: {query}"] * min(n_results, 3)