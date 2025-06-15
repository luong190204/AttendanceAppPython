# database/session_repository.py
from database.base_repository import BaseRepository
from database.connection_manager import ConnectionManager
import logging

logger = logging.getLogger(__name__)

class SessionRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    def add_session(self, session_id, start_time, end_time, date, teacher_id, subject_id, room=None):
        try:
            conn = ConnectionManager().get_connection()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO BuoiHoc (MaBuoiHoc, GioBatDau, GioKetThuc, NgayHoc, MaGV_FK, MaMonHoc_FK, PhongHoc)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (session_id, start_time, end_time, date, teacher_id, subject_id, room))
            conn.commit()
            logger.info(f"Đã thêm buổi học: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi thêm buổi học {session_id}: {e}", exc_info=True)
            return False

    def get_all_sessions(self):
        # Hàm này có thể join với bảng GiangVien và MonHoc để lấy tên thay vì chỉ ID
        query = """
        SELECT
            BH.MaBuoiHoc, BH.GioBatDau, BH.GioKetThuc, BH.NgayHoc,
            GV.TenGV, MH.TenMon, BH.PhongHoc, BH.TrangThaiBuoiHoc
        FROM BuoiHoc BH
        JOIN GiangVien GV ON BH.MaGV_FK = GV.MaGV
        JOIN MonHoc MH ON BH.MaMonHoc_FK = MH.MaMon
        ORDER BY BH.NgayHoc DESC, BH.GioBatDau ASC
        """
        return self.fetch_all(query)

    def get_session_by_id(self, session_id):
        query = "SELECT * FROM BuoiHoc WHERE MaBuoiHoc = %s"
        return self.fetch_one(query, (session_id,))

    def update_session(self, session_id, start_time, end_time, date, teacher_id, subject_id, room):
        try:
            conn = ConnectionManager().get_connection()
            with conn.cursor() as cursor:
                query = """
                UPDATE BuoiHoc SET
                    GioBatDau = %s, GioKetThuc = %s, NgayHoc = %s,
                    MaGV_FK = %s, MaMonHoc_FK = %s, PhongHoc = %s
                WHERE MaBuoiHoc = %s
                """
                cursor.execute(query, (start_time, end_time, date, teacher_id, subject_id, room, session_id))
            conn.commit()
            logger.info(f"Đã cập nhật buổi học: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật buổi học {session_id}: {e}", exc_info=True)
            return False

    def delete_session(self, session_id):
        try:
            conn = ConnectionManager().get_connection()
            with conn.cursor() as cursor:
                query = "DELETE FROM BuoiHoc WHERE MaBuoiHoc = %s"
                cursor.execute(query, (session_id,))
            conn.commit()
            logger.info(f"Đã xóa buổi học: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi xóa buổi học {session_id}: {e}", exc_info=True)
            return False

    # Thêm các hàm hỗ trợ khác nếu cần, ví dụ: get_sessions_by_teacher, get_sessions_by_date