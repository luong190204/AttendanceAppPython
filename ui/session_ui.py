from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem,
    QComboBox, QDateEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from database.session_repository import SessionRepository

class SessionManagementUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý thông tin lịch học")
        self.session_repo = SessionRepository()

        self.init_ui()
        self.load_sessions()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # === Left side: Form ===
        form_layout = QVBoxLayout()

        title = QLabel("Thông tin buổi học")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 16px; color: purple;")
        form_layout.addWidget(title)

        grid = QGridLayout()

        self.id_input = QLineEdit()
        self.start_time_input = QLineEdit()
        self.end_time_input = QLineEdit()
        self.date_input = QDateEdit()
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        self.date_input.setDate(QDate.currentDate())

        self.teacher_id_input = QLineEdit()
        self.teacher_name_input = QLineEdit()
        self.subject_id_input = QLineEdit()
        self.subject_name_input = QLineEdit()

        grid.addWidget(QLabel("ID Buổi học:"), 0, 0)
        grid.addWidget(self.id_input, 0, 1)
        grid.addWidget(QLabel("Giờ bắt đầu:"), 1, 0)
        grid.addWidget(self.start_time_input, 1, 1)
        grid.addWidget(QLabel("Giờ kết thúc:"), 2, 0)
        grid.addWidget(self.end_time_input, 2, 1)
        grid.addWidget(QLabel("Ngày:"), 3, 0)
        grid.addWidget(self.date_input, 3, 1)
        grid.addWidget(QLabel("ID Giảng viên:"), 4, 0)
        grid.addWidget(self.teacher_id_input, 4, 1)
        grid.addWidget(QLabel("Tên Giảng viên:"), 5, 0)
        grid.addWidget(self.teacher_name_input, 5, 1)
        grid.addWidget(QLabel("ID Môn học:"), 6, 0)
        grid.addWidget(self.subject_id_input, 6, 1)
        grid.addWidget(QLabel("Tên Môn học:"), 7, 0)
        grid.addWidget(self.subject_name_input, 7, 1)

        form_layout.addLayout(grid)

        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Thêm mới")
        self.delete_btn = QPushButton("Xóa")
        self.update_btn = QPushButton("Cập nhật")
        self.clear_btn = QPushButton("Làm mới")

        self.add_btn.clicked.connect(self.add_session)
        self.update_btn.clicked.connect(self.update_session)
        self.delete_btn.clicked.connect(self.delete_session)
        self.clear_btn.clicked.connect(self.clear_fields)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.update_btn)
        button_layout.addWidget(self.clear_btn)
        form_layout.addLayout(button_layout)

        main_layout.addLayout(form_layout, 1)

        # === Right side: Table ===
        right_layout = QVBoxLayout()
        search_layout = QHBoxLayout()

        self.search_field = QComboBox()
        self.search_field.addItems(["ID Buổi học", "ID Giảng viên", "ID Môn học"])
        self.search_input = QLineEdit()
        self.search_button = QPushButton("Tìm kiếm")
        self.view_all_button = QPushButton("Xem tất cả")

        self.search_button.clicked.connect(self.search_sessions)
        self.view_all_button.clicked.connect(self.load_sessions)

        search_layout.addWidget(QLabel("Tìm kiếm theo:"))
        search_layout.addWidget(self.search_field)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.view_all_button)

        right_layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID Buổi học", "Giờ bắt đầu", "Giờ kết thúc", "Ngày", "ID Giảng viên", "ID Môn học"])
        self.table.cellClicked.connect(self.table_item_clicked)

        right_layout.addWidget(self.table)
        main_layout.addLayout(right_layout, 2)

        self.setLayout(main_layout)

    def load_sessions(self):
        sessions = self.session_repo.get_all_sessions()
        self.table.setRowCount(0)
        for row_data in sessions:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            for col_idx, value in enumerate(row_data[:6]):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def table_item_clicked(self, row, column):
        self.id_input.setText(self.table.item(row, 0).text())
        self.start_time_input.setText(self.table.item(row, 1).text())
        self.end_time_input.setText(self.table.item(row, 2).text())
        date = QDate.fromString(self.table.item(row, 3).text(), "dd/MM/yyyy")
        self.date_input.setDate(date)
        self.teacher_id_input.setText(self.table.item(row, 4).text())
        self.subject_id_input.setText(self.table.item(row, 5).text())

    def search_sessions(self):
        field = self.search_field.currentText()
        value = self.search_input.text().strip()
        if not value:
            return

        if field == "ID Buổi học":
            session = self.session_repo.get_session_by_id(value)
            if session:
                self.table.setRowCount(1)
                for col_idx, val in enumerate(session[:6]):
                    self.table.setItem(0, col_idx, QTableWidgetItem(str(val)))
            else:
                self.table.setRowCount(0)
        else:
            QMessageBox.information(self, "Thông báo", "Tính năng tìm kiếm này chưa được hỗ trợ hoàn chỉnh.")

    def add_session(self):
        try:
            self.session_repo.add_session(
                self.id_input.text(),
                self.start_time_input.text(),
                self.end_time_input.text(),
                self.date_input.date().toString("yyyy-MM-dd"),
                self.teacher_id_input.text(),
                self.subject_id_input.text()
            )
            self.load_sessions()
            self.clear_fields()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def update_session(self):
        try:
            self.session_repo.update_session(
                self.id_input.text(),
                self.start_time_input.text(),
                self.end_time_input.text(),
                self.date_input.date().toString("yyyy-MM-dd"),
                self.teacher_id_input.text(),
                self.subject_id_input.text()
            )
            self.load_sessions()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def delete_session(self):
        try:
            self.session_repo.delete_session(self.id_input.text())
            self.load_sessions()
            self.clear_fields()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def clear_fields(self):
        self.id_input.clear()
        self.start_time_input.clear()
        self.end_time_input.clear()
        self.teacher_id_input.clear()
        self.teacher_name_input.clear()
        self.subject_id_input.clear()
        self.subject_name_input.clear()
        self.date_input.setDate(QDate.currentDate())
