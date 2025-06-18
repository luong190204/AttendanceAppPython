# ui/login_ui.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QFrame,
                             QSizePolicy, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPixmap, QPalette, QIcon, QColor
import sys
import os
import logging

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Thêm đường dẫn thư mục gốc của project vào sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Đảm bảo các import này chính xác
from database.user_repository import UserRepository

class LoginUI(QWidget):
    # Tín hiệu được phát ra khi đăng nhập thành công
    login_successful = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        try:
            self.user_repo = UserRepository()
        except Exception as e:
            logger.error(f"Lỗi khởi tạo UserRepository: {e}")
            self.user_repo = UserRepository()  # Sử dụng mock class

        self.init_ui()
        self.setup_animations()

    def init_ui(self):
        """Khởi tạo giao diện người dùng"""
        self.setWindowTitle("Hệ Thống Điểm Danh Sinh Viên")
        self.setFixedSize(1000, 700)
        self.setStyleSheet(self.get_main_stylesheet())

        # Căn giữa cửa sổ
        self.center_window()

        # Layout chính
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Tạo left panel (thông tin hệ thống)
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel)

        # Tạo right panel (form đăng nhập)
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel)

    def center_window(self):
        """Căn giữa cửa sổ trên màn hình"""
        from PyQt5.QtWidgets import QDesktopWidget
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def create_left_panel(self):
        """Tạo panel bên trái với thông tin hệ thống"""
        left_panel = QFrame()
        left_panel.setObjectName("leftPanel")
        left_panel.setFixedWidth(400)

        layout = QVBoxLayout(left_panel)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)

        # Logo hoặc icon (có thể thay bằng logo thật)
        logo_label = QLabel("🎓")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("font-size: 80px; color: white; margin-bottom: 20px;")
        layout.addWidget(logo_label)

        # Tiêu đề chính
        title_label = QLabel("HỆ THỐNG\nĐIỂM DANH\nSINH VIÊN")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("mainTitle")
        layout.addWidget(title_label)

        # Mô tả
        desc_label = QLabel("Quản lý điểm danh hiệu quả\nvà chính xác cho giáo dục")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setObjectName("description")
        layout.addWidget(desc_label)

        layout.addStretch()

        # Thông tin bổ sung
        info_label = QLabel("Phiên bản 1.0\n© 2025 Hệ Thống Điểm Danh")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setObjectName("info")
        layout.addWidget(info_label)

        return left_panel

    def create_right_panel(self):
        """Tạo panel bên phải với form đăng nhập"""
        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")

        layout = QVBoxLayout(right_panel)
        layout.setContentsMargins(80, 100, 80, 100)
        layout.setSpacing(0)

        # Tiêu đề đăng nhập
        login_title = QLabel("Đăng Nhập")
        login_title.setAlignment(Qt.AlignCenter)
        login_title.setObjectName("loginTitle")
        layout.addWidget(login_title)

        # Subtitle
        subtitle = QLabel("Vui lòng nhập thông tin đăng nhập của bạn")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        layout.addSpacing(50)

        # Form container
        form_container = QFrame()
        form_container.setObjectName("formContainer")
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(25)

        # Username field
        self.username_container = self.create_input_field("👤", "Tên đăng nhập")
        self.username_input = self.username_container.findChild(QLineEdit)
        form_layout.addWidget(self.username_container)

        # Password field
        self.password_container = self.create_input_field("🔒", "Mật khẩu", is_password=True)
        self.password_input = self.password_container.findChild(QLineEdit)
        form_layout.addWidget(self.password_container)

        # Login button
        self.login_button = QPushButton("Đăng Nhập")
        self.login_button.setObjectName("loginButton")
        self.login_button.clicked.connect(self.handle_login)
        form_layout.addWidget(self.login_button)

        # Forgot password link (optional)
        forgot_label = QLabel('<a href="#" style="color: #4285f4; text-decoration: none;">Quên mật khẩu?</a>')
        forgot_label.setAlignment(Qt.AlignCenter)
        forgot_label.setObjectName("forgotLink")
        form_layout.addWidget(forgot_label)

        layout.addWidget(form_container)
        layout.addStretch()

        return right_panel

    def create_input_field(self, icon, placeholder, is_password=False):
        """Tạo field input với icon và placeholder"""
        container = QFrame()
        container.setObjectName("inputContainer")

        layout = QHBoxLayout(container)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(10)

        # Icon
        icon_label = QLabel(icon)
        icon_label.setObjectName("inputIcon")
        layout.addWidget(icon_label)

        # Input field
        input_field = QLineEdit()
        input_field.setObjectName("inputField")
        input_field.setPlaceholderText(placeholder)
        input_field.setAttribute(Qt.WA_MacShowFocusRect, 0)  # Remove Mac focus ring

        if is_password:
            input_field.setEchoMode(QLineEdit.Password)

        # Thêm event handlers cho focus effects
        input_field.focusInEvent = lambda e: self.on_input_focus_in(container, e)
        input_field.focusOutEvent = lambda e: self.on_input_focus_out(container, e)

        layout.addWidget(input_field)

        return container

    def on_input_focus_in(self, container, event):
        """Xử lý khi input được focus"""
        container.setObjectName("inputContainerFocused")
        container.setStyleSheet(self.get_main_stylesheet())
        QLineEdit.focusInEvent(container.findChild(QLineEdit), event)

    def on_input_focus_out(self, container, event):
        """Xử lý khi input mất focus"""
        container.setObjectName("inputContainer")
        container.setStyleSheet(self.get_main_stylesheet())
        QLineEdit.focusOutEvent(container.findChild(QLineEdit), event)

    def setup_animations(self):
        """Thiết lập các animation effects"""
        # Shadow effect cho form
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 10)

        try:
            form_container = self.findChild(QFrame, "formContainer")
            if form_container:
                form_container.setGraphicsEffect(shadow)
        except:
            pass

    def handle_login(self):
        """Xử lý đăng nhập"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        # Validation
        if not username or not password:
            self.show_message("Cảnh báo", "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.", "warning")
            return

        # Disable button và hiển thị loading
        self.login_button.setEnabled(False)
        self.login_button.setText("Đang đăng nhập...")

        # Sử dụng QTimer để tạo hiệu ứng loading
        QTimer.singleShot(500, lambda: self.process_login(username, password))

    def process_login(self, username, password):
        """Xử lý quá trình đăng nhập"""
        try:
            user_role = self.user_repo.authenticate_user(username, password)

            if user_role:
                self.show_message("Thành công", "Đăng nhập thành công!", "success")
                QTimer.singleShot(1000, lambda: self.login_successful.emit(user_role))
            else:
                self.show_message("Lỗi", "Tên đăng nhập hoặc mật khẩu không đúng!", "error")
                self.password_input.clear()
                self.password_input.setFocus()
        except Exception as e:
            logger.error(f"Lỗi đăng nhập: {e}")
            self.show_message("Lỗi", f"Có lỗi xảy ra: {str(e)}", "error")
        finally:
            # Restore button
            self.login_button.setEnabled(True)
            self.login_button.setText("Đăng Nhập")

    def show_message(self, title, message, msg_type="info"):
        """Hiển thị thông báo với style tùy chỉnh"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)

        if msg_type == "success":
            msg_box.setIcon(QMessageBox.Information)
        elif msg_type == "warning":
            msg_box.setIcon(QMessageBox.Warning)
        elif msg_type == "error":
            msg_box.setIcon(QMessageBox.Critical)
        else:
            msg_box.setIcon(QMessageBox.Information)

        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #3367d6;
            }
        """)

        msg_box.exec_()

    def get_main_stylesheet(self):
        """Trả về stylesheet chính cho ứng dụng"""
        return """
            /* Main Panels */
            QFrame#leftPanel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border: none;
            }

            QFrame#rightPanel {
                background-color: #fafafa;
                border: none;
            }

            /* Typography */
            QLabel#mainTitle {
                color: white;
                font-size: 36px;
                font-weight: bold;
                line-height: 1.2;
                letter-spacing: 2px;
            }

            QLabel#description {
                color: rgba(255, 255, 255, 0.9);
                font-size: 16px;
                line-height: 1.5;
                margin-top: 20px;
            }

            QLabel#info {
                color: rgba(255, 255, 255, 0.7);
                font-size: 12px;
                line-height: 1.4;
            }

            QLabel#loginTitle {
                color: #333;
                font-size: 32px;
                font-weight: bold;
                margin-bottom: 10px;
            }

            QLabel#subtitle {
                color: #666;
                font-size: 14px;
                margin-bottom: 30px;
            }

            /* Input Containers */
            QFrame#inputContainer {
                background-color: white;
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                min-height: 45px;
            }

            QFrame#inputContainerFocused {
                background-color: white;
                border: 2px solid #4285f4;
                border-radius: 8px;
                min-height: 45px;
            }

            /* Input Fields */
            QLineEdit#inputField {
                background: transparent;
                border: none;
                font-size: 14px;
                color: #333;
                padding: 0;
            }

            QLineEdit#inputField:focus {
                outline: none;
            }

            /* Input Icons */
            QLabel#inputIcon {
                font-size: 16px;
                color: #666;
                min-width: 20px;
            }

            /* Login Button */
            QPushButton#loginButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4285f4, stop:1 #667eea);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                margin-top: 10px;
            }

            QPushButton#loginButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3367d6, stop:1 #5a67d8);
            }

            QPushButton#loginButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2c5aa0, stop:1 #553c9a);
            }

            QPushButton#loginButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }

            /* Form Container */
            QFrame#formContainer {
                background-color: transparent;
                border: none;
            }

            /* Forgot Link */
            QLabel#forgotLink {
                font-size: 13px;
                margin-top: 15px;
            }
        """