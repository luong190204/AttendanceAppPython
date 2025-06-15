# database\class_subject_repository.py
from database.base_repository import BaseRepository
from pymysql import Error
import sys
import os

# Thêm đường dẫn thư mục gốc của project vào sys.path để import config
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class ClassSubjectRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    # --- Các hàm cho bảng LopHoc ---
    def add_class(self, MaLop, TenLop, Khoa):
        """Thêm một lớp học mới."""
        query = """
                INSERT INTO LopHoc (MaLop, TenLop, Khoa)
                VALUES (%s, %s, %s) 
                """
        params = (MaLop, TenLop, Khoa)
        try:
            success = self.execute_query(query, params)
            if success:
                print("Thêm thành công!")
            return True
        except Error as e:
            if e.errno == 1062:  # Duplicate entry for primary key
                print(f"Lỗi: Mã lớp {MaLop} đã tồn tại.")
            else:
                print(f"Lỗi khi thêm lớp học: {e}")
            return False

    def get_all_classes(self):
        """Lấy tất cả các lớp học."""
        query = "SELECT MaLop, TenLop, Khoa FROM LopHoc"
        return self.fetch_all(query)

    def get_class_by_id(self, MaLop):
        """Lấy thông tin một lớp học theo Mã lớp."""
        query = "SELECT MaLop, TenLop, Khoa FROM LopHoc WHERE MaLop = %s"
        return self.fetch_one(query, (MaLop,))

    def update_class(self, MaLop, TenLop, Khoa):
        """Cập nhật thông tin một lớp học."""
        query = """
                UPDATE LopHoc
                SET TenLop = %s, \
                    Khoa   = %s
                WHERE MaLop = %s \
                """
        params = (TenLop, Khoa, MaLop)
        try:
            success = self.execute_query(query, params)
            if success:
                return True
        except Error as e:
            print(f"Lỗi khi cập nhật lớp học: {e}")
            return False

    def delete_class(self, MaLop):
        """Xóa một lớp học."""
        # CẦN XỬ LÝ: Xóa các bản ghi liên quan trong Lop_Mon_SinhVien và DiemDanh TRƯỚC
        # hoặc đảm bảo thiết lập CASCADE DELETE trong CSDL.
        # Nếu không, sẽ gây lỗi khóa ngoại.
        query = "DELETE FROM LopHoc WHERE MaLop = %s"
        try:
            success = self.execute_query(query, (MaLop,))
            if success:
                return True
        except Error as e:
            print(f"Lỗi khi xóa lớp học: {e}. Vui lòng xóa các dữ liệu liên quan trước.")
            return False

    def get_total_classes(self):
        query = "SELECT COUNT(*) FROM LopHoc"  # Tên bảng lớp học của bạn
        result = self.fetch_one(query)
        if result:
            return result[0] if isinstance(result, tuple) else list(result.values())[0]
        return 0

    # --- Các hàm cho bảng MonHoc ---
    def add_subject(self, MaMon, TenMon, SoTinChi):
        """Thêm một môn học mới."""
        query = """
                INSERT INTO MonHoc (MaMon, TenMon, SoTinChi)
                VALUES (%s, %s, %s) \
                """
        params = (MaMon, TenMon, SoTinChi)
        try:
            success = self.execute_query(query, params)
            if success:
                print(f"Đã thêm môn học: {MaMon}")
            return True
        except Error as e:
            if e.errno == 1062:
                print(f"Lỗi: Mã môn {MaMon} đã tồn tại.")
            else:
                print(f"Lỗi khi thêm môn học: {e}")
            return False

    def get_all_subjects(self):
        """Lấy tất cả các môn học."""
        query = "SELECT MaMon, TenMon, SoTinChi FROM MonHoc"
        return self.fetch_all(query)

    def get_subject_by_id(self, MaMon):
        """Lấy thông tin một môn học theo Mã môn."""
        query = "SELECT MaMon, TenMon, SoTinChi FROM MonHoc WHERE MaMon = %s"
        return self.fetch_one(query, (MaMon,))

    def update_subject(self, MaMon, TenMon, SoTinChi):
        """Cập nhật thông tin một môn học."""
        query = """
                UPDATE MonHoc
                SET TenMon   = %s, \
                    SoTinChi = %s
                WHERE MaMon = %s \
                """
        params = (TenMon, SoTinChi, MaMon)
        try:
            success = self.execute_query(query, params)
            if success:
                return True
        except Error as e:
            print(f"Lỗi khi cập nhật môn học: {e}")
            return False

    def delete_subject(self, MaMon):
        """Xóa một môn học."""
        # CẦN XỬ LÝ: Xóa các bản ghi liên quan trong Lop_Mon_SinhVien và DiemDanh TRƯỚC
        # hoặc đảm bảo thiết lập CASCADE DELETE trong CSDL.
        query = "DELETE FROM MonHoc WHERE MaMon = %s"
        try:
            success = self.execute_query(query, (MaMon,))
            if success:
                return True
        except Error as e:
            print(f"Lỗi khi xóa môn học: {e}. Vui lòng xóa các dữ liệu liên quan trước.")
            return False

    # --- Các hàm cho bảng Lop_Mon_SinhVien (bảng trung gian) ---
    def add_student_to_class_subject(self, MaLop_FK, MaMon_FK, MaSV_FK):
        """Gán một sinh viên vào một lớp học-môn học cụ thể."""
        query = """
                INSERT INTO Lop_Mon_SinhVien (MaLop_FK, MaMon_FK, MaSV_FK)
                VALUES (%s, %s, %s) \
                """
        params = (MaLop_FK, MaMon_FK, MaSV_FK)
        try:
            success = self.execute_query(query, params)
            if success:
                print("Gán thành công!")
                return True
            return False
        except Error as e:
            if e.errno == 1062:  # Duplicate entry for primary key
                print(f"Lỗi: SV {MaSV_FK} đã được gán vào lớp {MaLop_FK} - môn {MaMon_FK} rồi.")
            elif e.errno == 1452:  # Foreign key constraint fails
                print(f"Lỗi: Không tìm thấy Mã SV, Mã Lớp hoặc Mã Môn hợp lệ. {e}")
            else:
                print(f"Lỗi khi gán sinh viên vào lớp/môn: {e}")
            return False

    def remove_student_from_class_subject(self, MaLop_FK, MaMon_FK, MaSV_FK):
        """Xóa một sinh viên khỏi một lớp học-môn học cụ thể."""
        query = """
                DELETE \
                FROM Lop_Mon_SinhVien
                WHERE MaLop_FK = %s \
                  AND MaMon_FK = %s \
                  AND MaSV_FK = %s \
                """
        params = (MaLop_FK, MaMon_FK, MaSV_FK)
        try:
            success = self.execute_query(query, params)
            if success:
                return True
        except Error as e:
            print(f"Lỗi khi xóa sinh viên khỏi lớp/môn: {e}")
            return False

    def get_students_in_class_subject(self, MaLop_FK, MaMon_FK):
        """Lấy danh sách sinh viên trong một lớp học-môn học cụ thể."""
        query = """
                SELECT sv.MaSV, sv.TenSV, sv.Email
                FROM Lop_Mon_SinhVien lmsv
                JOIN SinhVien sv ON lmsv.MaSV_FK = sv.MaSV
                WHERE lmsv.MaLop_FK = %s \
                AND lmsv.MaMon_FK = %s \
                """
        params = (MaLop_FK, MaMon_FK)
        return self.fetch_all(query, params)

    def get_subjects_for_class(self, MaLop_FK):
        """Lấy danh sách các môn học được gán cho một lớp cụ thể."""
        query = """
                SELECT DISTINCT mh.MaMon, mh.TenMon, mh.SoTinChi
                FROM Lop_Mon_SinhVien lmsv
                         JOIN MonHoc mh ON lmsv.MaMon_FK = mh.MaMon
                WHERE lmsv.MaLop_FK = %s \
                """
        return self.fetch_all(query, (MaLop_FK,))

    def is_student_assigned_to_class_subject(self, MaSV_FK, MaLop_FK, MaMon_FK):
        """Kiểm tra xem một sinh viên có được gán vào lớp-môn học này không."""
        query = """
                SELECT COUNT(*) \
                FROM Lop_Mon_SinhVien
                WHERE MaSV_FK = %s \
                  AND MaLop_FK = %s \
                  AND MaMon_FK = %s \
                """
        params = (MaSV_FK, MaLop_FK, MaMon_FK)
        result = self.fetch_one(query, params)
        return result and result[0] > 0


