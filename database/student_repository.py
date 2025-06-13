# database/student_repository.py
from database.base_repository import BaseRepository
import pymysql
import numpy as np
import logging
# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StudentRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    def add_student(self, MaSV, TenSV, NgaySinh, GioiTinh, DiaChi, Email, SDT):
        query = """
        INSERT INTO SinhVien (MaSV, TenSV, NgaySinh, GioiTinh, DiaChi, Email, SDT)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (MaSV, TenSV, NgaySinh, GioiTinh, DiaChi, Email, SDT)
        return self.execute_query(query, params)

    def get_all_students(self):
        query = "SELECT * FROM SinhVien"
        return self.fetch_all(query)

    def get_student_by_id(self, ma_sv):
        query = "SELECT MaSV, TenSV FROM SinhVien WHERE MaSV = %s"
        with self.conn.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query, (ma_sv,))
            return cursor.fetchone()

    def update_student(self, MaSV, TenSV, NgaySinh, GioiTinh, DiaChi, Email, SDT):
        query = """
        UPDATE SinhVien
        SET TenSV = %s, NgaySinh = %s, GioiTinh = %s, DiaChi = %s, Email = %s, SDT = %s
        WHERE MaSV = %s
        """
        params = (TenSV, NgaySinh, GioiTinh, DiaChi, Email, SDT, MaSV)
        return self.execute_query(query, params)

    def delete_student(self, MaSV):
        # Cần xử lý xóa các bản ghi liên quan (KhuonMat, Lop_Mon_SinhVien, DiemDanh) trước
        # hoặc thiết lập CASCADE DELETE trong CSDL.
        # Ở đây chỉ minh họa, bạn cần thêm logic xóa các phụ thuộc
        query = "DELETE FROM SinhVien WHERE MaSV = %s"
        return self.execute_query(query, (MaSV,))

    def get_total_students(self):
        query = "SELECT COUNT(*) FROM SinhVien"
        result = self.fetch_one(query)  # base_repository.fetch_one trả về một tuple hoặc dict
        if result:
            # Nếu dùng DictCursor, result có thể là {'COUNT(*)': value} hoặc {'count': value}
            # Nếu không dùng DictCursor, result là (value,)
            return result[0] if isinstance(result, tuple) else list(result.values())[0]
        return 0

    # KhuonMat related methods
    def add_face_embedding(self, MaSV_FK, DuongDanAnh, DuLieuMaHoa):
        """
        Thêm embedding khuôn mặt vào bảng KhuonMat.
        DuLieuMaHoa phải là kiểu bytes (512 bytes tương ứng với 128 float32).
        """
        try:
            if isinstance(DuLieuMaHoa, np.ndarray):
                DuLieuMaHoa = DuLieuMaHoa.astype(np.float32).tobytes()
            elif isinstance(DuLieuMaHoa, memoryview):
                DuLieuMaHoa = DuLieuMaHoa.tobytes()
            elif isinstance(DuLieuMaHoa, str):
                logger.warning("⚠️ DuLieuMaHoa là kiểu str, có thể gây lỗi. Đang cố gắng encode lại...")
                DuLieuMaHoa = DuLieuMaHoa.encode('latin1')

            if not isinstance(DuLieuMaHoa, (bytes, bytearray)):
                logger.error("❌ DuLieuMaHoa không phải bytes. Không thể lưu vào BLOB.")
                return False

            query = """
                    INSERT INTO KhuonMat (MaSV_FK, DuongDanAnh, DuLieuMaHoa)
                    VALUES (%s, %s, %s) \
                    """
            params = (MaSV_FK, DuongDanAnh, DuLieuMaHoa)
            return self.execute_query(query, params)

        except Exception as e:
            logger.error(f"❌ Lỗi khi thêm embedding vào DB: {e}")
            return False

    def get_all_face_embeddings(self):
        """
        Lấy embedding từ DB, đảm bảo dữ liệu là bytes đúng chuẩn để convert sang numpy.
        """
        query = "SELECT MaSV_FK, DuLieuMaHoa FROM KhuonMat"
        raw_results = self.fetch_all(query)

        processed_results = []
        for student_id, embedding_data in raw_results:
            if isinstance(embedding_data, memoryview):
                # pymysql thường trả BLOB dưới dạng memoryview
                embedding_data = embedding_data.tobytes()
            elif isinstance(embedding_data, str):
                # Nếu vì lý do gì đó là str, phải convert an toàn (đã hỏng dữ liệu rồi)
                embedding_data = embedding_data.encode('latin1')  # chỉ dùng nếu buộc phải

            processed_results.append((student_id, embedding_data))

        return processed_results

    def get_face_embeddings_by_student_id(self, MaSV_FK):
        query = "SELECT DuLieuMaHoa FROM KhuonMat WHERE MaSV_FK = %s"
        return self.fetch_all(query, (MaSV_FK,))

# Example usage (for testing this specific repository)
