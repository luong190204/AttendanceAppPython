# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox, QProgressDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QThread, pyqtSignal, Qt  # Thêm các import này
import logging
import time  # Chỉ để mô phỏng độ trễ, có thể xóa sau

# Thiết lập logging cơ bản
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler(sys.stdout)
                    ])
logger = logging.getLogger(__name__)

# Thêm đường dẫn thư mục gốc của project vào sys.path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import các lớp cần thiết
from database.connection_manager import ConnectionManager
from ui.login_ui import LoginUI
from database.user_repository import UserRepository
import bcrypt


# --- LỚP MỚI ĐỂ XỬ LÝ KẾT NỐI CSDL TRONG LUỒNG RIÊNG ---
class ConnectionWorker(QThread):
    # Định nghĩa các tín hiệu để giao tiếp với luồng chính
    connection_successful = pyqtSignal()
    connection_failed = pyqtSignal(str)  # Truyền thông báo lỗi

    def run(self):
        logger.info("ConnectionWorker: Đang cố gắng kết nối CSDL trong luồng riêng...")
        try: # Thêm khối try này
            conn_manager = ConnectionManager()
            if conn_manager.connect():
                logger.info("ConnectionWorker: Kết nối CSDL thành công.")
                self.connection_successful.emit()
            else:
                # Nếu connect() trả về False, in ra log để biết
                error_msg = "Kết nối CSDL thất bại (kiểm tra log chi tiết từ ConnectionManager)."
                logger.error(f"ConnectionWorker: {error_msg}")
                self.connection_failed.emit(error_msg)
        except Exception as thread_e: # Bắt bất kỳ ngoại lệ nào trong luồng
            logger.critical(f"ConnectionWorker: LỖI NGHIÊM TRỌNG KHÔNG ĐƯỢC BẮT TRONG LUỒNG: {thread_e}", exc_info=True)
            self.connection_failed.emit(f"Lỗi khởi tạo CSDL không mong muốn: {thread_e}")


# --- KẾT THÚC LỚP MỚI ---

def main():
    """Hàm main để khởi chạy ứng dụng và kết nối CSDL."""
    logger.info("Bắt đầu khởi động ứng dụng...")

    app = QApplication(sys.argv)
    app.setApplicationName("Hệ Thống Điểm Danh Sinh Viên")
    font = QFont("Segoe UI", 12)
    app.setFont(font)

    # --- HIỂN THỊ HỘP THOẠI CHỜ KẾT NỐI CSDL ---
    progress_dialog = QProgressDialog("Đang kết nối CSDL...", "Hủy", 0, 0, None)
    progress_dialog.setWindowModality(Qt.WindowModal)
    progress_dialog.setCancelButton(None)  # Không cho hủy
    progress_dialog.setWindowTitle("Khởi động ứng dụng")
    progress_dialog.setMinimumDuration(0)  # Hiển thị ngay lập tức
    progress_dialog.show()
    logger.info("Đang hiển thị hộp thoại chờ kết nối CSDL.")

    # --- KHỞI TẠO VÀ CHẠY LUỒNG KẾT NỐI CSDL ---
    conn_worker = ConnectionWorker()

    # Kết nối tín hiệu từ worker đến các hàm xử lý trong luồng chính
    def on_conn_success():
        progress_dialog.close()
        logger.info("Kết nối CSDL thành công. Tiếp tục khởi tạo UI.")
        # Sau khi kết nối CSDL thành công, khởi tạo và hiển thị LoginUI

        # --- KHỞI TẠO DỮ LIỆU TEST (CHỈ CHẠY LẦN ĐẦU) ---
        user_repo = UserRepository()
        test_username = "admin"
        test_password = "admin123"

        if not user_repo.get_all_user_account_by_username(test_username):
            logger.info(f"Tài khoản '{test_username}' chưa tồn tại. Đang tạo...")
            try:
                hashed_test_password = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                if user_repo.add_user_account(test_username, hashed_test_password, 'admin'):
                    logger.info(f"Đã tạo tài khoản mặc định: {test_username}/{test_password} (vai trò: admin)")
                else:
                    logger.error(f"Không thể tạo tài khoản mặc định '{test_username}'.")
            except Exception as e:
                logger.error(f"Lỗi khi tạo tài khoản test: {e}")
        else:
            logger.info(f"Tài khoản '{test_username}' đã tồn tại.")
        # --- KẾT THÚC KHỞI TẠO DỮ LIỆU TEST ---

        # Khởi tạo và hiển thị cửa sổ đăng nhập
        logger.info("Khởi tạo và hiển thị cửa sổ đăng nhập...")
        login_window = LoginUI()

        def on_login_success(role):
            logger.info(f"Đăng nhập thành công với vai trò: {role}")
            QMessageBox.information(None, "Đăng Nhập Thành Công", f"Chào mừng, {role}!")
            login_window.close()

        login_window.login_successful.connect(on_login_success)
        login_window.show()
        logger.info("Ứng dụng đã sẵn sàng. Tài khoản test: admin/admin123")

    def on_conn_failed(error_message):
        progress_dialog.close()
        logger.error(f"Lỗi nghiêm trọng: Kết nối CSDL thất bại. {error_message}")
        QMessageBox.critical(None, "Lỗi Khởi Động",
                             f"Không thể khởi động ứng dụng do lỗi kết nối cơ sở dữ liệu.\nChi tiết: {error_message}")
        sys.exit(1)  # Thoát ứng dụng nếu không thể kết nối

    conn_worker.connection_successful.connect(on_conn_success)
    conn_worker.connection_failed.connect(on_conn_failed)

    # Bắt đầu luồng worker
    conn_worker.start()
    logger.info("Đã bắt đầu luồng worker kết nối CSDL.")

    # Bắt đầu vòng lặp sự kiện của PyQt
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()