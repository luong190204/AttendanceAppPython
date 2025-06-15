# database/student_repository.py
from database.base_repository import BaseRepository
from database.connection_manager import ConnectionManager
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

        # Tạo kết nối mới mỗi lần truy vấn
        conn = self.conn_manager.get_connection()
        with conn.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query, (ma_sv,))
            result = cursor.fetchone()
        conn.close()
        return result

    def update_student(self, MaSV, TenSV, NgaySinh, GioiTinh, DiaChi, Email, SDT):
        query = """
        UPDATE SinhVien
        SET TenSV = %s, NgaySinh = %s, GioiTinh = %s, DiaChi = %s, Email = %s, SDT = %s
        WHERE MaSV = %s
        """
        params = (TenSV, NgaySinh, GioiTinh, DiaChi, Email, SDT, MaSV)
        return self.execute_query(query, params)

    def delete_student(self, student_id):
        try:
            conn = self.conn_manager.get_connection()
            cursor = conn.cursor()

            # Xoá dữ liệu khuôn mặt
            cursor.execute("DELETE FROM KHUONMAT WHERE MaSV_FK = %s", (student_id,))

            # Xoá dữ liệu điểm danh
            cursor.execute("DELETE FROM DIEMDANH WHERE MaSV_FK = %s", (student_id,))

            # Xóa dữ liệu lop_mon_sinhvien
            cursor.execute("DELETE FROM lop_mon_sinhvien WHERE MaSV_FK = %s", (student_id,))

            # Sau đó xoá sinh viên
            cursor.execute("DELETE FROM SINHVIEN WHERE MaSV = %s", (student_id,))

            conn.commit()
            return True
        except Exception as e:
            print("Lỗi khi xóa sinh viên:", e)
            return False
        finally:
            cursor.close()
            conn.close()

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
        try:
            if isinstance(DuLieuMaHoa, np.ndarray):
                DuLieuMaHoa = DuLieuMaHoa.astype(np.float32).tobytes()
            elif isinstance(DuLieuMaHoa, memoryview):
                DuLieuMaHoa = DuLieuMaHoa.tobytes()

            if not isinstance(DuLieuMaHoa, (bytes, bytearray)):
                logger.error("❌ DuLieuMaHoa không phải bytes. Không thể lưu vào BLOB.")
                return False

            if len(DuLieuMaHoa) != 512:
                logger.error(f"❌ DuLieuMaHoa không đúng 512 bytes: {len(DuLieuMaHoa)}")
                return False

            query = """
                    INSERT INTO KhuonMat (MaSV_FK, DuongDanAnh, DuLieuMaHoa)
                    VALUES (%s, %s, %s)
                    """
            params = (MaSV_FK, DuongDanAnh, DuLieuMaHoa)

            success = self.execute_query(query, params)
            if success:
                print("✅ Dữ liệu đã lưu vào DB")
            else:
                print("❌ Không lưu được dữ liệu vào DB")
            return success

        except Exception as e:
            logger.exception(f"❌ Lỗi khi thêm khuôn mặt: {e}")
            return False

    def get_all_face_embeddings(self):
        """
        Lấy embedding từ DB, đảm bảo dữ liệu là bytes đúng chuẩn để convert sang numpy.
        Trả về list chứa (MaSV_FK, DuLieuMaHoa_bytes)
        """
        query = "SELECT MaSV_FK, DuLieuMaHoa FROM KhuonMat"
        try:
            # Dùng DictCursor để dễ debug
            with self.conn.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
                cursor.execute(query)
                raw_results = cursor.fetchall()

            processed_results = []
            for row in raw_results:
                ma_sv = row["MaSV_FK"]
                embedding_data = row["DuLieuMaHoa"]

                if isinstance(embedding_data, memoryview):
                    embedding_bytes = embedding_data.tobytes()
                elif isinstance(embedding_data, bytes):
                    embedding_bytes = embedding_data
                elif isinstance(embedding_data, str):
                    logger.warning(f"⚠️ MaSV_FK {ma_sv}: DuLieuMaHoa là str (có thể do lỗi lưu). Bỏ qua.")
                    continue
                else:
                    logger.warning(
                        f"⚠️ MaSV_FK {ma_sv}: DuLieuMaHoa kiểu không xác định ({type(embedding_data)}). Bỏ qua.")
                    continue

                # Kiểm tra kích thước đúng chuẩn (128 float32 = 512 bytes)
                if len(embedding_bytes) != 512:
                    logger.warning(
                        f"⚠️ MaSV_FK {ma_sv}: DuLieuMaHoa không đúng độ dài (được {len(embedding_bytes)} byte). Bỏ qua.")
                    continue

                processed_results.append((ma_sv, embedding_bytes))

            if not processed_results:
                logger.warning("⚠️ Không có dữ liệu khuôn mặt hợp lệ trong CSDL.")
            else:
                logger.info(f"✅ Tải xong {len(processed_results)} embedding từ DB.")

            return processed_results

        except Exception as e:
            logger.exception(f"❌ Lỗi khi lấy embedding từ DB: {e}")
            return []

    def get_face_embeddings_by_student_id(self, MaSV_FK):
        query = "SELECT DuLieuMaHoa FROM KhuonMat WHERE MaSV_FK = %s"
        return self.fetch_all(query, (MaSV_FK,))

# Example usage (for testing this specific repository)
