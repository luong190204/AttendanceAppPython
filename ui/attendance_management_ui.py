import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QHeaderView,
    QGroupBox, QFileDialog, QMessageBox, QAbstractItemView
)
from PyQt5.QtCore import QTimer, QTime, QDate, Qt
from PyQt5.QtGui import QPixmap, QFont, QPalette, QColor

from database.attendance_repository import AttendanceRepository


class AttendanceManagementUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý thông tin điểm danh")
        self.setGeometry(100, 100, 1200, 700)
        self.attendance = AttendanceRepository()
        self.init_ui()
        self.setup_styles()
        self.setup_connections()

    def setup_styles(self):
        """Thiết lập styles cho giao diện đẹp mắt"""
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }

            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2c3e50;
                font-size: 14px;
            }

            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
                background-color: white;
            }

            QLineEdit:focus {
                border-color: #3498db;
            }

            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }

            QPushButton:hover {
                background-color: #2980b9;
            }

            QPushButton:pressed {
                background-color: #21618c;
            }

            QPushButton#deleteBtn {
                background-color: #e74c3c;
            }

            QPushButton#deleteBtn:hover {
                background-color: #c0392b;
            }

            QPushButton#updateBtn {
                background-color: #27ae60;
            }

            QPushButton#updateBtn:hover {
                background-color: #229954;
            }

            QPushButton#viewImageBtn {
                background-color: #f39c12;
            }

            QPushButton#viewImageBtn:hover {
                background-color: #e67e22;
            }

            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                selection-background-color: #3498db;
                gridline-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }

            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }

            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }

            QComboBox {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
                min-width: 120px;
            }

            QComboBox:focus {
                border-color: #3498db;
            }

            QLabel {
                color: #2c3e50;
                font-weight: bold;
            }

            QLabel#timeLabel {
                font-size: 16px;
                color: #27ae60;
                background-color: white;
                border: 2px solid #27ae60;
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 10px;
            }
        """)

    def init_ui(self):
        main_layout = QHBoxLayout()

        # ==== BÊN TRÁI ====
        left_panel = QVBoxLayout()

        # Đồng hồ với style đẹp
        self.time_label = QLabel()
        self.time_label.setObjectName("timeLabel")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.update_time()
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        left_panel.addWidget(self.time_label)

        # Nhóm cập nhật điểm danh
        group_box = QGroupBox("Cập Nhật Điểm Danh")
        form_layout = QVBoxLayout()

        self.inputs = {}
        labels = [
            "ID Điểm danh", "Mã buổi học", "Mã sinh viên",
            "Thời gian", "Trạng thái", "Hình ảnh"
        ]

        for label_text in labels:
            row_layout = QHBoxLayout()
            label = QLabel(label_text + ":")
            label.setFixedWidth(120)
            line_edit = QLineEdit()
            line_edit.setFixedHeight(35)
            self.inputs[label_text] = line_edit
            row_layout.addWidget(label)
            row_layout.addWidget(line_edit)
            form_layout.addLayout(row_layout)

        # Spacer
        form_layout.addSpacing(10)

        # Nút Cập nhật / Làm mới
        action_buttons = QHBoxLayout()
        self.btn_update = QPushButton("Cập nhật")
        self.btn_update.setObjectName("updateBtn")
        self.btn_update.setFixedHeight(35)

        self.btn_refresh = QPushButton("Làm mới")
        self.btn_refresh.setFixedHeight(35)

        action_buttons.addWidget(self.btn_update)
        action_buttons.addWidget(self.btn_refresh)
        form_layout.addLayout(action_buttons)

        # Spacer
        form_layout.addSpacing(10)

        # Nút xem ảnh và xóa
        self.btn_view_image = QPushButton("Xem ảnh")
        self.btn_view_image.setObjectName("viewImageBtn")
        self.btn_view_image.setFixedHeight(35)

        self.btn_delete = QPushButton("Xóa")
        self.btn_delete.setObjectName("deleteBtn")
        self.btn_delete.setFixedHeight(35)

        form_layout.addWidget(self.btn_view_image)
        form_layout.addWidget(self.btn_delete)

        group_box.setLayout(form_layout)
        left_panel.addWidget(group_box)

        # Thêm stretch để căn layout
        left_panel.addStretch()

        # ==== BÊN PHẢI ====
        right_panel = QVBoxLayout()

        # Thanh tìm kiếm với style đẹp
        search_group = QGroupBox("Tìm Kiếm & Lọc")
        search_layout = QHBoxLayout()

        self.search_field = QComboBox()
        self.search_field.addItems(["ID Điểm danh", "Mã sinh viên", "Mã buổi học"])
        self.search_field.setFixedHeight(35)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập từ khóa tìm kiếm...")
        self.search_input.setFixedHeight(35)

        self.btn_search = QPushButton("Tìm kiếm")
        self.btn_search.setFixedHeight(35)

        self.btn_today = QPushButton("Hôm nay")
        self.btn_today.setFixedHeight(35)

        self.btn_view_all = QPushButton("Xem tất cả")
        self.btn_view_all.setFixedHeight(35)

        search_layout.addWidget(QLabel("Tìm theo:"))
        search_layout.addWidget(self.search_field)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btn_search)
        search_layout.addWidget(self.btn_today)
        search_layout.addWidget(self.btn_view_all)

        search_group.setLayout(search_layout)
        right_panel.addWidget(search_group)

        # Bảng điểm danh với style đẹp
        table_group = QGroupBox("Danh Sách Điểm Danh")
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(6)  # Bỏ cột hình ảnh
        self.table.setHorizontalHeaderLabels([
            "ID Điểm Danh", "Mã Buổi Học", "Mã Sinh Viên",
            "Thời Gian", "Trạng Thái", "Hình ảnh"
        ])

        # Cải thiện table
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.verticalHeader().setVisible(False)

        # Load dữ liệu
        self.load_all_attendance()

        table_layout.addWidget(self.table)
        table_group.setLayout(table_layout)
        right_panel.addWidget(table_group)

        # ==== Gộp layout tổng ====
        main_layout.addLayout(left_panel, 3)
        main_layout.addLayout(right_panel, 7)

        self.setLayout(main_layout)

    def setup_connections(self):
        """Thiết lập các kết nối sự kiện"""
        self.btn_view_image.clicked.connect(self.view_image)
        self.btn_refresh.clicked.connect(self.clear_inputs)
        self.btn_search.clicked.connect(self.search_attendance)
        self.btn_today.clicked.connect(self.show_today_attendance)
        self.btn_view_all.clicked.connect(self.load_all_attendance)
        self.table.cellClicked.connect(self.on_table_cell_clicked)

    def search_attendance(self):
        """ Tìm kiếm dựa trên tiêu chí chọn"""
        field = self.search_field.currentText()
        value = self.search_input.text().strip()
        print("DEBUG: ", value)
        if not value:
            QMessageBox.information(self, "Thông báo", "Vui lòng nhập từ khóa tìm kiếm!")
            return

        try:
            if field == "ID Điểm danh":
                attendance = self.attendance.get_attendance_by_id(value)
                if attendance:
                    self.populate_table(attendance)
                else:
                    self.populate_table(None)
                    QMessageBox.information(self, "Thông báo", "Không tìm thấy điểm danh với ID này!")
            elif field == "Mã sinh viên":
                attendance = self.attendance.get_attendance_by_student_id(value)
                if attendance:
                    self.populate_table(attendance)
                else:
                    self.populate_table(None)
                    QMessageBox.information(self, "Thông báo", "Không tìm thấy dữ liệu điểm danh cho sinh viên này!")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi tìm kiếm: {str(e)}")

    def load_all_attendance(self):
        """Load tất cả dữ liệu điểm danh"""
        try:
            records = self.attendance.get_all_attendance()
            self.populate_table(records)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải dữ liệu: {str(e)}")

    def populate_table(self, records):
        """Điền dữ liệu vào bảng"""
        if records is None:
            self.table.setRowCount(0)
            return
        self.table.setRowCount(len(records))
        for i, record in enumerate(records):
            self.table.setItem(i, 0, QTableWidgetItem(str(record["ID_DiemDanh"])))
            self.table.setItem(i, 1, QTableWidgetItem(str(record["MaBuoiHoc_FK"])))
            self.table.setItem(i, 2, QTableWidgetItem(str(record["MaSV_FK"])))

            # Format thời gian
            if hasattr(record["ThoiGian"], 'strftime'):
                thoigian_str = record["ThoiGian"].strftime("%H:%M:%S %d/%m/%Y")
            else:
                thoigian_str = str(record["ThoiGian"])

            self.table.setItem(i, 3, QTableWidgetItem(thoigian_str))
            self.table.setItem(i, 4, QTableWidgetItem(str(record["TrangThai"])))
            self.table.setItem(i, 5, QTableWidgetItem(str(record["HinhAnh"])))

            # Ân cột hình ảnh
            self.table.setColumnHidden(5, True)
    def on_table_cell_clicked(self, row, column):
        """Xử lý khi click vào cell trong bảng"""
        if row < self.table.rowCount():
            # Lấy dữ liệu từ row được chọn
            id_diemdanh = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
            ma_buoihoc = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
            ma_sv = self.table.item(row, 2).text() if self.table.item(row, 2) else ""
            thoi_gian = self.table.item(row, 3).text() if self.table.item(row, 3) else ""
            trang_thai = self.table.item(row, 4).text() if self.table.item(row, 4) else ""
            hinh_anh = self.table.item(row, 5).text() if self.table.item(row, 5) else ""
            # Điền vào các input
            self.inputs["ID Điểm danh"].setText(id_diemdanh)
            self.inputs["Mã buổi học"].setText(ma_buoihoc)
            self.inputs["Mã sinh viên"].setText(ma_sv)
            self.inputs["Thời gian"].setText(thoi_gian)
            self.inputs["Trạng thái"].setText(trang_thai)
            self.inputs["Hình ảnh"].setText(hinh_anh)

    def update_time(self):
        """Cập nhật thời gian hiện tại"""
        now = QTime.currentTime()
        date = QDate.currentDate()
        time_str = now.toString("hh:mm:ss")
        date_str = date.toString("dd/MM/yyyy")
        self.time_label.setText(f"🕐 {time_str}\n📅 {date_str}")

    def view_image(self):
        """Xem ảnh điểm danh"""
        # Lấy thông tin từ input
        image_path = self.inputs["Hình ảnh"].text().strip()
        ma_sv = self.inputs["Mã sinh viên"].text().strip()

        if not image_path or not os.path.exists(image_path):
            QMessageBox.warning(self, "Thông báo", f"Không tìm thấy ảnh tại: {image_path}")
            return

        try:
            self.show_image_window(image_path, ma_sv)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể hiển thị ảnh: {str(e)}")

    def show_image_window(self, image_path, ma_sv):
        """Hiển thị cửa sổ ảnh"""
        self.img_window = QWidget()
        self.img_window.setWindowTitle(f"Ảnh điểm danh - {ma_sv}")
        self.img_window.setGeometry(200, 200, 500, 600)

        layout = QVBoxLayout()

        # Label hiển thị ảnh
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)

        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(450, 450, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(scaled_pixmap)
            else:
                image_label.setText("Không thể tải ảnh")
        except Exception as e:
            image_label.setText(f"Lỗi: {str(e)}")

        # Label thông tin
        info_label = QLabel(f"Đường dẫn: {image_path}")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #7f8c8d; font-size: 10px; padding: 10px;")

        layout.addWidget(image_label)
        layout.addWidget(info_label)

        self.img_window.setLayout(layout)
        self.img_window.show()

    def clear_inputs(self):
        """Xóa tất cả input"""
        for input_field in self.inputs.values():
            input_field.clear()

    def show_today_attendance(self):
        """Hiển thị điểm danh hôm nay"""
        try:
            # Gọi phương thức lấy điểm danh hôm nay từ repository
            #today = QDate.currentDate().toString("yyyy-MM-dd")
            records = self.attendance.get_attendance_today()
            self.populate_table(records)
            #QMessageBox.information(self, "Thông báo", "Tính năng lọc theo ngày đang được phát triển!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi lọc dữ liệu: {str(e)}")


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#
#     # Thiết lập font cho toàn bộ ứng dụng
#     font = QFont("Segoe UI", 10)
#     app.setFont(font)
#
#     window = AttendanceManagementUI()
#     window.show()
#     sys.exit(app.exec_())