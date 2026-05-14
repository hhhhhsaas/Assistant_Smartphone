"""
Embedding Model for converting text to vectors
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import logging

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """
    Manages text embeddings using Sentence Transformers
    """

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize embedding model

        Args:
            model_name: Name of the sentence transformer model
                       Default: 'all-MiniLM-L6-v2' (fast and efficient)
                       Alternative: 'all-mpnet-base-v2' (better quality)
        """
        try:
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Loaded embedding model: {model_name}")
            logger.info(f"Embedding dimension: {self.embedding_dim}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

    def encode(self, texts: Union[str, List[str]],
               batch_size: int = 32,
               show_progress: bool = False) -> np.ndarray:
        """
        Convert text(s) to embeddings

        Args:
            texts: Single text or list of texts
            batch_size: Batch size for encoding
            show_progress: Show progress bar

        Returns:
            Numpy array of embeddings
        """
        if isinstance(texts, str):
            texts = [texts]

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )

        return embeddings

    def encode_phone_specs(self, phone_data: dict) -> np.ndarray:
        """
        Create embedding for phone specifications

        Args:
            phone_data: Dictionary containing phone specs

        Returns:
            Embedding vector
        """
        # Format phone specs into searchable text
        text_parts = []

        # Basic info
        if 'name' in phone_data:
            text_parts.append(f"Tên: {phone_data['name']}")
        if 'brand' in phone_data:
            text_parts.append(f"Hãng: {phone_data['brand']}")
        if 'price' in phone_data:
            text_parts.append(f"Giá: {phone_data['price']}")

        # Technical specs
        if 'screen_size' in phone_data:
            text_parts.append(f"Màn hình: {phone_data['screen_size']}")
        if 'ram' in phone_data:
            text_parts.append(f"RAM: {phone_data['ram']}")
        if 'storage' in phone_data:
            text_parts.append(f"Bộ nhớ: {phone_data['storage']}")
        if 'battery' in phone_data:
            text_parts.append(f"Pin: {phone_data['battery']}")
        if 'camera' in phone_data:
            text_parts.append(f"Camera: {phone_data['camera']}")
        if 'processor' in phone_data:
            text_parts.append(f"Chip: {phone_data['processor']}")

        # Features
        if 'features' in phone_data and isinstance(phone_data['features'], list):
            text_parts.append(f"Tính năng: {', '.join(phone_data['features'])}")

        # Combine all parts
        full_text = ". ".join(text_parts)

        return self.encode(full_text)

    def similarity(self, embedding1: np.ndarray,
                   embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score (0-1)
        """
        # Normalize vectors
        norm1 = embedding1 / np.linalg.norm(embedding1)
        norm2 = embedding2 / np.linalg.norm(embedding2)

        # Calculate cosine similarity
        similarity = np.dot(norm1, norm2)

        return float(similarity)