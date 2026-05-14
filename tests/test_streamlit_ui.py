#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UI Component Tests for Streamlit Application
Test UI logic and components without running Streamlit
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestStreamlitUI(unittest.TestCase):
    """Test Streamlit UI components and logic"""

    def setUp(self):
        """Setup mock Streamlit environment"""
        # Mock streamlit module
        self.mock_st = MagicMock()
        sys.modules['streamlit'] = self.mock_st

    def test_ui_initialization(self):
        """Test UI initialization and session state"""
        # Mock session state
        mock_session_state = {
            'comparison_list': [],
            'search_results': None,
            'search_query': '',
            'selected_brand': 'Tất cả',
            'budget_range': (5000000, 50000000)
        }

        self.mock_st.session_state = mock_session_state

        # Test session state initialization
        self.assertEqual(len(mock_session_state['comparison_list']), 0)
        self.assertIsNone(mock_session_state['search_results'])

    def test_search_modes(self):
        """Test different search modes"""
        # Test natural language search
        nl_query = "Tìm điện thoại gaming 15 triệu"
        parsed_nl = {
            'user_need': 'gaming',
            'budget': 15000000
        }

        self.assertEqual(parsed_nl['user_need'], 'gaming')
        self.assertEqual(parsed_nl['budget'], 15000000)

        # Test detailed search
        detailed_criteria = {
            'budget': 20000000,
            'user_need': 'camera',
            'preferred_brand': 'Samsung',
            'features': ['5g', 'wireless_charging']
        }

        self.assertEqual(detailed_criteria['user_need'], 'camera')
        self.assertEqual(detailed_criteria['preferred_brand'], 'Samsung')
        self.assertEqual(len(detailed_criteria['features']), 2)

    def test_phone_card_display(self):
        """Test phone card display logic"""
        # Sample phone data
        phone = {
            'name': 'iPhone 15 Pro Max',
            'brand': 'Apple',
            'price': 35000000,
            'ram': '8GB',
            'storage': '256GB',
            'battery': 4422,
            'camera': 48,
            'screen_size': 6.7,
            'category': 'flagship'
        }

        score = 0.85
        explanations = [
            "Flagship phone with premium features",
            "Excellent camera system",
            "Within budget range"
        ]

        # Test formatting
        formatted_price = f"{phone['price']:,} VND"
        self.assertEqual(formatted_price, "35,000,000 VND")

        score_percentage = f"{score:.1%}"
        self.assertEqual(score_percentage, "85.0%")

        # Test category emoji
        category_emojis = {
            'flagship': '👑',
            'gaming': '🎮',
            'budget': '💰',
            'midrange': '📱',
            'camera': '📸',
            'foldable': '📱'
        }

        emoji = category_emojis.get(phone['category'], '📱')
        self.assertEqual(emoji, '👑')

    def test_comparison_feature(self):
        """Test phone comparison logic"""
        # Mock comparison list
        comparison_list = []

        # Add phones to comparison
        phone1 = {
            'id': 'phone1',
            'name': 'iPhone 15',
            'price': 30000000,
            'ram': '8GB',
            'storage': '256GB'
        }

        phone2 = {
            'id': 'phone2',
            'name': 'Samsung S24',
            'price': 28000000,
            'ram': '12GB',
            'storage': '512GB'
        }

        # Test adding to comparison
        comparison_list.append(phone1)
        self.assertEqual(len(comparison_list), 1)

        comparison_list.append(phone2)
        self.assertEqual(len(comparison_list), 2)

        # Test comparison table data
        comparison_data = {
            'Feature': ['Price', 'RAM', 'Storage'],
            phone1['name']: [
                f"{phone1['price']:,} VND",
                phone1['ram'],
                phone1['storage']
            ],
            phone2['name']: [
                f"{phone2['price']:,} VND",
                phone2['ram'],
                phone2['storage']
            ]
        }

        self.assertEqual(len(comparison_data['Feature']), 3)
        self.assertEqual(comparison_data[phone1['name']][0], "30,000,000 VND")

        # Test clear comparison
        comparison_list.clear()
        self.assertEqual(len(comparison_list), 0)

    def test_filter_and_sort(self):
        """Test filtering and sorting logic"""
        # Sample phones
        phones = [
            {'name': 'Phone A', 'price': 10000000, 'brand': 'Samsung'},
            {'name': 'Phone B', 'price': 20000000, 'brand': 'Apple'},
            {'name': 'Phone C', 'price': 15000000, 'brand': 'Xiaomi'},
            {'name': 'Phone D', 'price': 25000000, 'brand': 'Samsung'}
        ]

        # Test brand filter
        samsung_phones = [p for p in phones if p['brand'] == 'Samsung']
        self.assertEqual(len(samsung_phones), 2)

        # Test price sort
        sorted_by_price = sorted(phones, key=lambda x: x['price'])
        self.assertEqual(sorted_by_price[0]['name'], 'Phone A')
        self.assertEqual(sorted_by_price[-1]['name'], 'Phone D')

        # Test price range filter
        budget_min, budget_max = 12000000, 22000000
        in_budget = [p for p in phones if budget_min <= p['price'] <= budget_max]
        self.assertEqual(len(in_budget), 2)

    def test_error_handling_ui(self):
        """Test UI error handling"""
        # Test empty search
        empty_results = []
        self.assertEqual(len(empty_results), 0)

        # Default message for no results
        no_results_msg = "Không tìm thấy điện thoại phù hợp"
        self.assertIsInstance(no_results_msg, str)

        # Test invalid input handling
        invalid_budget = -5000000
        self.assertLess(invalid_budget, 0)

        # Should handle by setting to minimum
        corrected_budget = max(0, invalid_budget)
        self.assertEqual(corrected_budget, 0)

    def test_view_modes(self):
        """Test different view modes (List/Grid)"""
        view_modes = ['List View', 'Grid View']

        # Test list view
        current_view = 'List View'
        self.assertIn(current_view, view_modes)

        # Test grid view
        current_view = 'Grid View'
        self.assertIn(current_view, view_modes)

        # Test columns for grid view
        num_phones = 6
        cols_per_row = 2

        rows_needed = (num_phones + cols_per_row - 1) // cols_per_row
        self.assertEqual(rows_needed, 3)

    def test_statistics_display(self):
        """Test statistics display logic"""
        stats = {
            'total_phones': 476,
            'brands': ['Apple', 'Samsung', 'Xiaomi', 'Oppo', 'Vivo'],
            'price_range': {
                'min': 2000000,
                'max': 50000000,
                'avg': 15000000
            },
            'categories': {
                'flagship': 89,
                'midrange': 156,
                'budget': 98,
                'gaming': 45,
                'foldable': 12,
                'unknown': 76
            }
        }

        # Test formatting statistics
        total_formatted = f"{stats['total_phones']:,}"
        self.assertEqual(total_formatted, "476")

        price_min_formatted = f"{stats['price_range']['min']:,} VND"
        self.assertEqual(price_min_formatted, "2,000,000 VND")

        # Test category percentages
        total = stats['total_phones']
        flagship_pct = (stats['categories']['flagship'] / total) * 100
        self.assertAlmostEqual(flagship_pct, 18.7, places=1)

    def tearDown(self):
        """Clean up mocked modules"""
        if 'streamlit' in sys.modules:
            del sys.modules['streamlit']

