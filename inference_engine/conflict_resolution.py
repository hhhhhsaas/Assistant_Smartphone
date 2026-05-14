"""
Conflict Resolution (Giải quyết xung đột luật)
Chiến lược chọn luật nào sẽ kích hoạt khi nhiều luật cùng thoả mãn.
"""

from typing import List
from knowledge_base.rules import Rule


class ConflictResolutionStrategy:
    """Base class cho các chiến lược giải quyết xung đột"""

    def resolve(self, candidates: List[Rule], activated_ids: List[str],
                facts: dict) -> List[Rule]:
        raise NotImplementedError


class PriorityStrategy(ConflictResolutionStrategy):
    """Ưu tiên luật có priority cao nhất (giảm dần)"""

    def resolve(self, candidates: List[Rule], activated_ids: List[str],
                facts: dict) -> List[Rule]:
        available = [r for r in candidates if r.id not in activated_ids]
        available.sort(key=lambda x: x.priority, reverse=True)
        return available


class SpecificityStrategy(ConflictResolutionStrategy):
    """Ưu tiên luật có nhiều điều kiện nhất (specificity)"""

    def resolve(self, candidates: List[Rule], activated_ids: List[str],
                facts: dict) -> List[Rule]:
        available = [r for r in candidates if r.id not in activated_ids]
        available.sort(key=lambda r: len(r.conditions), reverse=True)
        return available


class RecencyStrategy(ConflictResolutionStrategy):
    """Ưu tiên luật chưa được dùng gần đây"""

    def __init__(self):
        self.firing_history = []

    def resolve(self, candidates: List[Rule], activated_ids: List[str],
                facts: dict) -> List[Rule]:
        available = [r for r in candidates if r.id not in activated_ids]
        available.sort(key=lambda r: (
            self.firing_history.index(r.id)
            if r.id in self.firing_history else -1
        ))
        return available

    def record_firing(self, rule_id: str) -> None:
        self.firing_history.append(rule_id)


class CompositeStrategy(ConflictResolutionStrategy):
    """Kết hợp: priority → specificity → recency"""

    def __init__(self):
        self.recency = RecencyStrategy()

    def resolve(self, candidates: List[Rule], activated_ids: List[str],
                facts: dict) -> List[Rule]:
        available = [r for r in candidates if r.id not in activated_ids]
        available.sort(key=lambda r: (
            -r.priority,
            -len(r.conditions),
            self.recency.firing_history.index(r.id)
            if r.id in self.recency.firing_history else -1
        ))
        return available

    def record_firing(self, rule_id: str) -> None:
        self.recency.record_firing(rule_id)
