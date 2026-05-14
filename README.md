# Hệ thống Tư vấn Điện thoại AI-Assisted

## Giới thiệu
Đây là hệ thống Knowledge Base cho dự án tư vấn điện thoại thông minh sử dụng AI. Hệ thống sử dụng vector embeddings và semantic search để tìm kiếm và gợi ý điện thoại phù hợp với nhu cầu người dùng.

## Tính năng chính

### 1. Knowledge Base
- **Vector Store**: Sử dụng ChromaDB để lưu trữ vector embeddings
- **Embedding Model**: Sentence Transformers để chuyển đổi text sang vectors
- **Semantic Search**: Tìm kiếm theo ngữ nghĩa tự nhiên
- **Similarity Search**: Tìm điện thoại tương tự
- **Filtering**: Lọc theo giá, hãng, tính năng

### 2. Retrieval System
- Tìm kiếm theo câu hỏi tự nhiên
- Gợi ý theo yêu cầu cụ thể (gaming, chụp ảnh, giá rẻ...)
- So sánh nhiều điện thoại
- Tìm theo khoảng giá

### 3. REST API
- FastAPI server với endpoints đầy đủ
- CORS enabled cho web applications
- Swagger documentation tự động

## Cài đặt

### 1. Clone project
```bash
git clone <repository>
cd Assistant_Smartphone
```

### 2. Tạo môi trường ảo
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 4. Cấu hình môi trường
Chỉnh sửa file `.env` nếu cần:
```env
EMBEDDING_MODEL=all-MiniLM-L6-v2
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

## Sử dụng

### 1. Setup và Index dữ liệu
```bash
# Setup knowledge base
python run_system.py setup

# Index sample data
python run_system.py index --data-path data/sample_phones.json

# Clear và reindex
python run_system.py index --data-path data/sample_phones.json --clear
```

### 2. Chạy Interactive Search
```bash
python run_system.py search
```

Các lệnh trong interactive mode:
- `search <query>`: Tìm kiếm điện thoại
- `similar <phone_id>`: Tìm điện thoại tương tự
- `compare <id1> <id2>`: So sánh 2 điện thoại
- `price <min> <max>`: Tìm theo khoảng giá
- `stats`: Xem thống kê database
- `quit`: Thoát

### 3. Chạy API Server
```bash
python run_system.py api
```

Server sẽ chạy tại `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### 4. Test hệ thống
```bash
python run_system.py test
# hoặc
python test_knowledge_base.py
```

## API Endpoints

### Search
```http
POST /api/search
{
  "query": "điện thoại chơi game",
  "n_results": 5
}
```

### Recommend
```http
POST /api/recommend
{
  "purpose": "gaming",
  "budget_min": 10000000,
  "budget_max": 20000000,
  "features": ["5G", "120Hz"]
}
```

### Get Phone Details
```http
GET /api/phone/{phone_id}
```

### Find Similar Phones
```http
GET /api/similar/{phone_id}?n_results=5
```

### Compare Phones
```http
POST /api/compare
{
  "phone_ids": ["phone_id_1", "phone_id_2"]
}
```

### Price Range Search
```http
GET /api/price-range?min_price=5000000&max_price=15000000
```

## Cấu trúc dữ liệu

### Phone Data Schema
```json
{
  "name": "string",
  "brand": "string",
  "price": "number",
  "category": "flagship|midrange|budget|entry",
  "screen_size": "string",
  "ram": "string",
  "storage": "string",
  "battery": "string",
  "camera": "string",
  "processor": "string",
  "features": ["array", "of", "features"],
  "os": "string"
}
```

## Thêm dữ liệu mới

### 1. Từ JSON file
```python
from knowledge_base import DataIndexer, VectorStore, EmbeddingModel

# Initialize
embedding_model = EmbeddingModel()
vector_store = VectorStore()
indexer = DataIndexer(vector_store, embedding_model)

# Index from JSON
stats = indexer.index_from_json("path/to/phones.json")
```

### 2. Từ CSV file
```python
# With column mapping
column_mapping = {
    "Phone Name": "name",
    "Brand Name": "brand",
    "Price (VND)": "price"
}

stats = indexer.index_from_csv(
    "path/to/phones.csv",
    column_mapping=column_mapping
)
```

### 3. Single phone via API
```bash
curl -X POST "http://localhost:8000/api/index/phone" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "iPhone 15",
    "brand": "Apple",
    "price": 25000000,
    "ram": "6GB",
    "storage": "128GB"
  }'
```

## Embedding Models

Có thể thay đổi model trong `.env`:

- `all-MiniLM-L6-v2`: Nhanh, nhẹ, phù hợp cho production
- `all-mpnet-base-v2`: Chất lượng cao hơn, chậm hơn
- `paraphrase-multilingual-MiniLM-L12-v2`: Hỗ trợ đa ngôn ngữ

## Troubleshooting

### 1. ChromaDB errors
```bash
# Clear database
rm -rf data/chroma_db/
python run_system.py index --clear
```

### 2. Memory issues với embedding model
Giảm batch_size trong indexing:
```python
indexer.index_from_json("data.json", batch_size=16)
```

### 3. Port đã được sử dụng
Thay đổi port trong `.env`:
```env
API_PORT=8001
```

## Performance Tips

1. **Indexing**: Sử dụng batch processing với batch_size phù hợp
2. **Search**: Limit số kết quả trả về (n_results)
3. **Embedding Model**: Chọn model phù hợp với use case
4. **Caching**: ChromaDB tự động cache, không cần setup thêm

## Development

### Thêm retrieval strategy mới
```python
# In retriever.py
def retrieve_by_custom_strategy(self, params):
    # Your custom logic
    pass
```

### Customize embedding
```python
# In embeddings.py
def encode_custom_format(self, data):
    # Custom encoding logic
    pass
```

## Roadmap

- [ ] Thêm support cho nhiều ngôn ngữ
- [ ] Implement caching layer
- [ ] Thêm real-time price updates
- [ ] Integration với e-commerce APIs
- [ ] User feedback learning
- [ ] Advanced filtering options

## License
MIT

## Contact
For questions or support, please contact the development team.