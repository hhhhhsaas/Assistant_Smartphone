# Expert System - Smartphone Advisor

Hệ chuyên gia tư vấn điện thoại thông minh sử dụng **Forward Chaining** + **Fuzzy Logic**, xây dựng bằng Python và Streamlit.

## Tổng quan

Hệ thống giúp người dùng tìm điện thoại phù hợp dựa trên nhu cầu cá nhân (gaming, chụp ảnh, pin trâu, v.v.) và ngân sách. Người dùng có thể mô tả bằng ngôn ngữ tự nhiên tiếng Việt, hệ thống sẽ phân tích, suy luận và xếp hạng các điện thoại phù hợp nhất.

**Quy mô:** 525 điện thoại | 66 luật suy luận | 20 thương hiệu | 6 phân khúc

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
- Ngân sách (tầm X triệu, dưới X triệu, từ X đến Y triệu)
- Thương hiệu (iPhone, Samsung, Xiaomi, OPPO, Vivo, Realme, v.v.)
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
- Lọc tiếp theo inferred facts (RAM, pin, camera, processor tier, NFC, v.v.)

```
500 candidates → filter → 22 phones pass
```

### Bước 4: Fuzzy Logic Scoring
Tính điểm mờ cho mỗi phone qua 6 tiêu chí với trọng số thay đổi theo nhu cầu:

| Nhu cầu | Performance | Screen | RAM | Battery | Price | Camera |
|---------|-------------|--------|-----|---------|-------|--------|
| Gaming | 35% | 30% | 15% | 12% | 5% | 3% |
| Photography | 15% | 5% | 10% | 10% | 10% | 50% |
| Battery | 15% | 5% | 8% | 55% | 15% | 2% |
| Student | 10% | 5% | 10% | 15% | 40% | 20% |

**Công thức tổng điểm:**
```
Total Score = Fuzzy Score × 0.7 + Rule Compliance × 0.3
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
2. Conflict resolution: chọn rule có priority cao nhất
3. Fire rule → thêm actions vào working memory (inferred facts)
4. Lặp lại cho đến khi không còn rule nào fire được

**Đặc biệt:** Rules có budget range (min/max) sẽ fire khi budget nằm trong khoảng. Rules cùng loại nhưng budget khác nhau cho phép hệ thống gợi ý khác nhau tùy ngân sách.

### Fuzzy Logic System

Sử dụng hàm membership trapezoidal/triangular để đánh giá mức độ phù hợp:

- **Price fitness:** Điểm cao khi giá nằm trong ngân sách, giảm dần khi vượt
- **Battery fitness:** Dựa trên dung lượng mAh, chuẩn hóa theo phân khúc
- **Camera fitness:** MP camera chính + bonus cho camera front
- **RAM fitness:** Dựa trên GB RAM, chuẩn hóa
- **Screen fitness:** Kích thước + refresh rate
- **Performance fitness:** Dựa trên processor tier (low → mid → upper-mid → high)

### Processor Tier Classification

```
high:       Snapdragon 8 Gen 2/3, Apple A17/A18/A19, Dimensity 9200/9300
upper-mid:  Snapdragon 7+ Gen 2, Dimensity 1080/1200/1300
gaming-mid: Helio G95/G96/G99
mid:        Snapdragon 6xx, Dimensity 6xx
low:        Snapdragon 4xx, Snapdragon 2xx, Helio P series
```

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
→ 22 kết quả, top: HONOR Magic 7 Pro (86%)

"iPhone chụp ảnh đẹp dưới 25 triệu"
→ 9 kết quả (Apple + camera 48MP+ OIS)

"Pin trâu giá rẻ cho sinh viên"
→ 13 kết quả (OPPO/Xiaomi, 6000mAh, < 10 triệu)

"Samsung màn hình gập"
→ 9 foldable Samsung
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
