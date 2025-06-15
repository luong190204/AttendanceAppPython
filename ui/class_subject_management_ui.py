# python -m ui.class_subject_management_ui
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
                             QHBoxLayout, QGridLayout, QComboBox, QTableWidget,
                             QTableWidgetItem, QListWidget, QApplication, QGroupBox,
                             QMessageBox, QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette
from database.class_subject_repository import ClassSubjectRepository
from database.student_repository import StudentRepository
class ClassSubjectManagementUI(QWidget):
    def __init__(self):
        super().__init__()
        self.db_manager = ClassSubjectRepository()  # Nhận db_manager từ ClassSubjectRepository
        self.student_repo = StudentRepository()
        self.setWindowTitle("Quản lý Môn học và Lớp học")
        self.resize(1200, 800)
        self.init_ui()
        self.setup_styling()
        self.load_initial_data()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # --- PHẦN TRÊN: Thông tin môn học ---
        main_layout.addWidget(self.build_subject_info_section())

        # --- PHẦN DƯỚI: 2 khối song song ---
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)
        bottom_layout.addWidget(self.build_class_info_section())
        bottom_layout.addWidget(self.build_student_subject_class_section())
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def build_subject_info_section(self):
        group = QGroupBox("📚 Thông tin Môn học")
        group.setFont(QFont("Arial", 10, QFont.Bold))
        layout = QGridLayout()
        layout.setSpacing(8)

        # Input fields cho môn học
        self.ma_mon = QLineEdit()
        self.ma_mon.setPlaceholderText("Nhập mã môn học...")
        self.ten_mon = QLineEdit()
        self.ten_mon.setPlaceholderText("Nhập tên môn học...")
        self.so_tc = QLineEdit()
        self.so_tc.setPlaceholderText("Nhập số tín chỉ...")

        # Search components
        self.subject_search_combo = QComboBox()
        self.subject_search_combo.addItems(["Mã môn học", "Tên môn học"])
        self.subject_search_input = QLineEdit()
        self.subject_search_input.setPlaceholderText("Nhập từ khóa tìm kiếm...")

        # Table
        self.subject_table = QTableWidget(0, 3)
        self.subject_table.setHorizontalHeaderLabels(["Mã môn học", "Tên môn học", "Số tín chỉ"])
        self.subject_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.subject_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.subject_table.setAlternatingRowColors(True)
        self.subject_table.itemClicked.connect(self.on_subject_row_clicked)

        # Layout setup
        layout.addWidget(QLabel("Mã môn học:"), 0, 0)
        layout.addWidget(self.ma_mon, 0, 1)
        layout.addWidget(QLabel("Tên môn học:"), 1, 0)
        layout.addWidget(self.ten_mon, 1, 1)
        layout.addWidget(QLabel("Số tín chỉ:"), 2, 0)
        layout.addWidget(self.so_tc, 2, 1)

        # Buttons for subjects
        subject_btn_layout = QHBoxLayout()
        self.btn_add_subject = QPushButton("➕ Thêm mới")
        self.btn_delete_subject = QPushButton("🗑️ Xóa")
        self.btn_update_subject = QPushButton("✏️ Cập nhật")
        self.btn_refresh_subject = QPushButton("🔄 Làm mới")

        # Connect buttons
        self.btn_add_subject.clicked.connect(self.add_subject)
        self.btn_delete_subject.clicked.connect(self.delete_subject)
        self.btn_update_subject.clicked.connect(self.update_subject)
        self.btn_refresh_subject.clicked.connect(self.refresh_subjects)

        for btn in [self.btn_add_subject, self.btn_delete_subject, self.btn_update_subject, self.btn_refresh_subject]:
            subject_btn_layout.addWidget(btn)
        layout.addLayout(subject_btn_layout, 3, 0, 1, 2)

        # Search section
        layout.addWidget(QLabel("Tìm kiếm theo:"), 0, 2)
        layout.addWidget(self.subject_search_combo, 0, 3)
        layout.addWidget(self.subject_search_input, 1, 3)

        self.btn_search_subject = QPushButton("🔍 Tìm kiếm")
        self.btn_view_all_subjects = QPushButton("👁️ Xem tất cả")
        self.btn_search_subject.clicked.connect(self.search_subjects)
        self.btn_view_all_subjects.clicked.connect(self.load_all_subjects)

        layout.addWidget(self.btn_search_subject, 2, 3)
        layout.addWidget(self.btn_view_all_subjects, 3, 3)

        layout.addWidget(self.subject_table, 4, 0, 1, 4)
        group.setLayout(layout)
        return group

    def build_class_info_section(self):
        group = QGroupBox("🏫 Thông tin Lớp học")
        group.setFont(QFont("Arial", 10, QFont.Bold))
        layout = QGridLayout()
        layout.setSpacing(8)

        # Input fields cho lớp học
        self.ma_lop = QLineEdit()
        self.ma_lop.setPlaceholderText("Nhập mã lớp...")
        self.ten_lop = QLineEdit()
        self.ten_lop.setPlaceholderText("Nhập tên lớp...")
        self.khoa = QLineEdit()
        self.khoa.setPlaceholderText("Nhập tên khoa...")

        # List widget
        self.class_list = QListWidget()
        self.class_list.itemClicked.connect(self.on_class_item_clicked)

        layout.addWidget(QLabel("Mã lớp học:"), 0, 0)
        layout.addWidget(self.ma_lop, 0, 1)
        layout.addWidget(QLabel("Tên lớp học:"), 1, 0)
        layout.addWidget(self.ten_lop, 1, 1)
        layout.addWidget(QLabel("Khoa:"), 2, 0)
        layout.addWidget(self.khoa, 2, 1)

        # Buttons
        self.btn_search_class = QPushButton("🔍 Tìm kiếm")
        self.btn_view_all_classes = QPushButton("👁️ Xem tất cả")
        self.btn_search_class.clicked.connect(self.search_classes)
        self.btn_view_all_classes.clicked.connect(self.load_all_classes)

        layout.addWidget(self.btn_search_class, 0, 2)
        layout.addWidget(self.btn_view_all_classes, 1, 2)
        layout.addWidget(self.class_list, 2, 2, 2, 1)

        # Class management buttons
        class_btn_layout = QHBoxLayout()
        self.btn_add_class = QPushButton("➕ Thêm mới")
        self.btn_delete_class = QPushButton("🗑️ Xóa")
        self.btn_update_class = QPushButton("✏️ Cập nhật")
        self.btn_refresh_class = QPushButton("🔄 Làm mới")

        # Connect buttons
        self.btn_add_class.clicked.connect(self.add_class)
        self.btn_delete_class.clicked.connect(self.delete_class)
        self.btn_update_class.clicked.connect(self.update_class)
        self.btn_refresh_class.clicked.connect(self.refresh_classes)

        for btn in [self.btn_add_class, self.btn_delete_class, self.btn_update_class, self.btn_refresh_class]:
            class_btn_layout.addWidget(btn)
        layout.addLayout(class_btn_layout, 4, 0, 1, 3)

        group.setLayout(layout)
        return group

    def build_student_subject_class_section(self):
        group = QGroupBox("👨‍🎓 Gán Sinh viên - Môn học - Lớp học")
        group.setFont(QFont("Arial", 10, QFont.Bold))
        layout = QGridLayout()
        layout.setSpacing(8)

        # Input fields
        self.ma_sv_assign = QLineEdit()
        self.ma_sv_assign.setPlaceholderText("Nhập mã sinh viên...")
        self.ten_sv_display = QLineEdit()
        self.ten_sv_display.setReadOnly(True)
        self.ten_sv_display.setPlaceholderText("Tên sinh viên sẽ hiển thị tại đây...")
        self.ma_mon_assign = QComboBox()
        self.ma_lop_assign = QComboBox()

        # List widget
        self.assignment_list = QListWidget()

        layout.addWidget(QLabel("Mã Sinh viên:"), 0, 0)
        layout.addWidget(self.ma_sv_assign, 0, 1)
        layout.addWidget(QLabel("Tên SV:"), 1, 0)
        layout.addWidget(self.ten_sv_display, 1, 1)
        layout.addWidget(QLabel("Môn học:"), 2, 0)
        layout.addWidget(self.ma_mon_assign, 2, 1)
        layout.addWidget(QLabel("Lớp học:"), 3, 0)
        layout.addWidget(self.ma_lop_assign, 3, 1)

        # Buttons
        self.btn_search_assignment = QPushButton("🔍 Tìm kiếm")
        self.btn_view_all_assignments = QPushButton("👁️ Xem tất cả")
        self.btn_search_assignment.clicked.connect(self.search_assignments)
        self.btn_view_all_assignments.clicked.connect(self.load_all_assignments)

        layout.addWidget(self.btn_search_assignment, 0, 2)
        layout.addWidget(self.btn_view_all_assignments, 1, 2)
        layout.addWidget(self.assignment_list, 2, 2, 2, 1)

        # Assignment management buttons
        assign_btn_layout = QHBoxLayout()
        self.btn_add_assignment = QPushButton("➕ Gán")
        self.btn_remove_assignment = QPushButton("🗑️ Hủy gán")
        self.btn_refresh_assignment = QPushButton("🔄 Làm mới")

        # Connect buttons
        self.btn_add_assignment.clicked.connect(self.add_assignment)
        self.btn_remove_assignment.clicked.connect(self.remove_assignment)
        self.btn_refresh_assignment.clicked.connect(self.refresh_assignments)

        # Connect ma_sv_assign text change to lookup student name
        self.ma_sv_assign.editingFinished.connect(self.lookup_student_name)

        for btn in [self.btn_add_assignment, self.btn_remove_assignment, self.btn_refresh_assignment]:
            assign_btn_layout.addWidget(btn)
        layout.addLayout(assign_btn_layout, 4, 0, 1, 3)

        group.setLayout(layout)
        return group

    def setup_styling(self):
        # Thiết lập style cho toàn bộ widget
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 9pt;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin: 10px 0px;
                padding-top: 15px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QLineEdit, QComboBox {
                padding: 6px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #3498db;
            }
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
                alternate-background-color: #ecf0f1;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QListWidget {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                alternate-background-color: #ecf0f1;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)

    def load_initial_data(self):
        """Load dữ liệu ban đầu"""
        if self.db_manager:
            self.load_all_subjects()
            self.load_all_classes()
            self.load_combo_data()

    def load_combo_data(self):
        """Load dữ liệu cho các combobox"""
        if not self.db_manager:
            return

        # Load môn học vào combo
        subjects = self.db_manager.get_all_subjects()
        self.ma_mon_assign.clear()
        self.ma_mon_assign.addItem("-- Chọn môn học --", "")
        if subjects:
            for subject in subjects:
                ma_mon = subject[0] if isinstance(subject, tuple) else subject['MaMon']
                ten_mon = subject[1] if isinstance(subject, tuple) else subject['TenMon']
                self.ma_mon_assign.addItem(f"{ma_mon} - {ten_mon}", ma_mon)

        # Load lớp học vào combo
        classes = self.db_manager.get_all_classes()
        self.ma_lop_assign.clear()
        self.ma_lop_assign.addItem("-- Chọn lớp học --", "")
        if classes:
            for class_item in classes:
                ma_lop = class_item[0] if isinstance(class_item, tuple) else class_item['MaLop']
                ten_lop = class_item[1] if isinstance(class_item, tuple) else class_item['TenLop']
                self.ma_lop_assign.addItem(f"{ma_lop} - {ten_lop}", ma_lop)

    # ====== SUBJECT MANAGEMENT METHODS ======
    def load_all_subjects(self):
        """Load tất cả môn học vào table"""
        if not self.db_manager:
            return

        subjects = self.db_manager.get_all_subjects()
        self.populate_subject_table(subjects)

    def populate_subject_table(self, subjects):
        """Điền dữ liệu vào bảng môn học"""
        if not subjects:
            self.subject_table.setRowCount(0)
            return

        self.subject_table.setRowCount(len(subjects))
        for row, subject in enumerate(subjects):
            if isinstance(subject, tuple):
                ma_mon, ten_mon, so_tc = subject
            else:
                ma_mon = subject['MaMon']
                ten_mon = subject['TenMon']
                so_tc = subject['SoTinChi']

            self.subject_table.setItem(row, 0, QTableWidgetItem(str(ma_mon)))
            self.subject_table.setItem(row, 1, QTableWidgetItem(str(ten_mon)))
            self.subject_table.setItem(row, 2, QTableWidgetItem(str(so_tc)))

    def on_subject_row_clicked(self, item):
        """Xử lý khi click vào dòng trong bảng môn học"""
        row = item.row()
        ma_mon = self.subject_table.item(row, 0).text()
        ten_mon = self.subject_table.item(row, 1).text()
        so_tc = self.subject_table.item(row, 2).text()

        self.ma_mon.setText(ma_mon)
        self.ten_mon.setText(ten_mon)
        self.so_tc.setText(so_tc)

    def add_subject(self):
        """Thêm môn học mới"""
        if not self.db_manager:
            self.show_message("Lỗi", "Không có kết nối database!")
            return

        ma_mon = self.ma_mon.text().strip()
        ten_mon = self.ten_mon.text().strip()
        so_tc = self.so_tc.text().strip()

        if not all([ma_mon, ten_mon, so_tc]):
            self.show_message("Lỗi", "Vui lòng điền đầy đủ thông tin!")
            return

        try:
            so_tc = int(so_tc)
            if so_tc <= 0:
                self.show_message("Lỗi", "Số tín chỉ phải là số dương!")
                return
        except ValueError:
            self.show_message("Lỗi", "Số tín chỉ phải là số!")
            return

        try:
            if self.db_manager.add_subject(ma_mon, ten_mon, so_tc):
                self.show_message("Thành công", "Thêm môn học thành công!")
                self.clear_subject_fields()

                # Bao thêm log để debug
                print("Đang load lại danh sách môn học...")
                self.load_all_subjects()
                print("Đang load lại dữ liệu ComboBox...")
                self.load_combo_data()
            else:
                self.show_message("Lỗi", "Không thể thêm môn học!")
        except Exception as e:
            import traceback
            traceback.print_exc()  # In lỗi ra console
            self.show_message("Lỗi nghiêm trọng", f"Đã xảy ra lỗi: {str(e)}")

    def update_subject(self):
        """Cập nhật môn học"""
        if not self.db_manager:
            self.show_message("Lỗi", "Không có kết nối database!")
            return

        ma_mon = self.ma_mon.text().strip()
        ten_mon = self.ten_mon.text().strip()
        so_tc = self.so_tc.text().strip()

        if not all([ma_mon, ten_mon, so_tc]):
            self.show_message("Lỗi", "Vui lòng điền đầy đủ thông tin!")
            return

        try:
            so_tc = int(so_tc)
            if so_tc <= 0:
                self.show_message("Lỗi", "Số tín chỉ phải là số dương!")
                return
        except ValueError:
            self.show_message("Lỗi", "Số tín chỉ phải là số!")
            return

        if self.db_manager.update_subject(ma_mon, ten_mon, so_tc):
            self.show_message("Thành công", "Cập nhật môn học thành công!")
            self.load_all_subjects()
            self.load_combo_data()
        else:
            self.show_message("Lỗi", "Không thể cập nhật môn học!")

    def delete_subject(self):
        """Xóa môn học"""
        if not self.db_manager:
            self.show_message("Lỗi", "Không có kết nối database!")
            return

        ma_mon = self.ma_mon.text().strip()
        if not ma_mon:
            self.show_message("Lỗi", "Vui lòng chọn môn học cần xóa!")
            return

        reply = QMessageBox.question(self, 'Xác nhận',
                                     f'Bạn có chắc chắn muốn xóa môn học {ma_mon}?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.db_manager.delete_subject(ma_mon):
                self.show_message("Thành công", "Xóa môn học thành công!")
                self.clear_subject_fields()
                self.load_all_subjects()
                self.load_combo_data()
            else:
                self.show_message("Lỗi", "Không thể xóa môn học! Có thể môn học đang được sử dụng.")

    def search_subjects(self):
        """Tìm kiếm môn học"""
        if not self.db_manager:
            return

        search_type = self.subject_search_combo.currentText()
        search_value = self.subject_search_input.text().strip()

        if not search_value:
            self.show_message("Lỗi", "Vui lòng nhập từ khóa tìm kiếm!")
            return

        all_subjects = self.db_manager.get_all_subjects()
        if not all_subjects:
            return

        filtered_subjects = []
        for subject in all_subjects:
            if isinstance(subject, tuple):
                ma_mon, ten_mon, so_tc = subject
            else:
                ma_mon = subject['MaMon']
                ten_mon = subject['TenMon']
                so_tc = subject['SoTinChi']

            if search_type == "Mã môn học":
                if search_value.lower() in str(ma_mon).lower():
                    filtered_subjects.append(subject)
            else:  # Tên môn học
                if search_value.lower() in str(ten_mon).lower():
                    filtered_subjects.append(subject)

        self.populate_subject_table(filtered_subjects)

    def clear_subject_fields(self):
        """Xóa các trường nhập liệu môn học"""
        self.ma_mon.clear()
        self.ten_mon.clear()
        self.so_tc.clear()

    def refresh_subjects(self):
        """Làm mới danh sách môn học"""
        self.clear_subject_fields()
        self.subject_search_input.clear()
        self.load_all_subjects()

    # ====== CLASS MANAGEMENT METHODS ======
    def load_all_classes(self):
        """Load tất cả lớp học vào list"""
        if not self.db_manager:
            return

        classes = self.db_manager.get_all_classes()
        self.populate_class_list(classes)

    def populate_class_list(self, classes):
        """Điền dữ liệu vào list lớp học"""
        self.class_list.clear()

        if not classes:
            self.show_message("Thông báo", "Không tìm thấy lớp học!")
            return

        for class_item in classes:
            if isinstance(class_item, tuple):
                ma_lop, ten_lop, khoa = class_item
            else:
                ma_lop = class_item['MaLop']
                ten_lop = class_item['TenLop']
                khoa = class_item['Khoa']

            display_text = f"{ma_lop} - {ten_lop} ({khoa})"
            self.class_list.addItem(display_text)

    def search_classes(self):
        """Tìm kiếm lớp học"""
        if not self.db_manager:
            return

        # Tìm theo mã lớp hoặc tên lớp (có thể mở rộng thêm combo search)
        search_value = self.ma_lop.text().strip()
        if not search_value:
            self.show_message("Lỗi", "Vui lòng nhập mã lớp để tìm kiếm!")
            return

        class_info = self.db_manager.get_class_by_id(search_value)
        if class_info:
            self.class_list.clear()
            if isinstance(class_info, tuple):
                ma_lop, ten_lop, khoa = class_info
            else:
                ma_lop = class_info['MaLop']
                ten_lop = class_info['TenLop']
                khoa = class_info['Khoa']

            display_text = f"{ma_lop} - {ten_lop} ({khoa})"
            self.class_list.addItem(display_text)
        else:
            self.show_message("Thông báo", "Không tìm thấy lớp học!")

    def on_class_item_clicked(self, item):
        """Xử lý khi click vào item trong list lớp học"""
        text = item.text()
        # Parse text: "MA001 - Tên lớp (Khoa)"
        parts = text.split(' - ', 1)
        if len(parts) >= 2:
            ma_lop = parts[0]
            remaining = parts[1]
            # Tách tên lớp và khoa
            if '(' in remaining and ')' in remaining:
                ten_lop = remaining[:remaining.rfind('(')].strip()
                khoa = remaining[remaining.rfind('(') + 1:remaining.rfind(')')].strip()
            else:
                ten_lop = remaining
                khoa = ""

            self.ma_lop.setText(ma_lop)
            self.ten_lop.setText(ten_lop)
            self.khoa.setText(khoa)

    def add_class(self):
        """Thêm lớp học mới"""
        if not self.db_manager:
            self.show_message("Lỗi", "Không có kết nối database!")
            return

        ma_lop = self.ma_lop.text().strip()
        ten_lop = self.ten_lop.text().strip()
        khoa = self.khoa.text().strip()

        if not all([ma_lop, ten_lop, khoa]):
            self.show_message("Lỗi", "Vui lòng điền đầy đủ thông tin!")
            return

        if self.db_manager.add_class(ma_lop, ten_lop, khoa):
            self.show_message("Thành công", "Thêm lớp học thành công!")
            self.clear_class_fields()
            self.load_all_classes()
            self.load_combo_data()
        else:
            self.show_message("Lỗi", "Không thể thêm lớp học!")

    def update_class(self):
        """Cập nhật lớp học"""
        if not self.db_manager:
            self.show_message("Lỗi", "Không có kết nối database!")
            return

        ma_lop = self.ma_lop.text().strip()
        ten_lop = self.ten_lop.text().strip()
        khoa = self.khoa.text().strip()

        if not all([ma_lop, ten_lop, khoa]):
            self.show_message("Lỗi", "Vui lòng điền đầy đủ thông tin!")
            return

        if self.db_manager.update_class(ma_lop, ten_lop, khoa):
            self.show_message("Thành công", "Cập nhật lớp học thành công!")
            self.load_all_classes()
            self.load_combo_data()
        else:
            self.show_message("Lỗi", "Không thể cập nhật lớp học!")

    def delete_class(self):
        """Xóa lớp học"""
        if not self.db_manager:
            self.show_message("Lỗi", "Không có kết nối database!")
            return

        ma_lop = self.ma_lop.text().strip()
        if not ma_lop:
            self.show_message("Lỗi", "Vui lòng chọn lớp học cần xóa!")
            return

        reply = QMessageBox.question(self, 'Xác nhận',
                                     f'Bạn có chắc chắn muốn xóa lớp học {ma_lop}?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.db_manager.delete_class(ma_lop):
                self.show_message("Thành công", "Xóa lớp học thành công!")
                self.clear_class_fields()
                self.load_all_classes()
                self.load_combo_data()
            else:
                self.show_message("Lỗi", "Không thể xóa lớp học! Có thể lớp học đang được sử dụng.")

    def clear_class_fields(self):
        """Xóa các trường nhập liệu lớp học"""
        self.ma_lop.clear()
        self.ten_lop.clear()
        self.khoa.clear()

    def refresh_classes(self):
        """Làm mới danh sách lớp học"""
        self.clear_class_fields()
        self.load_all_classes()

    # ====== ASSIGNMENT MANAGEMENT METHODS ======
    def lookup_student_name(self):
        """Tìm và hiển thị tên sinh viên khi nhập mã SV"""
        try:
            if not self.student_repo or not hasattr(self, 'ten_sv_display'):
                print("Repo hoặc label không sẵn sàng")
                return

            ma_sv = self.ma_sv_assign.text().strip()
            print("Đang tra mã SV:", ma_sv)

            if not ma_sv:
                self.ten_sv_display.clear()
                return

            student = self.student_repo.get_student_by_id(ma_sv)
            print("Kết quả student:", student)

            if not student:
                self.ten_sv_display.setText("Không tìm thấy sinh viên")
                return

            ten_sv = student.get('TenSV', '')
            self.ten_sv_display.setText(ten_sv if ten_sv else "Không rõ tên")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.show_message("Lỗi nghiêm trọng", f"Lỗi khi hiển thị tên SV: {e}")

    def add_assignment(self):
        """Gán sinh viên vào lớp-môn"""
        if not self.db_manager:
            self.show_message("Lỗi", "Không có kết nối database!")
            return

        try:
            ma_sv = self.ma_sv_assign.text().strip()
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.show_message("Lỗi", f"Lỗi khi lấy Mã SV: {e}")
            return
        ma_mon = self.ma_mon_assign.currentData()
        ma_lop = self.ma_lop_assign.currentData()

        if not all([ma_sv, ma_mon, ma_lop]):
            self.show_message("Lỗi", "Vui lòng điền đầy đủ thông tin!")
            return

        if self.db_manager.add_student_to_class_subject(ma_lop, ma_mon, ma_sv):
            self.show_message("Thành công", "Gán sinh viên thành công!")
            self.clear_assignment_fields()
            self.load_assignments_for_display()
        else:
            self.show_message("Lỗi", "Không thể gán sinh viên!")

    def remove_assignment(self):
        """Hủy gán sinh viên khỏi lớp-môn"""
        if not self.db_manager:
            self.show_message("Lỗi", "Không có kết nối database!")
            return

        ma_sv = self.ma_sv_assign.text().strip()
        ma_mon = self.ma_mon_assign.currentData()
        ma_lop = self.ma_lop_assign.currentData()

        if not all([ma_sv, ma_mon, ma_lop]):
            self.show_message("Lỗi", "Vui lòng điền đầy đủ thông tin!")
            return

        reply = QMessageBox.question(self, 'Xác nhận',
                                     f'Bạn có chắc chắn muốn hủy gán sinh viên {ma_sv}?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.db_manager.remove_student_from_class_subject(ma_lop, ma_mon, ma_sv):
                self.show_message("Thành công", "Hủy gán sinh viên thành công!")
                self.clear_assignment_fields()
                self.load_assignments_for_display()
            else:
                self.show_message("Lỗi", "Không thể hủy gán sinh viên!")

    def search_assignments(self):
        """Tìm kiếm thông tin gán"""
        if not self.db_manager:
            return

        ma_lop = self.ma_lop_assign.currentData()
        ma_mon = self.ma_mon_assign.currentData()

        if not ma_lop or not ma_mon:
            self.show_message("Lỗi", "Vui lòng chọn lớp và môn học để tìm kiếm!")
            return

        students = self.db_manager.get_students_in_class_subject(ma_lop, ma_mon)
        self.populate_assignment_list(students, ma_lop, ma_mon)

    def load_all_assignments(self):
        """Load tất cả thông tin gán"""
        self.load_assignments_for_display()

    def load_assignments_for_display(self):
        """Load danh sách gán để hiển thị (có thể custom theo nhu cầu)"""
        # Hiển thị message hướng dẫn sử dụng
        self.assignment_list.clear()
        self.assignment_list.addItem("Chọn lớp và môn học, sau đó nhấn 'Tìm kiếm'")
        self.assignment_list.addItem("để xem danh sách sinh viên đã được gán.")

    def populate_assignment_list(self, students, ma_lop, ma_mon):
        """Điền danh sách sinh viên đã gán vào list"""
        self.assignment_list.clear()

        if not students:
            self.assignment_list.addItem(f"Không có sinh viên nào trong lớp {ma_lop} - môn {ma_mon}")
            return

        self.assignment_list.addItem(f"Danh sách sinh viên lớp {ma_lop} - môn {ma_mon}:")
        self.assignment_list.addItem("=" * 50)

        for student in students:
            if isinstance(student, tuple):
                ma_sv, ten_sv, email = student
            else:
                ma_sv = student.get('MaSV', '')
                ten_sv = student.get('TenSV', '')
                email = student.get('Email', '')

            display_text = f"• {ma_sv} - {ten_sv}"
            if email:
                display_text += f" ({email})"
            self.assignment_list.addItem(display_text)

    def clear_assignment_fields(self):
        """Xóa các trường nhập liệu gán"""
        self.ma_sv_assign.clear()
        self.ten_sv_display.clear()
        self.ma_mon_assign.setCurrentIndex(0)
        self.ma_lop_assign.setCurrentIndex(0)

    def refresh_assignments(self):
        """Làm mới phần gán"""
        self.clear_assignment_fields()
        self.load_assignments_for_display()
        self.load_combo_data()

    # ====== UTILITY METHODS ======
    def show_message(self, title, message, icon=QMessageBox.Information):
        """Hiển thị thông báo"""
        msg_box = QMessageBox()
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

    def closeEvent(self, event):
        """Xử lý khi đóng cửa sổ"""
        reply = QMessageBox.question(self, 'Xác nhận',
                                     'Bạn có chắc chắn muốn thoát?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


# ====== EXAMPLE USAGE ======
# if __name__ == "__main__":
#     import sys
#
#
#     # Tạo một class giả lập để test UI (không có database thật)
#     class MockDBManager:
#         def __init__(self):
#             self.subjects = [
#                 ('CS101', 'Lập trình căn bản', 3),
#                 ('CS102', 'Cấu trúc dữ liệu', 4),
#                 ('MATH101', 'Toán cao cấp', 3)
#             ]
#             self.classes = [
#                 ('CNTT01', 'Công nghệ thông tin 01', 'Công nghệ thông tin'),
#                 ('CNTT02', 'Công nghệ thông tin 02', 'Công nghệ thông tin'),
#                 ('KT01', 'Kinh tế 01', 'Kinh tế')
#             ]
#             self.students = [
#                 ('SV001', 'Nguyễn Văn A', 'nva@email.com'),
#                 ('SV002', 'Trần Thị B', 'ttb@email.com')
#             ]
#
#         def get_all_subjects(self):
#             return self.subjects
#
#         def get_all_classes(self):
#             return self.classes
#
#         def get_student_by_id(self, ma_sv):
#             for student in self.students:
#                 if student[0] == ma_sv:
#                     return student
#             return None
#
#         def add_subject(self, ma_mon, ten_mon, so_tc):
#             print(f"Mock: Thêm môn {ma_mon} - {ten_mon} - {so_tc} TC")
#             return True
#
#         def update_subject(self, ma_mon, ten_mon, so_tc):
#             print(f"Mock: Cập nhật môn {ma_mon} - {ten_mon} - {so_tc} TC")
#             return True
#
#         def delete_subject(self, ma_mon):
#             print(f"Mock: Xóa môn {ma_mon}")
#             return True
#
#         def add_class(self, ma_lop, ten_lop, khoa):
#             print(f"Mock: Thêm lớp {ma_lop} - {ten_lop} - {khoa}")
#             return True
#
#         def update_class(self, ma_lop, ten_lop, khoa):
#             print(f"Mock: Cập nhật lớp {ma_lop} - {ten_lop} - {khoa}")
#             return True
#
#         def delete_class(self, ma_lop):
#             print(f"Mock: Xóa lớp {ma_lop}")
#             return True
#
#         def get_class_by_id(self, ma_lop):
#             for class_item in self.classes:
#                 if class_item[0] == ma_lop:
#                     return class_item
#             return None
#
#         def add_student_to_class_subject(self, ma_lop, ma_mon, ma_sv):
#             print(f"Mock: Gán SV {ma_sv} vào lớp {ma_lop} môn {ma_mon}")
#             return True
#
#         def remove_student_from_class_subject(self, ma_lop, ma_mon, ma_sv):
#             print(f"Mock: Hủy gán SV {ma_sv} khỏi lớp {ma_lop} môn {ma_mon}")
#             return True
#
#         def get_students_in_class_subject(self, ma_lop, ma_mon):
#             return self.students[:2]  # Trả về 2 sinh viên đầu tiên
#
#
#     app = QApplication(sys.argv)
#
#     # Tạo mock database manager để test
#     mock_db = MockDBManager()
#
#     # Khởi tạo UI với mock database
#     window = ClassSubjectManagementUI(mock_db)
#     window.show()
#
#     sys.exit(app.exec_())({khoa})
#     self.class_list.addItem(display_text)
