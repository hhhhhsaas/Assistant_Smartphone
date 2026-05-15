# THUYẾT TRÌNH: HỆ CHUYÊN GIA TƯ VẤN ĐIỆN THOẠI THÔNG MINH

## 1. GIỚI THIỆU DỰ ÁN

### 1.1. Vấn đề thực tế
- **Khó khăn khi chọn điện thoại:** Thị trường có hàng trăm mẫu điện thoại với vô số thông số kỹ thuật
- **Người dùng bình thường:** Không am hiểu về chip, RAM, camera... chỉ biết nhu cầu của mình
- **Thiếu tư vấn cá nhân hóa:** Các website chỉ có bộ lọc cứng, không hiểu ngôn ngữ tự nhiên

### 1.2. Giải pháp: Expert System
- **Hệ chuyên gia** mô phỏng tư duy của chuyên gia tư vấn điện thoại
- **Input:** Câu tiếng Việt tự nhiên như "điện thoại chơi game tầm 15 triệu"
- **Output:** Top điện thoại phù hợp + giải thích tại sao

### 1.3. Công nghệ sử dụng
- **Forward Chaining:** Suy luận tiến từ facts → kết luận
- **Fuzzy Logic:** Xử lý tiêu chí mờ (pin "trâu", camera "đẹp")
- **NLP Parser:** Hiểu tiếng Việt tự nhiên
- **Python + Streamlit:** Backend + Web UI

---

## 2. KIẾN TRÚC HỆ THỐNG

### 2.1. Tổng quan kiến trúc 3 tầng

```
┌─────────────────────────────────────┐
│      USER INTERFACE (Streamlit)     │
│  - Input tiếng Việt tự nhiên        │
│  - Hiển thị kết quả + giải thích    │
│  - Chi tiết từng thành phần điểm    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│       INFERENCE ENGINE              │
│  - NLP Parser                       │
│  - Forward Chaining                 │
│  - Fuzzy Logic Scoring              │
│  - Rule Compliance Scoring          │
│  - Explanation Generator            │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│       KNOWLEDGE BASE                │
│  - 525 Phone Facts                  │
│  - 66 Inference Rules               │
│  - Classification Rules             │
└─────────────────────────────────────┘
```

### 2.2. Các thành phần chính

#### Knowledge Base (Cơ sở tri thức)
- **Phone Facts:** 525 điện thoại với 55 thuộc tính mỗi máy
- **Rules:** 66 luật IF-THEN được xây dựng từ kinh nghiệm chuyên gia
- **Lưu trữ:** Vector store (.pkl) để tìm kiếm nhanh

#### Inference Engine (Bộ máy suy luận)
- **NLP Parser:** Phân tích câu tiếng Việt → structured data
- **Forward Chaining:** Áp dụng rules để suy ra facts mới
- **Conflict Resolution:** Giải quyết xung đột khi nhiều rules cùng fire

#### Fuzzy Logic System
- **Membership Functions:** Đánh giá mức độ phù hợp của từng tiêu chí
- **Weighted Scoring:** Tính điểm tổng hợp với trọng số động
- **Budget-aware:** Điểm giá dựa trên tỷ lệ với ngân sách

#### Rule Compliance Scoring
- **Kiểm tra độ tuân thủ rules:** Mỗi inferred fact là 1 rule check
- **Tính điểm:** `Số rules pass / Tổng số rules kiểm tra`
- **Chi tiết:** Hiển thị từng rule pass/fail + lý do

---

## 3. QUY TRÌNH XỬ LÝ 5 BƯỚC

### Bước 1: NLP PARSING
**Input:** "Điện thoại chơi game tầm 15 triệu"

**Xử lý:**
```python
# Nhận dạng nhu cầu
"chơi game" → user_need = "gaming"

# Phân tích ngân sách  
"tầm 15 triệu" → budget = 16.5tr, budget_min = 13.5tr (±10%)

# Detect thương hiệu, tính năng...
"Samsung" → preferred_brand = "Samsung"
"NFC và 5G" → required_nfc = True, network = "5G"
```

**Output:**
```json
{
  "user_need": "gaming",
  "budget": 16500000,
  "budget_min": 13500000
}
```

### Bước 2: FORWARD CHAINING

**Đánh giá 66 rules:**
```python
IF user_need = "gaming" AND budget >= 15000000
THEN category_filter = ["gaming", "flagship"]
     min_ram = 12GB
     min_processor_tier = "high"
     min_refresh_rate = 120Hz
```

