# session_ui.py
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem,
    QComboBox, QDateEdit, QMessageBox, QHeaderView, QGroupBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QPalette
from database.session_repository import SessionRepository
from database.user_repository import UserRepository
from database.class_subject_repository import ClassSubjectRepository

class SessionManagementUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý thông tin lịch học")
        self.setMinimumSize(1500, 800)
        self.session_repo = SessionRepository()
        self.user_repo = UserRepository()
        self.subject_repo = ClassSubjectRepository()
        self.init_ui()
        self.setup_styles()
        self.load_sessions()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # === Left side: Form ===
        left_widget = self.create_form_section()
        main_layout.addWidget(left_widget, 1)

        self.load_initial_data()
        # === Right side: Table ===
        right_widget = self.create_table_section()
        main_layout.addWidget(right_widget, 2)

        self.setLayout(main_layout)

    def create_form_section(self):
        form_group = QGroupBox("Thông tin buổi học")
        form_layout = QVBoxLayout()

        # Form fields
        grid = QGridLayout()
        grid.setSpacing(10)

        # Initialize input fields
        self.id_input = QLineEdit()
        self.start_time_input = QLineEdit()
        self.start_time_input.setPlaceholderText("VD: 08:00:00")
        self.end_time_input = QLineEdit()
        self.end_time_input.setPlaceholderText("VD: 10:00:00")

        self.date_input = QDateEdit()
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)

        self.teacher_id_input = QLineEdit()
        self.teacher_id_input.textChanged.connect(self.on_teacher_id_changed)
        self.teacher_name_input = QLineEdit()
        self.teacher_name_input.setReadOnly(True)
        self.teacher_name_input.setStyleSheet("background-color: #f0f0f0;")

        self.subject_id_input = QLineEdit()
        self.subject_id_input.textChanged.connect(self.on_subject_id_changed)
        self.subject_name_input = QLineEdit()
        self.subject_name_input.setReadOnly(True)
        self.subject_name_input.setStyleSheet("background-color: #f0f0f0;")

        self.classroom_input = QLineEdit()
        self.class_combo = QComboBox()
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Scheduled", "Make up class"])
        # Add fields to grid
        labels = [
            "ID Buổi học:", "Giờ bắt đầu:", "Giờ kết thúc:", "Ngày:",
            "ID Giảng viên:", "Tên Giảng viên:", "ID Môn học:", "Tên Môn học:", "Phòng Học", "Lớp Học", "Trạng thái"
        ]
        inputs = [
            self.id_input, self.start_time_input, self.end_time_input, self.date_input,
            self.teacher_id_input, self.teacher_name_input, self.subject_id_input,
            self.subject_name_input, self.classroom_input,self.class_combo ,self.status_combo
        ]

        for i, (label_text, input_widget) in enumerate(zip(labels, inputs)):
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: bold;")
            grid.addWidget(label, i, 0)
            grid.addWidget(input_widget, i, 1)

        form_layout.addLayout(grid)
        form_layout.addSpacing(20)

        # Buttons
        button_layout = QGridLayout()

        self.add_btn = QPushButton("➕ Thêm mới")
        self.update_btn = QPushButton("✏️ Cập nhật")
        self.delete_btn = QPushButton("🗑️ Xóa")
        self.clear_btn = QPushButton("🔄 Làm mới")

        # Connect button events
        self.add_btn.clicked.connect(self.add_session)
        self.update_btn.clicked.connect(self.update_session)
        self.delete_btn.clicked.connect(self.delete_session)
        self.clear_btn.clicked.connect(self.clear_fields)

        # Arrange buttons in 2x2 grid
        button_layout.addWidget(self.add_btn, 0, 0)
        button_layout.addWidget(self.update_btn, 0, 1)
        button_layout.addWidget(self.delete_btn, 1, 0)
        button_layout.addWidget(self.clear_btn, 1, 1)

        form_layout.addLayout(button_layout)
        form_layout.addStretch()

        form_group.setLayout(form_layout)
        return form_group

    def load_initial_data(self):
        """Load dữ liệu ban đầu"""
        if self.subject_repo:
            self.load_combo_data_class()

    def load_combo_data_class(self):
        """Load dữ liệu cho combobox Lớp học"""
        if not self.subject_repo:
            return

        # Load lớp học vào combo
        classCombo = self.subject_repo.get_all_classes()
        self.class_combo.clear()
        self.class_combo.addItem("-- Chọn Lớp Học --", "")
        if classCombo:
            for classes in classCombo:
                ma_lop = classes[0] if isinstance(classes, tuple) else classes['MaLop']
                ten_lop = classes[1] if isinstance(classes, tuple) else classes['TenLop']
                self.class_combo.addItem(f"{ma_lop} - {ten_lop}", ma_lop)

    def create_table_section(self):
        table_group = QGroupBox("Danh sách lịch học")
        table_layout = QVBoxLayout()

        # Search section
        search_group = QGroupBox("Tìm kiếm")
        search_layout = QHBoxLayout()

        self.search_field = QComboBox()
        self.search_field.addItems(["ID Buổi học", "ID Giảng viên"])
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập từ khóa tìm kiếm...")

        self.search_button = QPushButton("🔍 Tìm kiếm")
        self.view_all_button = QPushButton("📋 Xem tất cả")

        self.search_button.clicked.connect(self.search_sessions)
        self.view_all_button.clicked.connect(self.load_sessions)
        self.search_input.returnPressed.connect(self.search_sessions)

        search_layout.addWidget(QLabel("Tìm theo:"))
        search_layout.addWidget(self.search_field)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.view_all_button)

        search_group.setLayout(search_layout)
        table_layout.addWidget(search_group)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "ID Buổi học", "Giờ bắt đầu", "Giờ kết thúc", "Ngày",
            "ID GV", "Tên GV", "ID MH", "Tên MH", "Phòng học", "Lớp học", "Trạng thái"
        ])

        # Table styling
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.cellClicked.connect(self.table_item_clicked)

        # Set column widths
        self.table.setColumnWidth(0, 100)  # ID Buổi học
        self.table.setColumnWidth(1, 120)  # Giờ bắt đầu
        self.table.setColumnWidth(2, 120)  # Giờ kết thúc
        self.table.setColumnWidth(3, 100)  # Ngày
        self.table.setColumnWidth(4, 140)  # ID GV
        self.table.setColumnWidth(5, 120)  # Tên GV
        self.table.setColumnWidth(6, 100)  # ID MH
        self.table.setColumnWidth(7, 100)  # Tên MH
        self.table.setColumnWidth(8, 60)  # Phòng học
        self.table.setColumnWidth(9, 80) # Lớp học
        self.table.setColumnWidth(10, 120)  # Trạng thái

        # Ẩn các cột ID GV và ID MH
        self.table.setColumnHidden(4, True)
        self.table.setColumnHidden(6, True)

        table_layout.addWidget(self.table)
        table_group.setLayout(table_layout)
        return table_group

    def setup_styles(self):
        # Main window style
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2c3e50;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QLineEdit, QDateEdit, QComboBox {
                padding: 5px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                min-height: 25px;
            }
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus {
                border-color: #3498db;
            }
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)

        # Button specific colors
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)

        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)

    def on_teacher_id_changed(self):
        """Auto-fill teacher name when teacher ID changes"""
        teacher_id = self.teacher_id_input.text().strip()
        if teacher_id:
            try:
                teacher = self.user_repo.get_lecturer_by_id(teacher_id)
                if teacher:
                    self.teacher_name_input.setText(teacher.get('TenGV', ''))
                else:
                    self.teacher_name_input.setText("Không tìm thấy giảng viên")
            except:
                self.teacher_name_input.setText("")
        else:
            self.teacher_name_input.setText("")

    def on_subject_id_changed(self):
        """Auto-fill subject name when subject ID changes"""
        subject_id = self.subject_id_input.text().strip()
        if subject_id:
            try:
                subject = self.subject_repo.get_subject_by_id(subject_id)
                if subject:
                    self.subject_name_input.setText(subject.get('TenMon', ''))
                else:
                    self.subject_name_input.setText("Không tìm thấy môn học")
            except:
                self.subject_name_input.setText("")
        else:
            self.subject_name_input.setText("")

    def load_sessions(self):
        """Load all sessions to table"""
        try:
            sessions = self.session_repo.get_all_sessions()
            print("DEBUG: ", sessions)
            self.table.setRowCount(len(sessions))

            for row_idx, session in enumerate(sessions):
                # Convert session dict to list of values for display
                session_values = [
                    session.get('MaBuoiHoc', ''),
                    str(session.get('GioBatDau', '')),
                    str(session.get('GioKetThuc', '')),
                    str(session.get('NgayHoc', '')),
                    session.get('MaGV', ''),
                    session.get('TenGV', ''),
                    session.get('MaMon', ''),
                    session.get('TenMon', ''),
                    session.get('PhongHoc', ''),
                    session.get('MaLop', ''),
                    session.get('TrangThaiBuoiHoc', '')
                ]

                for col_idx, value in enumerate(session_values):
                    item = QTableWidgetItem(str(value))
                    if col_idx in [4, 8]:  # ID columns
                        item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row_idx, col_idx, item)

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải dữ liệu: {str(e)}")

    def table_item_clicked(self, row, column):
        """Fill form when table row is clicked"""
        try:
            self.id_input.setText(self.table.item(row, 0).text())
            self.start_time_input.setText(self.table.item(row, 1).text())
            self.end_time_input.setText(self.table.item(row, 2).text())

            # Parse date
            date_str = self.table.item(row, 3).text()
            if date_str:
                try:
                    # Try different date formats
                    for fmt in ["yyyy-MM-dd", "dd/MM/yyyy", "MM/dd/yyyy"]:
                        date = QDate.fromString(date_str, fmt)
                        if date.isValid():
                            self.date_input.setDate(date)
                            break
                except:
                    pass

            # Gán ID Giảng viên và tra tên
            self.teacher_id_input.setText(self.table.item(row, 4).text())
            self.on_teacher_id_changed()

            # Gán ID Môn học và tra tên
            self.subject_id_input.setText(self.table.item(row, 6).text())
            self.on_subject_id_changed()

            self.classroom_input.setText(self.table.item(row, 8).text())

            # set lại dữ liệu cho class combo
            classCombo = self.table.item(row, 9).text()
            index = self.class_combo.findData(classCombo)
            if index != -1:
                self.class_combo.setCurrentIndex(index)

            status = self.table.item(row, 10).text()
            self.status_combo.setCurrentText(status)

        except Exception as e:
            QMessageBox.warning(self, "Cảnh báo", f"Lỗi khi tải dữ liệu từ bảng: {str(e)}")

    def search_sessions(self):
        """Search sessions based on selected criteria"""
        field = self.search_field.currentText()
        value = self.search_input.text().strip()

        if not value:
            QMessageBox.information(self, "Thông báo", "Vui lòng nhập từ khóa tìm kiếm!")
            return

        try:
            if field == "ID Buổi học":
                session = self.session_repo.get_session_by_id(value)
                if session:
                    self.display_search_results([session])
                else:
                    self.display_search_results([])
                    QMessageBox.information(self, "Thông báo", "Không tìm thấy buổi học với ID này!")

            elif field == "ID Giảng viên":
                # You can implement search by teacher ID in repository
                sessions = self.session_repo.search_sessions_by_teacher_id(value)
                self.display_search_results(sessions)

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi tìm kiếm: {str(e)}")

    def display_search_results(self, sessions):
        """Display search results in table"""
        self.table.setRowCount(len(sessions))

        for row_idx, session in enumerate(sessions):
            session_values = [
                session.get('MaBuoiHoc', ''),
                str(session.get('GioBatDau', '')),
                str(session.get('GioKetThuc', '')),
                str(session.get('NgayHoc', '')),
                session.get('MaGV', ''),
                session.get('TenGV', ''),
                session.get('MaMon', ''),
                session.get('TenMon', ''),
                session.get('PhongHoc', ''),
                session.get('MaLop', ''),
                session.get('TrangThaiBuoiHoc', '')
            ]

            for col_idx, value in enumerate(session_values):
                item = QTableWidgetItem(str(value))
                if col_idx in [4, 7]:  # ID columns
                    item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

    def validate_input(self):
        """Validate form input"""
        if not self.id_input.text().strip():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập ID buổi học!")
            return False

        if not self.start_time_input.text().strip():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập giờ bắt đầu!")
            return False

        if not self.end_time_input.text().strip():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập giờ kết thúc!")
            return False

        if not self.teacher_id_input.text().strip():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập ID giảng viên!")
            return False

        if not self.subject_id_input.text().strip():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập ID môn học!")
            return False

        # Validate teacher and subject exist
        if self.teacher_name_input.text() == "Không tìm thấy giảng viên":
            QMessageBox.warning(self, "Cảnh báo", "ID giảng viên không tồn tại!")
            return False

        if self.subject_name_input.text() == "Không tìm thấy môn học":
            QMessageBox.warning(self, "Cảnh báo", "ID môn học không tồn tại!")
            return False

        return True

    def add_session(self):
        """Add new session"""
        if not self.validate_input():
            return

        try:
            self.session_repo.add_session(
                self.id_input.text().strip(),
                self.start_time_input.text().strip(),
                self.end_time_input.text().strip(),
                self.date_input.date().toString("yyyy-MM-dd"),
                self.teacher_id_input.text().strip(),
                self.subject_id_input.text().strip(),
                self.classroom_input.text().strip(),
                self.class_combo.currentData(),
                self.status_combo.currentText().strip()
            )

            QMessageBox.information(self, "Thành công", "Thêm buổi học thành công!")
            self.load_sessions()
            self.clear_fields()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể thêm buổi học: {str(e)}")

    def update_session(self):
        """Update existing session"""
        if not self.validate_input():
            return

        try:
            self.session_repo.update_session(
                self.id_input.text().strip(),
                self.start_time_input.text().strip(),
                self.end_time_input.text().strip(),
                self.date_input.date().toString("yyyy-MM-dd"),
                self.teacher_id_input.text().strip(),
                self.subject_id_input.text().strip(),
                self.classroom_input.text().strip(),
                self.class_combo.currentData(),
                self.status_combo.currentText()
            )

            QMessageBox.information(self, "Thành công", "Cập nhật buổi học thành công!")
            self.load_sessions()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật buổi học: {str(e)}")

    def delete_session(self):
        """Delete session"""
        if not self.id_input.text().strip():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập ID buổi học cần xóa!")
            return

        reply = QMessageBox.question(
            self, "Xác nhận",
            f"Bạn có chắc chắn muốn xóa buổi học '{self.id_input.text()}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.session_repo.delete_session(self.id_input.text().strip())
                QMessageBox.information(self, "Thành công", "Xóa buổi học thành công!")
                self.load_sessions()
                self.clear_fields()

            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa buổi học: {str(e)}")

    def clear_fields(self):
        """Clear all form fields"""
        self.id_input.clear()
        self.start_time_input.clear()
        self.end_time_input.clear()
        self.teacher_id_input.clear()
        self.teacher_name_input.clear()
        self.subject_id_input.clear()
        self.subject_name_input.clear()
        self.date_input.setDate(QDate.currentDate())
        self.search_input.clear()
        self.classroom_input.clear()