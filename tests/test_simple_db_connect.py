# AttendanceApp/test_simple_db_connect.py
import mysql.connector
import sys
import os

print("--- Bắt đầu test_simple_db_connect.py ---")

# Định nghĩa DB_CONFIG TRỰC TIẾP TẠI ĐÂY để đảm bảo không có vấn đề import
DB_CONFIG_DIRECT = {
    'host': 'localhost',  # Địa chỉ MySQL server, thường là 'localhost'
    'user': 'root',       # Username mặc định của MySQL
    'password': '', # Thay bằng mật khẩu MySQL của bạn
    'database': 'attendance_app_python', # Tên cơ sở dữ liệu bạn đã tạo
    'port': 3306 # Cổng mặc định của MySQL,
}

conn = None  # Khởi tạo conn là None
try:
    print(
        f"Đang cố gắng kết nối tới CSDL: Host={DB_CONFIG_DIRECT['host']}, User={DB_CONFIG_DIRECT['user']}, DB={DB_CONFIG_DIRECT['database']}")

    # Kết nối với timeout
    conn = mysql.connector.connect(
        host=DB_CONFIG_DIRECT['host'],
        user=DB_CONFIG_DIRECT['user'],
        password=DB_CONFIG_DIRECT['password'],
        database=DB_CONFIG_DIRECT['database'],
        port=DB_CONFIG_DIRECT['port'],
        connection_timeout=5  # Đặt timeout 5 giây
    )

    if conn.is_connected():
        print("KẾT NỐI CSDL THÀNH CÔNG trong test_simple_db_connect.py!")
        # Thử một truy vấn đơn giản để xác nhận
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        print(f"Truy vấn test thành công, kết quả: {result}")
        cursor.close()
    else:
        print("KẾT NỐI CSDL THẤT BẠI trong test_simple_db_connect.py (không có ngoại lệ).")

except mysql.connector.Error as err:
    print(f"LỖI MySQL Connector TRONG test_simple_db_connect.py: {err}")
    print(f"Mã lỗi: {err.errno}")
    print(f"Trạng thái SQL: {err.sqlstate}")
    print(f"Thông báo lỗi: {err.msg}")
except Exception as e:
    print(f"LỖI KHÁC TRONG test_simple_db_connect.py: {e}")
finally:
    if conn and conn.is_connected():
        conn.close()
        print("Đã đóng kết nối CSDL trong test_simple_db_connect.py.")
    print("--- Kết thúc test_simple_db_connect.py ---")