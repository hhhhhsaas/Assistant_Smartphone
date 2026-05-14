# 📱 TECHNICAL SPECIFICATION
## HỆ THỐNG TƯ VẤN ĐIỆN THOẠI THÔNG MINH (AI-ASSISTED)

### 📋 TỔNG QUAN HỆ THỐNG

**Tên dự án**: Smart Phone Advisor System  
**Version**: 1.0  
**Ngày tạo**: 2024  
**Mục đích**: Xây dựng hệ thống tư vấn điện thoại thông minh sử dụng AI, Fuzzy Logic và Rule-based reasoning

---

## 1. KIẾN TRÚC HỆ THỐNG

### 1.1 Các thành phần chính

```
┌─────────────────────────────────────────────────┐
│                   USER INTERFACE                 │
│                   (Streamlit App)                │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│            INFERENCE ENGINE                      │
│  ┌─────────────────────────────────────────┐   │
│  │         Natural Language Parser          │   │
│  └─────────────────┬───────────────────────┘   │
│  ┌─────────────────▼───────────────────────┐   │
│  │         Rules Engine (Forward Chaining)  │   │
│  └─────────────────┬───────────────────────┘   │
│  ┌─────────────────▼───────────────────────┐   │
│  │         Fuzzy Logic System               │   │
│  └─────────────────┬───────────────────────┘   │
└─────────────────────┴───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│              KNOWLEDGE BASE                      │
│  ┌─────────────────────────────────────────┐   │
│  │     Vector Store (476 phones)            │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### 1.2 Luồng xử lý dữ liệu

```python
Input (User Request) 
    ↓
Parse Natural Language
    ↓
Apply Rules (Forward Chaining)
    ↓
Query Knowledge Base
    ↓
Calculate Fuzzy Scores
    ↓
Rank & Filter Results
    ↓
Generate Explanations
    ↓
Output (Recommendations)
```

---

## 2. CẤU TRÚC DỮ LIỆU

### 2.1 Phone Data Schema

```json
{
  "id": "string",
  "name": "string",
  "brand": "string",
  "price": "number",
  "ram": "string (e.g., '8GB')",
  "storage": "string (e.g., '256GB')",
  "processor": "string",
  "camera_rear": "number (MP)",
  "camera_front": "number (MP)",
  "battery": "string (e.g., '5000mAh')",
  "category": "enum ['flagship', 'midrange', 'budget', 'entry', 'gaming', 'foldable']",
  "features": ["array of strings"],
  "colors": "string"
}
```

### 2.2 User Request Schema

```json
{
  "user_need": "enum ['gaming', 'photography', 'battery_life', 'office', 'premium', 'innovation']",
  "budget": "number (VND)",
  "preferred_brand": "string",
  "user_type": "enum ['student', 'gamer', 'business', 'casual']",
  "network": "enum ['4G', '5G']",
  "priority_features": ["array of preferences"]
}
```

---

## 3. LOGIC MỜ (FUZZY LOGIC)

### 3.1 Các tập mờ (Fuzzy Sets)

#### PRICE (Giá - triệu VND)
- **Rất rẻ**: Trapezoidal(0, 0, 3, 5)
- **Rẻ**: Triangular(3, 7, 12)
- **Trung bình**: Triangular(10, 15, 25)
- **Đắt**: Triangular(20, 30, 40)
- **Rất đắt**: Trapezoidal(35, 45, 100, 100)

#### BATTERY (Pin - mAh)
- **Yếu**: Trapezoidal(0, 0, 3000, 3500)
- **Trung bình**: Triangular(3000, 4000, 4500)
- **Khỏe**: Triangular(4000, 4500, 5000)
- **Rất khỏe** ("Pin trâu"): Trapezoidal(4800, 5500, 10000, 10000)

#### CAMERA (MP)
- **Cơ bản**: Trapezoidal(0, 0, 12, 20)
- **Tốt**: Triangular(16, 32, 48)
- **Rất tốt**: Triangular(32, 50, 108)
- **Chuyên nghiệp**: Trapezoidal(64, 108, 500, 500)

#### WEIGHT (Trọng lượng - grams)
- **Nhẹ** ("Gọn nhẹ"): Trapezoidal(0, 0, 150, 175)
- **Vừa**: Triangular(160, 185, 210)
- **Hơi nặng**: Triangular(195, 220, 250)
- **Nặng**: Trapezoidal(240, 270, 500, 500)

#### RAM (GB)
- **Thấp**: Trapezoidal(0, 0, 3, 4)
- **Đủ dùng**: Triangular(3, 6, 10)
- **Cao**: Triangular(6, 8, 12)
- **Rất cao**: Trapezoidal(12, 16, 64, 64)

### 3.2 Membership Function

```python
def triangular(x, a, b, c):
    """
    a: left point (membership = 0)
    b: peak point (membership = 1)
    c: right point (membership = 0)
    """
    if x <= a or x >= c:
        return 0.0
    elif a < x <= b:
        return (x - a) / (b - a)
    else:
        return (c - x) / (c - b)

