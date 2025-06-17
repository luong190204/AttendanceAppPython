# ui/dashboard_ui.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QMessageBox, QScrollArea, QGridLayout, QPushButton,
    QSpacerItem, QSizePolicy, QProgressBar
)
from PyQt5.QtGui import QPixmap, QFont, QPalette, QLinearGradient, QBrush, QPainter
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect

# Import các Repository để lấy dữ liệu thống kê
from database.connection_manager import ConnectionManager
from database.student_repository import StudentRepository
from database.user_repository import UserRepository
from database.class_subject_repository import ClassSubjectRepository
from database.attendance_repository import AttendanceRepository

class StatCard(QFrame):
    """
    Widget card tùy chỉnh để hiển thị thống kê
    Bao gồm animation và hiệu ứng hover
    """

    def __init__(self, title, icon_text, color_scheme="blue", parent=None):
        """
        Khởi tạo StatCard

        Args:
            title (str): Tiêu đề của card
            icon_text (str): Icon unicode hoặc text
            color_scheme (str): Màu chủ đạo ("blue", "green", "purple", "orange")
            parent: Widget cha
        """
        super().__init__(parent)
        self.title = title
        self.icon_text = icon_text
        self.color_scheme = color_scheme
        self.count_value = 0

        # Thiết lập kích thước và thuộc tính cơ bản
        self.setFixedSize(280, 140)
        self.setObjectName("stat_card")

        # Tạo layout và các widget con
        self.init_ui()
        self.apply_card_styles()

        # Thiết lập hiệu ứng hover
        self.setMouseTracking(True)

    def init_ui(self):
        """Khởi tạo giao diện card"""

        # Layout chính của card
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(10)

        # === PHẦN HEADER CỦA CARD ===
        header_layout = QHBoxLayout()

        # Icon
        self.icon_label = QLabel(self.icon_text)
        self.icon_label.setObjectName("card_icon")
        self.icon_label.setFixedSize(50, 50)
        self.icon_label.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(self.icon_label)
        header_layout.addStretch()

        # === PHẦN NỘI DUNG CHÍNH ===
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        content_layout.setAlignment(Qt.AlignTop)

        # Tiêu đề
        self.title_label = QLabel(self.title)
        self.title_label.setObjectName("title_label")
        self.title_label.setAlignment(Qt.AlignCenter)  # Hoặc Qt.AlignCenter nếu muốn căn giữa

        # Số đếm chính (nằm dưới tiêu đề, cùng căn trái)
        self.count_label = QLabel("0")
        self.count_label.setObjectName("count_label")
        self.count_label.setAlignment(Qt.AlignCenter)  # Giống title để cùng hàng
        self.count_label.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: black;
            padding: 0px;
        """)

        content_layout.addWidget(self.title_label)
        content_layout.addWidget(self.count_label)

        # === PROGRESS BAR ===
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("card_progress")
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setValue(75)  # Có thể cập nhật sau

        # Thêm các phần vào layout chính
        main_layout.addLayout(header_layout)
        main_layout.addLayout(content_layout)
        main_layout.addWidget(self.progress_bar)

    def set_value(self, value):
        self.count_label.setText(str(value))

    def set_count(self, count):
        """
        Cập nhật số đếm với animation

        Args:
            count (int): Số đếm mới
        """
        if count != self.count_value:
            self.animate_count_change(self.count_value, count)
            self.count_value = count

    def animate_count_change(self, start_value, end_value):
        """
        Animation khi thay đổi số đếm

        Args:
            start_value (int): Giá trị bắt đầu
            end_value (int): Giá trị kết thúc
        """
        # Tạo timer để animate số đếm
        self.animation_timer = QTimer()
        self.current_value = start_value
        self.target_value = end_value
        self.animation_step = max(1, abs(end_value - start_value) // 20)

        self.animation_timer.timeout.connect(self.update_count_animation)
        self.animation_timer.start(50)  # Update mỗi 50ms

    def update_count_animation(self):
        """Cập nhật animation số đếm"""
        if self.current_value < self.target_value:
            self.current_value = min(self.current_value + self.animation_step, self.target_value)
        elif self.current_value > self.target_value:
            self.current_value = max(self.current_value - self.animation_step, self.target_value)

        self.count_label.setText(str(self.current_value))

        if self.current_value == self.target_value:
            self.animation_timer.stop()

    def apply_card_styles(self):
        """Áp dụng styles cho card dựa trên color scheme"""

        # Định nghĩa các màu cho từng scheme
        color_schemes = {
            "blue": {
                "gradient_start": "#4FC3F7",
                "gradient_end": "#29B6F6",
                "text_color": "#1976D2",
                "icon_bg": "rgba(25, 118, 210, 0.1)"
            },
            "green": {
                "gradient_start": "#81C784",
                "gradient_end": "#66BB6A",
                "text_color": "#388E3C",
                "icon_bg": "rgba(56, 142, 60, 0.1)"
            },
            "purple": {
                "gradient_start": "#BA68C8",
                "gradient_end": "#AB47BC",
                "text_color": "#7B1FA2",
                "icon_bg": "rgba(123, 31, 162, 0.1)"
            },
            "orange": {
                "gradient_start": "#FFB74D",
                "gradient_end": "#FFA726",
                "text_color": "#F57C00",
                "icon_bg": "rgba(245, 124, 0, 0.1)"
            }
        }

        colors = color_schemes.get(self.color_scheme, color_schemes["blue"])

        # CSS cho card
        card_style = f"""
        QFrame#stat_card {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                      stop: 0 {colors["gradient_start"]}, 
                                      stop: 1 {colors["gradient_end"]});
            border: none;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }}

        QFrame#stat_card:hover {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                      stop: 0 {colors["gradient_end"]}, 
                                      stop: 1 {colors["gradient_start"]});
        }}

        QLabel#card_icon {{
            background-color: {colors["icon_bg"]};
            border-radius: 25px;
            font-size: 24px;
            color: white;
            font-weight: bold;
        }}

        QLabel#count_label {{
            color: white;
            font-size: 36px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial, sans-serif;
        }}

        QLabel#title_label {{
            color: rgba(255, 255, 255, 0.9);
            font-size: 14px;
            font-weight: 500;
            font-family: 'Segoe UI', Arial, sans-serif;
        }}

        QProgressBar#card_progress {{
            background-color: rgba(255, 255, 255, 0.3);
            border: none;
            border-radius: 2px;
        }}

        QProgressBar#card_progress::chunk {{
            background-color: white;
            border-radius: 2px;
        }}
        """

        self.setStyleSheet(card_style)


class DashboardUI(QWidget):
    """
    Giao diện Dashboard chính hiển thị tổng quan hệ thống
    Bao gồm các thống kê và thông tin quan trọng
    """

    def __init__(self, user_role, parent=None):
        """
        Khởi tạo Dashboard UI

        Args:
            user_role (str): Vai trò người dùng (admin, teacher, student)
            parent: Widget cha
        """
        super().__init__(parent)
        self.user_role = user_role

        # Khởi tạo repositories nếu database có sẵn
        try:
            self.student_repo = StudentRepository()
            self.lecturer_repo = UserRepository()
            self.class_repo = ClassSubjectRepository()
            self.attendance_repo = AttendanceRepository()
            self.db_connected = True
        except Exception as e:
                print(f"Database connection failed: {e}")
                self.db_connected = False

        # Khởi tạo giao diện
        self.init_ui()
        self.apply_styles()

        # Tải dữ liệu sau khi UI đã sẵn sàng
        QTimer.singleShot(100, self.load_data)  # Delay nhỏ để UI render xong

    def init_ui(self):
        """Khởi tạo giao diện người dùng"""

        # === LAYOUT CHÍNH ===
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === TẠO SCROLL AREA ===
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setObjectName("dashboard_scroll")

        # Widget chứa nội dung trong scroll area
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(30, 30, 30, 30)
        scroll_layout.setSpacing(30)

        # === PHẦN HEADER ===
        self.create_header_section(scroll_layout)

        # === PHẦN THỐNG KÊ CARDS ===
        self.create_stats_section(scroll_layout)

        # === PHẦN QUICK ACTIONS ===
        self.create_quick_actions_section(scroll_layout)

        # === PHẦN WELCOME MESSAGE ===
        self.create_welcome_section(scroll_layout)

        # Thêm spacer để đẩy nội dung lên trên
        scroll_layout.addStretch()

        # Thiết lập scroll area
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

    def create_header_section(self, parent_layout):
        """Tạo phần header với thông tin tổng quan"""

        header_layout = QHBoxLayout()

        # === TIÊU ĐỀ CHÍNH ===
        title_section = QVBoxLayout()

        welcome_label = QLabel(f"Chào mừng, {self.user_role.title()}!")
        welcome_label.setObjectName("welcome_label")

        subtitle_label = QLabel("Tổng quan hệ thống điểm danh sinh viên")
        subtitle_label.setObjectName("subtitle_label")

        title_section.addWidget(welcome_label)
        title_section.addWidget(subtitle_label)
        title_section.addStretch()

        # === THÔNG TIN THỜI GIAN ===
        time_section = QVBoxLayout()
        time_section.setAlignment(Qt.AlignRight)

        from datetime import datetime
        current_time = datetime.now()

        date_label = QLabel(current_time.strftime("%d/%m/%Y"))
        date_label.setObjectName("date_label")
        date_label.setAlignment(Qt.AlignRight)

        self.time_label = QLabel(current_time.strftime("%H:%M:%S"))
        self.time_label.setObjectName("time_label")
        self.time_label.setAlignment(Qt.AlignRight)

        time_section.addWidget(date_label)
        time_section.addWidget(self.time_label)

        header_layout.addLayout(title_section)
        header_layout.addStretch()
        header_layout.addLayout(time_section)

        parent_layout.addLayout(header_layout)

        # === TIMER để cập nhật thời gian ===
        timer = QTimer(self)
        timer.timeout.connect(self.update_time_label)
        timer.start(1000)  # cập nhật mỗi 1000ms (1 giây)

    def update_time_label(self):
        """Hàm cập nhật giờ"""
        from datetime import datetime
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M:%S"))

    def create_stats_section(self, parent_layout):
        """Tạo phần hiển thị các thống kê chính"""

        # === Lấy dữ liệu từ repository (số sinh viên, giảng viên, lớp học) ===
        students_count = self.student_repo.get_total_students()
        lecturers_count = self.lecturer_repo.get_total_lecturers()
        classes_count = self.class_repo.get_total_classes()
        attendance_count = self.attendance_repo.count_attendance_today()
        # === Tiêu đề của section thống kê ===
        stats_title = QLabel("📊 Thống kê tổng quan")
        stats_title.setObjectName("section_title")
        parent_layout.addWidget(stats_title)

        # === Layout dạng lưới để chứa 4 stat cards (2x2) ===
        stats_grid = QGridLayout()
        stats_grid.setSpacing(20)  # Khoảng cách giữa các card

        # === TẠO CÁC THẺ STATISTIC CARD ===
        self.student_card = StatCard("Tổng số sinh viên", "👨‍🎓", "blue")
        self.lecturer_card = StatCard("Giảng viên", "👨‍🏫", "green")
        self.class_card = StatCard("Lớp học", "📚", "purple")
        self.attendance_card = StatCard("Điểm danh hôm nay", "✅", "orange")

        # === GÁN GIÁ TRỊ THỰC TẾ VÀO CÁC CARD ===
        # Hàm set_value sẽ truyền dữ liệu vào self.count_label (ở góc phải header)
        self.student_card.set_value(students_count)
        self.lecturer_card.set_value(lecturers_count)
        self.class_card.set_value(classes_count)
        self.attendance_card.set_value(attendance_count)

        # === Đặt 4 card vào Grid layout (2 hàng x 2 cột) ===
        stats_grid.addWidget(self.student_card, 0, 0)
        stats_grid.addWidget(self.lecturer_card, 0, 1)
        stats_grid.addWidget(self.class_card, 1, 0)
        stats_grid.addWidget(self.attendance_card, 1, 1)

        # === Gói grid vào widget rồi thêm vào layout cha ===
        stats_widget = QWidget()
        stats_widget.setLayout(stats_grid)
        parent_layout.addWidget(stats_widget)

    def create_quick_actions_section(self, parent_layout):
        """Tạo phần quick actions dựa trên user role"""

        # Tiêu đề section
        actions_title = QLabel("⚡ Thao tác nhanh")
        actions_title.setObjectName("section_title")
        parent_layout.addWidget(actions_title)

        # Layout cho các nút action
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)

        # Tạo các nút action dựa trên role
        if self.user_role.lower() == 'admin':
            actions = [
                ("👥 Quản lý người dùng", self.open_user_management),
                ("📊 Xem báo cáo", self.open_reports),
                ("⚙️ Cài đặt hệ thống", self.open_settings)
            ]
        elif self.user_role.lower() == 'lecturer':
            actions = [
                ("📝 Điểm danh lớp", self.start_attendance),
                ("📈 Xem thống kê", self.view_statistics),
                ("👨‍🎓 Quản lý sinh viên", self.manage_students)
            ]
        else:  # student
            actions = [
                ("📅 Xem lịch học", self.view_schedule),
                ("📊 Xem điểm danh", self.view_attendance),
                ("👤 Cập nhật thông tin", self.update_profile)
            ]

        for action_text, action_func in actions:
            btn = self.create_action_button(action_text, action_func)
            actions_layout.addWidget(btn)

        actions_layout.addStretch()
        parent_layout.addLayout(actions_layout)

    def create_action_button(self, text, callback):
        """Tạo nút action với style đẹp"""

        btn = QPushButton(text)
        btn.setObjectName("action_button")
        btn.setFixedSize(200, 50)
        btn.clicked.connect(callback)
        btn.setCursor(Qt.PointingHandCursor)

        return btn

    def create_welcome_section(self, parent_layout):
        """Tạo phần welcome với hình ảnh và thông điệp"""

        # Frame chứa welcome content
        welcome_frame = QFrame()
        welcome_frame.setObjectName("welcome_frame")
        welcome_frame.setFixedHeight(200)

        welcome_layout = QVBoxLayout(welcome_frame)
        welcome_layout.setAlignment(Qt.AlignCenter)

        # Icon lớn
        main_icon = QLabel("🎓")
        main_icon.setAlignment(Qt.AlignCenter)
        main_icon.setStyleSheet("font-size: 64px; margin-bottom: 10px;")

        # Thông điệp chính
        main_message = QLabel("Hệ thống Điểm danh Sinh viên")
        main_message.setObjectName("main_message")
        main_message.setAlignment(Qt.AlignCenter)

        # Thông điệp phụ
        sub_message = QLabel("Quản lý điểm danh hiệu quả với công nghệ nhận diện khuôn mặt")
        sub_message.setObjectName("sub_message")
        sub_message.setAlignment(Qt.AlignCenter)
        sub_message.setWordWrap(True)

        welcome_layout.addWidget(main_icon)
        welcome_layout.addWidget(main_message)
        welcome_layout.addWidget(sub_message)

        parent_layout.addWidget(welcome_frame)

    def load_data(self):
        """Tải dữ liệu thống kê từ database hoặc sử dụng dữ liệu demo"""

        try:
            if self.db_connected:
                # Tải dữ liệu thực từ database
                student_count = self.student_repo.get_total_students()
                lecturer_count = self.lecturer_repo.get_total_lecturers()
                class_count = self.class_repo.get_total_classes()
                attendance_today = self.get_today_attendance_count()
            else:
                # Sử dụng dữ liệu demo
                student_count = 1250
                lecturer_count = 45
                class_count = 28
                attendance_today = 892

            # Cập nhật các cards với animation
            self.student_card.set_count(student_count)
            self.lecturer_card.set_count(lecturer_count)
            self.class_card.set_count(class_count)
            self.attendance_card.set_count(attendance_today)

        except Exception as e:
            # Xử lý lỗi và hiển thị thông báo
            print(f"Error loading data: {e}")
            self.show_error_message("Không thể tải dữ liệu thống kê", str(e))

            # Hiển thị dữ liệu lỗi
            self.student_card.set_count(0)
            self.lecturer_card.set_count(0)
            self.class_card.set_count(0)
            self.attendance_card.set_count(0)

    def get_today_attendance_count(self):
        """Lấy số lượng điểm danh hôm nay (placeholder)"""
        # TODO: Implement khi có bảng attendance
        return 0

    def show_error_message(self, title, message):
        """Hiển thị thông báo lỗi"""

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.exec_()

    # === CALLBACK FUNCTIONS CHO QUICK ACTIONS ===

    def open_user_management(self):
        """Mở trang quản lý người dùng"""
        print("Opening user management...")
        # TODO: Implement navigation to user management page

    def open_reports(self):
        """Mở trang báo cáo"""
        print("Opening reports...")
        # TODO: Implement navigation to reports page

    def open_settings(self):
        """Mở trang cài đặt"""
        print("Opening settings...")
        # TODO: Implement navigation to settings page

    def start_attendance(self):
        """Bắt đầu điểm danh"""
        print("Starting attendance...")
        # TODO: Implement attendance functionality

    def view_statistics(self):
        """Xem thống kê"""
        print("Viewing statistics...")
        # TODO: Implement navigation to statistics page

    def manage_students(self):
        """Quản lý sinh viên"""
        print("Managing students...")
        # TODO: Implement student management

    def view_schedule(self):
        """Xem lịch học"""
        print("Viewing schedule...")
        # TODO: Implement schedule view

    def view_attendance(self):
        """Xem điểm danh"""
        print("Viewing attendance...")
        # TODO: Implement attendance history

    def update_profile(self):
        """Cập nhật thông tin cá nhân"""
        print("Updating profile...")
        # TODO: Implement profile update

    def apply_styles(self):
        """Áp dụng CSS styles cho toàn bộ dashboard"""

        dashboard_styles = """
        /* === GENERAL STYLES === */
        DashboardUI {
            background-color: #f8f9fa;
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
        }

        QScrollArea#dashboard_scroll {
            background-color: transparent;
            border: none;
        }

        QScrollArea#dashboard_scroll QScrollBar:vertical {
            background-color: #f1f3f4;
            width: 8px;
            border-radius: 4px;
        }

        QScrollArea#dashboard_scroll QScrollBar::handle:vertical {
            background-color: #c1c8cd;
            border-radius: 4px;
            min-height: 20px;
        }

        QScrollArea#dashboard_scroll QScrollBar::handle:vertical:hover {
            background-color: #a8b1b8;
        }

        /* === HEADER STYLES === */
        QLabel#welcome_label {
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }

        QLabel#subtitle_label {
            font-size: 16px;
            color: #6c757d;
            font-weight: normal;
        }

        QLabel#date_label {
            font-size: 18px;
            font-weight: bold;
            color: #495057;
        }

        QLabel#time_label {
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }

        /* === SECTION TITLES === */
        QLabel#section_title {
            font-size: 20px;
            font-weight: bold;
            color: #343a40;
            margin-bottom: 15px;
            padding: 10px 0;
            border-bottom: 2px solid #e9ecef;
        }

        /* === ACTION BUTTONS === */
        QPushButton#action_button {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #4285f4, stop: 1 #1a73e8);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 13px;
            font-weight: 500;
            padding: 12px 16px;
        }

        QPushButton#action_button:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #5a94f5, stop: 1 #2b7de9);
            transform: translateY(-2px);
        }

        QPushButton#action_button:pressed {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #3367d6, stop: 1 #1557b0);
        }

        /* === WELCOME FRAME === */
        QFrame#welcome_frame {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                      stop: 0 #667eea, stop: 1 #764ba2);
            border: none;
            border-radius: 20px;
            margin-top: 20px;
        }

        QLabel#main_message {
            color: white;
            font-size: 32px;
            font-weight: bold;
            margin: 10px 0;
        }

        QLabel#sub_message {
            color: rgba(255, 255, 255, 0.9);
            font-size: 16px;
            font-weight: normal;
            margin-bottom: 20px;
        }
        """

        self.setStyleSheet(dashboard_styles)