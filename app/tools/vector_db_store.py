from typing import List, Dict, Any

# Try to import vector store, fallback to mock if unavailable
try:
    from vector_db.vector_store import VectorStore
    VECTOR_STORE_AVAILABLE = True
except (ImportError, ValueError) as e:
    print(f"Vector store unavailable: {e}")
    VECTOR_STORE_AVAILABLE = False

def vector_db_store(texts: List[str], metadatas: List[Dict[str, Any]] = None) -> bool:
    """
    Store texts in vector database
    """
    if not VECTOR_STORE_AVAILABLE:
        print(f"Mock storing {len(texts)} texts (vector store unavailable)")
        return True

    try:
        store = VectorStore()
        store.store(texts, metadatas)
        return True
    except Exception as e:
        print(f"Vector storage failed: {e}")
        return False