def trapezoidal(x, a, b, c, d):
    """
    a: left start (membership = 0)
    b: left end (membership = 1)
    c: right start (membership = 1)
    d: right end (membership = 0)
    """
    if x <= a or x >= d:
        return 0.0
    elif a < x <= b:
        return (x - a) / (b - a)
    elif b < x <= c:
        return 1.0
    else:
        return (d - x) / (d - c)
```

### 3.3 Fuzzy Scoring Formula

```python
total_score = Σ(membership_degree[i] × weight[i]) / Σ(weight[i])

where:
- membership_degree[i]: Độ thuộc của thuộc tính i
- weight[i]: Trọng số của thuộc tính i
```

---

## 4. RULE-BASED SYSTEM

### 4.1 Cấu trúc Rule

```python
Rule {
    id: string,
    description: string,
    conditions: {
        key: value | {min, max} | {in: [values]} | {contains: string}
    },
    actions: {
        key: value
    },
    priority: number (1-10)
}
```

### 4.2 Danh sách Rules

| ID | Điều kiện | Hành động | Độ ưu tiên |
|----|-----------|-----------|------------|
| R1_GAMING | user_need='gaming' & budget≥10M | category='gaming', min_ram='8GB' | 10 |
| R2_PHOTOGRAPHY | user_need='photography' & budget≥15M | min_camera=48MP | 9 |
| R3_BATTERY | user_need='battery_life' | min_battery=4500mAh | 8 |
| R4_BUDGET | budget<5M | category=['entry','budget'] | 7 |
| R5_APPLE_FAN | preferred_brand='Apple' | brand_filter='Apple' | 6 |
| R6_FLAGSHIP | budget>25M & user_need='premium' | category='flagship' | 10 |
| R7_OFFICE | user_need='office' & 8M≤budget≤20M | category='midrange' | 5 |
| R8_FOLDABLE | user_need='innovation' & budget≥25M | category='foldable' | 9 |
| R9_STUDENT | user_type='student' & budget≤10M | category=['budget','entry'] | 6 |
| R10_5G | network='5G' | required_features=['5G'] | 4 |

### 4.3 Forward Chaining Algorithm

```python
def forward_chaining(facts):
    activated_rules = []
    changed = True
    
    while changed:
        changed = False
        for rule in rules:
            if rule.id not in activated_rules:
                if evaluate_conditions(rule.conditions, facts):
                    activated_rules.append(rule.id)
                    facts.update(rule.actions)
                    changed = True
    
    return facts
