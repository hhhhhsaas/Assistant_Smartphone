#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fuzzy Logic System for Phone Recommendation
Xử lý các tiêu chí mờ (cảm tính) của người dùng
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import re

class FuzzySet:
    """Định nghĩa tập mờ với các membership functions"""

    @staticmethod
    def triangular(x, a, b, c):
        """Hàm tam giác: a=left, b=peak, c=right"""
        if x <= a or x >= c:
            return 0.0
        elif a < x <= b:
            return (x - a) / (b - a)
        else:  # b < x < c
            return (c - x) / (c - b)

    @staticmethod
    def trapezoidal(x, a, b, c, d):
        """Hàm hình thang: a=left_start, b=left_end, c=right_start, d=right_end"""
        if x <= a or x >= d:
            return 0.0
        elif a < x <= b:
            if b - a == 0:
                return 1.0
            return (x - a) / (b - a)
        elif b < x <= c:
            return 1.0
        else:  # c < x < d
            if d - c == 0:
                return 0.0
            return (d - x) / (d - c)

class PhoneFuzzySystem:
    """Hệ thống logic mờ cho tư vấn điện thoại"""

    def __init__(self):
        """Khởi tạo các tập mờ cho từng thuộc tính"""
        self.initialize_fuzzy_sets()

    def initialize_fuzzy_sets(self):
        """Định nghĩa các tập mờ cho mỗi thuộc tính"""

        # 1. FUZZY SETS CHO GIÁ (triệu VND)
        self.price_sets = {
            'rất_rẻ': lambda x: FuzzySet.trapezoidal(x, 0, 0, 3, 5),  # 0-5 triệu
            'rẻ': lambda x: FuzzySet.triangular(x, 3, 7, 12),  # 3-12 triệu
            'trung_bình': lambda x: FuzzySet.triangular(x, 10, 15, 25),  # 10-25 triệu
            'đắt': lambda x: FuzzySet.triangular(x, 20, 30, 40),  # 20-40 triệu
            'rất_đắt': lambda x: FuzzySet.trapezoidal(x, 35, 45, 100, 100)  # 35+ triệu
        }

        # 2. FUZZY SETS CHO PIN (mAh)
        self.battery_sets = {
            'yếu': lambda x: FuzzySet.trapezoidal(x, 0, 0, 3000, 3500),  # <3500mAh
            'trung_bình': lambda x: FuzzySet.triangular(x, 3000, 4000, 4500),  # 3-4500mAh
            'khỏe': lambda x: FuzzySet.triangular(x, 4000, 4500, 5000),  # 4-5000mAh
            'rất_khỏe': lambda x: FuzzySet.trapezoidal(x, 4800, 5500, 10000, 10000)  # >5000mAh
        }

        # 3. FUZZY SETS CHO CAMERA (MP)
        self.camera_sets = {
            'cơ_bản': lambda x: FuzzySet.trapezoidal(x, 0, 0, 12, 20),  # <20MP
            'tốt': lambda x: FuzzySet.triangular(x, 16, 32, 48),  # 16-48MP
            'rất_tốt': lambda x: FuzzySet.triangular(x, 32, 50, 108),  # 32-108MP
            'chuyên_nghiệp': lambda x: FuzzySet.trapezoidal(x, 64, 108, 500, 500)  # >64MP
        }

        # 4. FUZZY SETS CHO TRỌNG LƯỢNG (grams)
        self.weight_sets = {
            'nhẹ': lambda x: FuzzySet.trapezoidal(x, 0, 0, 150, 175),  # <175g
            'vừa': lambda x: FuzzySet.triangular(x, 160, 185, 210),  # 160-210g
            'hơi_nặng': lambda x: FuzzySet.triangular(x, 195, 220, 250),  # 195-250g
            'nặng': lambda x: FuzzySet.trapezoidal(x, 240, 270, 500, 500)  # >240g
        }

        # 5. FUZZY SETS CHO RAM (GB)
        self.ram_sets = {
            'thấp': lambda x: FuzzySet.trapezoidal(x, 0, 0, 3, 4),  # <4GB
            'đủ_dùng': lambda x: FuzzySet.triangular(x, 3, 6, 10),  # 4-8GB
            'cao': lambda x: FuzzySet.triangular(x, 6, 8, 12),  # 8-12GB
            'rất_cao': lambda x: FuzzySet.trapezoidal(x, 12, 16, 64, 64)  # >12GB
        }

        # 6. FUZZY SETS CHO MÀN HÌNH (inches)
        self.screen_sets = {
            'nhỏ': lambda x: FuzzySet.trapezoidal(x, 0, 0, 5.5, 6.0),  # <6"
            'vừa': lambda x: FuzzySet.triangular(x, 5.8, 6.2, 6.5),  # 5.8-6.5"
            'lớn': lambda x: FuzzySet.triangular(x, 6.3, 6.7, 7.0),  # 6.3-7"
            'rất_lớn': lambda x: FuzzySet.trapezoidal(x, 6.8, 7.2, 10, 10)  # >7"
        }

        # 7. FUZZY SETS CHO HIỆU NĂNG (based on processor/chipset)
        self.performance_categories = {
            'snapdragon 8': 'rất_mạnh',
            'a19 pro': 'rất_mạnh',
            'a18 pro': 'rất_mạnh',
            'a19': 'mạnh',
            'a18': 'mạnh',
            'a17': 'mạnh',
            'a16': 'mạnh',
            'dimensity 9000': 'mạnh',
            'exynos 2': 'mạnh',
            'snapdragon 7': 'trung_bình',
            'dimensity 8': 'trung_bình',
            'dimensity 7': 'trung_bình',
            'helio g': 'yếu',
            'dimensity 6': 'yếu'
        }

    def extract_ram_value(self, ram_str: str) -> float:
        """Trích xuất giá trị RAM từ string"""
        try:
            if isinstance(ram_str, str):
                match = re.search(r'(\d+)', ram_str)
                if match:
                    return float(match.group(1))
            return float(ram_str)
        except:
            return 0

    def extract_battery_value(self, battery_str: str) -> float:
        """Trích xuất giá trị pin từ string"""
        try:
            if isinstance(battery_str, str):
                match = re.search(r'(\d+)', battery_str)
                if match:
                    return float(match.group(1))
            return float(battery_str)
        except:
            return 0

    def get_membership_value(self, value: float, sets_dict: Dict) -> Dict[str, float]:
        """Tính độ thuộc của giá trị vào từng tập mờ"""
        memberships = {}
        for set_name, fuzzy_func in sets_dict.items():
            memberships[set_name] = fuzzy_func(value)
        return memberships

    def calculate_memberships(self, phone_data: Dict) -> Dict:
        """Tính fuzzy membership cho một điện thoại"""
        memberships = {}

        # 1. Giá (triệu VND)
        price = phone_data.get('price', 0)
        if price and price > 0:
            price_million = float(price) / 1000000
            memberships['price'] = self.get_membership_value(price_million, self.price_sets)
        else:
            memberships['price'] = {'rất_rẻ': 0.01}  # price=0 → điểm rất thấp

        # 2. Pin (mAh)
        battery = phone_data.get('battery', '')
        battery_mah = self.extract_battery_value(battery)
        if battery_mah > 0:
            memberships['battery'] = self.get_membership_value(battery_mah, self.battery_sets)
        else:
            memberships['battery'] = {}

        # 3. Camera (MP)
        camera = phone_data.get('camera_rear', 0)
        try:
            camera_mp = float(camera) if camera else 0
            if camera_mp > 0:
                memberships['camera'] = self.get_membership_value(camera_mp, self.camera_sets)
            else:
                memberships['camera'] = {}
        except:
            memberships['camera'] = {}

        # 4. RAM (GB)
        ram = phone_data.get('ram', '')
        ram_gb = self.extract_ram_value(ram)
        if ram_gb > 0:
            memberships['ram'] = self.get_membership_value(ram_gb, self.ram_sets)
        else:
            memberships['ram'] = {}

        # 5. Màn hình (inches)
        screen_size = phone_data.get('screen_size', 0)
        try:
            screen_inches = float(screen_size) if screen_size else 0
            if screen_inches > 0:
                memberships['screen'] = self.get_membership_value(screen_inches, self.screen_sets)
            else:
                memberships['screen'] = {}
        except:
            memberships['screen'] = {}

        # 6. Hiệu năng (từ processor)
        processor = phone_data.get('processor', '').lower()
        performance_level = 'trung_bình'  # default
        for key, level in self.performance_categories.items():
            if key in processor:
                performance_level = level
                break
        memberships['performance'] = {performance_level: 1.0}

        return memberships

    def calculate_price_budget_fitness(self, phone_price: float, budget: float) -> float:
        """Tính price fitness dựa trên tỷ lệ giá/ngân sách.
        Phone nằm trong khoảng 50-100% budget được điểm cao nhất.
        Quá rẻ (<30% budget) bị giảm điểm vì thiếu tính năng.
        Vượt budget bị giảm nhanh."""
        if not budget or budget <= 0 or not phone_price or phone_price <= 0:
            return 0.0
        ratio = phone_price / budget
        if ratio <= 0.3:
            return 0.3 + (ratio / 0.3) * 0.3
        elif ratio <= 0.5:
            return 0.6 + ((ratio - 0.3) / 0.2) * 0.3
        elif ratio <= 1.0:
            return 0.9 + ((ratio - 0.5) / 0.5) * 0.1
        elif ratio <= 1.1:
            return 1.0 - ((ratio - 1.0) / 0.1) * 0.3
        else:
            return max(0.0, 0.7 - (ratio - 1.1) * 2)

    def calculate_score(self, phone_data: Dict, user_preferences: Dict = None,
                        budget: float = None) -> float:
        """Tính điểm fuzzy tổng hợp cho điện thoại"""
        memberships = self.calculate_memberships(phone_data)

        # Trọng số mặc định
        default_weights = {
            'price': 0.20,
            'battery': 0.20,
            'camera': 0.20,
            'ram': 0.15,
            'screen': 0.10,
            'performance': 0.15
        }

        # Sử dụng trọng số từ người dùng nếu có
        weights = user_preferences if user_preferences else default_weights

        total_score = 0
        total_weight = 0

        for criterion, weight in weights.items():
            if criterion == 'price' and budget and budget > 0:
                price_fitness = self.calculate_price_budget_fitness(
                    phone_data.get('price', 0), budget)
                total_score += price_fitness * weight
                total_weight += weight
            elif criterion in memberships and memberships[criterion]:
                max_membership = max(memberships[criterion].values())
                total_score += max_membership * weight
                total_weight += weight

        # Normalize score
        if total_weight > 0:
            total_score = total_score / total_weight

        return total_score

    def calculate_detailed_score(self, phone_data: Dict, user_preferences: Dict = None,
                                   budget: float = None) -> Dict:
        """Tính điểm chi tiết từng tiêu chí với giải thích"""
        memberships = self.calculate_memberships(phone_data)

        default_weights = {
            'price': 0.20, 'battery': 0.20, 'camera': 0.20,
            'ram': 0.15, 'screen': 0.10, 'performance': 0.15
        }
        weights = user_preferences if user_preferences else default_weights

        breakdown = {}

        for criterion, weight in weights.items():
            if criterion == 'price' and budget and budget > 0:
                price_fitness = self.calculate_price_budget_fitness(
                    phone_data.get('price', 0), budget)
                reason = self._get_score_reason(criterion, phone_data, price_fitness)
                breakdown[criterion] = {
                    'weight': weight,
                    'score': price_fitness,
                    'weighted_score': price_fitness * weight,
                    'reason': reason
                }
            elif criterion in memberships and memberships[criterion]:
                max_membership = max(memberships[criterion].values())
                reason = self._get_score_reason(criterion, phone_data, max_membership)
                breakdown[criterion] = {
                    'weight': weight,
                    'score': max_membership,
                    'weighted_score': max_membership * weight,
                    'reason': reason
                }
            else:
                breakdown[criterion] = {
                    'weight': weight,
                    'score': 0,
                    'weighted_score': 0,
                    'reason': 'Không có dữ liệu'
                }

        return breakdown
    
    def _get_score_reason(self, criterion: str, phone: Dict, score: float) -> str:
        """Tạo giải thích cho từng tiêu chí"""
        if criterion == 'performance':
            chip = phone.get('processor', phone.get('chip', ''))
            if '8 gen 3' in chip.lower() or '8 gen 2' in chip.lower():
                return f"Chip {chip} hiệu năng cao"
            elif '8 gen 1' in chip.lower() or '7 gen' in chip.lower():
                return f"Chip {chip} hiệu năng tốt"
            return f"Chip {chip}"
        elif criterion == 'battery':
            bat = phone.get('battery', 0)
            return f"Pin {bat}mAh"
        elif criterion == 'ram':
            ram = phone.get('ram', 'Unknown')
            return f"RAM {ram}"
        elif criterion == 'screen':
            size = phone.get('screen_size', '')
            return f"Màn hình {size}\""
        elif criterion == 'camera':
            cam = phone.get('camera_main', '')
            return f"Camera {cam}MP"
        elif criterion == 'price':
            price = phone.get('price', 0)
            return f"Giá {price:,.0f} VND"
        return "Không rõ"

    def apply_rules(self, phone_data: Dict, user_requirements: Dict) -> Dict:
        """Áp dụng luật suy luận dựa trên yêu cầu người dùng"""
        memberships = self.calculate_memberships(phone_data)
        results = {
            'matches': [],
            'score': 0,
            'explanation': []
        }

        # Rule 1: Nếu người dùng cần "pin trâu"
        if user_requirements.get('battery') == 'khỏe':
            if memberships.get('battery'):
                battery_score = memberships['battery'].get('khỏe', 0) + \
                               memberships['battery'].get('rất_khỏe', 0)
                if battery_score > 0.5:
                    results['matches'].append('pin_khỏe')
                    results['explanation'].append(f"Pin khỏe (score: {battery_score:.2f})")

        # Rule 2: Nếu người dùng cần "camera xịn"
        if user_requirements.get('camera') == 'tốt':
            if memberships.get('camera'):
                camera_score = memberships['camera'].get('rất_tốt', 0) + \
                              memberships['camera'].get('chuyên_nghiệp', 0)
                if camera_score > 0.5:
                    results['matches'].append('camera_tốt')
                    results['explanation'].append(f"Camera chất lượng cao (score: {camera_score:.2f})")

        # Rule 3: Nếu người dùng cần "máy nhẹ"
        if user_requirements.get('weight') == 'nhẹ':
            # Giả định trọng lượng dựa trên loại máy
            if phone_data.get('category') != 'gaming':
                results['matches'].append('máy_nhẹ')
                results['explanation'].append("Thiết kế gọn nhẹ")

        # Rule 4: Nếu người dùng cần "giá rẻ"
        if user_requirements.get('price') == 'rẻ':
            if memberships.get('price'):
                price_score = memberships['price'].get('rất_rẻ', 0) + \
                             memberships['price'].get('rẻ', 0)
                if price_score > 0.5:
                    results['matches'].append('giá_rẻ')
                    results['explanation'].append(f"Giá phải chăng (score: {price_score:.2f})")

        # Rule 5: Nếu người dùng cần "hiệu năng cao"
        if user_requirements.get('performance') == 'mạnh':
            if memberships.get('performance'):
                perf_score = memberships['performance'].get('mạnh', 0) + \
                            memberships['performance'].get('rất_mạnh', 0)
                if perf_score > 0.5:
                    results['matches'].append('hiệu_năng_cao')
                    results['explanation'].append(f"Hiệu năng mạnh mẽ (score: {perf_score:.2f})")

        # Rule 6: Nếu người dùng cần "màn hình lớn"
        if user_requirements.get('screen') == 'lớn':
            if memberships.get('screen'):
                screen_score = memberships['screen'].get('lớn', 0) + \
                              memberships['screen'].get('rất_lớn', 0)
                if screen_score > 0.5:
                    results['matches'].append('màn_hình_lớn')
                    results['explanation'].append(f"Màn hình lớn phù hợp xem phim (score: {screen_score:.2f})")

        # Tính điểm tổng hợp
        results['score'] = len(results['matches']) / max(len(user_requirements), 1)

        return results

