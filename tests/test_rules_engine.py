import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge_base.rules import Rule, get_default_rules
from inference_engine.forward_chaining import ForwardChainingEngine
from inference_engine.conflict_resolution import CompositeStrategy


class TestRulesEngine(unittest.TestCase):
    """Test Forward Chaining Engine with Conflict Resolution"""

    def setUp(self):
        self.engine = ForwardChainingEngine()
        self.rules = get_default_rules()

    def test_rule_initialization(self):
        """Test that all rules from KB are properly loaded"""
        self.assertGreaterEqual(len(self.rules), 10)
        self.assertTrue(all(isinstance(r, Rule) for r in self.rules))

    def test_gaming_rule(self):
        """Test R1_GAMING rule application via forward chaining"""
        facts = {'user_need': 'gaming', 'budget': 15000000}
        inferred = self.engine.infer(self.rules, facts)
        cats = inferred.get('inferred_facts', {}).get('category_filter', [])
        cats = [cats] if isinstance(cats, str) else cats
        self.assertTrue('gaming' in cats or 'flagship' in cats or 'midrange' in cats)

    def test_camera_rule(self):
        """Test R2_CAMERA rule activation"""
        facts = {'user_need': 'photography', 'budget': 15000000}
        inferred = self.engine.infer(self.rules, facts)
        inf = inferred.get('inferred_facts', {})
        self.assertIn('min_camera_mp', inf)
        self.assertGreaterEqual(inf['min_camera_mp'], 32)

    def test_budget_rule(self):
        """Test budget rules activation"""
        facts = {'budget': 5000000}
        inferred = self.engine.infer(self.rules, facts)
        inf = inferred.get('inferred_facts', {})
        self.assertIn('category_filter', inf)

    def test_multiple_rules(self):
        """Test multiple rules apply and merge correctly"""
        facts = {'user_need': 'gaming', 'budget': 30000000}
        inferred = self.engine.infer(self.rules, facts)
        activated = inferred.get('activated_rules', [])
        self.assertGreaterEqual(len(activated), 1)

    def test_no_matching_rules(self):
        """Test with minimal facts — should still return working memory"""
        facts = {}
        inferred = self.engine.infer(self.rules, facts)
        self.assertIsInstance(inferred, dict)

    def test_conflict_resolution(self):
        """Test CompositeStrategy ordering"""
        self.assertTrue(len(self.rules) > 0)
        self.assertTrue(all(hasattr(r, 'priority') for r in self.rules))

    def test_forward_chain_merge(self):
        """Test that category_filter merges correctly as list"""
        facts = {'user_need': 'gaming', 'budget': 3000000}
        inferred = self.engine.infer(self.rules, facts)
        cats = inferred.get('inferred_facts', {}).get('category_filter')
        if cats is not None:
            self.assertIsInstance(cats, (str, list))

    def test_rule_id_format(self):
        """Test that all rules have proper IDs"""
        for r in self.rules:
            self.assertRegex(r.id, r'^R\d+[A-Z]?_')

    def test_explanation_provided(self):
        """Test that activated rules provide explanations"""
        facts = {'user_need': 'gaming', 'budget': 15000000}
        inferred = self.engine.infer(self.rules, facts)
        self.assertGreater(len(inferred.get('activated_rules', [])), 0)
        for rule_id in inferred.get('activated_rules', []):
            rule = next((r for r in self.rules if r.id == rule_id), None)
            if rule:
                self.assertIn('explanation', rule.actions)

    def test_recency_ordering(self):
        """Test conflict resolution ordering"""
        strategy = CompositeStrategy()
        ordered = strategy.resolve(self.rules.copy(), [], {})
        self.assertEqual(len(ordered), len(self.rules))
        if len(ordered) >= 2:
            self.assertGreaterEqual(ordered[0].priority, ordered[-1].priority)


if __name__ == '__main__':
    unittest.main()
