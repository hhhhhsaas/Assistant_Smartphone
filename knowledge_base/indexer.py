"""
Data Indexer for processing and indexing phone data into the knowledge base
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from tqdm import tqdm
from .embeddings import EmbeddingModel
from .vector_store import VectorStore

logger = logging.getLogger(__name__)


class DataIndexer:
    """
    Indexes phone data into the vector store
    """

    def __init__(self, vector_store: VectorStore, embedding_model: EmbeddingModel):
        """
        Initialize indexer

        Args:
            vector_store: Vector store instance
            embedding_model: Embedding model instance
        """
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        logger.info("Initialized DataIndexer")

    def index_from_json(self, json_path: str,
                        batch_size: int = 32,
                        clear_existing: bool = False) -> Dict[str, Any]:
        """
        Index phone data from JSON file

        Args:
            json_path: Path to JSON file
            batch_size: Batch size for processing
            clear_existing: Whether to clear existing data

        Returns:
            Indexing statistics
        """
        json_path = Path(json_path)
        if not json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")

        # Load data
        with open(json_path, 'r', encoding='utf-8') as f:
            phones_data = json.load(f)

        if not isinstance(phones_data, list):
            phones_data = [phones_data]

        logger.info(f"Loaded {len(phones_data)} phones from {json_path}")

        # Clear existing data if requested
        if clear_existing:
            self.vector_store.clear_all()
            logger.info("Cleared existing data")

        # Process in batches
        total_indexed = 0
        failed_items = []

        for i in tqdm(range(0, len(phones_data), batch_size),
                      desc="Indexing phones"):
            batch = phones_data[i:i + batch_size]

            try:
                # Generate embeddings for batch
                embeddings = []
                valid_phones = []
                ids = []

                for phone in batch:
                    try:
                        # Validate required fields
                        if 'name' not in phone:
                            logger.warning(f"Skipping phone without name: {phone}")
                            continue

                        # Generate embedding
                        embedding = self.embedding_model.encode_phone_specs(phone)
                        embeddings.append(embedding[0].tolist())

                        # Generate ID
                        phone_id = self._generate_phone_id(phone)
                        ids.append(phone_id)

                        valid_phones.append(phone)

                    except Exception as e:
                        logger.error(f"Failed to process phone {phone.get('name', 'unknown')}: {e}")
                        failed_items.append(phone.get('name', 'unknown'))

                # Add batch to vector store
                if valid_phones:
                    self.vector_store.add_phones(valid_phones, embeddings, ids)
                    total_indexed += len(valid_phones)

            except Exception as e:
                logger.error(f"Failed to index batch {i//batch_size}: {e}")

        stats = {
            'total_processed': len(phones_data),
            'total_indexed': total_indexed,
            'failed_items': failed_items,
            'success_rate': total_indexed / len(phones_data) if phones_data else 0
        }

        logger.info(f"Indexing complete: {stats}")
        return stats

    def index_from_csv(self, csv_path: str,
                       column_mapping: Optional[Dict[str, str]] = None,
                       batch_size: int = 32,
                       clear_existing: bool = False) -> Dict[str, Any]:
        """
        Index phone data from CSV file

        Args:
            csv_path: Path to CSV file
            column_mapping: Mapping of CSV columns to phone attributes
            batch_size: Batch size for processing
            clear_existing: Whether to clear existing data

        Returns:
            Indexing statistics
        """
        csv_path = Path(csv_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        # Load data
        df = pd.read_csv(csv_path, encoding='utf-8')
        logger.info(f"Loaded {len(df)} rows from {csv_path}")

        # Apply column mapping if provided
        if column_mapping:
            df = df.rename(columns=column_mapping)

        # Convert to list of dictionaries
        phones_data = df.to_dict('records')

        # Clean data
        for phone in phones_data:
            # Remove NaN values
            phone = {k: v for k, v in phone.items()
                     if pd.notna(v)}

        return self.index_from_json(phones_data, batch_size, clear_existing)

    def index_single_phone(self, phone_data: Dict[str, Any]) -> str:
        """
        Index a single phone

        Args:
            phone_data: Phone data dictionary

        Returns:
            Phone ID
        """
        # Generate ID and embedding
        phone_id = self._generate_phone_id(phone_data)
        embedding = self.embedding_model.encode_phone_specs(phone_data)

        # Add to vector store
        self.vector_store.add_phones(
            [phone_data],
            [embedding[0].tolist()],
            [phone_id]
        )

        logger.info(f"Indexed phone: {phone_id}")
        return phone_id

    def update_phone(self, phone_id: str, phone_data: Dict[str, Any]) -> None:
        """
        Update an existing phone

        Args:
            phone_id: Phone ID
            phone_data: Updated phone data
        """
        # Generate new embedding
        embedding = self.embedding_model.encode_phone_specs(phone_data)

        # Update in vector store
        self.vector_store.update_phone(phone_id, phone_data, embedding[0].tolist())

        logger.info(f"Updated phone: {phone_id}")

    def reindex_all(self, batch_size: int = 32) -> Dict[str, Any]:
        """
        Reindex all existing phones (useful after embedding model change)

        Args:
            batch_size: Batch size for processing

        Returns:
            Reindexing statistics
        """
        # Get all existing phones
        all_phones = self.vector_store.search_by_criteria({}, n_results=10000)

        if not all_phones:
            return {'total_reindexed': 0}

        logger.info(f"Reindexing {len(all_phones)} phones")

        # Clear and reindex
        self.vector_store.clear_all()

        total_reindexed = 0
        for i in range(0, len(all_phones), batch_size):
            batch = all_phones[i:i + batch_size]

            embeddings = []
            ids = []

            for phone in batch:
                embedding = self.embedding_model.encode_phone_specs(phone)
                embeddings.append(embedding[0].tolist())
                ids.append(self._generate_phone_id(phone))

            self.vector_store.add_phones(batch, embeddings, ids)
            total_reindexed += len(batch)

        return {'total_reindexed': total_reindexed}

    def _generate_phone_id(self, phone_data: Dict[str, Any]) -> str:
        """
        Generate unique ID for a phone

        Args:
            phone_data: Phone data

        Returns:
            Unique phone ID
        """
        # Use brand and name for ID
        brand = phone_data.get('brand', 'unknown').lower().replace(' ', '_')
        name = phone_data.get('name', 'unknown').lower().replace(' ', '_')

        # Remove special characters
        import re
        brand = re.sub(r'[^a-z0-9_]', '', brand)
        name = re.sub(r'[^a-z0-9_]', '', name)

        return f"{brand}_{name}"

    def validate_data(self, phone_data: Dict[str, Any]) -> List[str]:
        """
        Validate phone data

        Args:
            phone_data: Phone data to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check required fields
        required_fields = ['name', 'brand']
        for field in required_fields:
            if field not in phone_data or not phone_data[field]:
                errors.append(f"Missing required field: {field}")

        # Validate data types
        if 'price' in phone_data:
            try:
                float(phone_data['price'])
            except (ValueError, TypeError):
                errors.append("Price must be a number")

        if 'ram' in phone_data:
            ram_str = str(phone_data['ram'])
            if not any(unit in ram_str.upper() for unit in ['GB', 'MB']):
                errors.append("RAM should include unit (GB/MB)")

        if 'storage' in phone_data:
            storage_str = str(phone_data['storage'])
            if not any(unit in storage_str.upper() for unit in ['GB', 'TB']):
                errors.append("Storage should include unit (GB/TB)")

        return errors