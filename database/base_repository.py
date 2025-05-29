# database/base_repository.py
from pymysql import Error
from database.connection_manager import ConnectionManager # Import from new file

class BaseRepository:
    def __init__(self):
        self.conn_manager = ConnectionManager()

    def execute_query(self, query, params=None):
        """Thực thi một câu truy vấn SQL và trả về đối tượng cursor."""
        connection = self.conn_manager.get_connection()
        cursor = self.conn_manager.get_cursor()
        if not connection or not cursor:
            print("Không thể thực hiện truy vấn: Không có kết nối DB.")
            return None
        try:
            cursor.execute(query, params)
            connection.commit()
            return cursor
        except Error as e:
            print(f"Lỗi khi thực thi truy vấn: {e}")
            connection.rollback()
            return None

    def fetch_all(self, query, params=None):
        """Thực thi truy vấn SELECT và trả về tất cả các hàng."""
        cursor = self.execute_query(query, params)
        if cursor:
            return cursor.fetchall()
        return None

    def fetch_one(self, query, params=None):
        """Thực thi truy vấn SELECT và trả về một hàng duy nhất."""
        cursor = self.execute_query(query, params)
        if cursor:
            return cursor.fetchone()
        return None