```

---

## 5. EXPLANATION FACILITY

### 5.1 Cấu trúc giải thích

```python
Explanation {
    phone_id: string,
    reasons: [
        {
            type: 'rule' | 'fuzzy' | 'match',
            description: string,
            score: number
        }
    ],
    total_score: number,
    rank: number
}
```

### 5.2 Template giải thích

```python
templates = {
    'price_match': "Giá {price} VND nằm trong ngân sách {budget} VND",
    'category_match': "Thuộc phân khúc {category} phù hợp yêu cầu",
    'brand_match': "Hãng {brand} theo sở thích của bạn",
    'camera_good': "Camera {camera}MP đáp ứng nhu cầu chụp ảnh",
    'battery_strong': "Pin {battery}mAh đảm bảo thời gian sử dụng lâu",
    'ram_sufficient': "RAM {ram} đủ mạnh cho {purpose}",
    'fuzzy_high': "Điểm tổng hợp cao ({score}/1.0)"
}
```

---

## 6. NATURAL LANGUAGE PROCESSING

### 6.1 Keyword Mapping

```python
keyword_mapping = {
    # Nhu cầu
    'chơi game|gaming': 'gaming',
    'chụp ảnh|camera|nhiếp ảnh': 'photography',
    'pin lâu|pin trâu|pin khủng': 'battery_life',
    'văn phòng|công việc|làm việc': 'office',
    'cao cấp|flagship|premium': 'premium',
    'màn hình gập|foldable': 'innovation',
    
    # Ngân sách
    r'(\d+)\s*(triệu|tr)': 'budget',
    'dưới (\d+)': 'max_budget',
    'tầm (\d+)': 'around_budget',
    
    # Thương hiệu
    'iphone|apple': 'Apple',
    'samsung': 'Samsung',
    'xiaomi': 'Xiaomi',
    'oppo': 'OPPO',
    'realme': 'Realme',
    
    # Tính năng
    '5g': '5G',
    'sạc nhanh': 'fast_charging',
    'chống nước': 'water_resistant'
}
```

### 6.2 Parse Algorithm

```python
def parse_request(text):
    text_lower = text.lower()
    parsed = {}
    
    # Extract budget
    budget_match = re.search(r'(\d+)\s*(triệu|tr)', text_lower)
    if budget_match:
        parsed['budget'] = int(budget_match.group(1)) * 1000000
    
    # Extract needs
    for pattern, value in need_patterns.items():
        if re.search(pattern, text_lower):
            parsed['user_need'] = value
            break
    
    # Extract brand preference
    for brand in brand_list:
        if brand.lower() in text_lower:
            parsed['preferred_brand'] = brand
            break
    
    return parsed
```

---

## 7. SCORING & RANKING

### 7.1 Công thức tính điểm tổng hợp

```python
Total_Score = α × Fuzzy_Score + β × Rule_Score + γ × Match_Score

where:
- α = 0.5 (trọng số fuzzy)
- β = 0.3 (trọng số rule compliance)
- γ = 0.2 (trọng số feature matching)
- Fuzzy_Score ∈ [0, 1]
- Rule_Score ∈ [0, 1]
- Match_Score ∈ [0, 1]
```

### 7.2 Ranking Algorithm

```python
def rank_phones(candidates, user_input):
    scored_phones = []
    
    for phone in candidates:
        fuzzy_score = calculate_fuzzy_score(phone)
        rule_score = calculate_rule_compliance(phone, rules)
        match_score = calculate_feature_match(phone, user_input)
        
        total_score = (0.5 * fuzzy_score + 
                      0.3 * rule_score + 
                      0.2 * match_score)
        
        scored_phones.append({
            'phone': phone,
            'score': total_score
        })
    
    return sorted(scored_phones, key=lambda x: x['score'], reverse=True)
