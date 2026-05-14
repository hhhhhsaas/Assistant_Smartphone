# Expert System - Smartphone Advisor

Hệ chuyên gia tư vấn điện thoại thông minh sử dụng **Forward Chaining** + **Fuzzy Logic**, xây dựng bằng Python và Streamlit.

## Tổng quan

Hệ thống giúp người dùng tìm điện thoại phù hợp dựa trên nhu cầu cá nhân (gaming, chụp ảnh, pin trâu, v.v.) và ngân sách. Người dùng có thể mô tả bằng ngôn ngữ tự nhiên tiếng Việt, hệ thống sẽ phân tích, suy luận và xếp hạng các điện thoại phù hợp nhất.

**Quy mô:** 525 điện thoại (361 có giá) | 66 luật suy luận | 20 thương hiệu | 6 phân khúc

---

## Kiến trúc hệ thống

```
┌────────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                             │
│                      (Streamlit Web App)                        │
│   - Tìm bằng mô tả (NLP)                                     │
│   - Tìm kiếm chi tiết (bộ lọc)                                │
│   - Hỏi đáp từng bước                                         │
│   - So sánh điện thoại                                         │
│   - Pipeline Log (xem quy trình suy luận)                      │
└────────────────────────┬───────────────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────────────┐
│                   INFERENCE ENGINE                              │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  1. NLP Parser (parse_natural_language)                   │  │
│  │     Input tiếng Việt → Dict cấu trúc                     │  │
│  │     (nhu cầu, ngân sách, hãng, tính năng, v.v.)          │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│  ┌──────────────────────▼───────────────────────────────────┐  │
│  │  2. Forward Chaining Engine                               │  │
│  │     Đánh giá 66 rules IF-THEN → Suy ra facts mới         │  │
│  │     Conflict Resolution: Priority → Specificity           │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│  ┌──────────────────────▼───────────────────────────────────┐  │
│  │  3. Fuzzy Logic System                                    │  │
│  │     Tính điểm mờ cho từng điện thoại                      │  │
│  │     6 tiêu chí: price, battery, camera, ram, screen,      │  │
│  │     performance (trọng số thay đổi theo nhu cầu)          │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│  ┌──────────────────────▼───────────────────────────────────┐  │
│  │  4. Explanation Generator                                 │  │
│  │     Giải thích TẠI SAO điện thoại được gợi ý              │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬───────────────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────────────┐
│                    KNOWLEDGE BASE                               │
│                                                                │
│  ┌─────────────────────────────────────────────────────┐       │
│  │  Rules (66 luật)                                     │       │
│  │  - Recommendation Rules (R1-R50): IF nhu cầu THEN   │       │
│  │    filters/preferences                               │       │
│  │  - Classification Rules (CLS_): Phân loại phone      │       │
│  │    theo giá/tên/RAM                                  │       │
│  └─────────────────────────────────────────────────────┘       │
│  ┌─────────────────────────────────────────────────────┐       │
│  │  Phone Facts (525 sự kiện)                           │       │
│  │  - 55 trường dữ liệu mỗi phone                      │       │
│  │  - Lưu trữ: cellphones_vector_store.pkl             │       │
│  │  - Tìm kiếm: theo giá, hãng, category              │       │
│  └─────────────────────────────────────────────────────┘       │
└────────────────────────────────────────────────────────────────┘
```

---

## Pipeline xử lý (5 bước)

Khi người dùng tìm kiếm, hệ thống thực hiện 5 bước tuần tự:

### Bước 1: NLP Parsing
Phân tích câu tiếng Việt thành dữ liệu cấu trúc.

```
Input:  "Điện thoại chơi game tầm 15 triệu"
Output: {user_need: "gaming", budget: 16500000, budget_min: 13500000}
```