# --- Phần kiểm thử (có thể xóa sau khi tích hợp vào UI) ---
# if __name__ == '__main__':
#     from database.connection_manager import ConnectionManager
#     from database.student_repository import StudentRepository  # Để thêm SV test
#
#     conn_manager = ConnectionManager()
#     if not conn_manager.connect():
#         print("Không thể kết nối CSDL, không thể chạy test ClassSubjectRepository.")
#         sys.exit(1)
#
#     repo = ClassSubjectRepository()
#     student_repo = StudentRepository()  # Dùng để thêm SV test nếu cần

    # print("\n--- TEST: Thêm Lớp Học ---")
    # if repo.add_class('L01', 'Lop Cong Nghe Thong Tin K20', 'CNTT'):
    #     print("Thêm L01 thành công.")
    # if repo.add_class('L02', 'Lop Dien Tu K20', 'DienTu'):
    #     print("Thêm L02 thành công.")
    #
    # print("\n--- TEST: Lấy tất cả Lớp Học ---")
    # classes = repo.get_all_classes()
    # if classes:
    #     for cls in classes:
    #         print(cls)
    #
    # print("\n--- TEST: Thêm Môn Học ---")
    # if repo.add_subject('M01', 'Lap Trinh Python', 3):
    #     print("Thêm M01 thành công.")
    # if repo.add_subject('M02', 'Co So Du Lieu', 2):
    #     print("Thêm M02 thành công.")
    #
    # print("\n--- TEST: Lấy tất cả Môn Học ---")
    # subjects = repo.get_all_subjects()
    # if subjects:
    #     for sub in subjects:
    #         print(sub)

    # print("\n--- TEST: Gán Sinh Viên vào Lớp-Môn ---")
    # # Đảm bảo có SV001 và SV002 trong bảng SinhVien trước khi gán
    # if not student_repo.get_student_by_id('SV001'):
    #     student_repo.add_student('SV001', 'Nguyen Van A', '2000-01-15', 'Nam', 'Ha Noi', 'vana@example.com',
    #                              '0912345678')
    # if not student_repo.get_student_by_id('SV002'):
    #     student_repo.add_student('SV002', 'Tran Thi B', '2001-05-20', 'Nu', 'TP Ho Chi Minh', 'thib@example.com',
    #                              '0987654321')
    #
    # if repo.add_student_to_class_subject('LH001', 'MH001', 'SV001'):
    #     print("Gán SV001 vào L01-M01 thành công.")
    # if repo.add_student_to_class_subject('LH001', 'MH001', 'SV002'):
    #     print("Gán SV002 vào L01-M01 thành công.")


    # print("\n--- TEST: Lấy Sinh Viên trong L01-M01 ---")
    # students_in_class_subject = repo.get_students_in_class_subject('L01', 'M01')
    # if students_in_class_subject:
    #     for s in students_in_class_subject:
    #         print(s)
    #
    # print("\n--- TEST: Lấy các Môn học cho Lớp L01 ---")
    # subjects_for_l01 = repo.get_subjects_for_class('L01')
    # if subjects_for_l01:
    #     for s in subjects_for_l01:
    #         print(s)
    #
    # print("\n--- TEST: Kiểm tra sinh viên có được gán vào lớp-môn không ---")
    # if repo.is_student_assigned_to_class_subject('SV001', 'L01', 'M01'):
    #     print("SV001 có trong L01-M01.")
    # else:
    #     print("SV001 KHÔNG có trong L01-M01.")
    #
    # if repo.is_student_assigned_to_class_subject('SV003', 'L01', 'M01'):
    #     print("SV003 có trong L01-M01.")
    # else:
    #     print("SV003 KHÔNG có trong L01-M01.")

    # Thử xóa và kiểm tra lại
    # print("\n--- TEST: Xóa Sinh Viên khỏi Lớp-Môn ---")
    # if repo.remove_student_from_class_subject('L01', 'M01', 'SV002'):
    #     print("Xóa SV002 khỏi L01-M01 thành công.")
    # else:
    #     print("Xóa SV002 khỏi L01-M01 thất bại.")

    # conn_manager.disconnect()