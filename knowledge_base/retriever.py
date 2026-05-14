"""
Retriever module for finding relevant phone information
"""

from typing import List, Dict, Any, Optional
import logging
from .embeddings import EmbeddingModel
from .vector_store import VectorStore

logger = logging.getLogger(__name__)


class PhoneRetriever:
    """
    Retrieves relevant phone information based on user queries
    """

    def __init__(self, vector_store: VectorStore, embedding_model: EmbeddingModel):
        """
        Initialize retriever

        Args:
            vector_store: Vector store instance
            embedding_model: Embedding model instance
        """
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        logger.info("Initialized PhoneRetriever")

    def retrieve_by_query(self, query: str,
                          n_results: int = 5,
                          filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve phones based on natural language query

        Args:
            query: User query in natural language
            n_results: Number of results to return
            filters: Optional filters (brand, price range, etc.)

        Returns:
            List of relevant phones with scores
        """
        # Convert query to embedding
        query_embedding = self.embedding_model.encode(query)[0].tolist()

        # Search in vector store
        results = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=n_results,
            filter_dict=filters
        )

        return results['results']

    def retrieve_by_requirements(self, requirements: Dict[str, Any],
                                  n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve phones based on specific requirements

        Args:
            requirements: Dictionary of requirements
                - budget: Price range
                - purpose: Use case (gaming, photography, etc.)
                - brand_preference: Preferred brands
                - features: Required features

        Returns:
            List of matching phones
        """
        # Build query from requirements
        query_parts = []

        if 'purpose' in requirements:
            purpose_map = {
                'gaming': 'điện thoại chơi game hiệu năng cao RAM lớn chip mạnh',
                'photography': 'điện thoại chụp ảnh đẹp camera tốt nhiều tính năng',
                'business': 'điện thoại doanh nhân sang trọng bảo mật tốt',
                'student': 'điện thoại sinh viên giá rẻ pin trâu đủ dùng',
                'general': 'điện thoại đa năng cân bằng mọi tính năng'
            }
            query_parts.append(purpose_map.get(requirements['purpose'], ''))

        if 'features' in requirements:
            query_parts.extend(requirements['features'])

        if 'brand_preference' in requirements:
            brands = requirements['brand_preference']
            if isinstance(brands, list):
                query_parts.append(' '.join(brands))
            else:
                query_parts.append(brands)

        # Create combined query
        combined_query = ' '.join(query_parts)

        # Prepare filters
        filters = {}
        if 'budget' in requirements:
            if 'min' in requirements['budget']:
                filters['min_price'] = requirements['budget']['min']
            if 'max' in requirements['budget']:
                filters['max_price'] = requirements['budget']['max']

        return self.retrieve_by_query(combined_query, n_results, filters)

    def retrieve_similar_phones(self, phone_id: str,
                                 n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Find phones similar to a given phone

        Args:
            phone_id: ID of the reference phone
            n_results: Number of similar phones to return

        Returns:
            List of similar phones
        """
        # Get the reference phone
        reference_phone = self.vector_store.get_by_id(phone_id)
        if not reference_phone:
            logger.warning(f"Phone {phone_id} not found")
            return []

        # Create embedding for reference phone
        reference_embedding = self.embedding_model.encode_phone_specs(reference_phone)

        # Search for similar phones (excluding the reference phone itself)
        results = self.vector_store.search(
            query_embedding=reference_embedding[0].tolist(),
            n_results=n_results + 1  # Get extra to exclude self
        )

        # Filter out the reference phone
        similar_phones = [
            r for r in results['results']
            if r['id'] != phone_id
        ][:n_results]

        return similar_phones

    def retrieve_by_comparison(self, phone_ids: List[str]) -> Dict[str, Any]:
        """
        Retrieve detailed comparison data for multiple phones

        Args:
            phone_ids: List of phone IDs to compare

        Returns:
            Comparison data including specs and differences
        """
        phones = []
        for phone_id in phone_ids:
            phone_data = self.vector_store.get_by_id(phone_id)
            if phone_data:
                phones.append(phone_data)

        if not phones:
            return {'phones': [], 'comparison': {}}

        # Create comparison matrix
        comparison = {
            'common_features': [],
            'differences': {},
            'recommendations': []
        }

        # Find common features
        if len(phones) > 1:
            common_keys = set(phones[0].keys())
            for phone in phones[1:]:
                common_keys &= set(phone.keys())

            for key in common_keys:
                values = [phone.get(key) for phone in phones]
                if len(set(map(str, values))) == 1:
                    comparison['common_features'].append({
                        'feature': key,
                        'value': values[0]
                    })
                else:
                    comparison['differences'][key] = values

        return {
            'phones': phones,
            'comparison': comparison
        }

    def retrieve_trending(self, n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve trending or popular phones

        Args:
            n_results: Number of phones to return

        Returns:
            List of trending phones
        """
        # For now, return phones with specific criteria
        # In production, this would use analytics data
        criteria = {
            'category': 'flagship'  # Get flagship phones as "trending"
        }

        return self.vector_store.search_by_criteria(criteria, n_results)

    def retrieve_by_price_range(self, min_price: int,
                                 max_price: int,
                                 n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve phones within a price range

        Args:
            min_price: Minimum price
            max_price: Maximum price
            n_results: Number of results

        Returns:
            List of phones in price range
        """
        criteria = {
            'min_price': min_price,
            'max_price': max_price
        }

        return self.vector_store.search_by_criteria(criteria, n_results)