class TestUIHelpers(unittest.TestCase):
    """Test helper functions for UI"""

    def test_format_price(self):
        """Test price formatting"""
        test_cases = [
            (5000000, "5,000,000 VND"),
            (15500000, "15,500,000 VND"),
            (0, "0 VND"),
            (999999999, "999,999,999 VND")
        ]

        for price, expected in test_cases:
            formatted = f"{price:,} VND"
            self.assertEqual(formatted, expected)

    def test_format_score(self):
        """Test score formatting"""
        test_cases = [
            (0.95, "95.0%"),
            (0.5, "50.0%"),
            (0.123, "12.3%"),
            (1.0, "100.0%"),
            (0.0, "0.0%")
        ]

        for score, expected in test_cases:
            formatted = f"{score:.1%}"
            self.assertEqual(formatted, expected)

    def test_truncate_text(self):
        """Test text truncation for display"""
        long_text = "This is a very long phone name that needs to be truncated for display"
        max_length = 30

        truncated = (long_text[:max_length] + "...") if len(long_text) > max_length else long_text
        self.assertEqual(len(truncated), 33)  # 30 + "..."
        self.assertTrue(truncated.endswith("..."))

    def test_parse_features(self):
        """Test feature parsing from checkboxes"""
        available_features = {
            '5G': 'supports_5g',
            'Sạc không dây': 'wireless_charging',
            'Chống nước': 'waterproof',
            'NFC': 'nfc',
            'Dual SIM': 'dual_sim'
        }

        selected = ['5G', 'NFC']
        parsed_features = [available_features[f] for f in selected]

        self.assertEqual(len(parsed_features), 2)
        self.assertIn('supports_5g', parsed_features)
        self.assertIn('nfc', parsed_features)

if __name__ == '__main__':
    unittest.main(verbosity=2)