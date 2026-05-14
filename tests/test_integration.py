#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Integration Tests for Complete System
Test the full workflow from user input to recommendations
"""

import unittest
import sys
import os
import json
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inference_engine.integrated_inference import IntegratedPhoneAdvisor

class TestIntegration(unittest.TestCase):
    """Test complete system integration"""

    @classmethod
    def setUpClass(cls):
        """One-time setup for all tests"""
        cls.advisor = IntegratedPhoneAdvisor()

    def test_system_initialization(self):
        """Test that system initializes correctly"""
        self.assertIsNotNone(self.advisor.knowledge_base)
        self.assertIsNotNone(self.advisor.fuzzy_system)
        self.assertIsNotNone(self.advisor.inference_engine)

        # Check data is loaded
        phones = self.advisor.knowledge_base.get_all_phones()
        self.assertGreater(len(phones), 0)

    def test_natural_language_processing(self):
        """Test NLP parsing of Vietnamese queries"""
        test_queries = [
            ("Tìm điện thoại gaming tầm 15 triệu", {
                'user_need': 'gaming',
                'budget': 15000000
            }),
            ("iPhone giá rẻ dưới 20 triệu", {
                'preferred_brand': 'Apple',
                'budget': 20000000
            }),
            ("Điện thoại pin trâu giá 10 triệu", {
                'user_need': 'battery_life',
                'budget': 10000000
            }),
            ("Samsung flagship cao cấp", {
                'preferred_brand': 'Samsung',
                'user_need': 'premium'
            })
        ]

        for query, expected in test_queries:
            with self.subTest(query=query):
                parsed = self.advisor.process_user_request(query)

                # Check expected fields are parsed
                for key, value in expected.items():
                    if key == 'budget':
                        # Allow some flexibility in budget parsing
                        self.assertLessEqual(
                            abs(parsed.get(key, 0) - value),
                            5000000,
                            f"Budget parsing failed for: {query}"
                        )
                    else:
                        self.assertEqual(
                            parsed.get(key),
                            value,
                            f"Failed to parse {key} from: {query}"
                        )

    def test_recommendation_flow(self):
        """Test complete recommendation workflow"""
        # Test 1: Gaming phones
        gaming_request = {
            'budget': 20000000,
            'user_need': 'gaming'
        }

        recommendations = self.advisor.recommend_phones(gaming_request, n_results=5)

        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        self.assertLessEqual(len(recommendations), 5)

        # Check recommendation structure
        for rec in recommendations:
            self.assertIn('phone', rec)
            self.assertIn('total_score', rec)
            self.assertIn('fuzzy_score', rec)
            self.assertIn('rule_score', rec)
            self.assertIn('explanations', rec)

            # Scores should be between 0 and 1
            self.assertGreaterEqual(rec['total_score'], 0)
            self.assertLessEqual(rec['total_score'], 1)

    def test_scoring_consistency(self):
        """Test that scoring is consistent and logical"""
        # High-end phone should score well for premium needs
        premium_request = {
            'budget': 50000000,
            'user_need': 'premium'
        }

        recommendations = self.advisor.recommend_phones(premium_request, n_results=3)

        if recommendations:
            top_phone = recommendations[0]
            # Premium phones should have high scores for premium requests
            self.assertGreater(top_phone['total_score'], 0.5)

            # At least one top-3 recommendation should have a reasonable premium price
            premium_prices = [r['phone'].get('price', 0) for r in recommendations[:3] if r['phone'].get('price', 0) > 0]
            if premium_prices:
                self.assertGreater(max(premium_prices), 15000000)

    def test_brand_filtering(self):
        """Test brand preference filtering via preferred_brands in inferred facts"""
        # Use Apple which has R5_APPLE_FAN rule that sets brand_filter
        request = {
            'preferred_brand': 'Apple',
            'budget': 30000000
        }
        recommendations = self.advisor.recommend_phones(request, n_results=5)

        if recommendations:
            # With Apple preference + budget, R5_APPLE_FAN should fire
            brands_found = set(r['phone'].get('brand', '').lower() for r in recommendations[:3])
            self.assertIn('apple', brands_found)

    def test_budget_constraints(self):
        """Test that budget constraints are respected"""
        test_budgets = [5000000, 10000000, 20000000, 50000000]

        for budget in test_budgets:
            with self.subTest(budget=budget):
                request = {'budget': budget}
                recommendations = self.advisor.recommend_phones(request, n_results=5)

                if recommendations:
                    # At least top recommendation should be within budget
                    top_phone_price = recommendations[0]['phone'].get('price', 0)

                    # Allow 20% flexibility for great matches slightly over budget
                    self.assertLessEqual(
                        top_phone_price,
                        budget * 1.2,
                        f"Recommended phone way over budget: {top_phone_price} > {budget}"
                    )

    def test_explanation_generation(self):
        """Test that explanations are generated properly"""
        request = {
            'budget': 15000000,
            'user_need': 'gaming',
            'preferred_brand': 'Xiaomi'
        }

        recommendations = self.advisor.recommend_phones(request, n_results=3)

        for rec in recommendations:
            explanations = rec['explanations']

            # Should have explanations
            self.assertIsInstance(explanations, list)
            self.assertGreater(len(explanations), 0)

            # Explanations should be strings
            for exp in explanations:
                self.assertIsInstance(exp, str)
                self.assertGreaterEqual(len(exp), 10)  # Not empty explanations

    def test_edge_cases(self):
        """Test system handles edge cases gracefully"""
        edge_cases = [
            # Empty request
            {},
            # Impossible budget
            {'budget': 100000},
            # Unknown brand
            {'preferred_brand': 'UnknownBrand'},
            # Conflicting requirements
            {'budget': 5000000, 'user_need': 'premium'},
            # Very specific requirements
            {
                'budget': 12345678,
                'user_need': 'gaming',
                'preferred_brand': 'Apple',
                'features': ['5g', 'wireless_charging', 'waterproof']
            }
        ]

        for request in edge_cases:
            with self.subTest(request=request):
                # Should not crash
                recommendations = self.advisor.recommend_phones(request, n_results=3)

                # Should return list (possibly empty)
                self.assertIsInstance(recommendations, list)

    def test_performance(self):
        """Test system performance"""
        import time

        request = {
            'budget': 20000000,
            'user_need': 'camera'
        }

        # Measure time for recommendation
        start_time = time.time()
        recommendations = self.advisor.recommend_phones(request, n_results=10)
        end_time = time.time()

        execution_time = end_time - start_time

        # Should be fast (under 2 seconds even for 10 results)
        self.assertLess(
            execution_time,
            2.0,
            f"Recommendation too slow: {execution_time:.2f} seconds"
        )

    def test_data_integrity(self):
        """Test that phone data is complete and valid"""
        phones = self.advisor.knowledge_base.get_all_phones()

        for phone in phones[:50]:  # Test sample of phones
            # Required fields should exist
            self.assertIn('name', phone)
            self.assertIn('price', phone)

            # Price should be numeric and reasonable
            price = phone.get('price', 0)
            self.assertIsInstance(price, (int, float))
            self.assertGreaterEqual(price, 0)
            self.assertLess(price, 200000000)  # Under 200 million VND

            # Name should not be empty
            name = phone.get('name', '')
            self.assertIsInstance(name, str)
            self.assertGreater(len(name), 0)

if __name__ == '__main__':
    # Run with verbosity
    unittest.main(verbosity=2)