# Công cụ NoSQL Injection

## Giới thiệu
Công cụ này cung cấp khả năng:

1. **Liệt kê các trường dữ liệu**:
   - Phát hiện các trường trong CSDL thông qua kỹ thuật injection
   - Hỗ trợ nhập các trường đã biết từ người dùng
   - Quét từng ký tự để phát hiện các trường chưa biết

2. **Trích xuất giá trị**:
   - Dump giá trị của các trường được chỉ định
   - Sử dụng các bộ ký tự khác nhau cho từng loại trường (email, mật khẩu, v.v.)
   - Hỗ trợ brute-force từng ký tự

3. **Tính năng nâng cao**:
   - Xử lý song song với ThreadPoolExecutor
   - Giao diện tương tác thân thiện
   - Cấu hình linh hoạt (URL, cookie, headers)
   - Quản lý phiên và kết nối hiệu quả

## Cách sử dụng
1. Chạy chương trình: `python NoSQL.py`
2. Nhập các trường đã biết (nếu có)
3. Chọn các trường cần dump giá trị
4. Xem kết quả và tiếp tục quét nếu cần

## Ưu điểm
- Linh hoạt: Cho phép người dùng nhập các trường đã biết
- Hiệu quả: Sử dụng kỹ thuật song song để tăng tốc quá trình quét
- Dễ sử dụng: Giao diện tương tác rõ ràng, hướng dẫn từng bước
- An toàn: Xử lý lỗi và ngoại lệ một cách chặt chẽ

