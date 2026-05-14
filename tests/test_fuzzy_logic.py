import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inference_engine.fuzzy_logic import PhoneFuzzySystem, FuzzySet


class TestFuzzyLogic(unittest.TestCase):
    """Test Fuzzy Logic System"""

    def setUp(self):
        self.fuzzy_system = PhoneFuzzySystem()

    def test_price_membership(self):
        """Test price fuzzy membership functions"""
        memberships = self.fuzzy_system.get_membership_value(3, self.fuzzy_system.price_sets)
        self.assertAlmostEqual(memberships.get('rất_rẻ', 0), 1.0, places=2)

    def test_battery_membership(self):
        """Test battery fuzzy membership functions"""
        memberships = self.fuzzy_system.get_membership_value(3000, self.fuzzy_system.battery_sets)
        self.assertAlmostEqual(memberships.get('yếu', 0), 1.0, places=2)

    def test_camera_membership(self):
        """Test camera fuzzy membership functions"""
        memberships = self.fuzzy_system.get_membership_value(108, self.fuzzy_system.camera_sets)
        self.assertGreater(memberships.get('chuyên_nghiệp', 0), 0.5)

    def test_ram_membership(self):
        """Test RAM fuzzy membership functions"""
        memberships = self.fuzzy_system.get_membership_value(8, self.fuzzy_system.ram_sets)
        self.assertGreater(memberships.get('cao', 0), 0.5)

    def test_fuzzy_score_calculation(self):
        """Test fuzzy score calculation for phones"""
        phone = {'price': 15000000, 'battery': '5000mAh', 'camera_rear': 64,
                 'ram': '8GB', 'screen_size': 6.5, 'processor': 'Snapdragon 8 Gen 2'}
        score = self.fuzzy_system.calculate_score(phone)
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 1)

    def test_edge_cases(self):
        """Test edge cases"""
        phone = {'price': 0, 'battery': '', 'camera_rear': 0, 'ram': '', 'screen_size': 0, 'processor': ''}
        score = self.fuzzy_system.calculate_score(phone)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)

    def test_user_preference_impact(self):
        """Test that user preferences affect scoring"""
        phone = {'price': 3000000, 'battery': '5000mAh', 'camera_rear': 50,
                 'ram': '4GB', 'screen_size': 6.5, 'processor': 'Helio G99'}
        default_score = self.fuzzy_system.calculate_score(phone)
        with_price_weight = self.fuzzy_system.calculate_score(phone, {'price': 1.0})
        self.assertNotAlmostEqual(default_score, with_price_weight, places=2)

    def test_fuzzy_set_shapes(self):
        """Test fuzzy set membership function shapes"""
        # Triangular: peak at b
        self.assertAlmostEqual(FuzzySet.triangular(5, 0, 5, 10), 1.0)
        self.assertAlmostEqual(FuzzySet.triangular(0, 0, 5, 10), 0.0)
        self.assertAlmostEqual(FuzzySet.triangular(10, 0, 5, 10), 0.0)

        # Trapezoidal: flat top between b and c
        self.assertAlmostEqual(FuzzySet.trapezoidal(3, 0, 2, 5, 7), 1.0)
        self.assertAlmostEqual(FuzzySet.trapezoidal(0, 0, 2, 5, 7), 0.0)
        self.assertAlmostEqual(FuzzySet.trapezoidal(7, 0, 2, 5, 7), 0.0)

    def test_price_bad_score(self):
        """Test that price=0 phones get very low score"""
        memberships = self.fuzzy_system.calculate_memberships({'price': 0})['price']
        self.assertAlmostEqual(memberships.get('rất_rẻ', 0), 0.01)


if __name__ == '__main__':
    unittest.main()
