#database/user_repository
from database.base_repository import BaseRepository
from pymysql import Error # Import Error để xử lý lỗi cụ thể nếu cần
import bcrypt

class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    # --- GiangVien ----
    def add_lecturer(self, MaGV, TenGV, Email, SDT):
        query = """
                INSERT INTO GiangVien (MaGV, TenGV, Email, SDT)
                VALUES (%s, %s, %s, %s)
                """
        params = (MaGV, TenGV, Email, SDT)
        return self.execute_query(query, params)

    def get_all_lecturer(self):
        query = "SELECT * FROM GiangVien"
        return self.fetch_all(query)

    def get_lecturer_by_id(self, MaGV):
        query = "SELECT * FROM GiangVien WHERE MaGV = %s"
        return self.fetch_one(query, (MaGV,))

    def update_lecturer(self, MaGV, TenGV, Email, SDT):
        query = """
        UPDATE GiangVien
        SET TenGV = %s, Email = %s, SDT = %s
        WHERE MaGV = %s
        """
        params = (TenGV, Email, SDT, MaGV)
        return self.execute_query(query, params)

    def delete_lecturer(self, MaGV):
        # Cần xử lý xóa các bản ghi liên quan (KhuonMat, Lop_Mon_SinhVien, DiemDanh) trước
        query = "DELETE FROM GiangVien WHERE MaGV = %s"
        return self.execute_query(query, (MaGV,))

    # --- TaiKhoan ---
    def add_user_account(self, TenDangNhap, MatKhau, LoaiTaiKhoan, MaGV_FK):
        # Hash mật khẩu trước khi lưu
        hashed_password = bcrypt.hashpw(MatKhau.encode("utf-8"), bcrypt.gensalt())

        query = """
        INSERT INTO TaiKhoan (TenDangNhap, MatKhau, LoaiTaiKhoan, MaGV_FK)
        VALUES (%s, %s, %s, %s)
        """
        params = (TenDangNhap, hashed_password, LoaiTaiKhoan, MaGV_FK)
        return self.execute_query(query, params)

    def get_all_user_account(self):
        query = "SELECT * FROM TaiKhoan"
        return self.fetch_all(query)

    def get_all_user_account_by_username(self, TenDangNhap):
        query = "SELECT * FROM TaiKhoan WHERE TenDangNhap = %s"
        return self.fetch_one(query, (TenDangNhap,))

    def update_user_account(self, TenDangNhap, MatKhau, LoaiTaiKhoan, MaGV_FK):
        # hash mật khẩu
        hash_password = bcrypt.hashpw(MatKhau.encode("utf-8"), bcrypt.gensalt())

        query = """
        UPDATE TaiKhoan 
        SET MatKhau = %s, LoaiTaiKhoan = %s, MaGV_FK = %s
        WHERE TenDangNhap = %s
        """
        params = (hash_password, LoaiTaiKhoan, MaGV_FK, TenDangNhap)
        return self.execute_query(query, params)

    def delete_user_account(self, TenDangNhap):
        query = "DELETE FROM TaiKhoan WHERE  TenDangNhap = %s"
        return self.execute_query(query, (TenDangNhap,))

    def authenticate_user(self, TenDangNhap, MatKhauNhapVao):
        query = "SELECT MatKhau, LoaiTaiKhoan FROM TaiKhoan WHERE TenDangNhap = %s"  # Lấy cả VaiTro
        result = self.fetch_one(query, (TenDangNhap,))

        if result:
            hashed_password = result['MatKhau'].encode("utf-8")  # Chuyển từ string sang bytes
            user_role = result['LoaiTaiKhoan']  # Lấy vai trò

            # Đảm bảo MatKhauNhapVao là string và hashed_password là bytes để bcrypt hoạt động
            if isinstance(MatKhauNhapVao, str):
                MatKhauNhapVao_bytes = MatKhauNhapVao.encode("utf-8")
            else:
                MatKhauNhapVao_bytes = MatKhauNhapVao  # Giả định đã là bytes

            if bcrypt.checkpw(MatKhauNhapVao_bytes, hashed_password):
                return user_role  # Trả về vai trò nếu mật khẩu đúng
        return False  # Trả về False nếu tên đăng nhập không tồn tại hoặc mật khẩu sai


if __name__ == '__main__':
    db = UserRepository()
    print("\n ------ Thêm Tài Khoản ---------")

    all_account = db.get_all_user_account()
    for account in all_account:
        print(account)
# Đừng quên ngắt kết nối khi hoàn tất
    db.conn_manager.disconnect()