Hỗ trợ nhận dạng:
- 14 loại nhu cầu (gaming, photography, battery_life, premium, office, media, selfie, video, student, business, outdoor, lightweight, innovation, water_resistant)
- Ngân sách linh hoạt:
  - "tầm X triệu" / "khoảng X triệu" → ±10% (ví dụ: tầm 15tr → 13.5–16.5tr)
  - "dưới X triệu" → max = X
  - "từ X đến Y triệu" / "X-Y triệu" → min-max chính xác
  - "trên X triệu" → min = X
- Thương hiệu (iPhone, Samsung, Xiaomi, OPPO, Vivo, Realme, Honor, Asus, Google, v.v.)
- Tính năng đặc biệt (NFC, 5G, sạc không dây, jack tai nghe, v.v.)
- Camera chi tiết (zoom, OIS, góc rộng, chụp đêm, macro, v.v.)

### Bước 2: Forward Chaining
Đánh giá 66 luật IF-THEN theo thứ tự ưu tiên (priority cao chạy trước).

```
IF user_need = "gaming" AND budget >= 15000000
THEN category_filter = [gaming, flagship]
     min_ram = 12GB
     min_processor_tier = high
     min_refresh_rate = 120Hz
```

**Conflict Resolution:** Khi nhiều rules cùng fire, rule có priority cao hơn ghi đè rule thấp hơn.

### Bước 3: Knowledge Base Search + Filtering
- Tìm tất cả phones thỏa criteria cơ bản (giá, category, brand)
- **Loại phone price=0** ("Liên Hệ" — không biết giá) khi có budget filter
- Lọc tiếp theo inferred facts (RAM, pin, camera, processor tier, NFC, v.v.)

```
525 phones → KB search (budget + category + brand) → 45 candidates → filter → 22 phones pass
```

### Bước 4: Fuzzy Logic Scoring
Tính điểm mờ cho mỗi phone qua 6 tiêu chí với trọng số thay đổi theo nhu cầu:

| Nhu cầu | Performance | Screen | RAM | Battery | Price | Camera |
|---------|-------------|--------|-----|---------|-------|--------|
| Gaming | 35% | 30% | 15% | 12% | 5% | 3% |
| Photography | 15% | 5% | 10% | 10% | 10% | 50% |
| Battery | 15% | 5% | 8% | 55% | 15% | 2% |
| Student | 10% | 5% | 10% | 15% | 40% | 20% |
| Media | 15% | 30% | 10% | 25% | 10% | 10% |
| Selfie | 15% | 7% | 8% | 5% | 20% | 45% |
| Office | 25% | 10% | 15% | 25% | 20% | 5% |

**Price-Budget Fitness (budget-aware):**

Thay vì phân loại giá tuyệt đối, hệ thống tính price fitness dựa trên tỷ lệ giá/ngân sách:

```
ratio = phone_price / user_budget

ratio ≤ 0.3  → score 0.3–0.6 (quá rẻ, thiếu tính năng)
ratio 0.3–0.5 → score 0.6–0.9 (rẻ hơn budget, chấp nhận được)
ratio 0.5–1.0 → score 0.9–1.0 (gần budget, giá trị tốt nhất ✓)
ratio 1.0–1.1 → score 0.7–1.0 (hơi vượt budget)
ratio > 1.1   → score giảm nhanh (vượt budget nhiều)
```

**Công thức tổng điểm:**
```
Total Score = Fuzzy Score × 0.7 + Rule Compliance × 0.3

# Phone không có giá (price=0, "Liên Hệ"):
Total Score × 0.6  (penalty vì không biết giá thực tế)
```

### Bước 5: Ranking & Output
Sắp xếp theo tổng điểm giảm dần, trả về top N kết quả kèm giải thích.

---

## Cấu trúc thư mục

