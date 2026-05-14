"""
Inference Engine — Forward Chaining (Suy luận tiến)
Thuật toán suy luận tiến, tách biệt khỏi Knowledge Base.
"""

import logging
from typing import Dict, List
from knowledge_base.rules import Rule
from inference_engine.conflict_resolution import (
    ConflictResolutionStrategy, CompositeStrategy
)
from working_memory import WorkingMemory

logger = logging.getLogger(__name__)


class ForwardChainingEngine:
    def __init__(self, conflict_strategy: ConflictResolutionStrategy = None):
        self.strategy = conflict_strategy or CompositeStrategy()
        self.memory = WorkingMemory()

    def infer(self, rules: List[Rule], initial_facts: Dict) -> Dict:
        self.memory.set_facts(initial_facts)
        changed = True

        while changed:
            changed = False

            # Lọc candidate: rules chưa kích hoạt và thoả mãn điều kiện
            candidates = [
                r for r in rules
                if r.id not in self.memory.activated_rules
                and r.evaluate(self.memory.facts)
            ]
            if not candidates:
                break

            # Dùng Conflict Resolution để sắp xếp thứ tự ưu tiên
            ordered = self.strategy.resolve(
                candidates, self.memory.activated_rules, self.memory.facts)

            for rule in ordered:
                self.memory.add_activated_rule(rule.id)
                self.memory.add_explanation(rule.description)

                for key, value in rule.actions.items():
                    if key == "explanation":
                        continue
                    self.memory.add_inferred_fact(key, value)
                    self.memory.facts[key] = self.memory.inferred_facts[key]

                self.strategy.record_firing(rule.id)
                changed = True
                logger.info(f"Activated: {rule.description}")

        return self.memory.get_snapshot()

    def get_rule_descriptions(self, rules: List[Rule]) -> Dict[str, str]:
        return {r.id: r.description for r in rules}