def demonstrate_fuzzy_system():
    """Demo hệ thống fuzzy logic"""
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("="*60)
    print("FUZZY LOGIC SYSTEM DEMO")
    print("="*60)

    # Khởi tạo system
    fuzzy = PhoneFuzzySystem()

    # Test phones
    test_phones = [
        {
            "name": "iPhone 17 Pro Max",
            "brand": "Apple",
            "price": 38000000,
            "battery": "4500mAh",
            "camera_rear": 48,
            "ram": "8GB",
            "processor": "Chip A19 Pro",
            "category": "flagship"
        },
        {
            "name": "Samsung Galaxy A15",
            "brand": "Samsung",
            "price": 4990000,
            "battery": "5000mAh",
            "camera_rear": 50,
            "ram": "8GB",
            "processor": "MediaTek G99",
            "category": "entry"
        },
        {
            "name": "Xiaomi Redmi Note 13",
            "brand": "Xiaomi",
            "price": 6500000,
            "battery": "5000mAh",
            "camera_rear": 108,
            "ram": "8GB",
            "processor": "Snapdragon 7 Gen 1",
            "category": "budget"
        }
    ]

    # Test fuzzy memberships
    print("\n1. TÍNH ĐỘ THUỘC (MEMBERSHIPS)")
    print("-" * 40)

    for phone in test_phones:
        print(f"\n📱 {phone['name']}")
        memberships = fuzzy.calculate_memberships(phone)

        # Hiển thị độ thuộc giá
        if memberships.get('price'):
            print("  Giá:")
            for set_name, value in memberships['price'].items():
                if value > 0:
                    print(f"    - {set_name}: {value:.2f}")

        # Hiển thị độ thuộc camera
        if memberships.get('camera'):
            print("  Camera:")
            for set_name, value in memberships['camera'].items():
                if value > 0:
                    print(f"    - {set_name}: {value:.2f}")

        # Hiển thị độ thuộc pin
        if memberships.get('battery'):
            print("  Pin:")
            for set_name, value in memberships['battery'].items():
                if value > 0:
                    print(f"    - {set_name}: {value:.2f}")

    # Test scoring
    print("\n2. TÍNH ĐIỂM TỔNG HỢP")
    print("-" * 40)

    for phone in test_phones:
        score = fuzzy.calculate_score(phone)
        print(f"📱 {phone['name']}: {score:.3f}")

    # Test rules
    print("\n3. ÁP DỤNG LUẬT SUY LUẬN")
    print("-" * 40)

    user_requirements = {
        'battery': 'khỏe',
        'camera': 'tốt',
        'price': 'rẻ',
        'performance': 'mạnh'
    }

    print(f"Yêu cầu người dùng: {user_requirements}")
    print()

    for phone in test_phones:
        results = fuzzy.apply_rules(phone, user_requirements)
        print(f"📱 {phone['name']}")
        print(f"  Điểm phù hợp: {results['score']:.2f}")
        if results['explanation']:
            print(f"  Giải thích:")
            for exp in results['explanation']:
                print(f"    - {exp}")
        else:
            print(f"  Không đáp ứng yêu cầu")

if __name__ == "__main__":
    demonstrate_fuzzy_system()