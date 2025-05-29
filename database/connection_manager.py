# database/connection_manager.py
# import mysql.connector
# from mysql.connector import Error
# from config import DB_CONFIG
#
# class ConnectionManager:
#     _instance = None # Singleton instance
#
#     def __new__(cls):
#         # Implement Singleton pattern to ensure only one connection manager exists
#         if cls._instance is None:
#             cls._instance = super(ConnectionManager, cls).__new__(cls)
#             cls._instance.connection = None
#             cls._instance.cursor = None
#         return cls._instance
#
#     def connect(self):
#         """Kết nối đến cơ sở dữ liệu MySQL."""
#         if self.connection and self.connection.is_connected():
#             return True # Already connected
#
#         try:
#             self.connection = mysql.connector.connect(**DB_CONFIG)
#             if self.connection.is_connected():
#                 self.cursor = self.connection.cursor(buffered=True)
#                 print("Kết nối MySQL thành công!!")
#                 return True
#         except Error as e:
#             print(f"Lỗi kết nối MySQL: {e}")
#             self.connection = None # Reset connection on failure
#             return False
#
#     def disconnect(self):
#         """Ngắt kết nối đến cơ sở dữ liệu MySQL."""
#         if self.connection and self.connection.is_connected():
#             self.cursor.close()
#             self.connection.close()
#             self.connection = None # Clear connection
#             print("Đã ngắt kết nối MySQL.")
#
#     def get_connection(self):
#         """Trả về đối tượng kết nối hiện tại."""
#         if not self.connection or not self.connection.is_connected():
#             self.connect() # Try to reconnect if not connected
#         return self.connection
#
#     def get_cursor(self):
#         """Trả về đối tượng con trỏ hiện tại."""
#         if not self.connection or not self.connection.is_connected():
#             self.connect()
#         return self.cursor
#
# # Test ConnectionManager (optional, for direct testing)
# if __name__ == '__main__':
#     conn_manager = ConnectionManager()
#     if conn_manager.connect():
#         cursor = conn_manager.get_cursor()
#         if cursor:
#             try:
#                 cursor.execute("SELECT VERSION()")
#                 db_version = cursor.fetchone()
#                 print(f"Phiên bản MySQL qua ConnectionManager: {db_version[0]}")
#             except Error as e:
#                 print(f"Lỗi khi thực thi truy vấn: {e}")
#             finally:
#                 conn_manager.disconnect()
#         else:
#             print("Không lấy được cursor.")
#     else:
#         print("Không thể kết nối DB qua ConnectionManager.")



# Version 2
# database/connection_manager.py
# Thay thế: import mysql.connector
# Thay thế: from mysql.connector import Error
import pymysql.cursors  # <-- THAY THẾ DÒNG NÀY
from pymysql import Error  # <-- THAY THẾ DÒNG NÀY

import sys
import os

# Đảm bảo import config.py
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config import DB_CONFIG


class ConnectionManager:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConnectionManager, cls).__new__(cls)
            cls._instance.connection = None
            cls._instance.cursor = None
        return cls._instance

    def connect(self):
        """Kết nối đến cơ sở dữ liệu MySQL."""
        if self.connection and self.connection.open:  # PyMySQL dùng .open thay vì .is_connected()
            print("ConnectionManager: Đã có kết nối CSDL hoạt động, không cần kết nối lại.")
            return True

        print("ConnectionManager: Đang cố gắng thiết lập kết nối CSDL...")

        try:
            print("ConnectionManager: Gọi pymysql.connect()...")
            self.connection = pymysql.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database'],
                port=DB_CONFIG['port'],
                cursorclass=pymysql.cursors.DictCursor,  # Tùy chọn: trả về kết quả dưới dạng dict
                connect_timeout=10  # Đặt timeout 10 giây
            )

            print("ConnectionManager: Đã gọi pymysql.connect(). Kiểm tra .open...")

            if self.connection.open:  # PyMySQL dùng .open
                print("ConnectionManager: Kết nối thành công!")
                self.cursor = self.connection.cursor()  # Con trỏ đã được định nghĩa bởi cursorclass

                # PyMySQL không có get_server_info() hay server_info trực tiếp như mysql.connector
                # Có thể lấy thông tin version bằng cách khác nếu cần
                print(f"ConnectionManager: Đã kết nối tới database: {DB_CONFIG['database']}")
                return True
            else:
                print(
                    "ConnectionManager: KHÔNG THỂ KẾT NỐI mặc dù không có ngoại lệ. Vui lòng kiểm tra CSDL/mạng hoặc config.")
                self.connection = None
                self.cursor = None
                return False
        except Error as e:  # PyMySQL.Error
            print(f"ConnectionManager: LỖI KẾT NỐI CSDL (PyMySQL): {e}")
            # Các thuộc tính lỗi có thể khác một chút so với mysql.connector
            # print(f"Mã lỗi: {e.errno}") # PyMySQL có thể không có
            # print(f"Trạng thái SQL: {e.sqlstate}") # PyMySQL có thể không có
            # print(f"Thông báo lỗi: {e.msg}") # PyMySQL có thể không có
            self.connection = None
            self.cursor = None
            return False
        except Exception as e:
            print(f"ConnectionManager: LỖI KHÔNG MONG MUỐN KHÁC KHI KẾT NỐI CSDL: {e}")
            self.connection = None
            self.cursor = None
            return False

    def disconnect(self):
        """Ngắt kết nối đến cơ sở dữ liệu MySQL."""
        if self.cursor:
            try:
                self.cursor.close()
            except Error as e:
                print(f"ConnectionManager: Lỗi khi đóng con trỏ: {e}")
            self.cursor = None

        if self.connection and self.connection.open:  # PyMySQL dùng .open
            try:
                self.connection.close()
                self.connection = None
                print("ConnectionManager: Đã ngắt kết nối MySQL.")
            except Error as e:
                print(f"ConnectionManager: Lỗi khi đóng kết nối: {e}")
        else:
            print("ConnectionManager: Không có kết nối để đóng.")

    def get_connection(self):
        if not self.connection or not self.connection.open:
            print("ConnectionManager: Kết nối chưa tồn tại hoặc đã mất, đang cố gắng kết nối lại.")
            self.connect()
        return self.connection

    def get_cursor(self):
        if not self.connection or not self.connection.open:
            print("ConnectionManager: Kết nối chưa tồn tại hoặc đã mất, đang cố gắng kết nối lại.")
            self.connect()
        if self.connection and self.connection.open and self.cursor is None:
            try:
                self.cursor = self.connection.cursor()
                print("ConnectionManager: Đã tạo lại con trỏ.")
            except Error as e:
                print(f"ConnectionManager: Lỗi khi tạo lại con trỏ: {e}")
        return self.cursor

# --- (Bạn có thể giữ phần kiểm thử if __name__ == '__main__': trong ConnectionManager.py để test riêng nếu muốn) ---