```

---

## 8. API SPECIFICATION

### 8.1 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/recommend | Nhận yêu cầu và trả về gợi ý |
| GET | /api/phone/{id} | Lấy thông tin chi tiết điện thoại |
| POST | /api/compare | So sánh nhiều điện thoại |
| GET | /api/explain/{id} | Giải thích cho một gợi ý |

### 8.2 Request/Response Format

#### Recommend Request
```json
{
  "query": "string (natural language)",
  "budget": "number (optional)",
  "preferences": {
    "brand": "string",
    "features": ["array"]
  },
  "limit": "number (default: 5)"
}
```

#### Recommend Response
```json
{
  "status": "success",
  "recommendations": [
    {
      "phone": {...},
      "score": 0.85,
      "explanations": ["array of reasons"],
      "rank": 1
    }
  ],
  "query_understanding": {
    "parsed_input": {...},
    "activated_rules": ["array"],
    "inferred_facts": {...}
  }
}
```

---

## 9. PERFORMANCE METRICS

### 9.1 Độ chính xác
- Precision: Tỷ lệ gợi ý phù hợp / tổng số gợi ý
- Recall: Tỷ lệ tìm được điện thoại phù hợp / tổng số phù hợp
- F1-Score: 2 × (Precision × Recall) / (Precision + Recall)

### 9.2 Hiệu suất
- Response time: < 500ms cho 5 recommendations
- Database query: < 100ms
- Fuzzy calculation: < 50ms per phone
- Memory usage: < 100MB

---

## 10. TESTING SCENARIOS

### 10.1 Test Cases

1. **Budget Constraint**: "Tìm điện thoại dưới 5 triệu"
2. **Gaming Need**: "Điện thoại chơi game tầm 15 triệu"
3. **Photography**: "Máy chụp ảnh đẹp, ngân sách 25 triệu"
4. **Battery Focus**: "Pin trâu, giá phải chăng"
5. **Premium**: "Flagship cao cấp nhất"
6. **Foldable**: "Màn hình gập Samsung"
7. **Student**: "Máy cho sinh viên, 4-6 triệu"
8. **Conflicting**: "Pin trâu nhưng nhẹ, giá rẻ nhưng flagship"

### 10.2 Edge Cases

- Budget = 0 → Show all phones
- No matches → Suggest closest alternatives
- Conflicting requirements → Prioritize by weights
- Invalid input → Return helpful error message

---

## 11. DEPLOYMENT

### 11.1 Requirements
```txt
python>=3.8
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
```

### 11.2 Directory Structure
```
project/
├── app.py                  # Streamlit UI
├── inference_engine/       # Logic engines
│   ├── fuzzy_logic.py
│   ├── rules_engine.py
│   └── integrated_inference.py
├── knowledge_base/         # Data storage
│   └── simple_vector_store.py
├── data/                   # Phone database
│   └── cellphones_vector_store.pkl
├── api/                    # REST API (optional)
│   └── main.py
├── tests/                  # Unit tests
├── requirements.txt
└── README.md
```

---

## 12. FUTURE ENHANCEMENTS

1. **Machine Learning Integration**
   - Train recommendation model from user feedback
   - Personalization based on history

2. **Advanced NLP**
   - Sentiment analysis for reviews
   - Multi-language support

3. **Real-time Updates**
   - Live price tracking
   - Stock availability

4. **Social Features**
   - User reviews integration
   - Community recommendations

---

## APPENDIX A: GLOSSARY

- **Fuzzy Logic**: Logic mờ, xử lý thông tin không chính xác
- **Forward Chaining**: Suy luận tiến, từ facts đến conclusions
- **Membership Function**: Hàm thuộc, xác định độ thuộc vào tập mờ
- **Knowledge Base**: Cơ sở tri thức, lưu trữ thông tin điện thoại
- **Inference Engine**: Bộ máy suy luận, xử lý logic

---

## APPENDIX B: REFERENCES

1. Zadeh, L.A. (1965). "Fuzzy Sets"
2. Russell, S. & Norvig, P. (2020). "Artificial Intelligence: A Modern Approach"
3. Streamlit Documentation: https://docs.streamlit.io
4. Python Fuzzy Logic: scikit-fuzzy

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Author**: AI Phone Advisor Team