**Conflict Resolution:**
- Rules được sắp xếp theo priority (0-10)
- Rule priority cao fire trước
- Working Memory merge facts thông minh:
  - `min_battery`: lấy MAX
  - `category_filter`: UNION
  - `preferred_brands`: UNION

**Output:** Inferred facts
```json
{
  "category_filter": ["gaming", "flagship", "midrange"],
  "min_ram": "12GB",
  "min_processor_tier": "high",
  "min_refresh_rate": 120
}
```

### Bước 3: KNOWLEDGE BASE SEARCH + FILTERING

**KB Search (Tìm kiếm thô):**
- Lọc theo: budget range, category, brand
- Loại bỏ phones price=0 (không biết giá)
- Kết quả: 525 → 45 candidates

**Filtering (Lọc tinh):**
- Apply inferred facts: RAM ≥ 12GB, processor tier ≥ high
- Check features: NFC, 5G, wireless charging...
- Kết quả: 45 → 22 phones pass

### Bước 4: FUZZY LOGIC SCORING (70% tổng điểm)

**Fuzzy Membership Functions:**
```
Pin (mAh):
- Yếu: < 3500 mAh
- Trung bình: 3000-4500 mAh  
- Khỏe: 4000-5000 mAh
- Rất khỏe: > 5000 mAh

Camera (MP):
- Cơ bản: < 20MP
- Tốt: 16-48MP
- Rất tốt: 32-108MP
- Chuyên nghiệp: > 64MP
```

**Asymmetric Weights (Trọng số bất đối xứng):**

| Nhu cầu | Performance | Screen | RAM | Battery | Price | Camera |
|---------|------------|--------|-----|---------|-------|--------|
| Gaming | **35%** | **30%** | 15% | 12% | 5% | 3% |
| Photography | 15% | 5% | 10% | 10% | 10% | **50%** |
| Battery | 15% | 5% | 8% | **55%** | 15% | 2% |

**Price-Budget Fitness:**
```
ratio = phone_price / user_budget

ratio 50-100%  → score 0.9-1.0 (Tốt nhất ✓)
ratio 30-50%   → score 0.6-0.9 (Chấp nhận)
ratio < 30%    → score 0.3-0.6 (Quá rẻ, thiếu tính năng)
ratio > 110%   → score giảm nhanh (Vượt budget)
```

#### Hiển thị Fuzzy Score chi tiết trên UI:
```
⚖️ Fuzzy Score chi tiết (70%):
- performance: Trọng số 35% → Đạt 92% • Chip Snapdragon 8 Gen 3
- screen: Trọng số 30% → Đạt 85% • Màn hình 6.8"
- ram: Trọng số 15% → Đạt 100% • RAM 16GB
- battery: Trọng số 12% → Đạt 95% • Pin 5850mAh
→ Tổng Fuzzy Score: 92%
```

### Bước 4b: RULE COMPLIANCE SCORING (30% tổng điểm)

Điểm Rule Compliance được tính dựa trên tỷ lệ facts suy ra được thỏa mãn bởi phone:

```python
Rule Score = (Số rules pass) / (Tổng số rules kiểm tra)
```

**Các rule checks điển hình:**
- Category filter: phone.category ∈ inferred.category_filter
- RAM: phone.ram_gb >= inferred.min_ram
- Processor tier: phone.tier >= inferred.min_processor_tier
- Refresh rate: phone.hz >= inferred.min_refresh_rate
- NFC: phone.has_nfc == True
- Storage: phone.storage_gb >= inferred.min_storage_gb
- Dual SIM: phone.sim_type == "dual"
- Water resistant: phone.water_resistance chứa "IP"

#### Hiển thị Rule Compliance chi tiết trên UI:
```
📋 Rule Compliance (30%):
Đạt: 6/8 rules → 75%

✓ Category: midrange ∈ ['gaming','flagship','midrange']
✓ RAM: 12GB ≥ 12GB
✗ NFC: Không có NFC
✓ Processor tier: high ≥ upper-mid
✓ Refresh rate: 120Hz ≥ 120Hz
✗ Storage: 256GB ≥ 512GB
```

### Bước 5: TỔNG HỢP ĐIỂM & GIẢI THÍCH

**Công thức tổng:**
```
Total Score = Fuzzy Score × 0.7 + Rule Compliance × 0.3
```

**Ví dụ:**
```
Fuzzy Score = 92%
Rule Compliance = 75%
Total = 92% × 0.7 + 75% × 0.3 = 64.4% + 22.5% = 87%
```

