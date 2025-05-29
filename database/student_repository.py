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
if __name__ == '__main__':
    # Lưu ý: Cần đảm bảo MySQL server đang chạy và DB/bảng đã được tạo
    # và config.py đã đúng
    repo = StudentRepository()

    print("\n--- Danh sách sinh viên ---")
    all_student = repo.get_all_students()
    if all_student:
        for students in all_student:
            print(students)


    # Đừng quên ngắt kết nối khi hoàn tất
    repo.conn_manager.disconnect()