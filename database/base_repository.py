import pymysql
from pymysql import Error
from database.connection_manager import ConnectionManager

class BaseRepository:
    def __init__(self):
        self.conn_manager = ConnectionManager()
        self.conn = self.conn_manager.get_connection()
        self.cursor = self.conn_manager.get_cursor()

    def execute_query(self, query, params=None):
        if not self.conn or not self.cursor:
            print("Không thể thực hiện truy vấn: Không có kết nối DB.")
            return None
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.cursor
        except Error as e:
            print(f"Lỗi khi thực thi truy vấn: {e}")
            self.conn.rollback()
            return None

    def fetch_all(self, query, params=None):
        with self.conn.cursor(cursor=pymysql.cursors.Cursor) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def fetch_one(self, query, params=None):
        cursor = self.execute_query(query, params)
        if cursor:
            return cursor.fetchone()

