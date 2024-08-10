#Định nghĩa về SQLi
Sqli là một lỗ hổng trong các ứng dụng web cho phép kẻ tấn công thực hiện các truy vấn SQL không được kiểm soát. Lỗ hổng này xuất phát từ việc không kiểm tra đầu vào của người dùng, dẫn đến việc kẻ tấn công có thể trích xuất toàn bộ thông tin của cơ sở dữ liệu, thêm sửa xóa dữ liệu, thậm chí chiếm quyền kiểm soát trên hệ thống.
#Phân loại SQLi: Có ba loại SQLi là:
1. In-band SQLi: là lỗ hổng mà kết quả của câu truy vấn được trả về trực tiếp cho người dùng. In-band được chia thành 2 loại là: Error-based SQLi và Union-based SQLi.
    a. Error-based SQLi: là loại lỗ hổng mà ứng dụng web trả về thông báo lỗi khi có lỗi trong câu truy vấn SQL. Từ đó hacker sẽ đoán được các thông tin về hệ quản trị CSDL được sử dụng, câu truy vấn gốc ...
    b. Union-based SQLi: là loại lỗ hổng cho phép kẻ tấn công sử dụng UNION SELECT để kết hợp kết quả truy vấn độc hại với kết quả truy vấn gốc.
2. Blind SQLi: là lỗ hổng sql mà kẻ tấn công không thể nhận được kết quả trực tiếp. Thay vào đó phải dựa vào các phản hồi gián tiếp để có thể suy luận thông tin. Có 2 loại Blind SQLi là: Time-based SQLi và Boolean-based SQLi.
    a. Boolean-based SQLi: là loại lỗ hổng mà kẻ tấn công sử dụng các câu truy vấn điều kiện đúng hoặc sai và quan sát phản hồi từ hệ thống (ví dụ như thông báo lỗi, thay đổi nội dung trang ...).
    b. Time-based SQLi: là loại lỗ hổng mà kẻ tấn công sử dụng các câu truy vấn điều kiện đúng hoặc sai và quan sát thời gian phản hồi từ hệ thống.
3. Out-of-band SQLi: là loại lỗ hổng mà kẻ tấn công không thể nhận được các ảnh hưởng trực tiếp của hệ thống thông qua kênh đang khai thác. Kỹ thuật này hacker sẽ sử dụng các câu truy vấn (các câu truy vấn thực hiện các loại lệnh cmd bash như nslookup, dns, ping ...) để gửi các yêu cầu đến một máy chủ của hacker để thu thập các thông tin.
#Làm sao để tìm ra SQLi?
1. Kiểm tra thủ công: thử các payload cố tình làm sai lệch câu lệnh, hoặc thử các lệnh điều kiện như boolean-bases, time-based, thử exec,nslookup, ping ...
  