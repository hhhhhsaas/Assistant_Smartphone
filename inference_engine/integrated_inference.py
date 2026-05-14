"""
Integrated Inference System
Kết hợp Knowledge Base + Forward Chaining + Fuzzy Logic
"""

import logging
import re
from typing import Dict, List, Optional

from knowledge_base import KnowledgeBase
from inference_engine.forward_chaining import ForwardChainingEngine
from inference_engine.fuzzy_logic import PhoneFuzzySystem
from inference_engine.explanation import ExplanationGenerator
from knowledge_acquisition import KnowledgeAcquisition


class IntegratedPhoneAdvisor:
    def __init__(self, kb_path: str = "./data/cellphones_vector_store.pkl"):
        logging.basicConfig(level=logging.INFO, format='%(message)s')
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Expert System...")

        # Khởi tạo các thành phần HCG
        self.knowledge_base = KnowledgeBase(facts_path=kb_path)
        self.inference_engine = ForwardChainingEngine()
        self.fuzzy_system = PhoneFuzzySystem()
        self.explanation = ExplanationGenerator()
        self.acquisition = KnowledgeAcquisition(self.knowledge_base)

        # Processor tier mapping for performance comparison
        self.processor_tiers = {
            # High-end flagship (2023-2024)
            'apple a17 pro': 'high', 'apple a18': 'high', 'apple a18 pro': 'high',
            'apple a19': 'high', 'apple a19 pro': 'high',
            'snapdragon 8 gen 3': 'high', 'snapdragon 8+ gen 1': 'high',
            'snapdragon 8 gen 2': 'high', 'snapdragon 888+': 'high',
            'snapdragon 888': 'high',
            'dimensity 9300': 'high', 'dimensity 9200': 'high',
            'dimensity 9200+': 'high',
            # Upper mid-range
            'snapdragon 7+ gen 2': 'upper-mid', 'snapdragon 7 gen 3': 'upper-mid',
            'snapdragon 7s gen 2': 'upper-mid',
            'dimensity 1080': 'upper-mid', 'dimensity 1200': 'upper-mid',
            'dimensity 1300': 'upper-mid',
            # Gaming focused mid-range
            'helio g99': 'gaming-mid', 'helio g96': 'gaming-mid',
            'helio g95': 'gaming-mid',
            # Will default to 'mid' or 'low' if not matched
        }

        stats = self.knowledge_base.get_stats()
        self.logger.info(
            f"✓ KB: {len(self.knowledge_base.get_all_rules())} rules, "
            f"{stats['total_phones']} phone facts")

    def _get_processor_tier(self, processor_str: str) -> str:
        """Convert processor string to performance tier for comparison"""
        if not processor_str:
            return 'low'
        
        proc_lower = processor_str.lower().strip()
        
        # Check for exact matches first
        for key, tier in self.processor_tiers.items():
            if key in proc_lower:
                return tier
        
        # Fallback patterns for unknown processors
        if any(x in proc_lower for x in ['snapdragon 8', 'snapdragon 7+', 'dimensity 9', 'dimensity 8']):
            return 'high'
        elif any(x in proc_lower for x in ['snapdragon 7', 'snapdragon 6+', 'dimensity 7', 'dimensity 10']):
            return 'upper-mid'
        elif any(x in proc_lower for x in ['snapdragon 6', 'snapdragon 4+', 'dimensity 6', 'helio g']):
            return 'mid'
        elif any(x in proc_lower for x in ['snapdragon 4', 'snapdragon 2', 'dimensity 4', 'helio p']):
            return 'low'
        else:
            return 'low'  # Default to low for unknown

    def process_user_request(self, user_request: str) -> Dict:
        return self.parse_natural_language(user_request)

    def parse_natural_language(self, text: str) -> Dict:
        text_lower = text.lower()
        parsed = {}

        # ─── 1. NHU CẦU CHÍNH — thu thập TẤT CẢ nhu cầu ──────
        need_map = [
            (['chơi game', 'gaming', 'pubg', 'liên quân', 'free fire',
              'cấu hình mạnh', 'chiến game'], 'gaming'),
            (['chụp ảnh', 'camera', 'nhiếp ảnh', 'chụp hình',
              'chụp chân dung', 'chụp macro', 'chụp cận',
              'chụp đêm', 'chụp thiếu sáng', 'chụp zoom', 'chụp xa',
              'chụp góc rộng', 'chụp cảnh', 'chụp pro',
              'sống ảo', 'insta', 'tiktok', 'chân dung', 'xóa phông'], 'photography'),
            (['pin trâu', 'pin lâu', 'trâu', 'dai', 'siêu pin'], 'battery_life'),
            (['cao cấp', 'flagship', 'xịn', 'đỉnh', 'sang', 'đẳng cấp', 'xa xỉ'], 'premium'),
            (['văn phòng', 'công việc', 'làm việc', 'dân văn phòng'], 'office'),
            (['xem phim', 'giải trí', 'netflix', 'youtube', 'phim ảnh'], 'media'),
            (['selfie', 'tự sướng', 'chụp selfie', 'chụp mặt'], 'selfie'),
            (['doanh nhân', 'business', 'kinh doanh', 'giám đốc'], 'business'),
            (['học sinh', 'sinh viên', 'hs', 'sv', 'học tập', 'hs/sv', 'đi học'], 'student'),
            (['chống nước', 'kháng nước', 'ip68', 'ip67', 'đi mưa'], 'water_resistant'),
            (['quay phim', 'quay video', 'quay 4k', 'quay 8k', 'quay cinematic',
              'vlog', 'youtuber', 'livestream', 'live stream', 'quay phim chuyên nghiệp',
              'làm vlog'], 'video'),
            (['nhẹ', 'gọn nhẹ', 'mỏng nhẹ', 'mỏng', 'nhỏ gọn'], 'lightweight'),
            (['công nghệ mới', 'màn hình gập', 'gập', 'fold', 'mới nhất'], 'innovation'),
            (['đi rừng', 'ngoài trời', 'dã ngoại', 'bền', 'leo núi', 'durable'], 'outdoor'),
        ]
        user_needs = []
        for keywords, need_val in need_map:
            for kw in keywords:
                if kw in text_lower:
                    if need_val not in user_needs:
                        user_needs.append(need_val)
                    break
        # Battery special: "pin" alone needs context
        if 'pin' in text_lower and 'battery_life' not in user_needs:
            if any(ctx in text_lower for ctx in ['lâu', 'trâu', 'tốt', 'khỏe', 'dai']):
                user_needs.append('battery_life')

        if user_needs:
            parsed['user_needs'] = user_needs
            parsed['user_need'] = user_needs[0]  # primary = first match (backward compat)

        # ─── 2. NGÂN SÁCH ─────────────────────────────────────
        budget_patterns = [
            (r'(?:từ|khoảng|tầm)\s*(\d+)\s*(?:triệu|tr)\s*(?:đến|->|–)\s*(\d+)\s*(?:triệu|tr)',
             lambda m: (int(m.group(1)) * 1000000, int(m.group(2)) * 1000000)),
            (r'(?:trên|hơn)\s*(\d+)\s*(?:triệu|tr)',
             lambda m: (int(m.group(1)) * 1000000, None)),
            (r'(?:dưới|dươi|dí|\bchưa tới)\s*(\d+)\s*(?:triệu|tr)',
             lambda m: (None, int(m.group(1)) * 1000000)),
            (r'(\d+)\s*(?:triệu|tr)\s*(?:đến|->|–)\s*(\d+)\s*(?:triệu|tr)',
             lambda m: (int(m.group(1)) * 1000000, int(m.group(2)) * 1000000)),
            # THU HẺP DUNG SAI: tầm 20 triệu → 18-22 triệu (±10% thay vì ±20%)
            (r'(?:tầm|khoảng|giá|tầm giá)\s*(\d+)\s*(?:triệu|tr)?',
             lambda m: (int(m.group(1)) * 1000000 * 0.9, int(m.group(1)) * 1000000 * 1.1)),
            (r'(\d+)\s*(?:triệu|tr)',
             lambda m: (None, int(m.group(1)) * 1000000)),
        ]
        for pattern, extractor in budget_patterns:
            match = re.search(pattern, text_lower)
            if match:
                min_b, max_b = extractor(match)
                if min_b is not None:
                    parsed['budget_min'] = min_b
                if max_b is not None:
                    parsed['budget'] = max_b
                break

        # ─── 2b. SUY LUẬN NGÂN SÁCH TỪ NHU CẦU ──────────────
        # Nếu không có budget rõ ràng, suy luận từ user_needs
        if 'budget' not in parsed:
            if 'student' in user_needs:
                parsed['budget'] = 10000000  # hs/sv → tối đa 10tr
            elif 'entry' in user_needs or 'budget' in user_needs:
                parsed['budget'] = 5000000
            # photography không có budget → vẫn để mở (không set budget), R2 không fire
            # nhưng vẫn có fuzzy scoring với camera weight cao

        # ─── 3. HÃNG ──────────────────────────────────────────
        brand_map = {
            'iphone': 'Apple', 'apple': 'Apple',
            'samsung': 'Samsung', 'galaxy': 'Samsung',
            'xiaomi': 'Xiaomi', 'redmi': 'Xiaomi', 'poco': 'Xiaomi',
            'oppo': 'OPPO', 'reno': 'OPPO',
            'vivo': 'Vivo',
            'realme': 'Realme',
            'nokia': 'Nokia',
            'huawei': 'Huawei', 'honor': 'Honor',
            'asus': 'Asus', 'rog': 'Asus',
            'google': 'Google', 'pixel': 'Google',
            'oneplus': 'OnePlus', 'one plus': 'OnePlus',
            'sony': 'Sony', 'xperia': 'Sony',
        }
        for key, val in brand_map.items():
            if key in text_lower:
                parsed['preferred_brand'] = val
                break

        # ─── 4. MÀN HÌNH ─────────────────────────────────────
        screen_sizes = [
            (['màn hình nhỏ', 'màn bé', 'màn hình bé', 'nhỏ gọn'], 'max', 6.0),
            (['màn hình lớn', 'màn to', 'màn hình to', 'màn rộng'], 'min', 6.5),
            (['màn hình siêu lớn', 'màn cực to'], 'min', 6.8),
        ]
        for keywords, direction, val in screen_sizes:
            for kw in keywords:
                if kw in text_lower:
                    key = f'{direction}_screen_size'
                    if key not in parsed or parsed[key] < val:
                        parsed[key] = val
                    break

        if 'màn hình' in text_lower and 'user_need' not in parsed:
            if any(w in text_lower for w in ['lớn', 'to', 'rộng']):
                parsed.setdefault('user_need', 'media')

        # ─── 5. TÍNH NĂNG ĐẶC BIỆT ────────────────────────────
        feature_keywords = {
            'need_nfc': ['nfc', 'thanh toán'],
            'need_wireless_charging': ['sạc không dây', 'sạc wireless', 'charge không dây'],
            'need_headphone_jack': ['jack tai nghe', '3.5mm', 'cổng tai nghe'],
            'need_expandable_storage': ['thẻ nhớ', 'microsd', 'gắn thẻ', 'mở rộng bộ nhớ'],
            'need_dual_sim': ['2 sim', 'dual sim', 'hai sim', '2 sim 2 sóng'],
            'need_high_refresh': ['120hz', '144hz', 'màn hình mượt', 'tần số quét cao',
                                   'mượt mà'],
            'need_large_storage': ['bộ nhớ lớn', '512gb', '1tb', 'nhiều bộ nhớ',
                                    'dung lượng cao'],
            'need_esim': ['esim', 'e-sim'],
            'need_ir_blaster': ['hồng ngoại', 'điều khiển từ xa', 'remote'],
            'need_premium_build': ['chất liệu cao cấp', 'vỏ kim loại', 'vỏ kính',
                                    'khung kim loại'],
            'need_good_audio': ['loa kép', 'âm thanh hay', 'hifi', 'loa stereo',
                                 'âm thanh vòm'],
            'need_good_gpu': ['gpu mạnh', 'xử lý đồ họa', 'render'],
        }
        for flag_key, keywords in feature_keywords.items():
            for kw in keywords:
                if kw in text_lower:
                    parsed[flag_key] = True
                    break

        # ─── 6. NHU CẦU CAMERA CHI TIẾT ────────────────────
        # Chỉ extract khi user_need=photography hoặc có từ khoá camera
        camera_keywords = ['chụp ảnh', 'camera', 'chụp hình', 'nhiếp ảnh',
                            'chụp', 'chân dung', 'xóa phông', 'selfie',
                            'macro', 'zoom', 'ois', 'chống rung']
        is_camera_related = any(k in text_lower for k in camera_keywords)

        if is_camera_related:
            camera_sub = []
            # OIS / Chống rung
            if any(k in text_lower for k in ['chống rung', 'ois', 'ổn định hình ảnh',
                                               'chống rung quang học']):
                camera_sub.append('ois')
            # Zoom
            if any(k in text_lower for k in ['zoom', 'chụp xa', 'tele', 'telephoto',
                                               'chụp từ xa']):
                camera_sub.append('zoom')
            # Góc rộng / Ultrawide
            if any(k in text_lower for k in ['góc rộng', 'siêu rộng', 'ultrawide',
                                               'chụp rộng', 'chụp cảnh']):
                camera_sub.append('ultrawide')
            # Chụp đêm / Thiếu sáng
            if any(k in text_lower for k in ['chụp đêm', 'thiếu sáng', 'chụp tối',
                                               'night', 'ánh sáng yếu']):
                camera_sub.append('night')
            # Chân dung / Xoá phông
            if any(k in text_lower for k in ['chân dung', 'xóa phông', 'xoá phông',
                                               'portrait']):
                camera_sub.append('portrait')
            # Macro / Cận cảnh
            if any(k in text_lower for k in ['macro', 'chụp cận', 'cận cảnh',
                                               'chụp gần']):
                camera_sub.append('macro')
            # Chuyên nghiệp / Pro
            if any(k in text_lower for k in ['chuyên nghiệp', 'pro', 'cao cấp',
                                               'dslr', 'máy ảnh']):
                camera_sub.append('professional')
            # Quay phim chất lượng cao (4K, 8K)
            if any(k in text_lower for k in ['4k', '8k', 'quay 4k', 'quay 8k',
                                               'cinematic']):
                camera_sub.append('high_res_video')
            # Selfie đẹp
            if any(k in text_lower for k in ['selfie đẹp', 'selfie tốt', 'chụp mặt đẹp',
                                               'selfie xinh']):
                camera_sub.append('selfie_beauty')

            if camera_sub:
                parsed['camera_sub_needs'] = camera_sub

        # ─── 7. THÔNG SỐ KỸ THUẬT TỪ CÂU ────────────────────
        # RAM
        ram_match = re.search(r'(\d+)\s*(?:gb|g)\s*ram', text_lower)
        if ram_match:
            parsed['min_ram'] = f"{ram_match.group(1)}GB"

        # Camera MP
        cam_match = re.search(r'camera\s*(\d+)', text_lower)
        if cam_match:
            parsed['min_camera_mp'] = int(cam_match.group(1))

        # Dung lượng pin
        batt_match = re.search(r'(\d+)\s*mah', text_lower)
        if batt_match:
            parsed['min_battery'] = int(batt_match.group(1))

        # 5G
        if '5g' in text_lower or '5 g' in text_lower:
            parsed['network'] = '5G'

        return parsed

    def recommend_phones(self, user_input: Dict, n_results: int = 50) -> List[Dict]:
        self.pipeline_log = []

        # Bước 1: Forward Chaining
        self.pipeline_log.append({
            'step': 1,
            'name': 'Forward Chaining',
            'icon': '🧠',
            'input': dict(user_input),
        })

        snapshot = self.inference_engine.infer(
            self.knowledge_base.get_all_rules(), user_input)
        inferred_facts = snapshot['inferred_facts']
        activated_rules = snapshot['activated_rules']

        self.last_inferred_facts = inferred_facts
        self.last_activated_rules = activated_rules
        self.logger.debug(f"User Input: {user_input}")
        self.logger.debug(f"Inferred Facts: {inferred_facts}")
        self.logger.debug(f"Activated Rules: {activated_rules}")

        self.pipeline_log[-1]['output'] = {
            'activated_rules': list(activated_rules),
            'inferred_facts': dict(inferred_facts),
        }

        # User's explicit filters override whatever rules inferred
        for override_key in ['category_filter', 'min_ram', 'min_battery',
                              'max_weight', 'min_camera_mp', 'min_screen_size',
                              'max_screen_size', 'min_camera_front_mp',
                              'min_refresh_rate', 'min_storage_gb']:
            if override_key in user_input:
                inferred_facts[override_key] = user_input[override_key]

        # Feature toggles: user's explicit True overrides
        for flag_key in ['required_nfc', 'required_water_resistant',
                          'required_wireless_charging', 'required_headphone_jack',
                          'required_memory_card_slot', 'required_dual_sim',
                          'required_esim', 'required_infrared',
                          'required_good_audio',
                          'required_camera_ois', 'required_camera_telephoto',
                          'required_camera_ultrawide', 'required_camera_night',
                          'required_camera_portrait', 'required_camera_macro',
                          'required_camera_multilens', 'required_high_res_video',
                          'min_processor_tier']:
            if flag_key in user_input:
                inferred_facts[flag_key] = user_input[flag_key]

        # Preferred brands: user's explicit preferred_brand takes priority
        if 'preferred_brand' in user_input:
            inferred_facts.pop('preferred_brands', None)

        # Features list: user explicitly sets features
        if 'features' in user_input:
            inferred_facts['required_features'] = user_input['features']

        # Bước 2: Tạo criteria cho KB
        search_criteria = {}
        if 'budget' in user_input:
            search_criteria['max_price'] = user_input['budget']
        if 'budget_min' in user_input:
            search_criteria['min_price'] = user_input['budget_min']
        if 'category_filter' in inferred_facts:
            cats = inferred_facts['category_filter']
            if isinstance(cats, list):
                search_criteria['category'] = cats
            else:
                search_criteria['category'] = cats
        if 'brand_filter' in inferred_facts:
            search_criteria['brand'] = inferred_facts['brand_filter']
        elif 'preferred_brand' in user_input:
            search_criteria['brand'] = user_input['preferred_brand']

        candidates = self.knowledge_base.search_phones(
            search_criteria, n_results=500)

        self.pipeline_log.append({
            'step': 2,
            'name': 'Knowledge Base Search',
            'icon': '📚',
            'input': dict(search_criteria),
            'output': {'candidates_count': len(candidates)},
        })

        # Bước 3: Lọc theo inferred facts
        filtered = []
        for phone in candidates:
            if self._passes_filters(phone, inferred_facts, user_input):
                filtered.append(phone)

        self.pipeline_log.append({
            'step': 3,
            'name': 'Filtering (Inferred Facts)',
            'icon': '🔍',
            'input': {k: v for k, v in inferred_facts.items()
                      if k.startswith(('min_', 'max_', 'required_', 'category_',
                                       'brand_', 'preferred_'))},
            'output': {
                'before': len(candidates),
                'after': len(filtered),
                'removed': len(candidates) - len(filtered),
            },
        })

        # Bước 4: Fuzzy scoring
        fuzzy_prefs = self._create_fuzzy_preferences(user_input, inferred_facts)

        self.last_fuzzy_weights = fuzzy_prefs
        self.pipeline_log.append({
            'step': 4,
            'name': 'Fuzzy Logic Scoring',
            'icon': '⚖️',
            'input': {
                'weights': {k: round(v, 2) for k, v in fuzzy_prefs.items()},
                'formula': 'Total = Fuzzy×0.7 + RuleCompliance×0.3',
            },
        })

        scored = []
        for phone in filtered:
            fuzzy_score = self.fuzzy_system.calculate_score(phone, fuzzy_prefs)
            fuzzy_breakdown = self.fuzzy_system.calculate_detailed_score(phone, fuzzy_prefs)
            rule_score, rule_details = self._calc_rule_compliance(phone, inferred_facts)
            total = fuzzy_score * 0.7 + rule_score * 0.3

            explanations = self.explanation.generate(
                phone, inferred_facts, user_input, activated_rules)

            scored.append({
                'phone': phone,
                'fuzzy_score': fuzzy_score,
                'fuzzy_breakdown': fuzzy_breakdown,
                'rule_score': rule_score,
                'rule_details': rule_details,
                'total_score': total,
                'explanations': explanations,
            })

        scored.sort(key=lambda x: x['total_score'], reverse=True)
        results = scored[:n_results]

        # Bước 5: Ranking
        top3 = [(r['phone'].get('name', '?'), round(r['total_score'] * 100))
                for r in results[:3]]
        self.pipeline_log[-1]['output'] = {
            'phones_scored': len(scored),
            'top_3': top3,
        }
        self.pipeline_log.append({
            'step': 5,
            'name': 'Ranking & Output',
            'icon': '🏆',
            'input': {'total_scored': len(scored), 'n_results': n_results},
            'output': {
                'returned': len(results),
                'score_range': (
                    f"{round(results[-1]['total_score']*100)}%–{round(results[0]['total_score']*100)}%"
                    if results else 'N/A'
                ),
                'top_3': top3,
            },
        })

        return results

    def _passes_filters(self, phone: Dict, inferred: Dict,
                        user_input: Dict = None) -> bool:
        if 'category_filter' in inferred:
            cats = inferred['category_filter']
            if isinstance(cats, str):
                cats = [cats]
            if phone.get('category') not in cats:
                return False
        # Nếu user_input có preferred_brand, ưu tiên nó; nếu không thì dùng preferred_brands từ inference
        if user_input and 'preferred_brand' in user_input:
            if phone.get('brand') != user_input['preferred_brand']:
                return False
        elif 'preferred_brands' in inferred:
            if phone.get('brand') not in inferred['preferred_brands']:
                return False
        if 'min_camera_mp' in inferred:
            try:
                if int(phone.get('camera_rear', 0)) < inferred['min_camera_mp']:
                    return False
            except (ValueError, TypeError):
                return False
        if 'min_camera_front_mp' in inferred:
            try:
                if int(phone.get('camera_front', 0)) < inferred['min_camera_front_mp']:
                    return False
            except (ValueError, TypeError):
                return False
        if 'min_ram' in inferred:
            pr = phone.get('ram', '')
            try:
                req = int(inferred['min_ram'].replace('GB', ''))
                pv = int(pr.replace('GB', ''))
                if pv < req:
                    return False
            except (ValueError, TypeError):
                if inferred['min_ram'] not in pr:
                    return False
        if 'min_screen_size' in inferred:
            ss = phone.get('screen_size')
            if ss and float(ss) < inferred['min_screen_size']:
                return False
        if 'max_screen_size' in inferred:
            ss = phone.get('screen_size')
            if ss and float(ss) > inferred['max_screen_size']:
                return False
        if 'min_battery' in inferred:
            bt = phone.get('battery', '0')
            try:
                bv = int(re.search(r'(\d+)', str(bt)).group(1)) \
                    if re.search(r'(\d+)', str(bt)) else 0
                if bv < inferred['min_battery']:
                    return False
            except (ValueError, TypeError):
                pass
        if 'max_weight' in inferred:
            wt = phone.get('weight', 999)
            try:
                if float(wt) > inferred['max_weight']:
                    return False
            except (ValueError, TypeError):
                pass
        if 'required_features' in inferred:
            feats = phone.get('features', [])
            if not all(f in feats for f in inferred['required_features']):
                return False
        if 'required_nfc' in inferred:
            nfc = phone.get('nfc')
            if not nfc or nfc is False or str(nfc).lower() == 'false':
                return False
        if 'required_water_resistant' in inferred:
            wr = str(phone.get('water_resistance', '')).lower()
            if 'ip' not in wr:
                return False
        if 'required_wireless_charging' in inferred:
            charging = str(phone.get('charging', '')).lower()
            if 'không dây' not in charging and 'wireless' not in charging:
                return False
        if 'required_headphone_jack' in inferred:
            hj = str(phone.get('headphone_jack', '')).lower()
            if 'không' in hj or 'none' in hj or not hj:
                return False
        if 'required_memory_card_slot' in inferred:
            mcs = str(phone.get('memory_card_slot', '')).lower()
            if 'không' in mcs or 'none' in mcs or not mcs:
                return False
        if 'required_dual_sim' in inferred:
            sim = str(phone.get('sim', '')).lower()
            if 'kép' not in sim and 'dual' not in sim and '2' not in sim:
                return False
        if 'min_refresh_rate' in inferred:
            rr = phone.get('refresh_rate', '0')
            try:
                hz = int(re.search(r'(\d+)', str(rr)).group(1))
                if hz < inferred['min_refresh_rate']:
                    return False
            except (ValueError, TypeError, AttributeError):
                pass
        if 'min_storage_gb' in inferred:
            st = phone.get('storage', '0')
            try:
                unit = 'TB' if 'TB' in str(st).upper() else 'GB'
                gb = int(re.search(r'(\d+)', str(st)).group(1))
                if unit == 'TB':
                    gb *= 1024
                if gb < inferred['min_storage_gb']:
                    return False
            except (ValueError, TypeError, AttributeError):
                pass
        if 'required_esim' in inferred:
            sim = str(phone.get('sim', '')).lower()
            if 'esim' not in sim and 'e-sim' not in sim:
                return False
        if 'required_infrared' in inferred:
            ir = str(phone.get('infrared', '')).lower()
            if 'có' not in ir and 'yes' not in ir and 'true' not in ir.lower():
                return False
        if 'preferred_back_material' in inferred:
            back = str(phone.get('back_material', '')).lower()
            allowed = [m.lower() for m in inferred['preferred_back_material']]
            if not any(m in back for m in allowed):
                return False
        if 'required_good_audio' in inferred:
            audio = str(phone.get('audio_tech', '')).lower()
            if 'stereo' not in audio and 'dual' not in audio and 'hi-fi' not in audio:
                return False

        # ─── PROCESSOR TIER FILTER ────────────────────────────────
        if 'min_processor_tier' in inferred:
            required_tier = inferred['min_processor_tier']
            processor_str = str(phone.get('processor', '')).lower()
            actual_tier = self._get_processor_tier(processor_str)
            
            # Tier order: low < mid < upper-mid < high
            tier_order = {'low': 0, 'mid': 1, 'gaming-mid': 1, 'upper-mid': 2, 'high': 3}
            required_level = tier_order.get(required_tier, 0)
            actual_level = tier_order.get(actual_tier, 0)
            
            if actual_level < required_level:
                return False

        return True

    def _create_fuzzy_preferences(self, user_input: Dict,
                                    inferred_facts: Dict) -> Dict:
        prefs = {
            'price': 0.20, 'battery': 0.15, 'camera': 0.15,
            'ram': 0.15, 'screen': 0.10, 'performance': 0.15
        }
        need = user_input.get('user_need', '')
        needs = user_input.get('user_needs', [need] if need else [])

        # === TRỌNG SỐ MỜ BẤT ĐỐI XỨNG (ASYMMETRIC FUZZY WEIGHTS) ===
        # Gaming: 60-70% cho Hiệu năng + Màn hình, rất thấp cho Camera
        # Photography: 50% cho Camera
        # Media: 40-50% cho Màn hình + Pin
        pref_map = {
            # GAMING: Dồn 65% cho performance + screen, chỉ 3% cho camera
            'gaming':     {'performance': 0.35, 'screen': 0.30, 'ram': 0.15,
                           'battery': 0.12, 'price': 0.05, 'camera': 0.03},
            
            # PHOTOGRAPHY: Dồn 50% cho camera, rất thấp cho các thứ khác
            'photography': {'camera': 0.50, 'performance': 0.15, 'ram': 0.10,
                            'screen': 0.05, 'battery': 0.10, 'price': 0.10},
            
            # BATTERY LIFE: Dồn 55% cho pin
            'battery_life': {'battery': 0.55, 'performance': 0.15, 'price': 0.15,
                             'ram': 0.08, 'screen': 0.05, 'camera': 0.02},
            
            # PREMIUM: Cân bằng nhưng ưu tiên performance + camera
            'premium':  {'performance': 0.30, 'camera': 0.25, 'ram': 0.15,
                         'screen': 0.10, 'battery': 0.10, 'price': 0.10},
            
            # MEDIA: Dồn 45% cho màn hình + pin cho xem phim
            'media':    {'screen': 0.30, 'battery': 0.25, 'performance': 0.15,
                         'ram': 0.10, 'camera': 0.10, 'price': 0.10},
            
            # STUDENT: Giá rẻ là ưu tiên số 1
            'student':  {'price': 0.40, 'camera': 0.20, 'battery': 0.15,
                         'performance': 0.10, 'ram': 0.10, 'screen': 0.05},
            
            # OFFICE: Cân bằng pin + performance + giá
            'office':   {'performance': 0.25, 'battery': 0.25, 'price': 0.20,
                         'ram': 0.15, 'screen': 0.10, 'camera': 0.05},
            
            # SELFIE: Camera trước là ưu tiên
            'selfie':   {'camera': 0.45, 'price': 0.20, 'performance': 0.15,
                         'ram': 0.08, 'screen': 0.07, 'battery': 0.05},
            
            # VIDEO: Camera + performance cho quay video
            'video':    {'camera': 0.30, 'performance': 0.25, 'battery': 0.20,
                         'storage': 0.15, 'price': 0.05, 'screen': 0.05},
            
            # BUSINESS: Performance + security + pin
            'business': {'performance': 0.30, 'battery': 0.20, 'ram': 0.20,
                         'camera': 0.10, 'price': 0.15, 'screen': 0.05},
            
            # OUTDOOR: Pin + bền + giá
            'outdoor':  {'battery': 0.40, 'performance': 0.20, 'price': 0.20,
                         'ram': 0.10, 'screen': 0.05, 'camera': 0.05},
        }

        if needs:
            # Nếu chỉ có 1 nhu cầu chính → sử dụng weights cực đoan
            if len(needs) == 1 and needs[0] in pref_map:
                return pref_map[needs[0]]
            
            # Nếu có nhiều nhu cầu → tính trung bình có trọng số
            keys = ['price', 'battery', 'camera', 'ram', 'screen', 'performance']
            sums = {k: 0.0 for k in keys}
            count = 0
            for n in needs:
                if n in pref_map:
                    for k in keys:
                        sums[k] += pref_map[n].get(k, prefs.get(k, 0.1))
                    count += 1
            if count > 0:
                for k in keys:
                    prefs[k] = sums[k] / count

        return prefs

    def _calc_rule_compliance(self, phone: Dict, inferred: Dict) -> float:
        score = 0.0
        max_score = 0.0
        
        # Lưu chi tiết từng rule
        rule_details = []

        if 'category_filter' in inferred:
            max_score += 1
            cats = [inferred['category_filter']] \
                if isinstance(inferred['category_filter'], str) \
                else inferred['category_filter']
            passed = phone.get('category') in cats
            if passed:
                score += 1
            rule_details.append(('Category', passed, f"{phone.get('category')} ∈ {cats}"))

        if 'brand_filter' in inferred:
            max_score += 1
            passed = phone.get('brand') == inferred['brand_filter']
            if passed:
                score += 1
            rule_details.append(('Brand', passed, phone.get('brand')))

        if 'min_screen_size' in inferred:
            ss = phone.get('screen_size')
            if ss:
                max_score += 1
                passed = float(ss) >= inferred['min_screen_size']
                if passed:
                    score += 1
                rule_details.append(('Screen size', passed, f"{ss}\" ≥ {inferred['min_screen_size']}\""))

        if 'preferred_features' in inferred:
            feats = phone.get('features', [])
            for f in inferred['preferred_features']:
                max_score += 1
                passed = f in feats
                if passed:
                    score += 1
                rule_details.append((f'Feature: {f}', passed, 'Có' if passed else 'Không'))

        # New filter scoring
        if 'required_nfc' in inferred:
            max_score += 1
            nfc = phone.get('nfc')
            passed = nfc and nfc is not False and str(nfc).lower() != 'false'
            if passed:
                score += 1
            rule_details.append(('NFC', passed, 'Có' if passed else 'Không'))

        if 'required_water_resistant' in inferred:
            max_score += 1
            wr = str(phone.get('water_resistance', '')).lower()
            passed = 'ip' in wr
            if passed:
                score += 1
            rule_details.append(('Water resistant', passed, phone.get('water_resistance', 'Không')))

        if 'min_refresh_rate' in inferred:
            max_score += 1
            try:
                hz = int(re.search(r'(\d+)', str(phone.get('refresh_rate', '0'))).group(1))
                passed = hz >= inferred['min_refresh_rate']
                if passed:
                    score += 1
                rule_details.append(('Refresh rate', passed, f"{hz}Hz ≥ {inferred['min_refresh_rate']}Hz"))
            except (ValueError, TypeError, AttributeError):
                rule_details.append(('Refresh rate', False, 'Không xác định'))

        if 'min_storage_gb' in inferred:
            max_score += 1
            try:
                st = str(phone.get('storage', '0'))
                unit = 'TB' if 'TB' in st.upper() else 'GB'
                gb = int(re.search(r'(\d+)', st).group(1))
                if unit == 'TB': gb *= 1024
                passed = gb >= inferred['min_storage_gb']
                if passed:
                    score += 1
                rule_details.append(('Storage', passed, f"{gb}GB ≥ {inferred['min_storage_gb']}GB"))
            except (ValueError, TypeError, AttributeError):
                rule_details.append(('Storage', False, 'Không xác định'))
        if 'required_dual_sim' in inferred:
            max_score += 1
            sim = str(phone.get('sim', '')).lower()
            passed = 'kép' in sim or 'dual' in sim
            if passed:
                score += 1
            rule_details.append(('Dual SIM', passed, 'Có' if passed else 'Không'))

        if 'required_wireless_charging' in inferred:
            max_score += 1
            passed = 'không dây' in str(phone.get('charging', '')).lower()
            if passed:
                score += 1
            rule_details.append(('Wireless charging', passed, 'Có' if passed else 'Không'))

        # Processor tier scoring
        if 'min_processor_tier' in inferred:
            max_score += 1
            required_tier = inferred['min_processor_tier']
            processor_str = str(phone.get('processor', '')).lower()
            actual_tier = self._get_processor_tier(processor_str)
            
            tier_order = {'low': 0, 'mid': 1, 'gaming-mid': 1, 'upper-mid': 2, 'high': 3}
            required_level = tier_order.get(required_tier, 0)
            actual_level = tier_order.get(actual_tier, 0)
            
            passed = actual_level >= required_level
            if passed:
                score += 1
            rule_details.append(('Processor tier', passed, f"{actual_tier} ≥ {required_tier}"))

        # RAM check
        if 'min_ram' in inferred:
            max_score += 1
            try:
                phone_ram = int(re.search(r'(\d+)', str(phone.get('ram', '0'))).group(1))
                req_ram = int(re.search(r'(\d+)', str(inferred['min_ram'])).group(1))
                passed = phone_ram >= req_ram
                if passed:
                    score += 1
                rule_details.append(('RAM', passed, f"{phone_ram}GB ≥ {req_ram}GB"))
            except (ValueError, TypeError, AttributeError):
                rule_details.append(('RAM', False, 'Không xác định'))

        # Battery check
        if 'min_battery' in inferred:
            max_score += 1
            try:
                phone_bat = int(phone.get('battery', 0))
                req_bat = int(inferred['min_battery'])
                passed = phone_bat >= req_bat
                if passed:
                    score += 1
                rule_details.append(('Battery', passed, f"{phone_bat}mAh ≥ {req_bat}mAh"))
            except (ValueError, TypeError, AttributeError):
                rule_details.append(('Battery', False, 'Không xác định'))

        final_score = score / max_score if max_score > 0 else 0.5
        return final_score, rule_details


def describe_system():
    return """
    ═══ HỆ CHUYÊN GIA TƯ VẤN ĐIỆN THOẠI ═══

    Knowledge Base:
      - Recommendation Rules: 50 luật IF-THEN (R1-R50)
      - Classification Rules: 10 luật phân loại điện thoại (CLS_)
      - Facts: 525 điện thoại với 58 trường dữ liệu

    Inference Engine:
      - Forward Chaining
      - Conflict Resolution: Priority → Specificity → Recency

    Working Memory: Bộ nhớ tạm trong suốt quá trình suy luận

    Explanation Facility: Giải thích WHY/HOW

    User Interface: Streamlit Web App

    Knowledge Acquisition: Thêm/sửa/xoá rules và facts
    """
