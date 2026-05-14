"""
Knowledge Base — Rules (Luật)
Chứa tất cả luật của hệ chuyên gia, tách biệt khỏi Inference Engine.
"""

from typing import Dict, List, Optional


class Rule:
    def __init__(self, rule_id: str, description: str, conditions: Dict,
                 actions: Dict, priority: int = 1):
        self.id = rule_id
        self.description = description
        self.conditions = conditions
        self.actions = actions
        self.priority = priority

    def evaluate(self, facts: Dict) -> bool:
        for key, expected_value in self.conditions.items():
            if key not in facts:
                return False
            fact_value = facts[key]
            if isinstance(expected_value, dict):
                if 'min' in expected_value:
                    if isinstance(fact_value, list):
                        if len(fact_value) < expected_value['min']:
                            return False
                    else:
                        if fact_value < expected_value['min']:
                            return False
                if 'max' in expected_value:
                    if isinstance(fact_value, list):
                        if len(fact_value) > expected_value['max']:
                            return False
                    else:
                        if fact_value > expected_value['max']:
                            return False
                if 'in' in expected_value and fact_value not in expected_value['in']:
                    return False
                if 'contains' in expected_value:
                    if isinstance(fact_value, list):
                        if expected_value['contains'] not in fact_value:
                            return False
                    elif expected_value['contains'] not in str(fact_value).lower():
                        return False
            else:
                if fact_value != expected_value:
                    return False
        return True

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'description': self.description,
            'conditions': self.conditions,
            'actions': self.actions,
            'priority': self.priority,
        }

    @staticmethod
    def from_dict(d: Dict) -> 'Rule':
        return Rule(
            rule_id=d['id'],
            description=d['description'],
            conditions=d['conditions'],
            actions=d['actions'],
            priority=d.get('priority', 1),
        )


class ClassificationRule:
    """Rule phân loại điện thoại (gaming, flagship, foldable, ...)
    Dùng để gán category cho phone facts trong Knowledge Base.
    """
    def __init__(self, rule_id: str, category: str,
                 field: str, match_type: str,
                 keywords: List[str] = None,
                 min_val: float = None, max_val: float = None):
        self.id = rule_id
        self.category = category
        self.field = field
        self.match_type = match_type  # 'keyword', 'contains', 'range', 'feature_keyword'
        self.keywords = keywords or []
        self.min_val = min_val
        self.max_val = max_val

    def evaluate(self, phone_data: Dict) -> bool:
        val = str(phone_data.get(self.field, '')).lower()
        if self.match_type == 'keyword':
            return any(kw in val for kw in self.keywords)
        if self.match_type == 'feature_keyword':
            feat = str(phone_data.get('special_features', '')).lower()
            return any(kw in feat for kw in self.keywords)
        if self.match_type == 'range':
            price = phone_data.get('price', 0) or 0
            if price <= 0:  # price=0 means Liên Hệ, don't classify by price
                return False
            if self.min_val is not None and price < self.min_val:
                return False
            if self.max_val is not None and price > self.max_val:
                return False
            return True
        if self.match_type == 'ram_threshold':
            ram_gb = 0
            try:
                import re
                m = re.search(r'(\d+)', str(phone_data.get('ram', '')))
                if m:
                    ram_gb = int(m.group(1))
            except (ValueError, TypeError):
                pass
            return ram_gb >= self.min_val if self.min_val else False
        return False


def get_classification_rules() -> List[ClassificationRule]:
    """Rules for classifying phones into categories (run during indexing)"""
    return [
        # Gaming — name keywords
        ClassificationRule("CLS_GAMING_NAME", "gaming",
                           "name", "keyword",
                           keywords=['gaming', 'rog', 'red magic', 'redmagic',
                                     'black shark', 'legion']),
        # Gaming — special features mentions gaming
        ClassificationRule("CLS_GAMING_FEATURE", "gaming",
                           "special_features", "feature_keyword",
                           keywords=['gaming', 'chơi game']),
        # Foldable
        ClassificationRule("CLS_FOLDABLE", "foldable",
                           "name", "keyword",
                           keywords=['fold', 'flip', 'galaxy z', 'razr',
                                     'find n', 'find n2', 'mix fold',
                                     'magic v', 'x fold']),
        # Flagship by price: Trên 20 triệu
        ClassificationRule("CLS_FLAGSHIP_PRICE", "flagship",
                           "price", "range", min_val=20000000),
        # Upper Midrange by price: 10-20 triệu
        ClassificationRule("CLS_UPPER_MIDRANGE_PRICE", "midrange",
                           "price", "range", min_val=10000000, max_val=19999999),
        # Midrange by price: 5-10 triệu
        ClassificationRule("CLS_MIDRANGE_PRICE", "midrange",
                           "price", "range", min_val=5000000, max_val=9999999),
        # Budget by price: Dưới 5 triệu
        ClassificationRule("CLS_BUDGET_PRICE", "budget",
                           "price", "range", min_val=0, max_val=4999999),
        # No price (Liên Hệ) — estimate by RAM before entry-by-price
        ClassificationRule("CLS_FLAGSHIP_RAM", "flagship",
                           "ram", "ram_threshold", min_val=12),
        ClassificationRule("CLS_MIDRANGE_RAM", "midrange",
                           "ram", "ram_threshold", min_val=8),
        ClassificationRule("CLS_BUDGET_RAM", "budget",
                           "ram", "ram_threshold", min_val=4),
        # Entry by price: Dưới 5 triệu (giá rẻ)
        ClassificationRule("CLS_ENTRY_PRICE", "entry",
                           "price", "range", max_val=4999999),
    ]


