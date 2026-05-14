"""
Knowledge Base — Phone Facts (Sự kiện về điện thoại)
Chứa dữ liệu điện thoại là các sự kiện (facts) trong hệ chuyên gia.
"""

import json
import pickle
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PhoneFacts:
    def __init__(self, persist_path: str = "./data/cellphones_vector_store.pkl"):
        self.persist_path = Path(persist_path)
        self.facts: List[Dict] = []

        stats_file = Path("data/cellphones_stats.json")
        self.stats = {}
        if stats_file.exists():
            with open(stats_file, 'r', encoding='utf-8') as f:
                self.stats = json.load(f)

        self.load()

    def load(self) -> None:
        if not self.persist_path.exists():
            logger.error(
                f"Data file not found: {self.persist_path.resolve()}. "
                f"The system will return no recommendations. "
                f"Please ensure the data file exists."
            )
            return

        try:
            with open(self.persist_path, 'rb') as f:
                data = pickle.load(f)
                self.facts = data.get('metadata', [])
            if not self.facts:
                logger.warning(
                    f"Data file loaded but contains no phone facts: {self.persist_path}"
                )
            else:
                logger.info(f"Loaded {len(self.facts)} phone facts")
        except Exception as e:
            logger.error(f"Failed to load phone facts from {self.persist_path}: {e}")

    def get_all(self) -> List[Dict]:
        return self.facts.copy()

    def get_by_id(self, phone_id: str) -> Optional[Dict]:
        for fact in self.facts:
            if fact.get('id') == phone_id:
                return fact
        return None

    def search_by_criteria(self, criteria: Dict[str, Any],
                           n_results: int = 500) -> List[Dict]:
        results = []
        for fact in self.facts:
            match = True
            if 'brand' in criteria and fact.get('brand') != criteria['brand']:
                match = False
            phone_price = fact.get('price', 0)
            # Phones with price=0 means "Liên Hệ" (unknown price) - exclude from budget-based searches
            if ('min_price' in criteria or 'max_price' in criteria) and (not phone_price or phone_price <= 0):
                match = False
            if 'min_price' in criteria and phone_price and phone_price < criteria['min_price']:
                match = False
            if 'max_price' in criteria and phone_price and phone_price > criteria['max_price']:
                match = False
            if 'category' in criteria:
                cats = criteria['category']
                if isinstance(cats, list):
                    if fact.get('category') not in cats:
                        match = False
                elif fact.get('category') != cats:
                    match = False
            if match:
                results.append(fact)
                if len(results) >= n_results:
                    break
        return results

    def add_fact(self, fact: Dict) -> None:
        self.facts.append(fact)

    def remove_fact(self, phone_id: str) -> bool:
        for i, fact in enumerate(self.facts):
            if fact.get('id') == phone_id:
                self.facts.pop(i)
                return True
        return False

    def count(self) -> int:
        return len(self.facts)

    def get_brands(self) -> List[str]:
        brands = set()
        for f in self.facts:
            if f.get('brand'):
                brands.add(f['brand'])
        return sorted(brands)

    def get_price_range(self) -> Dict:
        prices = [f.get('price') for f in self.facts if f.get('price')]
        if prices:
            return {'min': min(prices), 'max': max(prices), 'avg': sum(prices) // len(prices)}
        return {'min': 0, 'max': 0, 'avg': 0}

    def get_stats(self) -> Dict:
        return {
            'total_phones': self.count(),
            'brands': self.get_brands(),
            'price_range': self.get_price_range(),
            'categories': self._count_categories(),
        }

    def _count_categories(self) -> Dict:
        cats = {}
        for f in self.facts:
            c = f.get('category', 'unknown')
            cats[c] = cats.get(c, 0) + 1
        return cats
