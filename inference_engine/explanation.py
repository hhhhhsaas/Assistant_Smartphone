"""
Explanation Facility (Bộ giải thích)
Giải thích lý do hệ thống đưa ra kết luận / gợi ý.
Context-aware: Chỉ hiển thị các thông số PHÙ HỢP với nhu cầu user_need
"""

from typing import Dict, List

CAT_VN = {
    'flagship': 'cao cấp', 'midrange': 'tầm trung', 'budget': 'giá rẻ',
    'entry': 'phổ thông', 'gaming': 'chơi game', 'foldable': 'màn hình gập',
}


class ExplanationGenerator:
    def generate(self, phone_data: Dict, inferred_facts: Dict,
                 user_input: Dict, activated_rules: List[str]) -> List[str]:
        explanations = []
        
        # LẤY USER_NEED ĐỂ TẠO EXPLANATION THEO NGỮ CẢNH
        user_need = user_input.get('user_need', '')
        user_needs = user_input.get('user_needs', [])

        # === KIỂM TRA NGỮ CẢNH TRƯỚC KHI THÊM EXPLANATION ===
        
        # 1. Category - luôn hiển thị nếu khớp
        if 'category_filter' in inferred_facts:
            cats = [inferred_facts['category_filter']] \
                if isinstance(inferred_facts['category_filter'], str) \
                else inferred_facts['category_filter']
            if phone_data.get('category') in cats:
                vn = CAT_VN.get(phone_data['category'], phone_data['category'])
                explanations.append(f"✓ Thuộc phân khúc {vn} phù hợp yêu cầu")

        # 2. Brand - luôn hiển thị nếu khớp
        if 'brand_filter' in inferred_facts:
            if phone_data.get('brand') == inferred_facts['brand_filter']:
                explanations.append(
                    f"✓ Hãng {phone_data['brand']} theo sở thích")

        if 'preferred_brands' in inferred_facts:
            if phone_data.get('brand') in inferred_facts['preferred_brands']:
                explanations.append(
                    f"✓ {phone_data['brand']} là hãng được ưu tiên")

        # 3. Giá - luôn hiển thị
        self._check_price(phone_data, user_input, explanations)
        
        # 4. CAMERA - Chỉ hiển thị khi user_need là photography/selfie/video
        if user_need in ['photography', 'selfie', 'video'] or 'photography' in user_needs:
            self._check_camera(phone_data, inferred_facts, explanations, user_need)

        # 5. RAM - Hiển thị cho gaming, office, video
        if user_need in ['gaming', 'office', 'video', 'business'] or any(n in ['gaming', 'office'] for n in user_needs):
            self._check_ram(phone_data, inferred_facts, explanations, user_need)

        # 6. SCREEN - Chỉ hiển thị khi user_need là media/gaming/xem phim  
        if user_need in ['media', 'gaming'] or 'media' in user_needs:
            self._check_screen(phone_data, inferred_facts, explanations, user_need)

        # 7. BATTERY - Hiển thị cho battery_life, gaming, media, outdoor
        if user_need in ['battery_life', 'gaming', 'media', 'outdoor', 'business'] or any(n in ['battery_life', 'gaming', 'media'] for n in user_needs):
            self._check_battery(phone_data, inferred_facts, explanations, user_need)

        # 8. PROCESSOR/CHIP - Chỉ hiển thị cho gaming, video, photography
        if user_need in ['gaming', 'video', 'photography'] or 'gaming' in user_needs:
            self._check_processor(phone_data, inferred_facts, explanations)

        # 9. REFRESH RATE - Chỉ hiển thị cho gaming
        if user_need == 'gaming' or 'gaming' in user_needs:
            self._check_refresh_rate(phone_data, inferred_facts, explanations)

        return explanations

    def explain_rule_firing(self, activated_rules: List[str],
                            rule_descriptions: Dict[str, str]) -> str:
        lines = ["Quá trình suy luận:"]
        for rid in activated_rules:
            desc = rule_descriptions.get(rid, rid)
            lines.append(f"  → Kích hoạt: {desc}")
        return "\n".join(lines)

    def generate_how_explanation(self, phone_data: Dict,
                                inferred_facts: Dict,
                                user_input: Dict) -> List[str]:
        lines = []
        lines.append(f"Hệ thống đã tìm điện thoại {phone_data.get('name', '')}")
        lines.append("dựa trên các yêu cầu sau:")
        for key, value in user_input.items():
            if key != 'budget':
                lines.append(f"  - {key}: {value}")
        if 'budget' in user_input:
            lines.append(f"  - Ngân sách: {user_input['budget']:,} VND")
        return lines

    def generate_why_explanation(self, rule_id: str,
                                 rule_descriptions: Dict[str, str]) -> str:
        desc = rule_descriptions.get(rule_id, rule_id)
        return f"Luật {rule_id} được kích hoạt vì: {desc}"

    @staticmethod
    def _check_camera(phone, inferred, explanations, user_need=''):
        """Chỉ khen camera khi user thực sự quan tâm đến chụp ảnh"""
        if 'min_camera_mp' in inferred:
            try:
                cam = int(phone.get('camera_rear', 0))
                if cam >= inferred['min_camera_mp']:
                    # Context-aware: Khác nhau cho selfie vs photography
                    if user_need == 'selfie':
                        pass  # Selfie dùng camera trước
                    else:
                        explanations.append(
                            f"✓ Camera {cam}MP cho chụp ảnh sắc nét")
            except (ValueError, TypeError):
                pass
        if 'min_camera_front_mp' in inferred:
            try:
                front = int(phone.get('camera_front', 0))
                if front >= inferred['min_camera_front_mp']:
                    explanations.append(
                        f"✓ Camera trước {front}MP chụp selfie đẹp")
            except (ValueError, TypeError):
                pass

    @staticmethod
    def _check_ram(phone, inferred, explanations, user_need=''):
        """Khen RAM theo ngữ cảnh"""
        if 'min_ram' in inferred:
            phone_ram = phone.get('ram', '')
            if inferred['min_ram'] in phone_ram:
                # Context-aware: Khác nhau cho gaming vs office
                if user_need == 'gaming':
                    explanations.append(
                        f"✓ RAM {phone_ram} hỗ trợ chơi game mượt, đa nhiệm tốt")
                else:
                    explanations.append(
                        f"✓ RAM {phone_ram} đủ mạnh cho nhu cầu")

    @staticmethod
    def _check_price(phone, user_input, explanations):
        """Giá luôn được hiển thị"""
        price = phone.get('price', 0)
        budget = user_input.get('budget', 0)
        if price and budget and price <= budget:
            explanations.append(
                f"✓ Giá {price:,} VND nằm trong ngân sách")

    @staticmethod
    def _check_screen(phone, inferred, explanations, user_need=''):
        """Khen màn hình theo ngữ cảnh"""
        screen = phone.get('screen_size')
        if not screen:
            return
            
        # Nếu có yêu cầu màn hình cụ thể
        if 'min_screen_size' in inferred and float(screen) >= inferred['min_screen_size']:
            if user_need == 'media':
                explanations.append(
                    f"✓ Màn hình {screen}\" lớn, phù hợp xem phim giải trí")
            elif user_need == 'gaming':
                explanations.append(
                    f"✓ Màn hình {screen}\" cho trải nghiệm gaming đắm immers")
            else:
                explanations.append(
                    f"✓ Màn hình {screen}\" phù hợp")
        elif screen:
            # Hiển thị thông số cơ bản nếu không có yêu cầu đặc biệt
            explanations.append(f"✓ Màn hình {screen}\" hiển thị tốt")

    @staticmethod
    def _check_battery(phone, inferred, explanations, user_need=''):
        """Khen pin theo ngữ cảnh"""
        bat = phone.get('battery', '')
        if not bat:
            return
            
        # Lấy số pin
        try:
            import re
            match = re.search(r'(\d+)', str(bat))
            if match:
                bat_num = int(match.group(1))
                
                if user_need == 'gaming':
                    if bat_num >= 5000:
                        explanations.append(
                            f"✓ Pin {bat_num}mAh trâu, chơi game lâu không lo hết pin")
                    else:
                        explanations.append(
                            f"✓ Pin {bat_num}mAh đủ dùng chơi game")
                elif user_need == 'media' or user_need == 'battery_life':
                    if bat_num >= 5000:
                        explanations.append(
                            f"✓ Pin {bat_num}mAh xem phim cả ngày không cần sạc")
                    else:
                        explanations.append(
                            f"✓ Pin {bat_num}mAh đủ xem phim giải trí")
                else:
                    explanations.append(f"✓ Pin {bat_num}mAh")
            else:
                explanations.append(f"✓ Pin {bat}")
        except (ValueError, TypeError, AttributeError):
            explanations.append(f"✓ Pin {bat}")

    @staticmethod
    def _check_processor(phone, inferred, explanations):
        """Kiểm tra và khen chip - chỉ cho gaming/video/photography"""
        if 'min_processor_tier' in inferred:
            proc = phone.get('processor', '')
            if proc:
                # Context-aware: Khen chip theo cách khác nhau
                explanations.append(
                    f"✓ Chip {proc} mạnh, xử lý nhanh")

    @staticmethod
    def _check_refresh_rate(phone, inferred, explanations):
        """Kiểm tra tần số quét - chỉ cho gaming"""
        rr = phone.get('refresh_rate', '')
        if rr:
            try:
                import re
                match = re.search(r'(\d+)', str(rr))
                if match:
                    hz = int(match.group(1))
                    if hz >= 120:
                        explanations.append(
                            f"✓ Tần số quét {hz}Hz màn hình mượt mà, gaming đỉnh cao")
                    elif hz >= 90:
                        explanations.append(
                            f"✓ Tần số quét {hz}Hz gaming ổn định")
            except (ValueError, TypeError, AttributeError):
                pass
