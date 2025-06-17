# ui/main_window.py
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QStackedWidget,
    QSpacerItem, QSizePolicy, QFrame
)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPainter, QPalette
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect

from ui.manage_ui import DashboardWidget


class MainWindow(QMainWindow):
    """
    Cửa sổ chính của ứng dụng hệ thống điểm danh sinh viên
    Bao gồm sidebar điều hướng và khu vực nội dung chính
    """

    # Tín hiệu được phát ra khi người dùng yêu cầu đăng xuất
    logout_requested = pyqtSignal()

    def __init__(self, user_role, parent=None):
        """
        Khởi tạo cửa sổ chính

        Args:
            user_role (str): Vai trò của người dùng (admin, lecturer, student)
            parent: Widget cha (mặc định None)
        """
        super().__init__(parent)
        self.user_role = user_role
        self.current_button = None  # Theo dõi nút hiện tại được chọn

        # Thiết lập cửa sổ chính
        self.setWindowTitle(f"Hệ thống Điểm danh Sinh viên - {self.user_role.upper()}")
        self.setGeometry(100, 100, 1400, 900)  # Tăng kích thước cho giao diện rộng rãi hơn
        self.setMinimumSize(1200, 800)  # Kích thước tối thiểu

        # Khởi tạo giao diện và áp dụng styles
        self.init_ui()
        self.apply_styles()

        # Thiết lập nút mặc định được chọn
        self.set_active_button(self.btn_dashboard)

    def init_ui(self):
        """Khởi tạo giao diện người dùng"""

        # === THIẾT LẬP WIDGET TRUNG TÂM ===
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout chính theo chiều ngang (sidebar + content)
        main_h_layout = QHBoxLayout(central_widget)
        main_h_layout.setContentsMargins(0, 0, 0, 0)
        main_h_layout.setSpacing(0)

        # === TẠO SIDEBAR ===
        self.create_sidebar()
        main_h_layout.addWidget(self.sidebar)

        # === TẠO KHU VỰC NỘI DUNG CHÍNH ===
        self.create_main_content_area()
        main_h_layout.addWidget(self.content_frame)

        # === THIẾT LẬP CÁC TRANG NỘI DUNG ===
        self.setup_content_pages()

        # === KẾT NỐI SỰ KIỆN ===
        self.connect_signals()

    def create_sidebar(self):
        """Tạo sidebar với các nút điều hướng"""

        # Frame chứa sidebar để dễ styling
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setObjectName("sidebar")

        # Layout chính của sidebar
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(5)

        # === PHẦN HEADER SIDEBAR ===
        # Logo và tên ứng dụng
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 20)

        # Label cho logo (có thể thêm hình ảnh sau)
        logo_label = QLabel("📊")  # Sử dụng emoji tạm thời
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("font-size: 48px; margin-bottom: 10px;")

        # Tên ứng dụng
        app_name_label = QLabel("Điểm Danh\nSinh Viên")
        app_name_label.setAlignment(Qt.AlignCenter)
        app_name_label.setObjectName("app_name")

        header_layout.addWidget(logo_label)
        header_layout.addWidget(app_name_label)
        sidebar_layout.addWidget(header_widget)

        # === PHẦN NAVIGATION BUTTONS ===
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 20, 0, 0)
        nav_layout.setSpacing(8)

        # Tạo các nút điều hướng với icon unicode
        self.btn_dashboard = self._create_sidebar_button("🏠 Trang chủ", "dashboard")
        self.btn_manage = self._create_sidebar_button("👥 Quản lý", "manage")
        self.btn_statistics = self._create_sidebar_button("📈 Thống kê", "statistics")
        self.btn_recognition = self._create_sidebar_button("👤 Nhận diện", "recognition")

        # Thêm các nút vào layout
        nav_layout.addWidget(self.btn_dashboard)
        nav_layout.addWidget(self.btn_manage)
        nav_layout.addWidget(self.btn_statistics)
        nav_layout.addWidget(self.btn_recognition)

        sidebar_layout.addWidget(nav_widget)

        # === KHOẢNG TRỐNG LINH HOẠT ===
        sidebar_layout.addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        # === PHẦN FOOTER SIDEBAR ===
        footer_widget = QWidget()
        footer_layout = QVBoxLayout(footer_widget)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(8)

        # Nút tài khoản và đăng xuất
        self.btn_account = self._create_sidebar_button("⚙️ Tài khoản", "account")
        self.btn_logout = self._create_sidebar_button("🚪 Đăng xuất", "logout")

        footer_layout.addWidget(self.btn_account)
        footer_layout.addWidget(self.btn_logout)
        sidebar_layout.addWidget(footer_widget)

    def create_main_content_area(self):
        """Tạo khu vực nội dung chính"""

        # Frame chứa nội dung chính
        self.content_frame = QFrame()
        self.content_frame.setObjectName("content_frame")

        # Layout cho khu vực nội dung
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # === HEADER BAR ===
        header_bar = QWidget()
        header_bar.setFixedHeight(60)
        header_bar.setObjectName("header_bar")

        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(20, 10, 20, 10)

        # Tiêu đề trang hiện tại
        self.page_title = QLabel("Trang chủ tổng quan")
        self.page_title.setObjectName("page_title")

        # Thông tin người dùng
        user_info = QLabel(f"Xin chào, {self.user_role.title()}")
        user_info.setObjectName("user_info")

        header_layout.addWidget(self.page_title)
        header_layout.addStretch()  # Đẩy thông tin user sang phải
        header_layout.addWidget(user_info)

        # === STACKED WIDGET CHO NỘI DUNG ===
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("stacked_widget")

        # Thêm vào layout chính
        content_layout.addWidget(header_bar)
        content_layout.addWidget(self.stacked_widget)

    def setup_content_pages(self):
        """Thiết lập các trang nội dung"""

        try:
            # Import và tạo trang Dashboard
            from .dashboard_ui import DashboardUI
            self.dashboard_page = DashboardUI(self.user_role)
            self.stacked_widget.addWidget(self.dashboard_page)
        except ImportError:
            # Tạo trang tạm thời nếu chưa có dashboard_ui.py
            temp_dashboard = self._create_temp_page("Trang chủ tổng quan",
                                                    "Chào mừng bạn đến với hệ thống điểm danh sinh viên!")
            self.stacked_widget.addWidget(temp_dashboard)

        # Trang Quản lý
        try:
            from .manage_ui import AttendanceManagerUI
            self.manage_page = AttendanceManagerUI()
            self.stacked_widget.addWidget(self.manage_page)

            print("✅ Đã tải thành công trang Quản lý (AttendanceManagerUI)")
        except ImportError:
            manage_page = self._create_temp_page("Quản lý người dùng",
                                                 "Quản lý thông tin sinh viên và giảng viên")
            self.stacked_widget.addWidget(manage_page)

        # Trang Thống kê
        stats_page = self._create_temp_page("Thống kê và báo cáo",
                                            "Xem các báo cáo và thống kê điểm danh")
        self.stacked_widget.addWidget(stats_page)

        # Trang Nhận diện
        try:
            from .attendance_taking_ui import AttendanceUI
            self.attendance_page = AttendanceUI()
            self.stacked_widget.addWidget(self.attendance_page)

            print("✅ Đã tải thành công trang nhận diện (Attendace taking)")
        except ImportError:
            recognition_page = self._create_temp_page("Nhận diện khuôn mặt",
                                                  "Chức năng nhận diện khuôn mặt để điểm danh")
            self.stacked_widget.addWidget(recognition_page)

        # Trang Tài khoản
        account_page = self._create_temp_page("Cài đặt tài khoản",
                                              "Quản lý thông tin tài khoản cá nhân")
        self.stacked_widget.addWidget(account_page)

    def _create_temp_page(self, title, description):
        """Tạo trang tạm thời cho demo"""

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        # Tiêu đề trang
        title_label = QLabel(title)
        title_label.setObjectName("temp_page_title")
        title_label.setAlignment(Qt.AlignCenter)

        # Mô tả
        desc_label = QLabel(description)
        desc_label.setObjectName("temp_page_desc")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(desc_label)

        return page

    def connect_signals(self):
        """Kết nối các tín hiệu và slot"""

        # Kết nối các nút điều hướng với việc chuyển trang
        self.btn_dashboard.clicked.connect(lambda: self.switch_page(0, "Trang chủ tổng quan", self.btn_dashboard))
        self.btn_manage.clicked.connect(lambda: self.switch_page(1, "Quản lý người dùng", self.btn_manage))
        self.btn_statistics.clicked.connect(lambda: self.switch_page(2, "Thống kê và báo cáo", self.btn_statistics))
        self.btn_recognition.clicked.connect(lambda: self.switch_page(3, "Nhận diện khuôn mặt", self.btn_recognition))
        self.btn_account.clicked.connect(lambda: self.switch_page(4, "Cài đặt tài khoản", self.btn_account))

        # Kết nối nút đăng xuất
        self.btn_logout.clicked.connect(self.logout)

    def _create_sidebar_button(self, text, button_id):
        """
        Tạo nút sidebar với style tùy chỉnh

        Args:
            text (str): Văn bản hiển thị trên nút
            button_id (str): ID định danh cho nút

        Returns:
            QPushButton: Nút đã được tạo và style
        """
        button = QPushButton(text)
        button.setFixedSize(220, 50)
        button.setObjectName(f"sidebar_btn_{button_id}")
        button.setCursor(Qt.PointingHandCursor)  # Con trỏ chuột dạng tay khi hover

        # Thiết lập font
        font = QFont("Segoe UI", 11, QFont.Medium)
        button.setFont(font)

        return button

    def switch_page(self, page_index, page_title, button):
        """
        Chuyển đổi trang và cập nhật UI

        Args:
            page_index (int): Chỉ số trang trong stacked widget
            page_title (str): Tiêu đề trang
            button (QPushButton): Nút được nhấn
        """
        # Chuyển trang
        self.stacked_widget.setCurrentIndex(page_index)

        # Cập nhật tiêu đề
        self.page_title.setText(page_title)

        # Cập nhật trạng thái active của nút
        self.set_active_button(button)

    def set_active_button(self, button):
        """
        Thiết lập nút active và bỏ active các nút khác

        Args:
            button (QPushButton): Nút cần thiết lập active
        """
        # Bỏ active nút hiện tại
        if self.current_button:
            self.current_button.setProperty("active", False)
            self.current_button.style().unpolish(self.current_button)
            self.current_button.style().polish(self.current_button)

        # Thiết lập nút mới active
        button.setProperty("active", True)
        button.style().unpolish(button)
        button.style().polish(button)

        self.current_button = button

    def logout(self):
        """Xử lý đăng xuất với hộp thoại xác nhận"""

        # Tạo hộp thoại xác nhận với style đẹp
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('Xác nhận Đăng xuất')
        msg_box.setText("Bạn có chắc muốn đăng xuất khỏi hệ thống?")
        msg_box.setIcon(QMessageBox.Question)

        # Tùy chỉnh các nút
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        # Đặt văn bản tiếng Việt cho các nút
        yes_button = msg_box.button(QMessageBox.Yes)
        no_button = msg_box.button(QMessageBox.No)
        yes_button.setText("Đăng xuất")
        no_button.setText("Hủy bỏ")

        # Hiển thị và xử lý kết quả
        reply = msg_box.exec_()

        if reply == QMessageBox.Yes:
            self.logout_requested.emit()  # Phát tín hiệu đăng xuất
            self.close()  # Đóng cửa sổ

    def apply_styles(self):
        """Áp dụng CSS styles cho toàn bộ ứng dụng"""

        style_sheet = """
        /* === THIẾT LẬP CHUNG === */
        QMainWindow {
            background-color: #f8f9fa;
            color: #2c3e50;
        }

        /* === SIDEBAR STYLES === */
        QFrame#sidebar {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                      stop: 0 #667eea, stop: 1 #764ba2);
            border: none;
            border-radius: 0px;
        }

        QLabel#app_name {
            color: white;
            font-size: 18px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial, sans-serif;
            margin-bottom: 10px;
        }

        /* === SIDEBAR BUTTONS === */
        QPushButton[class="sidebar_btn"] {
            background-color: rgba(255, 255, 255, 0.1);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 12px 16px;
            text-align: left;
            font-size: 13px;
            font-weight: 500;
            margin: 2px 0px;
        }

        QPushButton[class="sidebar_btn"]:hover {
            background-color: rgba(255, 255, 255, 0.2);
            transform: translateX(5px);
        }

        QPushButton[class="sidebar_btn"][active="true"] {
            background-color: rgba(255, 255, 255, 0.25);
            border-left: 4px solid #00d4aa;
            font-weight: bold;
        }

        QPushButton[class="sidebar_btn"]:pressed {
            background-color: rgba(255, 255, 255, 0.15);
        }

        /* === CONTENT AREA === */
        QFrame#content_frame {
            background-color: white;
            border: none;
            border-radius: 0px;
        }

        /* === HEADER BAR === */
        QWidget#header_bar {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                      stop: 0 #ffffff, stop: 1 #f8f9fa);
            border-bottom: 2px solid #e9ecef;
            border-radius: 8px;
            margin-bottom: 10px;
        }

        QLabel#page_title {
            color: #2c3e50;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial, sans-serif;
        }

        QLabel#user_info {
            color: #6c757d;
            font-size: 14px;
            font-weight: 500;
            background-color: #e3f2fd;
            padding: 8px 16px;
            border-radius: 20px;
            border: 1px solid #bbdefb;
        }

        /* === STACKED WIDGET === */
        QStackedWidget#stacked_widget {
            background-color: #ffffff;
            border: 1px solid #e9ecef;
            border-radius: 12px;
            padding: 20px;
        }

        /* === TEMPORARY PAGES === */
        QLabel#temp_page_title {
            color: #495057;
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 20px;
        }

        QLabel#temp_page_desc {
            color: #6c757d;
            font-size: 16px;
            line-height: 1.5;
            max-width: 600px;
        }

        /* === SCROLLBAR STYLES === */
        QScrollBar:vertical {
            background-color: #f1f3f4;
            width: 12px;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical {
            background-color: #c1c8cd;
            border-radius: 6px;
            min-height: 20px;
        }

        QScrollBar::handle:vertical:hover {
            background-color: #a8b1b8;
        }
        """

        self.setStyleSheet(style_sheet)

        # Thiết lập thuộc tính class cho các nút sidebar
        for button in [self.btn_dashboard, self.btn_manage, self.btn_statistics,
                       self.btn_recognition, self.btn_account, self.btn_logout]:
            button.setProperty("class", "sidebar_btn")

    def resizeEvent(self, event):
        """Xử lý sự kiện thay đổi kích thước cửa sổ"""
        super().resizeEvent(event)

        # Có thể thêm logic responsive design ở đây nếu cần
        # Ví dụ: thu gọn sidebar khi cửa sổ quá nhỏ
        if self.width() < 1000:
            self.sidebar.setFixedWidth(200)
        else:
            self.sidebar.setFixedWidth(250)