**Tạo giải thích tự nhiên:**
```
✓ Thuộc phân khúc tầm trung phù hợp yêu cầu
✓ Giá 18,660,000 VND nằm trong ngân sách
✓ RAM 12GB hỗ trợ chơi game mượt, đa nhiệm tốt
✓ Màn hình 6.7" hiển thị tốt
✓ Pin 6000mAh trâu, chơi game lâu không lo hết pin
✓ Chip Snapdragon 8 Gen 3 mạnh, xử lý nhanh
```

---

## 4. GIAO DIỆN CHI TIẾT

### 4.1. Màn hình chính
- **Input:** Ô nhập tiếng Việt + nút tìm kiếm
- **Category buttons:** Gaming, Photography, Pin trâu, Giải trí, Văn phòng...
- **Stats:** Tổng số máy, thương hiệu, giá thấp/cao nhất

### 4.2. Kết quả tìm kiếm
- Danh sách phone kèm điểm %
- Mỗi phone có expander detail với:
  - **Fuzzy Score chi tiết:** Từng tiêu chí × trọng số + lý do
  - **Rule Compliance chi tiết:** Từng rule pass/fail + giải thích
  - **Giải thích tự nhiên:** Tổng quan tại sao phù hợp

### 4.3. Pipeline Log
```
🔍 Pipeline Expert System
├── Step 1: NLP Parsing
│   Input: "điện thoại chơi game tầm 15 triệu"
│   Output: {user_need: gaming, budget: 16.5M}
│
├── Step 2: Forward Chaining
│   Activated: R1A_GAMING_HIGH_BUDGET (priority=10)
│   Inferred: min_ram=12GB, min_processor_tier=upper-mid
│
├── Step 3: KB Search + Filter
│   Candidates: 525 → 45 → 22 phones
│
├── Step 4: Fuzzy Scoring
│   Weights: Performance 35%, Screen 30%, RAM 15%
│
└── Step 5: Ranking
    Top 3: OPPO Reno14 (79%), Find X5 (79%), HONOR (77%)
```

---

## 5. DEMO THỰC TẾ

### 5.1. Các trường hợp test

**Test 1: Gaming**
```
Input: "Điện thoại chơi game tầm 15 triệu"
→ 5 results: OPPO Reno14, Find X5 Pro (Snapdragon 8, 12GB RAM)
```

**Test 2: Photography**  
```
Input: "iPhone chụp ảnh đẹp dưới 25 triệu"
→ 9 results: iPhone 16, 15 Plus (48MP, OIS)
```

**Test 3: Battery Life**
```
Input: "Pin trâu giá rẻ cho sinh viên"
→ 10 results: OPPO A6 Pro (7000mAh), Xiaomi phones (5000-6000mAh)
```

**Test 4: Foldable**
```
Input: "Samsung màn hình gập"
→ 9 results: Galaxy Z Flip5, Z Fold7
```

### 5.2. Ví dụ output chi tiết (máy đạt 83%)
```
📊 Chi tiết cách tính độ phù hợp (83%):
🎯 Dựa trên nhu cầu của bạn:
  Nhu cầu: gaming
  Ngân sách: 22 triệu VND

⚖️ Fuzzy Score chi tiết (70%):
  performance: Trọng số 35% → Đạt 80% • Chip Snapdragon 8 Gen 3
  screen: Trọng số 30% → Đạt 80% • Màn hình 6.7"
  ram: Trọng số 15% → Đạt 90% • RAM 12GB
  battery: Trọng số 12% → Đạt 90% • Pin 6000mAh
  price: Trọng số 5% → Đạt 70% • Giá 18,660,000VND
  camera: Trọng số 3% → Đạt 60% • Camera 50MP
  → Tổng Fuzzy Score: 83%

📋 Rule Compliance (30%):
  Đạt: 6/8 rules → 75%
  ✓ Category: midrange ∈ ['gaming','flagship','midrange']
  ✓ RAM: 12GB ≥ 12GB
  ✓ Processor tier: high ≥ upper-mid
  ✓ Refresh rate: 120Hz ≥ 120Hz
  ✗ NFC: Không có NFC
  ✗ Storage: 256GB ≥ 512GB

📝 Giải thích chi tiết:
  ✓ Thuộc phân khúc tầm trung phù hợp yêu cầu
  ✓ Giá 18,660,000 VND nằm trong ngân sách
  ✓ RAM 12GB hỗ trợ chơi game mượt, đa nhiệm tốt
  ✓ Màn hình 6.7" hiển thị tốt
  ✓ Pin 6000mAh trâu, chơi game lâu không lo hết pin
  ✓ Chip Snapdragon 8 Gen 3 mạnh, xử lý nhanh

💡 Công thức: Tổng điểm = (Fuzzy × 0.7) + (Rule × 0.3)
```

