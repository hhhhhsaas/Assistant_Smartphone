"""
Working Memory (Bộ nhớ làm việc)
Lưu trữ các sự kiện tạm thời trong quá trình suy luận.
"""

from typing import Dict, List, Any


class WorkingMemory:
    def __init__(self):
        self.facts: Dict[str, Any] = {}
        self.inferred_facts: Dict[str, Any] = {}
        self.explanations: List[str] = []
        self.activated_rules: List[str] = []
        self.history: List[Dict] = []

    def set_facts(self, facts: Dict) -> None:
        self.facts = facts.copy()
        self.inferred_facts = {}
        self.explanations = []
        self.activated_rules = []
        self.history = []

    def get_fact(self, key: str, default=None):
        if key in self.inferred_facts:
            return self.inferred_facts[key]
        return self.facts.get(key, default)

    def add_inferred_fact(self, key: str, value: Any) -> None:
        old_value = self.inferred_facts.get(key)
        self.history.append({
            'key': key,
            'old_value': old_value,
            'new_value': value,
        })

        if old_value is None:
            self.inferred_facts[key] = value
            return

        if key == "min_ram":
            try:
                old = int(str(old_value).replace("GB", ""))
                new = int(str(value).replace("GB", ""))
                self.inferred_facts[key] = f"{max(old, new)}GB"
            except ValueError:
                self.inferred_facts[key] = value

        elif key in ("min_battery", "min_camera_mp", "min_screen_size",
                     "min_camera_front_mp"):
            try:
                self.inferred_facts[key] = max(float(old_value), float(value))
            except (ValueError, TypeError):
                self.inferred_facts[key] = value

        elif key in ("max_weight",):
            try:
                self.inferred_facts[key] = min(float(old_value), float(value))
            except (ValueError, TypeError):
                self.inferred_facts[key] = value

        elif key == "category_filter":
            old_list = [old_value] if isinstance(old_value, str) else list(old_value)
            new_list = [value] if isinstance(value, str) else list(value)
            merged = list(dict.fromkeys(old_list + new_list))
            self.inferred_facts[key] = merged if len(merged) > 1 else merged[0]

        elif key in ("preferred_brands", "preferred_features",
                     "required_features"):
            old_list = list(old_value) if isinstance(old_value, list) else [old_value]
            new_list = list(value) if isinstance(value, list) else [value]
            self.inferred_facts[key] = list(dict.fromkeys(old_list + new_list))

        else:
            self.inferred_facts[key] = value

    def add_explanation(self, text: str) -> None:
        self.explanations.append(text)

    def add_activated_rule(self, rule_id: str) -> None:
        if rule_id not in self.activated_rules:
            self.activated_rules.append(rule_id)

    def get_snapshot(self) -> Dict:
        return {
            'facts': {**self.facts, **self.inferred_facts},
            'inferred_facts': dict(self.inferred_facts),
            'activated_rules': list(self.activated_rules),
            'explanations': list(self.explanations),
            'history': list(self.history),
        }

    def undo_last_step(self) -> bool:
        if not self.history:
            return False
        last = self.history.pop()
        key = last['key']
        if last['old_value'] is None:
            self.inferred_facts.pop(key, None)
        else:
            self.inferred_facts[key] = last['old_value']
        return True

    def clear(self) -> None:
        self.facts = {}
        self.inferred_facts = {}
        self.explanations = []
        self.activated_rules = []
        self.history = []

    def __repr__(self) -> str:
        return (f"WorkingMemory(facts={len(self.facts)}, "
                f"inferred={len(self.inferred_facts)}, "
                f"activated={len(self.activated_rules)})")
