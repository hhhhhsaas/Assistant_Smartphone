"""
Knowledge Base (Cơ sở tri thức)
Quản lý toàn bộ tri thức của hệ chuyên gia gồm:
- Rules (Luật) — các luật suy luận IF-THEN
- Facts (Sự kiện) — dữ liệu về điện thoại
"""

import logging
from typing import Dict, List, Optional
from knowledge_base.rules import Rule, get_default_rules
from knowledge_base.phone_facts import PhoneFacts

logger = logging.getLogger(__name__)


class KnowledgeBase:
    def __init__(self, facts_path: str = "./data/cellphones_vector_store.pkl"):
        self.rules: List[Rule] = []
        self.facts: PhoneFacts = PhoneFacts(facts_path)
        self._load_default_rules()

    def _load_default_rules(self) -> None:
        self.rules = get_default_rules()
        logger.info(f"Loaded {len(self.rules)} rules")

    def get_all_rules(self) -> List[Rule]:
        return self.rules.copy()

    def get_rule_by_id(self, rule_id: str) -> Optional[Rule]:
        for r in self.rules:
            if r.id == rule_id:
                return r
        return None

    def add_rule(self, rule: Rule) -> None:
        self.rules.append(rule)
        self.rules.sort(key=lambda x: x.priority, reverse=True)

    def remove_rule(self, rule_id: str) -> bool:
        for i, r in enumerate(self.rules):
            if r.id == rule_id:
                self.rules.pop(i)
                return True
        return False

    def update_rule(self, rule_id: str, new_rule: Rule) -> bool:
        for i, r in enumerate(self.rules):
            if r.id == rule_id:
                self.rules[i] = new_rule
                return True
        return False

    def get_all_phones(self) -> List[Dict]:
        return self.facts.get_all()

    def search_phones(self, criteria: Dict, n_results: int = 100) -> List[Dict]:
        return self.facts.search_by_criteria(criteria, n_results)

    def add_phone_fact(self, phone: Dict) -> None:
        self.facts.add_fact(phone)

    def remove_phone_fact(self, phone_id: str) -> bool:
        return self.facts.remove_fact(phone_id)

    def get_stats(self) -> Dict:
        return self.facts.get_stats()

    def get_rules_summary(self) -> List[Dict]:
        return [{
            'id': r.id,
            'description': r.description,
            'priority': r.priority,
            'conditions': r.conditions,
            'actions': {k: v for k, v in r.actions.items() if k != 'explanation'},
        } for r in self.rules]
