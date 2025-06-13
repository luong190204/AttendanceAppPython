import sys
from idlelib import window

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QGridLayout, QPushButton, QLabel,
                             QScrollArea, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor
from functools import partial

# Import các UI modules
def safe_import(module_name, class_name):
    """Safely import modules and return class or None"""
    try:
        module = __import__(module_name, fromlist=[class_name])
        return getattr(module, class_name)
    except ImportError as e:
        print(f"Warning: Could not import {class_name} from {module_name}: {e}")
        return None


# Import tất cả các UI classes
StudentManagementUI = safe_import('ui.student_management_ui', 'StudentManagementUI')
# TeacherManagementUI = safe_import('teacher_management_ui', 'TeacherManagementUI')
# AttendanceManagementUI = safe_import('attendance_management_ui', 'AttendanceManagementUI')
# SessionManagementUI = safe_import('session_management_ui', 'SessionManagementUI')
# CourseManagementUI = safe_import('course_management_ui', 'CourseManagementUI')
# ImageViewerUI = safe_import('image_viewer_ui', 'ImageViewerUI')


class ModuleButton(QPushButton):
    def __init__(self, title, icon_text, color, parent=None):
        super().__init__(parent)
        self.title = title
        self.icon_text = icon_text
        self.color = color
        self.setupUI()

    def setupUI(self):
        self.setFixedSize(200, 140)  # Tăng kích thước button
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 {self.color}, stop:1 {self.adjust_color(self.color, -30)});
                border: none;
                border-radius: 20px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                text-align: left;
                padding: 20px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 {self.adjust_color(self.color, 20)}, 
                           stop:1 {self.adjust_color(self.color, -10)});
                transform: translateY(-2px);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 {self.adjust_color(self.color, -20)}, 
                           stop:1 {self.adjust_color(self.color, -50)});
                transform: translateY(1px);
            }}
        """)

        layout = QVBoxLayout()

        # Icon container
        icon_label = QLabel(self.icon_text)
        icon_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.3);
                border-radius: 25px;
                padding: 10px;
                font-size: 24px;
                font-weight: bold;
                color: white;
            }
        """)
        icon_label.setFixedSize(50, 50)
        icon_label.setAlignment(Qt.AlignCenter)

        # Title label
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                padding: 10px 0px;
            }
        """)
        title_label.setWordWrap(True)

        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addStretch()
        layout.setContentsMargins(20, 20, 20, 20)

        self.setLayout(layout)

    def adjust_color(self, color, amount):
        """Điều chỉnh độ sáng của màu"""
        color = color.lstrip('#')
        if len(color) != 6:
            return color
        try:
            r, g, b = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
            r = max(0, min(255, r + amount))
            g = max(0, min(255, g + amount))
            b = max(0, min(255, b + amount))
            return f"#{r:02x}{g:02x}{b:02x}"
        except ValueError:
            return color


class HeaderWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        layout = QHBoxLayout()

        # Title section
        title_section = QWidget()
        title_layout = QVBoxLayout()

        main_title = QLabel("Hệ thống Quản lý")
        main_title.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;
                color: #1F2937;
                margin: 0;
                padding: 0;
            }
        """)

        subtitle = QLabel("Dashboard điều khiển")
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #6B7280;
                margin: 0;
                padding: 0;
            }
        """)

        title_layout.addWidget(main_title)
        title_layout.addWidget(subtitle)
        title_layout.setContentsMargins(20, 20, 0, 20)
        title_section.setLayout(title_layout)

        layout.addWidget(title_section)
        layout.addStretch()

        # User info section
        user_info = QLabel("👤 Administrator")
        user_info.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #374151;
                background-color: rgba(99, 102, 241, 0.1);
                padding: 10px 20px;
                border-radius: 25px;
                margin: 20px;
            }
        """)
        layout.addWidget(user_info)

        self.setLayout(layout)