---

## 6. ƯU ĐIỂM CỦA HỆ THỐNG

### 6.1. Thông minh & Linh hoạt
- **Hiểu tiếng Việt tự nhiên:** Không cần chọn từ menu cứng nhắc
- **Suy luận đa tầng:** Kết hợp rules + fuzzy logic
- **Giải thích được:** Không phải "black box", user hiểu tại sao
- **Chi tiết từng điểm thành phần:** Biết chính xác tại sao đạt điểm đó

### 6.2. Xử lý dữ liệu thực tế
- **Price=0 handling:** Loại phones "Liên Hệ" khi có budget
- **Processor normalization:** Strip ®™ để classify chính xác
- **Budget flexibility:** "tầm X triệu" → ±10%

### 6.3. Tùy biến cao
- **66 rules** có thể thêm/sửa/xóa dễ dàng
- **Fuzzy weights** điều chỉnh theo từng nhu cầu
- **Expandable:** Dễ thêm features mới (so sánh, wishlist...)

---

## 7. HẠN CHẾ & HƯỚNG PHÁT TRIỂN

### 7.1. Hạn chế hiện tại
- **Data limitations:** 164/525 phones không có giá thực
- **NLP cần dấu:** "dien thoai" không nhận dạng được
- **Single need:** Chưa tối ưu cho multi-criteria cùng lúc

### 7.2. Hướng phát triển
- **Machine Learning:** Train model từ user feedback
- **Real-time pricing:** Crawl giá từ websites
- **Chatbot integration:** Hỏi đáp qua lại
- **Personal profile:** Lưu preferences của user

---

## 8. KẾT LUẬN

### Thành công
✅ Xây dựng hệ chuyên gia hoàn chỉnh với 525 phones, 66 rules
✅ Forward Chaining + Fuzzy Logic hoạt động hiệu quả
✅ UI thân thiện với Pipeline Log chi tiết
✅ Hiển thị chi tiết cách tính điểm: Fuzzy (70%) + Rule (30%)
✅ Giải thích được từng thành phần điểm cho người dùng

### Ý nghĩa
- **Học thuật:** Áp dụng thành công AI cổ điển vào bài toán thực tế
- **Thực tiễn:** Có thể triển khai cho cửa hàng điện thoại
- **Mở rộng:** Framework có thể dùng cho các lĩnh vực khác (laptop, xe hơi...)

---

## 9. DEMO CODE

### NLP Parser
```python
def parse_natural_language(self, text: str) -> Dict:
    # Nhận dạng nhu cầu
    if "chơi game" in text:
        parsed["user_need"] = "gaming"
    
    # Parse ngân sách
    match = re.search(r"tầm (\d+) triệu", text)
    if match:
        value = int(match.group(1)) * 1000000
        parsed["budget"] = value * 1.1  # +10%
        parsed["budget_min"] = value * 0.9  # -10%
```

### Forward Chaining
```python
class ForwardChainingEngine:
    def infer(self, rules, initial_facts):
        while changed:
            candidates = [r for r in rules 
                         if r.evaluate(facts)]
            
            # Conflict resolution
            ordered = sorted(candidates, 
                           key=lambda r: r.priority, 
                           reverse=True)
            
            for rule in ordered:
                apply_actions(rule.actions)
```

### Fuzzy Scoring
```python
def calculate_price_budget_fitness(phone_price, budget):
    ratio = phone_price / budget
    
    if ratio <= 0.5:
        return 0.6 + (ratio/0.5) * 0.3
    elif ratio <= 1.0:
        return 0.9 + (ratio-0.5) * 0.2
    else:  # Vượt budget
        return max(0, 1.0 - (ratio-1.0) * 3)
```

### Rule Compliance (tính điểm chi tiết)
```python
def _calc_rule_compliance(self, phone, inferred):
    score = 0.0
    max_score = 0.0
    details = []
    
    if 'min_ram' in inferred:
        max_score += 1
        passed = phone_ram >= inferred['min_ram']
        if passed: score += 1
        details.append(('RAM', passed, f"{ram}GB ≥ {req}GB"))
    
    # ... tương tự cho category, NFC, processor...
    
    return score/max_score, details
```

---

## THANK YOU! 🙏

### Thông tin dự án
- **GitHub:** https://github.com/hhhhhsaas/Assistant_Smartphone
- **Tech Stack:** Python, Streamlit, Fuzzy Logic, Forward Chaining
- **Data:** 525 phones, 66 rules, 20 brands

### Q&A
Sẵn sàng trả lời câu hỏi!