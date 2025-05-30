# database/student_repository.py
from database.base_repository import BaseRepository
from pymysql import Error # Import Error để xử lý lỗi cụ thể nếu cần

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

    def get_student_by_id(self, MaSV):
        query = "SELECT * FROM SinhVien WHERE MaSV = %s"
        return self.fetch_one(query, (MaSV,))

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
        query = """
        INSERT INTO KhuonMat (MaSV_FK, DuongDanAnh, DuLieuMaHoa)
        VALUES (%s, %s, %s)
        """
        params = (MaSV_FK, DuongDanAnh, DuLieuMaHoa)
        return self.execute_query(query, params)

    def get_all_face_embeddings(self):
        # Trả về MaSV và DuLieuMaHoa để nhận diện
        query = "SELECT MaSV_FK, DuLieuMaHoa FROM KhuonMat"
        return self.fetch_all(query)

    def get_face_embeddings_by_student_id(self, MaSV_FK):
        query = "SELECT DuLieuMaHoa FROM KhuonMat WHERE MaSV_FK = %s"
        return self.fetch_all(query, (MaSV_FK,))

# Example usage (for testing this specific repository)
