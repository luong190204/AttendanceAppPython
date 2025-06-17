# database/attendance_repository.py
from database.base_repository import BaseRepository
from pymysql import Error  # Import Error for specific error handling if needed
from datetime import datetime, timedelta


class AttendanceRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    def add_attendance_record(self, MaBuoiHoc_FK, MaSV_FK, ThoiGian, TrangThai):
        """
        Thêm một bản ghi điểm danh mới vào CSDL.
        """
        query = """
                INSERT INTO DiemDanh (MaBuoiHoc_FK, MaSV_FK, ThoiGian, TrangThai)
                VALUES (%s, %s, %s, %s)
                """
        params = (MaBuoiHoc_FK, MaSV_FK, ThoiGian, TrangThai)
        return self.execute_query(query, params)

    def get_attendance_records(self, MaBuoiHoc=None, MaSV=None, Ngay=None, TrangThai=None):
        """
        Lấy các bản ghi điểm danh dựa trên các tiêu chí lọc.
        """
        base_query = """
                     SELECT dd.ID_DiemDanh,
                            sv.MaSV,
                            sv.TenSV,
                            bh.MaBuoiHoc,
                            bh.NgayHoc,
                            bh.MaMon,
                            bh.MaLop_FK,
                            dd.ThoiGian,
                            dd.TrangThai
                     FROM DiemDanh dd
                              JOIN SinhVien sv ON dd.MaSV_FK = sv.MaSV
                              JOIN BuoiHoc bh ON dd.MaBuoiHoc_FK = bh.MaBuoiHoc
                     WHERE 1 = 1 \
                     """
        params = []

        if MaBuoiHoc:
            base_query += " AND dd.MaBuoiHoc_FK = %s"
            params.append(MaBuoiHoc)
        if MaSV:
            base_query += " AND dd.MaSV_FK = %s"
            params.append(MaSV)
        if Ngay:
            base_query += " AND DATE(dd.ThoiGian) = %s"
            ngay_str = Ngay.strftime('%Y-%m-%d') if isinstance(Ngay, datetime.date) else Ngay
            params.append(ngay_str)
        if TrangThai:
            base_query += " AND dd.TrangThai = %s"
            params.append(TrangThai)

        base_query += " ORDER BY dd.ThoiGian DESC"
        return self.fetch_all(base_query, tuple(params))

    def get_daily_attendance_summary(self, Ngay=None, MaBuoiHoc=None):
        """
        Tóm tắt điểm danh (số lượng theo trạng thái) cho 1 ngày hoặc buổi học cụ thể.
        """
        if not Ngay and not MaBuoiHoc:
            print("Cần ngày hoặc mã buổi học để thống kê.")
            return None

        query = """
                SELECT dd.TrangThai,
                       COUNT(DISTINCT dd.MaSV_FK) as SoLuong
                FROM DiemDanh dd
                         JOIN BuoiHoc bh ON dd.MaBuoiHoc_FK = bh.MaBuoiHoc
                WHERE 1 = 1 \
                """
        params = []

        if Ngay:
            query += " AND DATE(dd.ThoiGian) = %s"
            ngay_str = Ngay.strftime('%Y-%m-%d') if isinstance(Ngay, datetime.date) else Ngay
            params.append(ngay_str)

        if MaBuoiHoc:
            query += " AND dd.MaBuoiHoc_FK = %s"
            params.append(MaBuoiHoc)

        query += " GROUP BY dd.TrangThai"

        results = self.fetch_all(query, tuple(params))
        return {status: count for status, count in results} if results else {}

    def check_student_attended_today(self, MaSV_FK, MaBuoiHoc_FK):
        """
        Kiểm tra xem sinh viên đã điểm danh 'Có mặt' trong buổi học này chưa.
        """
        query = """
                SELECT COUNT(*)
                FROM DiemDanh
                WHERE MaSV_FK = %s
                  AND MaBuoiHoc_FK = %s
                  AND TrangThai = 'Có mặt' \
                """
        params = (MaSV_FK, MaBuoiHoc_FK)
        result = self.fetch_one(query, params)
        return bool(result and result[0] > 0)

    def count_attendance_today(self):
        """
        Đếm số sinh viên đã điểm danh trong ngày hôm nay.

        Returns:
            int: Số lượng bản ghi điểm danh hôm nay.
        """
        """Đếm số lượt điểm danh trong ngày hôm nay"""
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)

        query = """
                SELECT COUNT(*) AS total
                FROM DiemDanh
                WHERE ThoiGian >= %s \
                  AND ThoiGian < %s \
                """
        params = (today.strftime("%Y-%m-%d"), tomorrow.strftime("%Y-%m-%d"))

        result = self.fetch_one(query, params)
        return result.get('total', 0) if result else 0