def get_default_rules() -> List[Rule]:
    return [
        # R1: Gaming FALLBACK (không có ngân sách - Priority thấp nhất)
        Rule("R1_GAMING",
             "Nếu người dùng chơi game (không có ngân sách) → Gaming trung bình khá",
             conditions={"user_need": "gaming"},
             # SOFT FILTER: Dùng list thay vì single value để mở rộng tìm kiếm
             actions={"category_filter": ["gaming", "midrange", "flagship"],
                      "min_ram": "8GB",
                      "min_processor_tier": "upper-mid",
                      "preferred_features": ["High RAM", "High Performance"],
                      "explanation": "Chọn máy gaming với RAM 8GB+, chip upper-mid trở lên"},
             priority=3),  # Priority thấp nhất - chỉ chạy khi không có budget

        # R1A: Gaming ngân sách cao (>15 triệu) - Ưu tiên Chip Flagship + Màn hình 120Hz+
        Rule("R1A_GAMING_HIGH_BUDGET",
             "Nếu người dùng chơi game + ngân sách >15 triệu → Flagship Gaming",
             conditions={"user_need": "gaming", "budget": {"min": 15000000}},
             actions={"category_filter": ["gaming", "flagship"],
                      "min_ram": "12GB",
                      "min_processor_tier": "high",
                      "min_refresh_rate": 120,
                      "preferred_features": ["High RAM", "High Performance", "High Refresh Rate"],
                      "explanation": "Với ngân sách trên 15 triệu, bạn cần máy gaming flagship với chip mạnh và màn hình 120Hz+"},
             priority=10),

        # R1B: Gaming ngân sách trung bình (10-15 triệu) - Cân bằng hiệu năng và pin
        Rule("R1B_GAMING_MID_BUDGET",
             "Nếu người dùng chơi game + ngân sách 10-15 triệu → Gaming tầm trung cao",
             conditions={"user_need": "gaming", "budget": {"min": 10000000, "max": 15000000}},
             actions={"category_filter": ["gaming", "midrange"],
                      "min_ram": "8GB",
                      "min_processor_tier": "upper-mid",
                      "min_refresh_rate": 90,
                      "min_battery": 5000,
                      "preferred_features": ["High RAM", "High Performance"],
                      "explanation": "Với ngân sách 10-15 triệu, bạn cần máy gaming có chip mạnh, pin trâu và RAM từ 8GB"},
             priority=9),

        # R1C: Gaming ngân sách thấp (<10 triệu) - Ưu tiên Pin + RAM, giảm yêu cầu chip
        Rule("R1C_GAMING_LOW_BUDGET",
             "Nếu người dùng chơi game + ngân sách <10 triệu → Gaming giá rẻ",
             conditions={"user_need": "gaming", "budget": {"max": 10000000}},
             actions={"category_filter": ["gaming", "budget"],
                      "min_ram": "8GB",
                      "min_battery": 5000,
                      "min_processor_tier": "mid",
                      "preferred_features": ["High RAM", "High Battery"],
                      "explanation": "Với ngân sách dưới 10 triệu, ưu tiên pin trâu 5000mAh+ và RAM 8GB+ để chơi game mượt"},
             priority=8),

        # R2: Photography ngân sách cao (>15 triệu) - Flagship camera
        Rule("R2_PHOTOGRAPHY_HIGH",
             "Nếu người dùng thích chụp ảnh + ngân sách cao → Flagship Camera",
             conditions={"user_need": "photography", "budget": {"min": 15000000}},
             actions={"min_camera_mp": 50,
                      "required_camera_ois": True,
                      "required_camera_night": True,
                      "preferred_brands": ["Apple", "Samsung", "Google", "OPPO"],
                      "explanation": "Với ngân sách trên 15 triệu, bạn cần điện thoại flagship với camera 50MP+, OIS và chế độ chụp đêm"},
             priority=10),

        # R2A: Photography ngân sách trung (8-15 triệu) - Camera tốt, giá hợp lý
        Rule("R2A_PHOTOGRAPHY_MID",
             "Nếu người dùng thích chụp ảnh + ngân sách trung → Camera khá",
             conditions={"user_need": "photography", "budget": {"min": 8000000, "max": 15000000}},
             actions={"min_camera_mp": 48,
                      "preferred_brands": ["Apple", "Samsung", "Google", "OPPO", "Xiaomi"],
                      "explanation": "Với ngân sách 8-15 triệu, bạn cần điện thoại có camera từ 48MP trở lên"},
             priority=9),

        # R2B: Photography ngân sách thấp (<8 triệu) - Camera khá, giá rẻ
        Rule("R2B_PHOTOGRAPHY_BUDGET",
             "Nếu người dùng thích chụp ảnh ngân sách thấp → Camera khá",
             conditions={"user_need": "photography", "budget": {"max": 8000000}},
             actions={"min_camera_mp": 32,
                      "preferred_brands": ["Xiaomi", "OPPO", "Vivo", "Realme"],
                      "explanation": "Với ngân sách dưới 8 triệu, chọn máy có camera từ 32MP, ưu tiên Xiaomi/Realme"},
             priority=7),

        # ═══ BATTERY (PIN TRÂU) THEO NGÂN SÁCH ═══
        # R3A: Battery cao cấp (>15 triệu) - Pin lớn + sạc nhanh + chip tiết kiệm
        Rule("R3A_BATTERY_HIGH",
             "Nếu cần pin trâu + ngân sách cao → Flagship pin khủng",
             conditions={"user_need": "battery_life", "budget": {"min": 15000000}},
             actions={"min_battery": 5000,
                     "min_processor_tier": "high",  # Chip tiết kiệm
                     "category_filter": ["flagship", "midrange"],
                     "explanation": "Với ngân sách trên 15 triệu, chọn pin 5000mAh+ và chip tiết kiệm"},
             priority=10),

        # R3B: Battery trung (8-15 triệu) - Pin rất lớn, giá hợp lý
        Rule("R3B_BATTERY_MID",
             "Nếu cần pin trâu + ngân sách trung → Pin khủng giá tốt",
             conditions={"user_need": "battery_life", "budget": {"min": 8000000, "max": 15000000}},
             actions={"min_battery": 5500,
                     "min_processor_tier": "mid",
                     "category_filter": ["midrange", "budget"],
                     "explanation": "Với ngân sách 8-15 triệu, ưu tiên pin 5500mAh+"},
             priority=9),

        # R3C: Battery thấp (<8 triệu) - Pin cực lớn, spec khác thấp
        Rule("R3C_BATTERY_LOW",
             "Nếu cần pin trâu + ngân sách thấp → Pin cực lớn",
             conditions={"user_need": "battery_life", "budget": {"max": 8000000}},
             actions={"min_battery": 6000,
                     "min_processor_tier": "mid",
                     "category_filter": ["budget", "entry"],
                     "preferred_brands": ["Xiaomi", "Realme", "OPPO"],
                     "explanation": "Với ngân sách dưới 8 triệu, chọn pin 6000mAh+ cho dùng cả ngày"},
             priority=8),

        # R3: Battery FALLBACK (không có ngân sách)
        Rule("R3_BATTERY",
             "Nếu người dùng cần pin lâu (không có ngân sách)",
             conditions={"user_need": "battery_life"},
             actions={"min_battery": 4500, "preferred_features": ["High Battery"],
                      "category_filter": ["midrange", "flagship", "budget"],
                      "explanation": "Bạn cần điện thoại có pin từ 4500mAh trở lên"},
             priority=4),  # Priority thấp - fallback

        # R4: Budget low
        Rule("R4_BUDGET",
             "Nếu ngân sách < 5 triệu → Tìm máy giá rẻ",
             conditions={"budget": {"max": 5000000}},
             actions={"category_filter": ["entry", "budget"],
                      "preferred_brands": ["Xiaomi", "Realme", "OPPO", "Nokia"],
                      "explanation": "Với ngân sách dưới 5 triệu, tìm điện thoại phân khúc giá rẻ"},
             priority=7),

        # R4b: Budget mid
        Rule("R4B_BUDGET_MID",
             "Nếu ngân sách 5-10 triệu → Máy tầm trung giá rẻ",
             conditions={"budget": {"min": 5000000, "max": 10000000}},
             actions={"category_filter": ["budget", "midrange"], "min_ram": "6GB",
                      "explanation": "Với ngân sách 5-10 triệu, tìm điện thoại pin tốt, cấu hình ổn"},
             priority=6),

        # R5: Apple
        Rule("R5_APPLE_FAN",
             "Nếu thích Apple → Ưu tiên iPhone",
             conditions={"preferred_brand": "Apple"},
             actions={"brand_filter": "Apple",
                      "explanation": "Ưu tiên các sản phẩm iPhone theo yêu cầu"},
             priority=6),

        # R6: Flagship
        Rule("R6_FLAGSHIP",
             "Nếu ngân sách > 25 triệu và cần cao cấp → Flagship",
             conditions={"budget": {"min": 25000000}, "user_need": "premium"},
             actions={"category_filter": "flagship",
                      "preferred_brands": ["Apple", "Samsung"],
                      "explanation": "Tìm điện thoại flagship cao cấp nhất"},
             priority=10),

        # R7: Office (bỏ max — R13_BUSINESS xử lý budget cao)
        Rule("R7_OFFICE",
             "Nếu dùng cho văn phòng → Máy tầm trung, pin tốt",
             conditions={"user_need": "office",
                         "budget": {"min": 5000000}},
             actions={"category_filter": "midrange", "min_battery": 4000,
                      "min_ram": "8GB",
                      "explanation": "Điện thoại tầm trung, đủ dùng cho công việc văn phòng"},
             priority=5),

        # R16: General mid-high budget (không có user_need cụ thể)
        Rule("R16_GENERAL",
             "Ngân sách 10-25 triệu, không nhu cầu đặc biệt → Tầm trung-cao cấp",
             conditions={"budget": {"min": 10000000, "max": 25000000}},
             actions={"category_filter": ["midrange", "flagship"],
                      "explanation": "Với ngân sách 10-25 triệu, tìm điện thoại tầm trung đến cao cấp"},
             priority=4),

        # R8: Foldable
        Rule("R8_FOLDABLE",
             "Nếu thích công nghệ mới → Màn hình gập",
             conditions={"user_need": "innovation", "budget": {"min": 25000000}},
             actions={"category_filter": "foldable",
                      "preferred_brands": ["Samsung"],
                      "explanation": "Điện thoại màn hình gập với công nghệ tiên tiến"},
             priority=9),

        # R9: Student (UI set user_need=student, không phải user_type)
        Rule("R9_STUDENT",
             "Nếu là học sinh/sinh viên → Máy giá phải chăng",
             conditions={"user_need": "student", "budget": {"max": 10000000}},
             actions={"category_filter": ["budget", "entry"], "min_ram": "6GB",
                      "explanation": "Điện thoại phù hợp cho học sinh/sinh viên với giá phải chăng"},
             priority=6),

        # ═══ MEDIA (XEM PHIM) THEO NGÂN SÁCH ═══
        # R10A: Media cao cấp (>15 triệu) - Màn hình 120Hz+, OLED, Loa stereo
        Rule("R10A_MEDIA_HIGH",
             "Nếu xem phim + ngân sách cao → Flagship giải trí",
             conditions={"user_need": "media", "budget": {"min": 15000000}},
             actions={"min_screen_size": 6.6, "min_refresh_rate": 120,
                      "min_battery": 4500,
                      "category_filter": ["flagship", "midrange"],
                      "explanation": "Với ngân sách trên 15 triệu, chọn màn hình 120Hz+, pin trâu"},
             priority=10),

        # R10B: Media trung (8-15 triệu) - Màn hình lớn, pin tốt
        Rule("R10B_MEDIA_MID",
             "Nếu xem phim + ngân sách trung → Media tầm trung",
             conditions={"user_need": "media", "budget": {"min": 8000000, "max": 15000000}},
             actions={"min_screen_size": 6.5, "min_battery": 4500,
                      "category_filter": ["midrange", "flagship"],
                      "explanation": "Với ngân sách 8-15 triệu, chọn máy màn hình 6.5\"+, pin 4500mAh+"},
             priority=9),

        # R10C: Media thấp (<8 triệu) - Pin tốt, màn hình hiển thị tốt
        Rule("R10C_MEDIA_LOW",
             "Nếu xem phim + ngân sách thấp → Media giá rẻ",
             conditions={"user_need": "media", "budget": {"max": 8000000}},
             actions={"min_screen_size": 6.0, "min_battery": 5000,
                      "category_filter": ["midrange", "budget"],
                      "explanation": "Với ngân sách dưới 8 triệu, ưu tiên pin trâu 5000mAh+"},
             priority=8),

        # R10: Media FALLBACK (không có ngân sách)
        Rule("R10_MEDIA",
             "Nếu người dùng xem phim / giải trí (không có ngân sách)",
             conditions={"user_need": "media"},
             actions={"min_screen_size": 6.5, "min_battery": 4500,
                      "preferred_features": ["High Battery"],
                      "category_filter": ["midrange", "flagship", "gaming"],
                      "explanation": "Bạn cần điện thoại màn hình lớn từ 6.5\" trở lên, pin tốt để xem phim"},
             priority=4),  # Priority thấp - fallback

        # R11: 5G
        Rule("R11_5G",
             "Nếu cần 5G → Lọc máy hỗ trợ 5G",
             conditions={"network": "5G"},
             actions={"required_features": ["5G"],
                      "explanation": "Chỉ tìm điện thoại hỗ trợ mạng 5G"},
             priority=4),

        # R12: Selfie
        Rule("R12_SELFIE",
             "Nếu người dùng thích chụp ảnh selfie → Camera trước tốt",
             conditions={"user_need": "selfie"},
             actions={"min_camera_front_mp": 16,
                      "preferred_brands": ["OPPO", "Vivo", "Apple", "Samsung"],
                      "explanation": "Bạn cần điện thoại có camera trước từ 16MP trở lên để selfie đẹp"},
             priority=7),

        # R13: Business (UI set user_need=business)
        Rule("R13_BUSINESS",
             "Nếu doanh nhân / chuyên nghiệp → Máy cao cấp, bảo mật",
             conditions={"user_need": "business"},
             actions={"category_filter": ["flagship", "midrange"], "min_ram": "8GB",
                      "preferred_brands": ["Apple", "Samsung"],
                      "explanation": "Điện thoại cao cấp phù hợp cho doanh nhân"},
             priority=7),

        # R14: Outdoor / durable
        Rule("R14_DURABLE",
             "Nếu người dùng cần máy bền / đi rừng → Pin khủng, cấu hình ổn",
             conditions={"user_need": "outdoor"},
             actions={"min_battery": 5000,
                      "category_filter": ["entry", "budget"],
                      "explanation": "Điện thoại pin khủng, bền bỉ phù hợp đi rừng"},
             priority=6),

        # R15: Lightweight
        Rule("R15_LIGHTWEIGHT",
             "Nếu người dùng cần máy nhẹ → Dưới 180g",
             conditions={"user_need": "lightweight"},
             actions={"max_weight": 180,
                      "category_filter": ["entry", "midrange", "flagship"],
                      "explanation": "Điện thoại gọn nhẹ dưới 180g"},
             priority=5),

        # R17: NFC
        Rule("R17_NFC",
             "Nếu cần NFC → Lọc máy hỗ trợ NFC",
             conditions={"need_nfc": True},
             actions={"required_nfc": True,
                      "explanation": "Chỉ tìm điện thoại hỗ trợ NFC thanh toán không tiếp xúc"},
             priority=4),

        # R18: Water Resistant
        Rule("R18_WATER_RESISTANT",
             "Nếu cần chống nước → Lọc máy kháng nước",
             conditions={"user_need": "water_resistant"},
             actions={"required_water_resistant": True,
                      "explanation": "Chỉ tìm điện thoại có khả năng chống nước IP68"},
             priority=6),

        # R19: Wireless Charging
        Rule("R19_WIRELESS_CHARGING",
             "Nếu cần sạc không dây → Lọc máy hỗ trợ sạc không dây",
             conditions={"need_wireless_charging": True},
             actions={"required_wireless_charging": True,
                      "explanation": "Chỉ tìm điện thoại hỗ trợ sạc không dây tiện lợi"},
             priority=4),

        # R20: Headphone Jack
        Rule("R20_HEADPHONE_JACK",
             "Nếu cần jack tai nghe 3.5mm → Lọc máy có jack tai nghe",
             conditions={"need_headphone_jack": True},
             actions={"required_headphone_jack": True,
                      "explanation": "Chỉ tìm điện thoại có jack tai nghe 3.5mm"},
             priority=4),

        # R21: Expandable Storage
        Rule("R21_EXPANDABLE_STORAGE",
             "Nếu cần thẻ nhớ mở rộng → Lọc máy hỗ trợ thẻ nhớ",
             conditions={"need_expandable_storage": True},
             actions={"required_memory_card_slot": True,
                      "explanation": "Chỉ tìm điện thoại có khe cắm thẻ nhớ mở rộng"},
             priority=4),

        # R22: Dual SIM
        Rule("R22_DUAL_SIM",
             "Nếu cần 2 SIM → Lọc máy hỗ trợ 2 SIM",
             conditions={"need_dual_sim": True},
             actions={"required_dual_sim": True,
                      "explanation": "Chỉ tìm điện thoại hỗ trợ 2 SIM"},
             priority=4),

        # R23: High Refresh Rate
        Rule("R23_HIGH_REFRESH",
             "Nếu cần màn hình mượt → Tần số quét cao ≥120Hz",
             conditions={"need_high_refresh": True},
             actions={"min_refresh_rate": 120, "preferred_features": ["High Refresh Rate"],
                      "explanation": "Chỉ tìm điện thoại có tần số quét từ 120Hz trở lên"},
             priority=4),

        # ═══ VIDEO QUAY PHIM THEO NGÂN SÁCH ═══
        # R24A: Video cao cấp (>15 triệu) - Quay 4K/8K, OIS, chip mạnh
        Rule("R24A_VIDEO_HIGH",
             "Nếu quay video + ngân sách cao → Flagship video",
             conditions={"user_need": "video", "budget": {"min": 15000000}},
             actions={"min_camera_mp": 50, "required_camera_ois": True,
                      "required_high_res_video": True,
                      "min_processor_tier": "high",
                      "preferred_features": ["Good Camera", "High Performance"],
                      "preferred_brands": ["Apple", "Samsung", "Google", "Sony"],
                      "explanation": "Với ngân sách trên 15 triệu, bạn cần máy quay 4K/8K, chip mạnh xử lý video"},
             priority=9),

        # R24B: Video trung bình (8-15 triệu) - Quay 4K, ổn định
        Rule("R24B_VIDEO_MID",
             "Nếu quay video + ngân sách trung → Camera 4K, OIS",
             conditions={"user_need": "video", "budget": {"min": 8000000, "max": 15000000}},
             actions={"min_camera_mp": 48,
                      "required_camera_ois": True,
                      "min_processor_tier": "upper-mid",
                      "explanation": "Với ngân sách 8-15 triệu, chọn máy quay 4K có OIS ổn định"},
             priority=8),

        # R24C: Video thấp (<8 triệu) - Quay 1080p, camera khá
        Rule("R24C_VIDEO_LOW",
             "Nếu quay video + ngân sách thấp → Camera quay tốt",
             conditions={"user_need": "video", "budget": {"max": 8000000}},
             actions={"min_camera_mp": 32,
                      "min_processor_tier": "mid",
                      "preferred_brands": ["Xiaomi", "Realme", "OPPO"],
                      "explanation": "Với ngân sách dưới 8 triệu, chọn máy quay video 1080p ổn định"},
             priority=7),

        # R24: Video fallback (không có ngân sách) - Priority thấp nhất
        Rule("R24_VIDEO",
             "Nếu cần quay phim (không có ngân sách) → Camera quay tốt",
             conditions={"user_need": "video"},
             actions={"min_camera_mp": 32,
                      "preferred_features": ["Good Camera"],
                      "explanation": "Bạn cần điện thoại có camera quay phim chất lượng tốt"},
             priority=4),  # Priority thấp để fallback

        # R25: Large Storage
        Rule("R25_LARGE_STORAGE",
             "Nếu cần nhiều bộ nhớ → Bộ nhớ trong lớn ≥256GB",
             conditions={"need_large_storage": True},
             actions={"min_storage_gb": 256,
                      "explanation": "Chỉ tìm điện thoại có bộ nhớ trong từ 256GB trở lên"},
             priority=3),

        # R26: eSIM
        Rule("R26_ESIM",
             "Nếu cần eSIM → Lọc máy hỗ trợ eSIM",
             conditions={"need_esim": True},
             actions={"required_esim": True,
                      "explanation": "Chỉ tìm điện thoại hỗ trợ eSIM"},
             priority=4),

        # R27: Good GPU
        Rule("R27_GOOD_GPU",
             "Nếu cần xử lý đồ họa mạnh → GPU cao cấp",
             conditions={"need_good_gpu": True},
             actions={"required_gpu_features": True,
                      "category_filter": ["flagship", "gaming"],
                      "explanation": "Chỉ tìm điện thoại flagship hoặc gaming có GPU mạnh"},
             priority=3),

        # R28: IR Blaster
        Rule("R28_IR_BLASTER",
             "Nếu cần điều khiển hồng ngoại → Lọc máy có IR",
             conditions={"need_ir_blaster": True},
             actions={"required_infrared": True,
                      "explanation": "Chỉ tìm điện thoại có tích hợp hồng ngoại (IR blaster)"},
             priority=3),

        # R29: Premium Build — metal/glass back
        Rule("R29_PREMIUM_BUILD",
             "Nếu cần chất liệu cao cấp → Vỏ kim loại/kính",
             conditions={"need_premium_build": True},
             actions={"preferred_back_material": ["Kính", "Kính cường lực"],
                      "explanation": "Chỉ tìm điện thoại có chất liệu cao cấp (kính/kim loại)"},
             priority=2),

        # R30: Good Audio — dual speakers / Hi-Fi
        Rule("R30_GOOD_AUDIO",
             "Nếu cần âm thanh hay → Loa kép/Hi-Fi",
             conditions={"need_good_audio": True},
             actions={"required_good_audio": True,
                      "preferred_features": ["High Performance"],
                      "explanation": "Tìm điện thoại có âm thanh chất lượng cao"},
             priority=2),

        # ═══ CHI TIẾT CAMERA — CHỤP ẢNH ═══
        # R31: Photography cần chống rung OIS
        Rule("R31_PHOTOGRAPHY_OIS",
             "Nếu chụp ảnh cần ổn định hình ảnh → Máy có OIS",
             conditions={"user_need": "photography",
                         "camera_sub_needs": {"contains": "ois"}},
             actions={"required_camera_ois": True,
                      "explanation": "Bạn cần điện thoại có chống rung quang học OIS cho ảnh sắc nét"},
             priority=5),

        # R32: Photography cần zoom xa
        Rule("R32_PHOTOGRAPHY_ZOOM",
             "Nếu chụp ảnh cần zoom xa → Máy có telephoto/zoom quang",
             conditions={"user_need": "photography",
                         "camera_sub_needs": {"contains": "zoom"}},
             actions={"required_camera_telephoto": True,
                      "explanation": "Bạn cần điện thoại có camera telephoto hoặc zoom quang học"},
             priority=5),

        # R33: Photography cần góc rộng
        Rule("R33_PHOTOGRAPHY_ULTRAWIDE",
             "Nếu chụp ảnh cần góc rộng → Máy có ultra-wide",
             conditions={"user_need": "photography",
                         "camera_sub_needs": {"contains": "ultrawide"}},
             actions={"required_camera_ultrawide": True,
                      "explanation": "Bạn cần điện thoại có camera góc siêu rộng (ultrawide)"},
             priority=5),

        # R34: Photography chụp đêm
        Rule("R34_PHOTOGRAPHY_NIGHT",
             "Nếu chụp ảnh thiếu sáng → Máy có chế độ chụp đêm tốt",
             conditions={"user_need": "photography",
                         "camera_sub_needs": {"contains": "night"}},
             actions={"required_camera_night": True,
                      "explanation": "Bạn cần điện thoại có chế độ chụp đêm, cảm biến lớn để chụp thiếu sáng"},
             priority=5),

        # R35: Photography chân dung
        Rule("R35_PHOTOGRAPHY_PORTRAIT",
             "Nếu chụp chân dung → Máy có chế độ chân dung/xoá phông",
             conditions={"user_need": "photography",
                         "camera_sub_needs": {"contains": "portrait"}},
             actions={"required_camera_portrait": True,
                      "preferred_brands": ["OPPO", "Vivo", "Apple", "Samsung"],
                      "explanation": "Bạn cần điện thoại có chế độ chân dung xoá phông đẹp"},
             priority=5),

        # R36: Photography macro/cận cảnh
        Rule("R36_PHOTOGRAPHY_MACRO",
             "Nếu chụp macro cận cảnh → Máy có camera macro",
             conditions={"user_need": "photography",
                         "camera_sub_needs": {"contains": "macro"}},
             actions={"required_camera_macro": True,
                      "explanation": "Bạn cần điện thoại có camera macro chụp cận cảnh chi tiết"},
             priority=5),

        # R37: Photography chuyên nghiệp
        Rule("R37_PHOTOGRAPHY_PRO",
             "Nếu chụp ảnh chuyên nghiệp → Máy flagship nhiều camera",
             conditions={"user_need": "photography",
                         "camera_sub_needs": {"contains": "professional"}},
             actions={"category_filter": "flagship", "min_camera_mp": 48,
                      "required_camera_ois": True,
                      "required_camera_telephoto": True,
                      "required_camera_ultrawide": True,
                      "preferred_brands": ["Apple", "Samsung", "Google", "Sony"],
                      "explanation": "Bạn cần điện thoại flagship với hệ thống camera đa năng chuyên nghiệp"},
             priority=7),

        # R38: Photography quay video 4K/8K
        Rule("R38_PHOTOGRAPHY_4K",
             "Nếu quay video chất lượng cao → Máy quay 4K/8K",
             conditions={"user_need": "photography",
                         "camera_sub_needs": {"contains": "high_res_video"}},
             actions={"required_high_res_video": True, "min_camera_mp": 48,
                      "preferred_features": ["Good Camera"],
                      "explanation": "Bạn cần điện thoại quay video 4K/8K chất lượng cao"},
             priority=5),

        # R39: Selfie đẹp chuyên sâu
        Rule("R39_SELFIE_BEAUTY",
             "Nếu selfie đẹp → Camera trước độ phân giải cao + AI làm đẹp",
             conditions={"user_need": "selfie",
                         "camera_sub_needs": {"contains": "selfie_beauty"}},
             actions={"min_camera_front_mp": 32,
                      "preferred_brands": ["OPPO", "Vivo", "Xiaomi"],
                      "explanation": "Bạn cần điện thoại có camera trước độ phân giải cao và AI làm đẹp"},
             priority=7),

        # R40: Photography tổng quát (khi có camera_sub_needs nhưng không match rule cụ thể)
        Rule("R40_PHOTOGRAPHY_MULTI_CAM",
             "Nếu chụp ảnh nói chung → Nhiều camera, cảm biến lớn",
             conditions={"user_need": "photography",
                         "camera_sub_needs": {"min": 2}},
             actions={"required_camera_multilens": True,
                      "preferred_brands": ["Apple", "Samsung", "Google", "OPPO", "Xiaomi"],
                      "explanation": "Bạn cần điện thoại có nhiều camera với cảm biến lớn"},
             priority=3),

        # ═══ RẺ HƠN / THAY THẾ ═══
        # R41: Photography budget-friendly — camera_sub_needs không có budget cao
        Rule("R41_PHOTOGRAPHY_BUDGET_SUB",
             "Chụp ảnh ngân sách eo hẹp → Camera chính tốt, ít tính năng phụ",
             conditions={"user_need": "photography", "budget": {"max": 8000000},
                         "camera_sub_needs": {"min": 0}},
             actions={"min_camera_mp": 32,
                      "preferred_brands": ["Xiaomi", "OPPO", "Vivo", "Realme"],
                      "explanation": "Với ngân sách thấp, chọn máy có camera chính tốt từ 32MP"},
             priority=6),

        # R42: High-end selfie  
        Rule("R42_SELFIE_HIGHEND",
             "Nếu selfie + flagship → Camera trước siêu khủng",
             conditions={"user_need": "selfie", "budget": {"min": 10000000}},
             actions={"min_camera_front_mp": 24,
                      "preferred_brands": ["OPPO", "Vivo", "Apple", "Samsung"],
                      "explanation": "Bạn cần điện thoại selfie đỉnh cao với camera trước từ 24MP"},
             priority=6),

        # ═══ KẾT HỢP NHU CẦU ═══
        # R43: Photography + Student — chụp ảnh cho học sinh/sinh viên
        Rule("R43_PHOTOGRAPHY_STUDENT",
             "Chụp ảnh cho học sinh → Camera khá, giá phải chăng",
             conditions={"user_need": "photography",
                         "user_needs": {"contains": "student"}},
             actions={"category_filter": ["budget", "midrange", "entry"],
                      "min_camera_mp": 32, "min_ram": "6GB",
                      "preferred_brands": ["Xiaomi", "OPPO", "Vivo", "Realme", "Samsung"],
                      "explanation": "Điện thoại chụp ảnh tốt với giá phải chăng cho học sinh"},
             priority=8),

        # R44: Student general (dùng user_needs, không cần user_need=student)
        Rule("R44_STUDENT_GENERAL",
             "Học sinh/sinh viên (từ user_needs) → Giá phải chăng",
             conditions={"user_needs": {"contains": "student"}},
             actions={"category_filter": ["budget", "entry"],
                      "preferred_brands": ["Xiaomi", "Realme", "OPPO", "Nokia"],
                      "explanation": "Điện thoại giá phải chăng phù hợp học sinh"},
             priority=5),

        # R45: Office + Student — văn phòng kết hợp học tập
        Rule("R45_OFFICE_STUDENT",
             "Văn phòng + học tập → Tầm trung, pin tốt, giá mềm",
             conditions={"user_need": "office",
                         "user_needs": {"contains": "student"}},
             actions={"category_filter": ["midrange", "budget"],
                      "min_ram": "6GB", "min_battery": 4000,
                      "explanation": "Điện thoại văn phòng + học tập, pin tốt, giá hợp lý"},
             priority=6),

        # R46: Gaming + Student — chơi game cho học sinh
        Rule("R46_GAMING_STUDENT",
             "Chơi game cho học sinh → Gaming giá rẻ, RAM lớn",
             conditions={"user_need": "gaming",
                         "user_needs": {"contains": "student"}},
             actions={"category_filter": ["gaming", "budget"],
                      "min_ram": "8GB",
                      "preferred_brands": ["Xiaomi", "Realme"],
                      "explanation": "Điện thoại gaming giá phải chăng cho học sinh"},
             priority=7),

        # R47: Gaming chipset performance — chip mạnh cho gaming
        Rule("R47_GAMING_CHIPSET",
             "Nếu chơi game cần chip mạnh → Ưu tiên chip hiệu năng cao",
             conditions={"user_need": "gaming"},
             actions={"min_processor_tier": "high",
                      "explanation": "Bạn cần điện thoại có chipset hiệu năng cao để chơi game mượt"},
             priority=8),

        # R48: Photography + Video creator — chip mạnh cho xử lý ảnh/video
        Rule("R48_PHOTO_VIDEO_PRO",
             "Nếu chụp ảnh/video chuyên nghiệp → Chip mạnh để xử lý",
             conditions={"user_need": "photography",
                         "user_needs": {"contains": "professional"}},
             actions={"min_processor_tier": "high",
                      "preferred_features": ["Good Camera"],
                      "explanation": "Bạn cần chipset mạnh để xử lý ảnh/video chất lượng cao"},
             priority=7),

        # R49: Multimedia + gaming — cân bằng chipset và màn hình
        Rule("R49_MEDIA_GAMING",
             "Nếu chơi game + xem phim → Cân bằng chipset và màn hình",
             conditions={"user_need": "gaming",
                         "user_needs": {"contains": "media"}},
             actions={"min_processor_tier": "upper-mid",
                      "min_screen_size": 6.5,
                      "min_refresh_rate": 90,
                      "explanation": "Bạn cần điện thoại cân bằng hiệu năng và màn hình cho game + phim"},
             priority=6),

        # R50: Battery + efficiency — chipset tiết kiệm pin
        Rule("R50_BATTERY_EFFICIENT",
             "Nếu cần pin lâu + hiệu năng tốt → Chipset tiết kiệm",
             conditions={"user_need": "battery_life"},
             actions={"min_processor_tier": "mid",
                      "preferred_features": ["Efficient Chipset"],
                      "explanation": "Bạn cần điện thoại có chipset tiết kiệm pin nhưng đủ mạnh"},
             priority=5),
    ]
