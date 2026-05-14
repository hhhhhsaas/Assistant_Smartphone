"""
Knowledge Acquisition (Thu thập tri thức)
Cho phép thêm / sửa / xoá luật và sự kiện trong Knowledge Base.
"""

import json
import logging
from typing import Dict, List, Optional
from knowledge_base.rules import Rule
from knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)


class KnowledgeAcquisition:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb

    # ── Rule operations ──

    def add_rule(self, rule_id: str, description: str,
                 conditions: Dict, actions: Dict,
                 priority: int = 1) -> Rule:
        if self.kb.get_rule_by_id(rule_id):
            raise ValueError(f"Rule {rule_id} already exists")
        rule = Rule(rule_id, description, conditions, actions, priority)
        self._validate_rule(rule)
        self.kb.add_rule(rule)
        logger.info(f"Added rule: {rule_id}")
        return rule

    def remove_rule(self, rule_id: str) -> bool:
        if self.kb.remove_rule(rule_id):
            logger.info(f"Removed rule: {rule_id}")
            return True
        logger.warning(f"Rule not found: {rule_id}")
        return False

    def edit_rule(self, rule_id: str, **updates) -> Optional[Rule]:
        rule = self.kb.get_rule_by_id(rule_id)
        if not rule:
            logger.warning(f"Rule not found: {rule_id}")
            return None
        for key, value in updates.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        self._validate_rule(rule)
        self.kb.update_rule(rule_id, rule)
        logger.info(f"Updated rule: {rule_id}")
        return rule

    def list_rules(self) -> List[Dict]:
        return self.kb.get_rules_summary()

    # ── Phone fact operations ──

    def add_phone(self, phone_data: Dict) -> None:
        required = ['name', 'brand', 'price']
        missing = [f for f in required if f not in phone_data]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        self.kb.add_phone_fact(phone_data)
        logger.info(f"Added phone: {phone_data.get('name')}")

    def remove_phone(self, phone_id: str) -> bool:
        return self.kb.remove_phone_fact(phone_id)

    # ── Import / Export ──

    def export_rules_to_json(self, filepath: str) -> None:
        data = [r.to_dict() for r in self.kb.get_all_rules()]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Exported {len(data)} rules to {filepath}")

    def import_rules_from_json(self, filepath: str) -> int:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        count = 0
        for d in data:
            if not self.kb.get_rule_by_id(d['id']):
                self.kb.add_rule(Rule.from_dict(d))
                count += 1
        logger.info(f"Imported {count} rules from {filepath}")
        return count

    # ── Validation ──

    def _validate_rule(self, rule: Rule) -> None:
        if not rule.id:
            raise ValueError("Rule must have an ID")
        if not rule.conditions:
            raise ValueError(f"Rule {rule.id} must have conditions")
        if not rule.actions:
            raise ValueError(f"Rule {rule.id} must have actions")
