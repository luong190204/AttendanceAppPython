import pymysql
from pymysql import Error
from database.connection_manager import ConnectionManager

class BaseRepository:
    def __init__(self):
        self.conn_manager = ConnectionManager()
        self.conn = self.conn_manager.get_connection()
        self.cursor = self.conn_manager.get_cursor()

    def execute_query(self, query, params=None):
        try:
            if not self.conn or not self.conn.open:
                print("⚠️ Kết nối đã mất. Đang tái kết nối...")
                self.conn = self.conn_manager.get_connection()

            with self.conn.cursor() as cursor:
                cursor.execute(query, params or ())
                self.conn.commit()
                return True

        except pymysql.err.InterfaceError as e:
            print(f"❌ InterfaceError khi thực thi truy vấn: {e}")
        except pymysql.MySQLError as e:
            print(f"❌ MySQL Error: {e}")
        except Exception as e:
            print(f"❌ Lỗi khác khi thực thi truy vấn: {e}")

        self.conn.rollback()
        return False

    def fetch_all(self, query, params=None):
        try:
            conn = self.conn_manager.get_connection()
            with conn:  # đảm bảo connection tự động đóng đúng cách
                with conn.cursor() as cursor:
                    cursor.execute(query, params or ())
                    return cursor.fetchall()
        except Exception as e:
            print("⚠️ Lỗi khi fetch_all:", e)
            raise

    def fetch_one(self, query, params=None):
        self.conn = self.conn_manager.get_connection()
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchone()
        except Exception as e:
            print(f"❌ Lỗi khi fetch_one: {e}")
            return None



