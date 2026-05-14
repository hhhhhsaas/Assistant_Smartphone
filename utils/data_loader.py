"""
Data Loader utilities for loading and preprocessing phone data
"""

import json
import pandas as pd
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Handles loading and preprocessing of phone data from various sources
    """

    @staticmethod
    def load_json(file_path: str) -> List[Dict[str, Any]]:
        """
        Load phone data from JSON file

        Args:
            file_path: Path to JSON file

        Returns:
            List of phone dictionaries
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            data = [data]

        logger.info(f"Loaded {len(data)} phones from {file_path}")
        return data

    @staticmethod
    def load_csv(file_path: str,
                 column_mapping: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Load phone data from CSV file

        Args:
            file_path: Path to CSV file
            column_mapping: Optional mapping of CSV columns to standard names

        Returns:
            List of phone dictionaries
        """
        df = pd.read_csv(file_path, encoding='utf-8')

        # Apply column mapping if provided
        if column_mapping:
            df = df.rename(columns=column_mapping)

        # Convert to list of dictionaries
        data = df.to_dict('records')

        # Clean NaN values
        cleaned_data = []
        for item in data:
            cleaned_item = {k: v for k, v in item.items() if pd.notna(v)}
            cleaned_data.append(cleaned_item)

        logger.info(f"Loaded {len(cleaned_data)} phones from {file_path}")
        return cleaned_data

    @staticmethod
    def normalize_price(price_str: Any) -> Optional[float]:
        """
        Normalize price to float value

        Args:
            price_str: Price string or number

        Returns:
            Price as float or None
        """
        if pd.isna(price_str) or price_str is None:
            return None

        if isinstance(price_str, (int, float)):
            return float(price_str)

        # Convert string to number
        price_str = str(price_str)

        # Remove currency symbols and spaces
        price_str = re.sub(r'[^\d.,]', '', price_str)

        # Handle different number formats
        price_str = price_str.replace(',', '')
        price_str = price_str.replace('.', '')

        try:
            return float(price_str)
        except ValueError:
            logger.warning(f"Could not parse price: {price_str}")
            return None

    @staticmethod
    def normalize_ram(ram_str: Any) -> Optional[str]:
        """
        Normalize RAM specification

        Args:
            ram_str: RAM string

        Returns:
            Normalized RAM string or None
        """
        if pd.isna(ram_str) or ram_str is None:
            return None

        ram_str = str(ram_str).upper()

        # Extract number and unit
        match = re.search(r'(\d+)\s*(GB|MB)?', ram_str)
        if match:
            value = match.group(1)
            unit = match.group(2) or 'GB'
            return f"{value}{unit}"

        return ram_str

    @staticmethod
    def normalize_storage(storage_str: Any) -> Optional[str]:
        """
        Normalize storage specification

        Args:
            storage_str: Storage string

        Returns:
            Normalized storage string or None
        """
        if pd.isna(storage_str) or storage_str is None:
            return None

        storage_str = str(storage_str).upper()

        # Extract number and unit
        match = re.search(r'(\d+)\s*(GB|TB)?', storage_str)
        if match:
            value = match.group(1)
            unit = match.group(2) or 'GB'
            return f"{value}{unit}"

        return storage_str

    @staticmethod
    def normalize_battery(battery_str: Any) -> Optional[str]:
        """
        Normalize battery specification

        Args:
            battery_str: Battery string

        Returns:
            Normalized battery string or None
        """
        if pd.isna(battery_str) or battery_str is None:
            return None

        battery_str = str(battery_str)

        # Extract number and unit
        match = re.search(r'(\d+)\s*(mAh|MAH)?', battery_str, re.IGNORECASE)
        if match:
            value = match.group(1)
            return f"{value} mAh"

        return battery_str

    @staticmethod
    def normalize_screen_size(screen_str: Any) -> Optional[float]:
        """
        Normalize screen size to float (inches)

        Args:
            screen_str: Screen size string

        Returns:
            Screen size in inches as float or None
        """
        if pd.isna(screen_str) or screen_str is None:
            return None

        if isinstance(screen_str, (int, float)):
            return float(screen_str)

        screen_str = str(screen_str)
        match = re.search(r'(\d+\.?\d*)', screen_str)
        if match:
            return float(match.group(1))
        return None

    @staticmethod
    def extract_features(phone_data: Dict[str, Any]) -> List[str]:
        """
        Extract features from phone specifications

        Args:
            phone_data: Phone data dictionary

        Returns:
            List of features
        """
        features = []

        # Check for 5G
        if any(term in str(phone_data.get('name', '')).upper()
               for term in ['5G', '5 G']):
            features.append('5G')

        # Check for high refresh rate
        for field in ['screen', 'display', 'features']:
            if field in phone_data:
                value = str(phone_data[field])
                if re.search(r'\d+\s*Hz', value, re.IGNORECASE):
                    features.append('High refresh rate')
                    break

        # Check for fast charging
        for field in ['charging', 'features']:
            if field in phone_data:
                value = str(phone_data[field])
                if re.search(r'\d+W', value):
                    features.append('Fast charging')
                    break

        # Check for wireless charging
        if 'wireless' in str(phone_data).lower():
            features.append('Wireless charging')

        # Check for water resistance
        if re.search(r'IP\d{2}', str(phone_data)):
            features.append('Water resistant')

        # Check for dual SIM
        if 'dual' in str(phone_data).lower() and 'sim' in str(phone_data).lower():
            features.append('Dual SIM')

        return features

    @staticmethod
    def preprocess_phone_data(phone_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess and clean phone data

        Args:
            phone_data: Raw phone data

        Returns:
            Preprocessed phone data
        """
        processed = phone_data.copy()

        # Normalize fields
        if 'price' in processed:
            processed['price'] = DataLoader.normalize_price(processed['price'])

        if 'ram' in processed:
            processed['ram'] = DataLoader.normalize_ram(processed['ram'])

        if 'storage' in processed:
            processed['storage'] = DataLoader.normalize_storage(processed['storage'])

        if 'battery' in processed:
            processed['battery'] = DataLoader.normalize_battery(processed['battery'])

        if 'screen_size' in processed:
            processed['screen_size'] = DataLoader.normalize_screen_size(processed['screen_size'])

        # Extract features if not present
        if 'features' not in processed or not processed['features']:
            processed['features'] = DataLoader.extract_features(processed)

        # Ensure required fields
        if 'category' not in processed:
            # Determine category based on price
            price = processed.get('price', 0)
            if price:
                if price > 25000000:
                    processed['category'] = 'flagship'
                elif price > 10000000:
                    processed['category'] = 'midrange'
                elif price > 5000000:
                    processed['category'] = 'budget'
                else:
                    processed['category'] = 'entry'
            else:
                processed['category'] = 'smartphone'

        return processed

    @staticmethod
    def validate_phone_data(phone_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate phone data

        Args:
            phone_data: Phone data to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check required fields
        required = ['name', 'brand']
        for field in required:
            if field not in phone_data or not phone_data[field]:
                errors.append(f"Missing required field: {field}")

        # Validate data types
        if 'price' in phone_data and phone_data['price']:
            try:
                float(phone_data['price'])
            except (ValueError, TypeError):
                errors.append("Price must be a number")

        # Validate specifications format
        spec_fields = ['ram', 'storage', 'battery']
        for field in spec_fields:
            if field in phone_data and phone_data[field]:
                value = str(phone_data[field])
                if field == 'ram' and not re.search(r'\d+\s*(GB|MB)', value, re.IGNORECASE):
                    errors.append(f"{field} should include unit (GB/MB)")
                elif field == 'storage' and not re.search(r'\d+\s*(GB|TB)', value, re.IGNORECASE):
                    errors.append(f"{field} should include unit (GB/TB)")
                elif field == 'battery' and not re.search(r'\d+\s*mAh', value, re.IGNORECASE):
                    errors.append(f"{field} should include unit (mAh)")

        is_valid = len(errors) == 0
        return is_valid, errors

    @staticmethod
    def load_and_preprocess(file_path: str,
                           file_type: str = 'auto') -> List[Dict[str, Any]]:
        """
        Load and preprocess phone data from file

        Args:
            file_path: Path to data file
            file_type: File type ('json', 'csv', or 'auto' to detect)

        Returns:
            List of preprocessed phone data
        """
        file_path = Path(file_path)

        # Auto-detect file type
        if file_type == 'auto':
            if file_path.suffix.lower() == '.json':
                file_type = 'json'
            elif file_path.suffix.lower() == '.csv':
                file_type = 'csv'
            else:
                raise ValueError(f"Unknown file type: {file_path.suffix}")

        # Load data
        if file_type == 'json':
            data = DataLoader.load_json(str(file_path))
        elif file_type == 'csv':
            data = DataLoader.load_csv(str(file_path))
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        # Preprocess each item
        processed_data = []
        for item in data:
            processed = DataLoader.preprocess_phone_data(item)

            # Validate
            is_valid, errors = DataLoader.validate_phone_data(processed)
            if is_valid:
                processed_data.append(processed)
            else:
                logger.warning(f"Skipping invalid item {item.get('name', 'unknown')}: {errors}")

        logger.info(f"Preprocessed {len(processed_data)} valid phones")
        return processed_data