```
Assistant_Smartphone/
├── app.py                          # Streamlit UI chính
├── inference_engine/
│   ├── integrated_inference.py     # IntegratedPhoneAdvisor (điều phối toàn bộ)
│   ├── forward_chaining.py         # Forward Chaining Engine
│   ├── fuzzy_logic.py              # Fuzzy Logic scoring system
│   ├── explanation.py              # Explanation Generator
│   └── conflict_resolution.py      # Conflict resolution strategies
├── knowledge_base/
│   ├── __init__.py                 # KnowledgeBase class (facade)
│   ├── rules.py                    # 66 rules + ClassificationRules
│   ├── phone_facts.py              # PhoneFacts - quản lý dữ liệu phone
│   ├── vector_store.py             # Vector store interface
│   ├── embeddings.py               # Embedding utilities
│   ├── indexer.py                   # Data indexer
│   └── retriever.py                # Retrieval interface
├── data/
│   ├── cellphones_vector_store.pkl # Knowledge Base chính (525 phones)
│   ├── cellphones_stats.json       # Thống kê DB
│   ├── cellphones_processed_full.json # Dữ liệu đã xử lý (JSON)
│   ├── CellphoneS_Data_Final_Cleaned.xlsx # Source data gốc
│   └── column_mapping.json         # Mapping cột Excel → field
├── knowledge_acquisition.py        # Module thêm/sửa/xóa rules & facts
├── working_memory.py               # Working memory cho inference
├── index_cellphones_data.py        # Script index data từ Excel → pkl
├── utils/
│   ├── config.py                   # Configuration
│   └── data_loader.py              # Data loading utilities
├── tests/                          # Unit tests
├── api/                            # FastAPI endpoints (optional)
├── deploy/                         # Docker, Heroku configs
├── .streamlit/config.toml          # Streamlit theme config
├── requirements.txt                # Full dependencies
└── requirements_simple.txt         # Minimal dependencies
```

---

## Cài đặt & Chạy

### Yêu cầu
- Python 3.10+
- Windows / Linux / macOS

### Cài đặt

```bash
git clone https://github.com/hhhhhsaas/Assistant_Smartphone.git
cd Assistant_Smartphone

python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements_simple.txt
```

### Chạy ứng dụng

```bash
streamlit run app.py
```

Mở trình duyệt tại `http://localhost:8501`

### Index lại dữ liệu (nếu cần)

```bash
python index_cellphones_data.py
```

File `data/cellphones_vector_store.pkl` sẽ được tạo lại từ `data/CellphoneS_Data_Final_Cleaned.xlsx`.

---

## Chi tiết kỹ thuật

### Forward Chaining Engine

Engine đánh giá rules theo vòng lặp:
1. Thu thập tất cả rules có conditions thỏa mãn (matching rules)
2. Conflict resolution: sắp xếp theo priority giảm dần
3. Fire tất cả rules theo thứ tự → thêm actions vào working memory (inferred facts)
4. Lặp lại cho đến khi không còn rule nào fire được

**Working Memory merging strategy:**
- `category_filter`: **Union** (merge tất cả categories từ các rules)
- `min_battery`, `min_camera_mp`: **Max** (lấy giá trị cao nhất)
- `max_weight`: **Min** (lấy giá trị thấp nhất)
- `preferred_brands`, `preferred_features`: **Union** (gộp danh sách)
- `min_ram`: **Max** (so sánh số GB, lấy cao hơn)
- Các key khác: Rule sau override rule trước

**Đặc biệt:** Rules có budget range (min/max) sẽ fire khi budget nằm trong khoảng. Rules cùng loại nhưng budget khác nhau cho phép hệ thống gợi ý khác nhau tùy ngân sách.

### Fuzzy Logic System

Sử dụng hàm membership trapezoidal/triangular để đánh giá mức độ phù hợp:

- **Price fitness (budget-aware):** Tính theo tỷ lệ giá/ngân sách — phone ở 50-100% budget được điểm cao nhất, quá rẻ (<30%) bị giảm, vượt budget (>110%) bị phạt nặng
- **Battery fitness:** Dựa trên dung lượng mAh (yếu <3500, trung bình 3000-4500, khỏe 4000-5000, rất khỏe >5000)
- **Camera fitness:** MP camera chính (cơ bản <20, tốt 16-48, rất tốt 32-108, chuyên nghiệp >64)
- **RAM fitness:** Dựa trên GB RAM (thấp <4, đủ dùng 3-10, cao 6-12, rất cao >12)
- **Screen fitness:** Kích thước inches (nhỏ <6", vừa 5.8-6.5", lớn 6.3-7", rất lớn >7")
- **Performance fitness:** Dựa trên processor tier (low → gaming-mid → mid → upper-mid → high)

