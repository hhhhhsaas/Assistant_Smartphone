"""
Configuration management
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""

    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    EMBEDDINGS_DIR = DATA_DIR / "embeddings"
    CHROMA_DB_DIR = DATA_DIR / "chroma_db"

    # Model settings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    # Alternative: "all-mpnet-base-v2" for better quality

    # Vector store settings
    VECTOR_STORE_NAME = "phones"
    SIMILARITY_METRIC = "cosine"

    # API settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))

    # Search settings
    DEFAULT_SEARCH_RESULTS = 5
    MAX_SEARCH_RESULTS = 20

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @classmethod
    def create_directories(cls):
        """Create required directories"""
        for dir_path in [cls.DATA_DIR, cls.RAW_DATA_DIR,
                          cls.PROCESSED_DATA_DIR, cls.EMBEDDINGS_DIR,
                          cls.CHROMA_DB_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)