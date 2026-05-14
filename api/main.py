"""
FastAPI application for Phone Assistant Knowledge Base
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from knowledge_base import VectorStore, EmbeddingModel, PhoneRetriever, DataIndexer
from utils.config import Config

# Setup logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Phone Assistant API",
    description="AI-powered phone consultation system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Knowledge Base components
embedding_model = None
vector_store = None
retriever = None
indexer = None


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global embedding_model, vector_store, retriever, indexer

    Config.create_directories()

    logger.info("Initializing Knowledge Base components...")
    embedding_model = EmbeddingModel(Config.EMBEDDING_MODEL)
    vector_store = VectorStore(str(Config.CHROMA_DB_DIR))
    retriever = PhoneRetriever(vector_store, embedding_model)
    indexer = DataIndexer(vector_store, embedding_model)

    # Index sample data if vector store is empty
    if vector_store.get_stats()['total_phones'] == 0:
        sample_file = Config.DATA_DIR / "sample_phones.json"
        if sample_file.exists():
            logger.info("Indexing sample data...")
            indexer.index_from_json(str(sample_file))

    logger.info("Knowledge Base ready!")


# Pydantic models for request/response
class SearchQuery(BaseModel):
    query: str = Field(..., description="Search query in natural language")
    n_results: int = Field(5, description="Number of results to return")
    filters: Optional[Dict[str, Any]] = Field(None, description="Optional filters")


class RequirementsQuery(BaseModel):
    purpose: Optional[str] = Field(None, description="Use case: gaming, photography, business, student, general")
    budget_min: Optional[int] = Field(None, description="Minimum budget in VND")
    budget_max: Optional[int] = Field(None, description="Maximum budget in VND")
    brand_preference: Optional[List[str]] = Field(None, description="Preferred brands")
    features: Optional[List[str]] = Field(None, description="Required features")
    n_results: int = Field(10, description="Number of results")


class CompareRequest(BaseModel):
    phone_ids: List[str] = Field(..., description="List of phone IDs to compare")


class PhoneData(BaseModel):
    name: str
    brand: str
    price: float
    category: Optional[str] = "smartphone"
    screen_size: Optional[str] = None
    ram: Optional[str] = None
    storage: Optional[str] = None
    battery: Optional[str] = None
    camera: Optional[str] = None
    processor: Optional[str] = None
    features: Optional[List[str]] = None
    os: Optional[str] = None


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Phone Assistant API",
        "endpoints": {
            "search": "/api/search",
            "recommend": "/api/recommend",
            "compare": "/api/compare",
            "phone": "/api/phone/{phone_id}",
            "stats": "/api/stats"
        }
    }


@app.post("/api/search")
async def search_phones(query: SearchQuery):
    """
    Search for phones using natural language query
    """
    try:
        results = retriever.retrieve_by_query(
            query.query,
            query.n_results,
            query.filters
        )

        return {
            "success": True,
            "query": query.query,
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/recommend")
async def recommend_phones(requirements: RequirementsQuery):
    """
    Get phone recommendations based on requirements
    """
    try:
        # Build requirements dict
        req_dict = {}

        if requirements.purpose:
            req_dict['purpose'] = requirements.purpose

        if requirements.budget_min or requirements.budget_max:
            req_dict['budget'] = {}
            if requirements.budget_min:
                req_dict['budget']['min'] = requirements.budget_min
            if requirements.budget_max:
                req_dict['budget']['max'] = requirements.budget_max

        if requirements.brand_preference:
            req_dict['brand_preference'] = requirements.brand_preference

        if requirements.features:
            req_dict['features'] = requirements.features

        results = retriever.retrieve_by_requirements(
            req_dict,
            requirements.n_results
        )

        return {
            "success": True,
            "requirements": req_dict,
            "recommendations": results,
            "total": len(results)
        }
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/phone/{phone_id}")
async def get_phone(phone_id: str):
    """
    Get phone details by ID
    """
    try:
        phone = vector_store.get_by_id(phone_id)

        if not phone:
            raise HTTPException(status_code=404, detail="Phone not found")

        return {
            "success": True,
            "phone_id": phone_id,
            "data": phone
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get phone error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/similar/{phone_id}")
async def get_similar_phones(
    phone_id: str,
    n_results: int = Query(5, description="Number of similar phones")
):
    """
    Find phones similar to a given phone
    """
    try:
        similar = retriever.retrieve_similar_phones(phone_id, n_results)

        if not similar:
            raise HTTPException(status_code=404, detail="Phone not found")

        return {
            "success": True,
            "reference_phone_id": phone_id,
            "similar_phones": similar,
            "total": len(similar)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Similar phones error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/compare")
async def compare_phones(request: CompareRequest):
    """
    Compare multiple phones
    """
    try:
        comparison = retriever.retrieve_by_comparison(request.phone_ids)

        if not comparison['phones']:
            raise HTTPException(status_code=404, detail="No phones found")

        return {
            "success": True,
            "comparison": comparison
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Comparison error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/price-range")
async def get_phones_by_price(
    min_price: int = Query(..., description="Minimum price in VND"),
    max_price: int = Query(..., description="Maximum price in VND"),
    n_results: int = Query(10, description="Number of results")
):
    """
    Get phones within a price range
    """
    try:
        phones = retriever.retrieve_by_price_range(
            min_price,
            max_price,
            n_results
        )

        return {
            "success": True,
            "price_range": {
                "min": min_price,
                "max": max_price
            },
            "phones": phones,
            "total": len(phones)
        }
    except Exception as e:
        logger.error(f"Price range error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/index/phone")
async def index_phone(phone_data: PhoneData):
    """
    Add a new phone to the knowledge base
    """
    try:
        phone_dict = phone_data.dict()
        phone_id = indexer.index_single_phone(phone_dict)

        return {
            "success": True,
            "message": "Phone indexed successfully",
            "phone_id": phone_id
        }
    except Exception as e:
        logger.error(f"Index phone error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats():
    """
    Get knowledge base statistics
    """
    try:
        stats = vector_store.get_stats()

        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trending")
async def get_trending(
    n_results: int = Query(10, description="Number of results")
):
    """
    Get trending phones
    """
    try:
        trending = retriever.retrieve_trending(n_results)

        return {
            "success": True,
            "trending": trending,
            "total": len(trending)
        }
    except Exception as e:
        logger.error(f"Trending error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=True
    )