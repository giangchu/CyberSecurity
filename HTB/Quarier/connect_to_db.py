import pyodbc

# Thông tin kết nối từ macro VBA
server = '10.129.6.7'
database = 'volume'
username = 'reporting'  # Đây là username
password = 'PcwTWTHRwryjc$c6'  # Đây là mật khẩu

# Chuỗi kết nối
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};Connection Timeout=30'

try:
    # Kết nối đến cơ sở dữ liệu
    conn = pyodbc.connect(connection_string)
    print("Kết nối thành công!")

    # Tạo một cursor để thực hiện truy vấn
    cursor = conn.cursor()

    # Thực hiện truy vấn
    cursor.execute("SELECT * FROM volume")

    # Lấy kết quả truy vấn
    rows = cursor.fetchall()

    # In kết quả
    for row in rows:
        print(row)

    # Đóng kết nối
    cursor.close()
    conn.close()

except Exception as e:
    print(f"Đã xảy ra lỗi: {e}")
