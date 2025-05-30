# database/attendance_repository.py
from database.base_repository import BaseRepository
from pymysql import Error  # Import Error for specific error handling if needed
import datetime


class AttendanceRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    def add_attendance_record(self, MaLop_FK, MaMon_FK, MaSV_FK, ThoiGian, TrangThai):
        """
        Thêm một bản ghi điểm danh mới vào CSDL.

        Args:
            MaLop_FK (str): Mã lớp học.
            MaMon_FK (str): Mã môn học.
            MaSV_FK (str): Mã sinh viên.
            ThoiGian (datetime.datetime): Thời gian điểm danh.
            TrangThai (str): Trạng thái điểm danh ('Có mặt', 'Vắng mặt', 'Có phép', v.v.).

        Returns:
            cursor: Đối tượng cursor nếu thành công, None nếu có lỗi.
        """
        query = """
                INSERT INTO DiemDanh (MaLop_FK, MaMon_FK, MaSV_FK, ThoiGian, TrangThai)
                VALUES (%s, %s, %s, %s, %s) \
                """
        params = (MaLop_FK, MaMon_FK, MaSV_FK, ThoiGian, TrangThai)
        return self.execute_query(query, params)

    def get_attendance_records(self, MaLop=None, MaMon=None, MaSV=None, Ngay=None, TrangThai=None):
        """
        Lấy các bản ghi điểm danh dựa trên các tiêu chí lọc.

        Args:
            MaLop (str, optional): Lọc theo mã lớp học.
            MaMon (str, optional): Lọc theo mã môn học.
            MaSV (str, optional): Lọc theo mã sinh viên.
            Ngay (datetime.date or str, optional): Lọc theo ngày điểm danh (ví dụ: 'YYYY-MM-DD').
            TrangThai (str, optional): Lọc theo trạng thái điểm danh.

        Returns:
            list: Danh sách các bản ghi điểm danh, mỗi bản ghi là một tuple.
                  Hoặc None nếu có lỗi.
        """
        base_query = """
                     SELECT dd.ID_DiemDanh, \
                            sv.MaSV, \
                            sv.TenSV, \
                            mh.MaMon, \
                            mh.TenMon, \
                            lh.MaLop, \
                            lh.TenLop, \
                            dd.ThoiGian, \
                            dd.TrangThai
                     FROM DiemDanh dd \
                              JOIN \
                          SinhVien sv ON dd.MaSV_FK = sv.MaSV \
                              JOIN \
                          MonHoc mh ON dd.MaMon_FK = mh.MaMon \
                              JOIN \
                          LopHoc lh ON dd.MaLop_FK = lh.MaLop
                     WHERE 1 = 1 \
                     """
        params = []

        if MaLop:
            base_query += " AND dd.MaLop_FK = %s"
            params.append(MaLop)
        if MaMon:
            base_query += " AND dd.MaMon_FK = %s"
            params.append(MaMon)
        if MaSV:
            base_query += " AND dd.MaSV_FK = %s"
            params.append(MaSV)
        if Ngay:
            base_query += " AND DATE(dd.ThoiGian) = %s"
            if isinstance(Ngay, datetime.date):
                params.append(Ngay.strftime('%Y-%m-%d'))
            else:
                params.append(Ngay)
        if TrangThai:
            base_query += " AND dd.TrangThai = %s"
            params.append(TrangThai)

        base_query += " ORDER BY dd.ThoiGian DESC"
        return self.fetch_all(base_query, tuple(params))

    def get_daily_attendance_summary(self, Ngay=None, MaLop=None, MaMon=None):
        """
        Lấy tóm tắt điểm danh (số lượng có mặt/vắng mặt) cho một ngày, lớp, môn cụ thể.

        Args:
            Ngay (datetime.date or str): Ngày cần lấy tóm tắt.
            MaLop (str, optional): Lọc theo mã lớp học.
            MaMon (str, optional): Lọc theo mã môn học.

        Returns:
            dict: Một dictionary chứa tóm tắt (ví dụ: {'Có mặt': 25, 'Vắng mặt': 5})
                  Hoặc None nếu có lỗi.
        """
        if not Ngay:
            print("Cần cung cấp ngày để lấy tóm tắt điểm danh.")
            return None

        query = """
                SELECT dd.TrangThai, \
                       COUNT(DISTINCT dd.MaSV_FK) as SoLuong
                FROM DiemDanh dd
                WHERE DATE (dd.ThoiGian) = %s \
                """
        params = []
        if isinstance(Ngay, datetime.date):
            params.append(Ngay.strftime('%Y-%m-%d'))
        else:
            params.append(Ngay)

        if MaLop:
            query += " AND dd.MaLop_FK = %s"
            params.append(MaLop)
        if MaMon:
            query += " AND dd.MaMon_FK = %s"
            params.append(MaMon)

        query += " GROUP BY dd.TrangThai"

        results = self.fetch_all(query, tuple(params))
        summary = {}
        if results:
            for status, count in results:
                summary[status] = count
        return summary

    def check_student_attended_today(self, MaSV_FK, MaLop_FK, MaMon_FK, Ngay=None):
        """
        Kiểm tra xem một sinh viên đã điểm danh 'Có mặt' trong một lớp/môn cụ thể vào ngày nhất định hay chưa.
        Đây là một chức năng quan trọng để tránh điểm danh trùng lặp.

        Args:
            MaSV_FK (str): Mã sinh viên.
            MaLop_FK (str): Mã lớp học.
            MaMon_FK (str): Mã môn học.
            Ngay (datetime.date or str, optional): Ngày cần kiểm tra. Mặc định là ngày hiện tại.

        Returns:
            bool: True nếu sinh viên đã điểm danh 'Có mặt', False nếu chưa hoặc có lỗi.
        """
        if Ngay is None:
            Ngay = datetime.date.today()

        query = """
                SELECT COUNT(*)
                FROM DiemDanh
                WHERE MaSV_FK = %s
                  AND MaLop_FK = %s
                  AND MaMon_FK = %s
                  AND DATE (ThoiGian) = %s
                  AND TrangThai = 'Có mặt' \
                """

        if isinstance(Ngay, datetime.date):
            ngay_str = Ngay.strftime('%Y-%m-%d')
        else:
            ngay_str = Ngay  # Giả định Ngay đã là chuỗi định dạng YYYY-MM-DD

        params = (MaSV_FK, MaLop_FK, MaMon_FK, ngay_str)

        result = self.fetch_one(query, params)
        if result and result[0] > 0:
            return True
        return False
