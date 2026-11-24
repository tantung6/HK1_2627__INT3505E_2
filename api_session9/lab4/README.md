# Week 9 - Lab 4: Blue-Green Routing với Gateway Pattern

Thực hành theo **Slide 23 (Practice 4 / 5)** - Môn Kiến trúc hướng dịch vụ (SOA): *09 API Versioning & Lifecycle Management*.

---

## 1. Mục tiêu bài lab

- Cùng một URL duy nhất: `POST /orders`, hệ thống API Gateway tự động quyết định điều hướng request tới `v1_create_order` hay `v2_create_order` một cách trong suốt đối với client.
- Triển khai **3 tầng điều hướng (3-Tier Routing Architecture)**:
  1. **Tầng 1 (Ưu tiên cao nhất): Explicit Cohort Header**
     - Nếu request gửi kèm header `X-Cohort: beta` hoặc `X-Cohort: internal` $\rightarrow$ luôn định tuyến tới `v2`.
  2. **Tầng 2: Allow-listed Account**
     - Nếu payload có `account_id` nằm trong danh sách ép buộc thử nghiệm (`acct_42`, `acct_99`) $\rightarrow$ luôn định tuyến tới `v2`.
  3. **Tầng 3: Deterministic Percentage Bucket (Hash MD5)**
     - Với các tài khoản thông thường còn lại, băm MD5 `account_id` để chia thành 100 buckets (`0 - 99`).
     - Nếu bucket `< V2_PERCENT` (mặc định 5%) $\rightarrow$ vào `v2`; ngược lại vào `v1`. Đảm bảo cùng một account sẽ luôn luôn vào cùng một version (tính nhất quán).
- Phục vụ chiến lược chuyển đổi **Strangler Fig / Blue-Green**: Rollout tăng dần từ `5%` $\rightarrow$ `100%`, sau khi ổn định thì lưu trữ và sunset v1.

---

## 2. Cấu trúc thư mục

```text
Week9/lab4/
├── handlers.py                 # Logic xử lý đơn hàng của v1 (HTTP 200) và v2 (HTTP 201)
├── gateway.py                  # Module 3-tier routing quyết định version phục vụ
├── app.py                      # Flask Gateway API (/orders và dashboard /admin/rollout)
├── requirements.txt            # Thư viện phụ thuộc
├── tests/
│   ├── __init__.py
│   └── test_gateway_routing.py # 7 bài unit test tự động bao phủ 5 kịch bản Slide 23
└── README.md                   # Tài liệu hướng dẫn chi tiết
```

---

## 3. Cài đặt và Khởi chạy Gateway Server

### Kích hoạt môi trường ảo:
```bash
source /Users/tuanphong/Downloads/KTHDV/HK1_2627__INT3505E_2/Week7/.venv/bin/activate
```

### Khởi chạy ứng dụng:
```bash
cd /Users/tuanphong/Downloads/KTHDV/HK1_2627__INT3505E_2/Week9/lab4
python app.py
```
Server sẽ chạy mặc định tại: `http://127.0.0.1:5000`.

---

## 4. Kiểm thử 5 kịch bản (Test Commands từ Slide 23)

Mở một Terminal khác và thực hiện các lệnh cURL tương ứng:

### Kịch bản 1: Header Cohort beta $\rightarrow$ v2
```bash
curl -i -X POST http://127.0.0.1:5000/orders \
  -H "Content-Type: application/json" \
  -H "X-Cohort: beta" \
  -d '{"account_id": "any"}'
```
*Kết quả:* Status `201 CREATED`, Header `X-Order-Handler: v2`.

### Kịch bản 2: Tài khoản được ép trong Allow-list (`acct_42`) $\rightarrow$ v2
```bash
curl -i -X POST http://127.0.0.1:5000/orders \
  -H "Content-Type: application/json" \
  -d '{"account_id": "acct_42"}'
```
*Kết quả:* Status `201 CREATED`, Header `X-Order-Handler: v2`.

### Kịch bản 3: Tài khoản thông thường $\rightarrow$ Hash Bucket quyết định (5%)
- Tài khoản rơi vào nhóm 95% (`user_1`):
  ```bash
  curl -i -X POST http://127.0.0.1:5000/orders \
    -H "Content-Type: application/json" \
    -d '{"account_id": "user_1"}'
  ```
  *Kết quả:* Status `200 OK`, Header `X-Order-Handler: v1`.

- Tài khoản rơi vào nhóm 5% (`user_38`):
  ```bash
  curl -i -X POST http://127.0.0.1:5000/orders \
    -H "Content-Type: application/json" \
    -d '{"account_id": "user_38"}'
  ```
  *Kết quả:* Status `201 CREATED`, Header `X-Order-Handler: v2`.

### Kịch bản 4: Tăng tỉ lệ rollout lên 100% (`V2_PERCENT = 100`) $\rightarrow$ Toàn bộ vào v2
- Chỉnh tỉ lệ qua endpoint dashboard:
  ```bash
  curl -i -X POST http://127.0.0.1:5000/admin/rollout \
    -H "Content-Type: application/json" \
    -d '{"v2_percent": 100}'
  ```
- Kiểm tra lại với `user_1`:
  ```bash
  curl -i -X POST http://127.0.0.1:5000/orders \
    -H "Content-Type: application/json" \
    -d '{"account_id": "user_1"}'
  ```
  *Kết quả:* Lúc này `user_1` đã tự động chuyển sang `v2` (Status `201`, `X-Order-Handler: v2`).

### Kịch bản 5: Hoàn tất chuyển đổi & Archive
Sau khi chạy 100% ổn định trong thời gian theo dõi (ví dụ 30 ngày), toàn bộ traffic đã phục vụ bởi v2, v1 có thể lưu trữ (archive) và gỡ bỏ hoàn toàn mà không gây gián đoạn (zero-downtime).

---

## 5. Chạy Automated Tests (Pytest)

Chạy bộ unit test tự động:
```bash
cd /Users/tuanphong/Downloads/KTHDV/HK1_2627__INT3505E_2/Week9/lab4
/Users/tuanphong/Downloads/KTHDV/HK1_2627__INT3505E_2/Week7/.venv/bin/pytest tests/ -v
```
Hoặc từ thư mục gốc của repository:
```bash
PYTHONPATH=Week9/lab4 /Users/tuanphong/Downloads/KTHDV/HK1_2627__INT3505E_2/Week7/.venv/bin/pytest Week9/lab4/tests/ -v
```
*(Kết quả: 7/7 test PASSED 100%)*