### Processor Tier Classification

Hệ thống normalize tên chip (strip ® ™) trước khi phân loại:

```
high:       Snapdragon 8 Gen 2/3, Snapdragon 8 Elite, Apple A17/A18/A19, Dimensity 9200/9300
upper-mid:  Snapdragon 7+ Gen 2, Snapdragon 7 Gen 3, Dimensity 1080/1200/1300, Dimensity 7xxx
gaming-mid: Helio G95/G96/G99
mid:        Snapdragon 6xx (kể cả 6s Gen 3), Dimensity 6xx
low:        Snapdragon 4xx, Snapdragon 2xx, Helio P series
```

### Xử lý dữ liệu giá

Trong 525 phones, có 164 phone không có giá thực (price=0, tương đương "Liên Hệ" trên website). Hệ thống xử lý:

1. **Khi có budget:** Loại hoàn toàn phones price=0 khỏi kết quả (không thể so sánh giá)
2. **Khi không có budget:** Phones price=0 vẫn xuất hiện nhưng bị penalty ×0.6 trong scoring → đẩy xuống cuối danh sách
3. **Fuzzy price scoring:** Chỉ tính khi phone có giá > 0, ngược lại trả membership 0.01

### Classification Rules

Phones được phân loại tự động khi indexing:
1. **Gaming:** Tên chứa "ROG", "Red Magic", "Black Shark", "Legion"
2. **Foldable:** Tên chứa "Fold", "Flip", "Galaxy Z", "Razr"
3. **Flagship:** Giá > 20 triệu (hoặc RAM >= 12GB khi không có giá)
4. **Midrange:** Giá 5-20 triệu (hoặc RAM >= 8GB)
5. **Budget:** Giá < 5 triệu (hoặc RAM >= 4GB)
6. **Entry:** Fallback

### Pipeline Log UI

Sau mỗi lần tìm kiếm, UI hiển thị expander "Pipeline Expert System" với chi tiết:
- Input parsed từ NLP
- Rules được kích hoạt (tên + mô tả)
- Facts suy ra
- Bộ lọc áp dụng + số máy trước/sau lọc
- Fuzzy weights (bar chart)
- Top 3 kết quả + điểm

---

## Ví dụ sử dụng

### Tìm bằng mô tả
```
"Điện thoại chơi game tầm 15 triệu"
→ 5 kết quả, top: OPPO Reno14 5G 12GB (79%)

"iPhone chụp ảnh đẹp dưới 25 triệu"
→ 9 kết quả, top: iPhone 16 128GB (95%)

"Pin trâu giá rẻ cho sinh viên"
→ 10 kết quả, top: OPPO A6 Pro 7000mAh (89%)

"Samsung màn hình gập"
→ 9 foldable Samsung, top: Galaxy Z Flip5 (90%)

"Xiaomi pin trâu tầm 7 triệu"
→ 7 kết quả, top: Redmi Note 15 5G 5520mAh (89%)

"Điện thoại có NFC và 5G tầm 8 triệu"
→ 10 kết quả, top: HONOR X7d 5G (98%)

"Điện thoại từ 10 đến 15 triệu"
→ 36 kết quả đa dạng thương hiệu
```

### Tìm kiếm chi tiết
- Kéo slider ngân sách: 10-20 triệu
- Chọn hãng: Xiaomi
- Chọn mục đích: Gaming
- Tick: 5G, RAM >= 12GB
- Nhấn Tìm kiếm

---

## Dependencies chính

| Package | Mục đích |
|---------|----------|
| streamlit | Web UI |
| pandas | Data processing |
| numpy | Numerical computing |
| scikit-learn | Cosine similarity |
| openpyxl | Đọc file Excel |

---

## License

MIT
