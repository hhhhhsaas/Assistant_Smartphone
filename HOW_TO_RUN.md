# 🚀 HƯỚNG DẪN CHẠY ỨNG DỤNG

## 📋 Kiểm tra trước khi chạy

1. **Python đã cài chưa?**
```bash
python --version
# Cần Python 3.8 trở lên
```

2. **Kiểm tra files cần thiết**
```bash
# Phải có các files sau:
- app.py
- data/cellphones_vector_store.pkl
- data/cellphones_stats.json
- inference_engine/fuzzy_logic.py
- inference_engine/rules_engine.py
- inference_engine/integrated_inference.py
- knowledge_base/simple_vector_store.py
```

## 🔧 Cài đặt nhanh

### Bước 1: Mở Terminal/Command Prompt
```bash
cd d:\Code\Projects\Python\Assistant_Smartphone
```

### Bước 2: Cài đặt packages
```bash
pip install streamlit pandas numpy scikit-learn
```

### Bước 3: Chạy ứng dụng
```bash
streamlit run app.py
```

## 🎯 Chạy thành công khi:

1. Terminal hiển thị:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

2. Trình duyệt tự động mở với giao diện ứng dụng

## ❌ Xử lý lỗi thường gặp

### Lỗi 1: ModuleNotFoundError
```bash
# Cài lại packages
pip install -r requirements.txt
```

### Lỗi 2: FileNotFoundError cho data files
```bash
# Chạy lại indexing
python index_cellphones_data.py
```

### Lỗi 3: Port 8501 đã được sử dụng
```bash
# Dùng port khác
streamlit run app.py --server.port 8502
```

### Lỗi 4: Encoding error (Windows)
```bash
# Set encoding cho terminal
chcp 65001
```

## 🎮 Cách sử dụng nhanh

### Test 1: Ngôn ngữ tự nhiên
1. Chọn "🗣️ Ngôn ngữ tự nhiên" ở sidebar
2. Nhập: "Tìm điện thoại gaming tầm 15 triệu"
3. Nhấn "🔍 Tìm kiếm"

### Test 2: Tìm kiếm chi tiết
1. Chọn "⚙️ Tìm kiếm chi tiết"
2. Kéo thanh ngân sách: 10-20 triệu
3. Chọn mục đích: "🎮 Gaming"
4. Nhấn "🔍 Tìm kiếm"

### Test 3: So sánh điện thoại
1. Tìm kiếm bất kỳ
2. Nhấn "So sánh" trên 2-3 điện thoại
3. Xem bảng so sánh ở cuối trang

## 📱 Demo nhanh không cần UI

```bash
# Test Fuzzy Logic
python -m inference_engine.fuzzy_logic

# Test Rules Engine
python -m inference_engine.rules_engine

# Test tìm kiếm
python quick_test.py
```

## 🔄 Cập nhật dữ liệu mới

```bash
# Nếu có file Excel mới
python index_cellphones_data.py

# Xem thống kê
python demo_cellphones_kb.py
```

## 💡 Tips

1. **Chạy nhanh hơn**: Thêm `--server.fastRefresh false`
2. **Debug mode**: Thêm `--logger.level debug`
3. **Share online**: Thêm `--server.headless true`

## 📞 Cần hỗ trợ?

- Kiểm tra file `TEST_GUIDE.md` để test từng component
- Xem `TECHNICAL_SPECIFICATION.md` để hiểu logic
- Đọc `README.md` cho thông tin tổng quan

---

**Quick Start Command:**
```bash
streamlit run app.py
```

**Chúc bạn trải nghiệm vui vẻ! 🎉**