# Week 9 - Lab 3: Sunset Middleware với Decorator `@deprecate_at` (RFC 8594)

Thực hành theo **Slide 22 (Practice 3 / 5)** - Môn Kiến trúc hướng dịch vụ (SOA): *09 API Versioning & Lifecycle Management*.

---

## 1. Mục tiêu bài lab

- Chuẩn hóa quy trình Deprecation theo tiêu chuẩn IETF **RFC 8594** (Sunset HTTP Header Field).
- Xây dựng middleware dạng decorator tái sử dụng: `@deprecate_at(sunset_date, replacement)`.
- Xử lý 2 giai đoạn vòng đời của một API endpoint:
  1. **Trước ngày Sunset:** Vẫn phục vụ dữ liệu bình thường (**HTTP 200**), đồng thời gửi kèm các HTTP response headers báo hiệu cho client biết API sắp ngừng hoạt động:
     - `Sunset: <HTTP-date>` (ví dụ: `Thu, 31 Dec 2026 23:59:59 GMT`).
     - `Deprecation: true`.
     - `Link: </api/v2/...>; rel="successor-version"` (trỏ đến phiên bản kế thừa).
     - Ghi cảnh báo server log: `WARN deprecated_call <path> <client_ip>` để đội ngũ vận hành thống kê lượng client còn sử dụng bản cũ.
  2. **Sau ngày Sunset:** Khi đã vượt qua mốc thời gian ấn định, ngắt kết nối an toàn bằng **HTTP 410 Gone** kèm JSON body giải thích và cung cấp endpoint thay thế (`use_instead`).

---

## 2. Cấu trúc thư mục

```text
Week9/lab3/
├── sunset.py                   # Decorator @deprecate_at theo chuẩn RFC 8594
├── app.py                      # Flask app áp dụng decorator cho v1 & v0 (quá khứ)
├── requirements.txt            # Danh sách thư viện phụ thuộc
├── tests/
│   ├── __init__.py
│   └── test_sunset.py          # 5 unit tests tự động (trước sunset, sau sunset, mock time, v2)
└── README.md                   # Tài liệu hướng dẫn chi tiết
```

---

## 3. Cài đặt và Khởi chạy Server

### Kích hoạt môi trường ảo:
```bash
source /Users/tuanphong/Downloads/KTHDV/HK1_2627__INT3505E_2/Week7/.venv/bin/activate
```

### Khởi chạy ứng dụng Flask:
```bash
cd /Users/tuanphong/Downloads/KTHDV/HK1_2627__INT3505E_2/Week9/lab3
python app.py
```
Server sẽ chạy mặc định tại: `http://127.0.0.1:5000`.

---

## 4. Kiểm thử 3 tình huống với cURL (Theo Slide 22)

Mở một Terminal khác và thực hiện các lệnh kiểm tra:

### Tình huống 1: Trước Sunset (Endpoint v1 còn hạn)
```bash
curl -i http://127.0.0.1:5000/api/v1/users/1
```
*Kết quả phản hồi:*
- Mã trạng thái: `HTTP/1.1 200 OK`
- Response Headers:
  ```http
  Sunset: Thu, 31 Dec 2026 23:59:59 GMT
  Deprecation: true
  Link: </api/v2/users>; rel="successor-version"
  ```
- Response Body:
  ```json
  {
    "full_name": "Nguyễn Văn A",
    "id": 1
  }
  ```

### Tình huống 2: Sau Sunset (Endpoint v0 đã hết hạn)
```bash
curl -i http://127.0.0.1:5000/api/v0/users/1
```
*Kết quả phản hồi:*
- Mã trạng thái: `HTTP/1.1 410 GONE`
- Response Body:
  ```json
  {
    "error": "gone",
    "sunset": "Mon, 01 Jan 2024 00:00:00 GMT",
    "use_instead": "/api/v1/users"
  }
  ```

### Tình huống 3: Kiểm tra Server Log
Tại terminal đang chạy Flask app, kiểm tra log console:
```text
[WARNING] sunset: deprecated_call /api/v1/users/1 127.0.0.1
```
Log cảnh báo này giúp hệ thống giám sát (như Prometheus / Grafana / Datadog) phát hiện các client chưa kịp nâng cấp lên v2 trước ngày shutdown.

---

## 5. Chạy Automated Tests (Pytest)

Chạy bộ kiểm thử tự động kiểm tra cả tình huống thực tế và mô phỏng thời gian tương lai:
```bash
cd /Users/tuanphong/Downloads/KTHDV/HK1_2627__INT3505E_2/Week9/lab3
/Users/tuanphong/Downloads/KTHDV/HK1_2627__INT3505E_2/Week7/.venv/bin/pytest tests/ -v
```
Hoặc từ thư mục gốc của repository:
```bash
PYTHONPATH=Week9/lab3 /Users/tuanphong/Downloads/KTHDV/HK1_2627__INT3505E_2/Week7/.venv/bin/pytest Week9/lab3/tests/ -v
```

---

## 6. Tổng kết kiến thức chuẩn RFC 8594

1. **`Sunset` header** mang giá trị thời gian chuẩn HTTP-date (`RFC 7231`), chỉ rõ thời điểm chính xác endpoint sẽ bị ngừng cung cấp.
2. **`Deprecation` header** (thường mang giá trị `true` hoặc ngày tháng) báo hiệu endpoint này đã bị coi là lỗi thời nhưng vẫn đang hoạt động.
3. **`Link` header với `rel="successor-version"`** giúp các client tự động hoặc lập trình viên biết tài nguyên kế thừa nằm ở đâu.
4. **Mã HTTP 410 Gone** là mã chuẩn xác nhất theo đặc tả HTTP để thông báo một tài nguyên trước đây từng tồn tại nhưng nay đã bị xóa vĩnh viễn và sẽ không bao giờ hoạt động trở lại.
