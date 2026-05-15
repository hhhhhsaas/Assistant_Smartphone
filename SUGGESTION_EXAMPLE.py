# Ví dụ thêm tính năng Gợi Ý Liên Quan

class SuggestionEngine:
    """Engine gợi ý lựa chọn liên quan dựa trên selection hiện tại"""

    def __init__(self, knowledge_base):
        self.kb = knowledge_base

        # Mapping nhu cầu → gợi ý filters
        self.suggestion_map = {
            'gaming': {
                'suggested_budget': (15000000, 30000000),
                'suggested_ram': ['12GB', '16GB'],
                'suggested_refresh_rate': [120, 144, 165],
                'suggested_brands': ['ASUS', 'Xiaomi', 'Samsung', 'OPPO'],
                'suggested_features': ['Tản nhiệt tốt', 'Pin lớn', 'Sạc nhanh'],
                'tips': 'Nên chọn chip Snapdragon 8 series hoặc Dimensity 9000+'
            },

            'photography': {
                'suggested_budget': (15000000, 40000000),
                'suggested_camera_mp': [48, 50, 108, 200],
                'suggested_brands': ['Apple', 'Samsung', 'Google', 'Xiaomi'],
                'suggested_features': ['OIS', 'Zoom quang học', 'Chụp đêm', 'AI camera'],
                'tips': 'iPhone và Samsung Galaxy S series có camera tốt nhất'
            },

            'battery_life': {
                'suggested_budget': (5000000, 15000000),
                'suggested_battery': [5000, 6000, 7000],
                'suggested_brands': ['Xiaomi', 'OPPO', 'Realme'],
                'suggested_features': ['Sạc nhanh', 'Tiết kiệm pin'],
                'tips': 'Chọn phone có pin >= 5000mAh và chip tiết kiệm điện'
            },

            'student': {
                'suggested_budget': (3000000, 10000000),
                'suggested_ram': ['6GB', '8GB'],
                'suggested_brands': ['Xiaomi', 'Realme', 'OPPO', 'Samsung'],
                'suggested_features': ['Dual SIM', 'Thẻ nhớ', 'Pin trâu'],
                'tips': 'Xiaomi và Realme có giá tốt nhất cho sinh viên'
            }
        }

    def get_suggestions(self, user_selection: dict) -> dict:
        """
        Input: {'user_need': 'gaming', 'budget': 20000000}
        Output: Gợi ý filters và tips liên quan
        """
        suggestions = {
            'filters': {},
            'tips': [],
            'related_phones': []
        }

        # Lấy gợi ý từ mapping
        need = user_selection.get('user_need')
        if need and need in self.suggestion_map:
            base_suggestions = self.suggestion_map[need]

            # Gợi ý budget nếu user chưa set
            if 'budget' not in user_selection:
                min_b, max_b = base_suggestions['suggested_budget']
                suggestions['filters']['budget_range'] = f"{min_b/1e6:.0f}-{max_b/1e6:.0f} triệu"

            # Gợi ý RAM
            if 'suggested_ram' in base_suggestions:
                suggestions['filters']['ram_options'] = base_suggestions['suggested_ram']

            # Gợi ý brands
            if 'suggested_brands' in base_suggestions:
                suggestions['filters']['recommended_brands'] = base_suggestions['suggested_brands']

            # Tips
            if 'tips' in base_suggestions:
                suggestions['tips'].append(base_suggestions['tips'])

        # Gợi ý phones cụ thể dựa trên combination
        suggestions['related_phones'] = self._find_related_phones(user_selection)

        return suggestions

    def _find_related_phones(self, selection: dict) -> list:
        """Tìm phones phù hợp với selection"""
        # Query KB với selection
        criteria = {}
        if 'user_need' in selection:
            # Map need to category
            need_to_category = {
                'gaming': ['gaming', 'flagship'],
                'photography': ['flagship', 'midrange'],
                'battery_life': ['midrange', 'budget'],
                'student': ['budget', 'entry', 'midrange']
            }
            criteria['category'] = need_to_category.get(selection['user_need'], [])

        if 'budget' in selection:
            criteria['max_price'] = selection['budget']

        # Search phones
        phones = self.kb.search_phones(criteria, n_results=5)

        return [p['name'] for p in phones[:3]]  # Top 3 suggestions

# Tích hợp vào UI (app.py)
def render_dynamic_suggestions(advisor, current_filters):
    """Hiển thị gợi ý động trong Streamlit"""

    suggestion_engine = SuggestionEngine(advisor.knowledge_base)
    suggestions = suggestion_engine.get_suggestions(current_filters)

    if suggestions['filters'] or suggestions['tips']:
        st.markdown("### 💡 Gợi ý cho bạn")

        # Hiển thị filter suggestions
        if suggestions['filters']:
            col1, col2, col3 = st.columns(3)

            with col1:
                if 'budget_range' in suggestions['filters']:
                    st.info(f"💰 Ngân sách phù hợp: {suggestions['filters']['budget_range']}")

            with col2:
                if 'ram_options' in suggestions['filters']:
                    rams = suggestions['filters']['ram_options']
                    st.info(f"💾 RAM gợi ý: {', '.join(rams)}")

            with col3:
                if 'recommended_brands' in suggestions['filters']:
                    brands = suggestions['filters']['recommended_brands'][:3]
                    st.info(f"📱 Hãng tốt: {', '.join(brands)}")

        # Hiển thị tips
        if suggestions['tips']:
            for tip in suggestions['tips']:
                st.success(f"💡 Mẹo: {tip}")

        # Hiển thị related phones
        if suggestions['related_phones']:
            st.markdown("**📱 Có thể bạn quan tâm:**")
            for phone in suggestions['related_phones']:
                st.write(f"• {phone}")

# Sử dụng trong workflow
if __name__ == "__main__":
    # Test
    from knowledge_base import KnowledgeBase
    kb = KnowledgeBase()

    engine = SuggestionEngine(kb)

    # User chọn gaming
    suggestions = engine.get_suggestions({'user_need': 'gaming'})
    print("Gaming suggestions:", suggestions)

    # User chọn gaming + budget
    suggestions = engine.get_suggestions({
        'user_need': 'gaming',
        'budget': 20000000
    })
    print("Gaming + 20tr suggestions:", suggestions)