class DashboardWidget(QWidget):
    moduleSelected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        layout = QVBoxLayout()

        # Header
        header = HeaderWidget()
        layout.addWidget(header)

        # Modules grid
        modules_widget = QWidget()
        grid_layout = QGridLayout()
        grid_layout.setSpacing(25)
        grid_layout.setContentsMargins(30, 20, 30, 30)

        # Module definitions với màu sắc đa dạng hơn
        modules = [
            ("Quản lý Sinh viên", "👤", "#3B82F6"),  # Blue
            ("Quản lý Điểm danh", "📋", "#10B981"),  # Green
            ("Quản lý Buổi học", "📚", "#F59E0B"),  # Orange
            ("Quản lý Môn học", "📖", "#8B5CF6"),  # Purple
            ("Quản lý Giảng viên", "👨‍🏫", "#EF4444"),  # Red
            ("Xem ảnh", "🖼️", "#06B6D4")  # Cyan
        ]

        for i, (title, icon, color) in enumerate(modules):
            button = ModuleButton(title, icon, color)
            button.clicked.connect(partial(self.handleButtonClick, title))

            row = i // 3
            col = i % 3
            grid_layout.addWidget(button, row, col)

        modules_widget.setLayout(grid_layout)

        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(modules_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background: #F3F4F6;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #D1D5DB;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9CA3AF;
            }
        """)

        layout.addWidget(scroll_area)
        self.setLayout(layout)

    def handleButtonClick(self, title):
        print(f"Module '{title}' được chọn")
        self.moduleSelected.emit(title)


class PlaceholderUI(QMainWindow):
    """UI tạm thời cho các module chưa được implement"""

    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        self.setGeometry(200, 200, 900, 650)
        self.setupUI()

    def setupUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Header
        header_label = QLabel(self.windowTitle())
        header_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #1F2937;
                padding: 30px;
                background-color: #F9FAFB;
                border-bottom: 2px solid #E5E7EB;
            }
        """)
        header_label.setAlignment(Qt.AlignCenter)

        # Content
        content_label = QLabel("🚧 Module đang được phát triển\n\nVui lòng quay lại sau!")
        content_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #6B7280;
                text-align: center;
                padding: 80px 40px;
                background-color: white;
                border-radius: 10px;
                margin: 20px;
            }
        """)
        content_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(header_label)
        layout.addWidget(content_label)
        layout.addStretch()

        central_widget.setLayout(layout)


class AttendanceManagerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.module_windows = {}  # Lưu trữ các cửa sổ đã mở
        self.setupUI()
        self.setupConnections()

    def setupUI(self):
        self.setWindowTitle("Hệ thống Quản lý Điểm danh")
        self.setGeometry(100, 100, 1200, 800)

        # Modern styling
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 #F8FAFC, stop:1 #E2E8F0);
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.dashboard = DashboardWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.dashboard)
        layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(layout)

    def setupConnections(self):
        self.dashboard.moduleSelected.connect(self.onModuleSelected)

    def onModuleSelected(self, module_name):
        print(f"[DEBUG] Đã chọn module: {module_name}")

        if module_name in self.module_windows:
            existing_window = self.module_windows[module_name]
            if existing_window and not existing_window.isVisible():
                del self.module_windows[module_name]
            else:
                existing_window.raise_()
                existing_window.activateWindow()
                return

        # Tạo cửa sổ mới
        window = self.createModuleWindow(module_name)
        if window:
            # 👉 RẤT QUAN TRỌNG: giữ tham chiếu
            self.module_windows[module_name] = window

            # 👇 Đặt thuộc tính tránh bị garbage collect
            window.setAttribute(Qt.WA_DeleteOnClose, False)

            window.show()
            print(f"[DEBUG] Đã mở cửa sổ Placeholder cho: {module_name}")

    def createModuleWindow(self, module_name):
        """Tạo cửa sổ cho module tương ứng"""
        window = None

        try:
            if module_name == "Quản lý Sinh viên" and StudentManagementUI:
                window = StudentManagementUI()
            # elif module_name == "Quản lý Giảng viên" and TeacherManagementUI:
            #     window = TeacherManagementUI()
            # elif module_name == "Quản lý Điểm danh" and AttendanceManagementUI:
            #     window = AttendanceManagementUI()
            # elif module_name == "Quản lý Buổi học" and SessionManagementUI:
            #     window = SessionManagementUI()
            # elif module_name == "Quản lý Môn học" and CourseManagementUI:
            #     window = CourseManagementUI()
            # elif module_name == "Xem ảnh" and ImageViewerUI:
            #     window = ImageViewerUI()
            else:
                # Tạo placeholder UI nếu module chưa được implement
                window = PlaceholderUI(module_name)

        except Exception as e:
            print(f"Lỗi khi tạo cửa sổ cho {module_name}: {e}")
            # Tạo placeholder UI trong trường hợp lỗi
            window = PlaceholderUI(module_name)

        return window

    def closeEvent(self, event):
        """Xử lý khi đóng ứng dụng chính"""
        # Đóng tất cả các cửa sổ con
        for window in list(self.module_windows.values()):
            if window and window.isVisible():
                window.close()

        event.accept()


def main():
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Hệ thống Quản lý Điểm danh")
    app.setApplicationVersion("1.0")

    # Create and show main window
    main_window = AttendanceManagerUI()
    main_window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())