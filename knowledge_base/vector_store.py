"""
Vector Store - Smart selection between ChromaDB and simple in-memory store
"""

import logging
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from knowledge_base.phone_facts import PhoneFacts

logger = logging.getLogger(__name__)

# Try to import ChromaDB
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
    logger.info("ChromaDB is available")
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("ChromaDB not available, using PhoneFacts-based store")

if CHROMADB_AVAILABLE:
    class VectorStore:
        """
        Manages vector database for phone specifications using ChromaDB
        """
        def __init__(self, persist_directory: str = "./data/chroma_db"):
            self.persist_directory = Path(persist_directory)
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=Settings(anonymized_telemetry=False, allow_reset=True)
            )
            self.collection = self.client.get_or_create_collection(
                name="phones", metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Initialized ChromaDB vector store at {persist_directory}")

        def add_phones(self, phones: List[Dict[str, Any]], embeddings: List[List[float]], ids: Optional[List[str]] = None) -> None:
            if ids is None:
                ids = [f"phone_{i}" for i in range(len(phones))]
            metadatas = [{"name": p.get("name",""), "brand": p.get("brand",""), "price": str(p.get("price",0)), "category": p.get("category",""), "full_data": json.dumps(p, ensure_ascii=False)} for p in phones]
            documents = [" | ".join(f"{k}: {', '.join(map(str,v)) if isinstance(v,list) else v}" for k,v in p.items() if isinstance(v,(str,int,float,list))) for p in phones]
            self.collection.add(embeddings=embeddings, documents=documents, metadatas=metadatas, ids=ids)
            logger.info(f"Added {len(phones)} phones to vector store")

        def search(self, query_embedding: List[float], n_results: int = 5, filter_dict: Optional[Dict] = None) -> Dict:
            where_clause = {k: {"$eq": str(v)} if not isinstance(v, dict) else v for k,v in (filter_dict or {}).items()} or None
            results = self.collection.query(query_embeddings=[query_embedding], n_results=n_results, where=where_clause)
            parsed = [{'id': results['ids'][0][i], 'score': 1 - results['distances'][0][i], 'data': json.loads(results['metadatas'][0][i]['full_data'])} for i in range(len(results['ids'][0]))] if results['ids'] and len(results['ids'][0]) > 0 else []
            return {'results': parsed, 'total': len(parsed)}

        def search_by_criteria(self, criteria: Dict[str, Any], n_results: int = 10) -> List[Dict]:
            where = {}
            if 'brand' in criteria: where['brand'] = {"$eq": criteria['brand']}
            if 'min_price' in criteria and 'max_price' in criteria: where['price'] = {"$gte": str(criteria['min_price']), "$lte": str(criteria['max_price'])}
            if 'category' in criteria: where['category'] = {"$eq": criteria['category']}
            results = self.collection.get(where=where if where else None, limit=n_results)
            return [json.loads(m['full_data']) for m in results['metadatas']] if results['ids'] else []

        def get_by_id(self, phone_id: str) -> Optional[Dict]:
            results = self.collection.get(ids=[phone_id])
            return json.loads(results['metadatas'][0]['full_data']) if results['ids'] else None

        def clear_all(self) -> None:
            self.client.delete_collection("phones")
            self.collection = self.client.create_collection(name="phones", metadata={"hnsw:space": "cosine"})

        def get_stats(self) -> Dict:
            return {"total_phones": self.collection.count(), "collection_name": "phones", "persist_directory": str(self.persist_directory)}
else:
    class VectorStore:
        """
        Simple in-memory vector store using PhoneFacts
        """
        def __init__(self, persist_path: str = "./data/cellphones_vector_store.pkl"):
            self.persist_path = Path(persist_path)
            self.facts = PhoneFacts(persist_path)

        def search_by_criteria(self, criteria: Dict[str, Any], n_results: int = 10) -> List[Dict]:
            return self.facts.search_by_criteria(criteria, n_results)

        def get_by_id(self, phone_id: str) -> Optional[Dict]:
            return self.facts.get_by_id(phone_id)

        def get_all_phones(self) -> List[Dict]:
            return self.facts.get_all()

        def get_stats(self) -> Dict:
            return self.facts.get_stats()
