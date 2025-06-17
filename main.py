# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox, QProgressDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import logging
import time

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
    connection_successful = pyqtSignal()
    connection_failed = pyqtSignal(str)

    def run(self):
        logger.info("ConnectionWorker: Đang cố gắng kết nối CSDL trong luồng riêng...")
        try:
            conn_manager = ConnectionManager()
            if conn_manager.connect():
                logger.info("ConnectionWorker: Kết nối CSDL thành công.")
                self.connection_successful.emit()
            else:
                error_msg = "Kết nối CSDL thất bại (kiểm tra log chi tiết từ ConnectionManager)."
                logger.error(f"ConnectionWorker: {error_msg}")
                self.connection_failed.emit(error_msg)
        except Exception as thread_e:
            logger.critical(f"ConnectionWorker: LỖI NGHIÊM TRỌNG KHÔNG ĐƯỢC BẮT TRONG LUỒNG: {thread_e}", exc_info=True)
            self.connection_failed.emit(f"Lỗi khởi tạo CSDL không mong muốn: {thread_e}")

# Biến toàn cục để giữ tham chiếu đến cửa sổ đăng nhập và cửa sổ chính
# Điều này giúp chúng ta có thể đóng/mở chúng từ các hàm callback
login_window = None
main_window = None
app_instance = None # Giữ tham chiếu đến QApplication

def show_login_window():
    global login_window, app_instance
    if login_window is None:
        login_window = LoginUI()
        login_window.login_successful.connect(on_login_success)
    login_window.show()
    logger.info("Hiển thị cửa sổ đăng nhập.")


def on_login_success(role):
    global login_window, main_window
    logger.info(f"Đăng nhập thành công với vai trò: {role}")
    if login_window:
        login_window.close() # Đóng cửa sổ đăng nhập

    from ui.main_window import MainWindow # Import MainWindow ở đây
    main_window = MainWindow(role) # Tạo thể hiện của MainWindow
    main_window.logout_requested.connect(on_logout_requested) # Kết nối tín hiệu đăng xuất
    main_window.show() # Hiển thị cửa sổ chính


def on_logout_requested():
    global main_window, login_window
    logger.info("Yêu cầu đăng xuất đã được phát hiện.")
    if main_window:
        main_window.close() # Đóng cửa sổ chính
        main_window = None # Xóa tham chiếu để GC có thể dọn dẹp

    show_login_window() # Hiển thị lại cửa sổ đăng nhập

def on_conn_failed(error_message):
    global app_instance
    if progress_dialog: # Đảm bảo progress_dialog tồn tại
        progress_dialog.close()
    logger.error(f"Lỗi nghiêm trọng: Kết nối CSDL thất bại. {error_message}")
    QMessageBox.critical(None, "Lỗi Khởi Động",
                         f"Không thể khởi động ứng dụng do lỗi kết nối cơ sở dữ liệu.\nChi tiết: {error_message}")
    if app_instance:
        app_instance.quit() # Đảm bảo ứng dụng thoát nếu không kết nối được

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
def main():
    global app_instance, progress_dialog
    logger.info("Bắt đầu khởi động ứng dụng...")

    app_instance = QApplication(sys.argv)
    app_instance.setApplicationName("Hệ Thống Điểm Danh Sinh Viên")
    font = QFont("Segoe UI", 12)
    app_instance.setFont(font)

    progress_dialog = QProgressDialog("Đang kết nối CSDL...", "Hủy", 0, 0, None)
    progress_dialog.setWindowModality(Qt.WindowModal)
    progress_dialog.setCancelButton(None)
    progress_dialog.setWindowTitle("Khởi động ứng dụng")
    progress_dialog.setMinimumDuration(0)
    progress_dialog.show()
    logger.info("Đang hiển thị hộp thoại chờ kết nối CSDL.")

    # --- KHỞI TẠO VÀ CHẠY LUỒNG KẾT NỐI CSDL ---
    conn_worker = ConnectionWorker()
    conn_worker.connection_successful.connect(lambda: on_initial_conn_success(progress_dialog)) # Pass progress_dialog
    conn_worker.connection_failed.connect(on_conn_failed)
    conn_worker.start()
    logger.info("Đã bắt đầu luồng worker kết nối CSDL.")

    sys.exit(app_instance.exec_())


def on_initial_conn_success(dialog):
    # Hàm này chỉ chạy sau khi kết nối CSDL ban đầu thành công
    dialog.close()
    logger.info("Kết nối CSDL thành công. Tiếp tục khởi tạo UI.")

    # --- KHỞI TẠO DỮ LIỆU TEST (CHỈ CHẠY LẦN ĐẦU) ---
    user_repo = UserRepository()
    test_username = "admin"
    test_password = "admin123"
    # Giả sử MaGV_FK có thể là NULL hoặc có một giá trị mặc định cho admin
    # HOẶC bạn đã sửa DB để MaGV_FK không cần cho Admin nếu vai trò là 'admin'
    test_magv_fk = None # HOẶC một giá trị mặc định như 'GV000' nếu bắt buộc

    if not user_repo.get_all_user_account_by_username(test_username):
        logger.info(f"Tài khoản '{test_username}' chưa tồn tại. Đang tạo...")
        try:
            hashed_test_password = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            # Cung cấp thêm đối số MaGV_FK (nếu add_user yêu cầu)
            if user_repo.add_user_account(test_username, hashed_test_password, 'admin', test_magv_fk): # Thêm đối số này
                logger.info(f"Đã tạo tài khoản mặc định: {test_username}/{test_password} (vai trò: admin)")
            else:
                logger.error(f"Không thể tạo tài khoản mặc định '{test_username}'.")
        except Exception as e:
            logger.error(f"Lỗi khi tạo tài khoản test: {e}")
    else:
        logger.info(f"Tài khoản '{test_username}' đã tồn tại.")
    # --- KẾT THÚC KHỞI TẠO DỮ LIỆU TEST ---

    show_login_window() # Hiển thị cửa sổ đăng nhập sau khi kết nối và tạo user test


if __name__ == '__main__':
    main()