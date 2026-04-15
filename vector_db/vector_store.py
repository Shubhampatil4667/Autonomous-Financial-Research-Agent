# Try to import chromadb, fallback gracefully if unavailable
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except Exception as e:
    print(f"ChromaDB not available: {e}")
    CHROMADB_AVAILABLE = False
    chromadb = None

import os
from typing import List, Dict, Any
import hashlib

class VectorStore:
    def __init__(self, persist_directory: str = "./vector_db/data"):
        os.makedirs(persist_directory, exist_ok=True)

        if not CHROMADB_AVAILABLE:
            self.client = None
            self.collection = None
            return

        try:
            # Try to use default embedding function
            self.client = chromadb.PersistentClient(path=persist_directory)
            self.collection = self.client.get_or_create_collection(name="financial_research")
        except Exception as e:
            print(f"ChromaDB initialization error: {e}")
            # Fallback: create client without default embedding
            from chromadb.utils import embedding_functions
            try:
                # Try with a simple embedding function
                embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
                self.client = chromadb.PersistentClient(path=persist_directory)
                self.collection = self.client.get_or_create_collection(
                    name="financial_research",
                    embedding_function=embedding_function
                )
            except Exception as e2:
                print(f"Fallback embedding function failed: {e2}")
                # Last resort: disable vector store
                self.client = None
                self.collection = None

    def _get_id(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()

    def store(self, texts: List[str], metadatas: List[Dict[str, Any]] = None):
        """Store texts with optional metadata"""
        if self.collection is None:
            print("Vector store not available - skipping storage")
            return

        ids = [self._get_id(text) for text in texts]
        if metadatas is None:
            metadatas = [{}] * len(texts)
        try:
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
        except Exception as e:
            print(f"Vector storage error: {e}")

    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar texts"""
        if self.collection is None:
            print("Vector store not available - returning empty results")
            return []

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            return [
                {
                    "document": doc,
                    "metadata": meta,
                    "distance": dist
                }
                for doc, meta, dist in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                )
            ]
        except Exception as e:
            print(f"Vector search error: {e}")
            return []

    def delete(self, text: str):
        """Delete a specific text"""
        if self.collection is None:
            return

        try:
            doc_id = self._get_id(text)
            self.collection.delete(ids=[doc_id])
        except Exception as e:
            print(f"Vector delete error: {e}")