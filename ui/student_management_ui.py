import sys
import time
import traceback

import cv2
import numpy as np
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QLineEdit, QTextEdit, QGroupBox, QGridLayout, QComboBox,
                             QDialogButtonBox, QScrollArea, QMessageBox, QMainWindow,
                             QTableWidget, QTableWidgetItem, QApplication, QWidget, QAbstractItemView,
                            QDateEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor


from database.student_repository import StudentRepository
from face_recognition_module.face_embedder import FaceEmbedder

class FaceCaptureDialog(QDialog):
    facesCaptured = pyqtSignal(list)

    def __init__(self, student_id, student_name="Unknown", parent=None):
        super().__init__(parent)
        self.student_name = student_name
        self.student_id = student_id
        self.face_embedder = FaceEmbedder()
        self.face_embeddings = []
        self.cap = None
        self.timer = None
        self.setupUI()
        self.sample_count = 0
        self.max_samples = 3
        self.save_dir = f"assets/student_faces"
        os.makedirs(self.save_dir, exist_ok=True)
        self.student_repo = StudentRepository()

    def setupUI(self):
        self.setWindowTitle(f"Chụp khuôn mặt - {self.student_name}")
        self.setFixedSize(800, 600)

        layout = QVBoxLayout()

        self.video_label = QLabel()
        self.video_label.setFixedSize(640, 480)
        self.video_label.setStyleSheet("border: 2px solid #D1D5DB; border-radius: 5px;")
        layout.addWidget(self.video_label)

        self.status_label = QLabel("Nhấn 'Bắt đầu' để chụp khuôn mặt")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #6B7280;
                padding: 10px;
                text-align: center;
            }
        """)
        layout.addWidget(self.status_label)

        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("▶ Bắt đầu")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.start_btn.clicked.connect(self.startCapture)
        button_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("■ Dừng")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        self.stop_btn.clicked.connect(self.stopCapture)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Ok).setText("💾 Lưu")
        self.button_box.button(QDialogButtonBox.Cancel).setText("❌ Hủy")
        self.button_box.accepted.connect(self.saveFaces)
        self.button_box.rejected.connect(self.reject)
        self.button_box.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton[text="💾 Lưu"] {
                background-color: #6B46C1;
                color: white;
                border: none;
            }
            QPushButton[text="💾 Lưu"]:hover {
                background-color: #553C9A;
            }
            QPushButton[text="❌ Hủy"] {
                background-color: #6B7280;
                color: white;
                border: none;
            }
            QPushButton[text="❌ Hủy"]:hover {
                background-color: #4B5563;
            }
        """)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

    def startCapture(self):
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                QMessageBox.critical(self, "Lỗi", "Không thể mở camera!")
                return

            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.timer = self.startTimer(30)
            self.status_label.setText("Đang chụp khuôn mặt... Vui lòng nhìn vào camera.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể bắt đầu chụp: {str(e)}")

    def timerEvent(self, event):
        try:
            ret, frame = self.cap.read()
            if not ret:
                return

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Detect và encode embedding
            embeddings = self.face_embedder.detect_and_encode_faces(frame_rgb)
            if embeddings:
                embedding = embeddings[0]  # lấy khuôn mặt đầu tiên
                # Lưu ảnh vào thư mục với tên rõ ràng
                timestamp = int(time.time())
                img_filename = f"{self.student_id}_{self.sample_count + 1}_{timestamp}.jpg"
                img_path = os.path.join(self.save_dir, img_filename)
                cv2.imwrite(img_path, frame)

                # Lưu embedding vào CSDL
                embedding_blob = embedding.astype(np.float32).tobytes()
                with self.face_embedder.processing_lock:
                    if self.student_repo.add_face_embedding(self.student_id, img_path, embedding_blob):
                        self.face_embeddings.append(embedding)
                        self.sample_count += 1
                        self.status_label.setText(f"Đã chụp {self.sample_count}/{self.max_samples} mẫu")
                    else:
                        print(f"Lỗi khi lưu embedding mẫu {self.sample_count + 1}")

                if self.sample_count >= self.max_samples:
                    self.stopCapture()

            # Hiển thị video
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            q_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image).scaled(self.video_label.size(), Qt.KeepAspectRatio)
            self.video_label.setPixmap(pixmap)

        except Exception as e:
            print(f"Error in timerEvent: {e}")

    def stopCapture(self):
        if self.cap:
            self.cap.release()
            self.cap = None
        if self.timer:
            self.killTimer(self.timer)
            self.timer = None
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText(f"Đã chụp {len(self.face_embeddings)}/3 mẫu khuôn mặt")

    def saveFaces(self):
        if len(self.face_embeddings) < 3:
            QMessageBox.warning(self, "Cảnh báo", "Cần ít nhất 3 mẫu khuôn mặt!")
            return
        self.facesCaptured.emit(self.face_embeddings)
        self.accept()

    def closeEvent(self, event):
        self.stopCapture()
        event.accept()


class StudentFormDialog(QDialog):
    studentSaved = pyqtSignal(dict)

    def __init__(self, student_data=None, parent=None):
        super().__init__(parent)
        self.student_id_edit = None
        self.student_data = student_data
        self.face_embeddings = []
        self.student_repository = StudentRepository()
        self.setupUI()
        if student_data:
            self.loadStudentData()

        self.capture_face_btn.clicked.connect(self.captureFace)
        self.clear_faces_btn.clicked.connect(self.clearFaceData)
        self.button_box = self.findChild(QDialogButtonBox)
        self.button_box.accepted.connect(self.saveStudent)
        self.button_box.rejected.connect(self.reject)

    def setupUI(self):
        self.setWindowTitle("Thêm sinh viên" if not self.student_data else "Sửa thông tin sinh viên")
        self.setFixedSize(750, 850)

        main_layout = QVBoxLayout()

        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        layout = QVBoxLayout()

        title = QLabel("📚 Thông tin sinh viên")
        title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #6B46C1;
                padding: 15px;
                text-align: center;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 10px;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form_group = QGroupBox("Thông tin cơ bản")
        form_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #E5E7EB;
                border-radius: 10px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #6B46C1;
            }
        """)
        form_layout = QGridLayout()

        # Mã sinh viên
        form_layout.addWidget(QLabel("Mã sinh viên: *"), 0, 0)
        self.student_id_edit = QLineEdit()
        self.student_id_edit.setPlaceholderText("Nhập mã sinh viên (VD: SV001)")
        form_layout.addWidget(self.student_id_edit, 0, 1)

        # Họ tên
        form_layout.addWidget(QLabel("Họ tên: *"), 1, 0)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nhập họ tên đầy đủ")
        form_layout.addWidget(self.name_edit, 1, 1)

        # Ngày sinh (Date Picker)
        form_layout.addWidget(QLabel("Ngày sinh:"), 2, 0)
        self.birth_edit = QDateEdit()
        self.birth_edit.setCalendarPopup(True)
        self.birth_edit.setDisplayFormat("dd/MM/yyyy")
        form_layout.addWidget(self.birth_edit, 2, 1)

        # Giới tính (ComboBox)
        form_layout.addWidget(QLabel("Giới tính:"), 3, 0)
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Nam", "Nữ", "Khác"])
        form_layout.addWidget(self.gender_combo, 3, 1)

        # Địa chỉ
        form_layout.addWidget(QLabel("Địa chỉ:"), 4, 0)
        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("Nhập địa chỉ liên lạc")
        form_layout.addWidget(self.address_edit, 4, 1)

        # Email
        form_layout.addWidget(QLabel("Email:"), 5, 0)
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Nhập địa chỉ email")
        form_layout.addWidget(self.email_edit, 5, 1)

        # Số điện thoại
        form_layout.addWidget(QLabel("Số điện thoại:"), 6, 0)
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("Nhập số điện thoại")
        form_layout.addWidget(self.phone_edit, 6, 1)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # === Nhóm dữ liệu khuôn mặt ===
        self.face_group = QGroupBox("🎭 Dữ liệu khuôn mặt")
        self.face_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #E5E7EB;
                border-radius: 10px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #10B981;
            }
        """)
        face_layout = QVBoxLayout()

        self.face_status_label = QLabel("❌ Chưa có dữ liệu khuôn mặt")
        self.face_status_label.setStyleSheet("""
            QLabel {
                color: #F59E0B; 
                font-weight: bold; 
                padding: 10px;
                background-color: #FEF3C7;
                border-radius: 5px;
                border: 1px solid #F59E0B;
            }
        """)
        face_layout.addWidget(self.face_status_label)

        face_button_layout = QHBoxLayout()
        self.capture_face_btn = QPushButton("📸 Chụp khuôn mặt")
        self.capture_face_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)

        self.clear_faces_btn = QPushButton("🗑️ Xóa dữ liệu")
        self.clear_faces_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)

        face_button_layout.addWidget(self.capture_face_btn)
        face_button_layout.addWidget(self.clear_faces_btn)
        face_button_layout.addStretch()
        face_layout.addLayout(face_button_layout)

        self.face_group.setLayout(face_layout)

        # 👉 Chỉ hiển thị nếu đang ở chế độ sửa sinh viên
        self.face_group.setVisible(bool(self.student_data))
        layout.addWidget(self.face_group)

        note_label = QLabel("* Trường bắt buộc")
        note_label.setStyleSheet("color: #EF4444; font-style: italic; padding: 5px;")
        layout.addWidget(note_label)

        scroll_widget.setLayout(layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Ok).setText("💾 Lưu")
        self.button_box.button(QDialogButtonBox.Cancel).setText("❌ Hủy")
        self.button_box.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton[text="💾 Lưu"] {
                background-color: #6B46C1;
                color: white;
                border: none;
            }
            QPushButton[text="💾 Lưu"]:hover {
                background-color: #553C9A;
            }
            QPushButton[text="❌ Hủy"] {
                background-color: #6B7280;
                color: white;
                border: none;
            }
            QPushButton[text="❌ Hủy"]:hover {
                background-color: #4B5563;
            }
        """)
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

    def loadStudentData(self):
        try:
            self.student_id_edit.setText(self.student_data.get('MaSV', ''))
            self.student_id_edit.setEnabled(False)
            self.name_edit.setText(self.student_data.get('TenSV', ''))

            # Ngày sinh (QDateEdit)
            ngaysinh_str = self.student_data.get('NgaySinh', '')
            if ngaysinh_str:
                try:
                    date = QDate.fromString(ngaysinh_str, "dd/MM/yyyy")
                    if not date.isValid():
                        date = QDate.fromString(ngaysinh_str, "yyyy-MM-dd")
                    if date.isValid():
                        self.birth_edit.setDate(date)
                except:
                    pass

            # Giới tính (QComboBox)
            gioitinh = self.student_data.get('GioiTinh', '')
            index = self.gender_combo.findText(gioitinh)
            if index >= 0:
                self.gender_combo.setCurrentIndex(index)

            # Các trường còn lại
            self.address_edit.setText(self.student_data.get('DiaChi', ''))
            self.email_edit.setText(self.student_data.get('Email', ''))
            self.phone_edit.setText(self.student_data.get('SDT', ''))

            self.face_embeddings = self.student_data.get('embeddings', [])
            self.updateFaceStatus()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải dữ liệu sinh viên: {str(e)}")

    def updateFaceStatus(self):
        if len(self.face_embeddings) >= 3:
            self.face_status_label.setText("✅ Đã có đủ dữ liệu khuôn mặt")
            self.face_status_label.setStyleSheet("""
                QLabel {
                    color: #059669; 
                    font-weight: bold; 
                    padding: 10px;
                    background-color: #D1FAE5;
                    border-radius: 5px;
                    border: 1px solid #059669;
                }
            """)
        else:
            self.face_status_label.setText(f"⚠️ Đã có {len(self.face_embeddings)}/3 mẫu khuôn mặt")
            self.face_status_label.setStyleSheet("""
                QLabel {
                    color: #F59E0B; 
                    font-weight: bold; 
                    padding: 10px;
                    background-color: #FEF3C7;
                    border-radius: 5px;
                    border: 1px solid #F59E0B;
                }
            """)

    def captureFace(self):
        student_id = self.student_id_edit.text().strip()
        try:
            dialog = FaceCaptureDialog(student_id ,student_name=self.name_edit.text() or "Sinh viên", parent=self)
            dialog.facesCaptured.connect(self.storeFaceEmbeddings)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể mở giao diện chụp khuôn mặt: {str(e)}")

    def storeFaceEmbeddings(self, embeddings):
        self.face_embeddings = embeddings
        self.updateFaceStatus()

    def clearFaceData(self):
        if QMessageBox.question(self, "Xác nhận",
                                "Bạn có chắc muốn xóa dữ liệu khuôn mặt?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.face_embeddings = []
            self.updateFaceStatus()

    def validateInput(self):
        student_id = self.student_id_edit.text().strip()
        name = self.name_edit.text().strip()

        if not student_id:
            QMessageBox.warning(self, "Lỗi nhập liệu", "Mã sinh viên là bắt buộc!")
            return False
        if not name:
            QMessageBox.warning(self, "Lỗi nhập liệu", "Họ tên là bắt buộc!")
            return False
        """ Hiện tại không lấy dữ liệu khuôn mặt khi thêm sinh viên
        if len(self.face_embeddings) < 3 and not self.student_data:
            QMessageBox.warning(self, "Lỗi nhập liệu", "Cần ít nhất 3 mẫu dữ liệu khuôn mặt!")
            return False
        """
        return True

    def saveStudent(self):
        try:
            if not self.validateInput():
                return

            student_data = {
                'MaSV': self.student_id_edit.text().strip(),
                'TenSV': self.name_edit.text().strip(),
                'NgaySinh': self.birth_edit.date().toString("yyyy-MM-dd"),
                'GioiTinh': self.gender_combo.currentText(),
                'DiaChi': self.address_edit.text().strip(),
                'Email': self.email_edit.text().strip(),
                'SDT': self.phone_edit.text().strip(),
            }

            if self.student_data:  # cập nhật
                success = self.student_repository.update_student(
                    student_data['MaSV'],
                    student_data['TenSV'],
                    student_data['NgaySinh'],
                    student_data['GioiTinh'],
                    student_data['DiaChi'],
                    student_data['Email'],
                    student_data['SDT']
                )
                action = "cập nhật"
            else:  # thêm mới
                success = self.student_repository.add_student(
                    student_data['MaSV'],
                    student_data['TenSV'],
                    student_data['NgaySinh'],
                    student_data['GioiTinh'],
                    student_data['DiaChi'],
                    student_data['Email'],
                    student_data['SDT']
                )
                action = "thêm"

            if success:
                QMessageBox.information(self, "Thành công", f"Đã {action} sinh viên thành công!")
                self.studentSaved.emit(student_data)
                self.accept()
            else:
                traceback.print_exc()
                QMessageBox.critical(self, "Lỗi", f"Không thể {action} sinh viên. Vui lòng kiểm tra lại.")
        except Exception as e:

            QMessageBox.critical(self, "Lỗi", f"Lỗi khi lưu dữ liệu sinh viên: {str(e)}")

    def closeEvent(self, event):
        event.accept()


class StudentManagementUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.student_repository = StudentRepository()
        self.setupUI()
        self.loadStudents()
        self.setFixedSize(1350, 800)

    def setupUI(self):
        self.setWindowTitle("Quản lý Sinh viên")
        self.setGeometry(150, 150, 1000, 700)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #F9FAFB;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        header = QLabel("Quản lý Sinh viên")
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #6B46C1;
                padding: 20px;
            }
        """)
        layout.addWidget(header)

        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ Thêm sinh viên")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.add_btn.clicked.connect(self.addStudent)

        self.edit_btn = QPushButton("✏️ Sửa sinh viên")
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:disabled {
                background-color: #D1D5DB;
                color: #9CA3AF;
            }
        """)
        self.edit_btn.clicked.connect(self.editStudent)
        self.edit_btn.setEnabled(False)

        self.delete_btn = QPushButton("🗑️ Xóa sinh viên")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
            QPushButton:disabled {
                background-color: #D1D5DB;
                color: #9CA3AF;
            }
        """)
        self.delete_btn.clicked.connect(self.deleteStudent)
        self.delete_btn.setEnabled(False)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.student_table = QTableWidget()
        self.student_table.setColumnCount(7)
        self.student_table.setHorizontalHeaderLabels([
            "Mã SV", "Họ tên", "Ngày sinh", "Giới tính", "Địa chỉ", "Email", "SĐT"
        ])
        self.student_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #D1D5DB;
                border-radius: 5px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #6B46C1;
                color: white;
                padding: 5px;
                border: none;
            }
        """)
        self.student_table.horizontalHeader().setStretchLastSection(True)
        self.student_table.setSelectionMode(QTableWidget.SingleSelection)
        self.student_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.student_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.student_table.itemSelectionChanged.connect(self.onTableSelectionChanged)
        layout.addWidget(self.student_table)

        central_widget.setLayout(layout)

    def loadStudents(self):
        print("Reload danh sách sinh viên...")
        try:
            students = self.student_repository.get_all_students()
            self.student_table.setRowCount(len(students))
            for row, student in enumerate(students):
                self.student_table.setItem(row, 0, QTableWidgetItem(student["MaSV"]))  # MaSV
                self.student_table.setItem(row, 1, QTableWidgetItem(student["TenSV"]))  # TenSV
                self.student_table.setItem(row, 2, QTableWidgetItem(student["NgaySinh"].strftime("%d/%m/%Y")))  # NgaySinh
                self.student_table.setItem(row, 3, QTableWidgetItem(student["GioiTinh"]))  # GioiTinh
                self.student_table.setItem(row, 4, QTableWidgetItem(student["DiaChi"]))  # DiaChi
                self.student_table.setItem(row, 5, QTableWidgetItem(student["Email"]))  # Email
                self.student_table.setItem(row, 6, QTableWidgetItem(student["SDT"]))  # SDT
            self.student_table.resizeColumnsToContents()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Lỗi", f"Không thể tải danh sách sinh viên: {str(e)}")

    def addStudent(self):
        dialog = StudentFormDialog(parent=self)
        dialog.studentSaved.connect(self.onStudentSaved)
        dialog.exec_()

    def onStudentUpdated(self, row, student_data):
        self.student_table.setItem(row, 0, QTableWidgetItem(student_data['MaSV']))
        self.student_table.setItem(row, 1, QTableWidgetItem(student_data['TenSV']))
        self.student_table.setItem(row, 2, QTableWidgetItem(student_data['NgaySinh']))
        self.student_table.setItem(row, 3, QTableWidgetItem(student_data['GioiTinh']))
        self.student_table.setItem(row, 4, QTableWidgetItem(student_data['DiaChi']))
        self.student_table.setItem(row, 5, QTableWidgetItem(student_data['Email']))
        self.student_table.setItem(row, 6, QTableWidgetItem(student_data['SDT']))

        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)

    def editStudent(self):
        selected_rows = self.student_table.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()

        student_data = {
            'MaSV': self.student_table.item(row, 0).text(),  # Mã SV
            'TenSV': self.student_table.item(row, 1).text(),  # Họ tên
            'NgaySinh': self.student_table.item(row, 2).text(),  # Ngày sinh
            'GioiTinh': self.student_table.item(row, 3).text(),  # Giới tính
            'DiaChi': self.student_table.item(row, 4).text(),  # Địa chỉ
            'Email': self.student_table.item(row, 5).text(),  # Email
            'SDT': self.student_table.item(row, 6).text(),  # SĐT
            'embeddings': self.student_repository.get_face_embeddings_by_student_id(
                self.student_table.item(row, 0).text()
            )
        }

        dialog = StudentFormDialog(student_data=student_data, parent=self)
        dialog.studentSaved.connect(lambda updated_data: self.onStudentUpdated(row, updated_data))
        dialog.exec_()

    def deleteStudent(self):
        selected_rows = self.student_table.selectionModel().selectedRows()
        if not selected_rows:
            return

        student_id = self.student_table.item(selected_rows[0].row(), 0).text()
        if QMessageBox.question(self, "Xác nhận xóa",
                                f"Bạn có chắc muốn xóa sinh viên {student_id}?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                success = self.student_repository.delete_student(student_id)
                if success:
                    QMessageBox.information(self, "Thành công", "Đã xóa sinh viên!")
                    self.loadStudents()
                else:
                    QMessageBox.critical(self, "Lỗi", "Không thể xóa sinh viên.")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Lỗi khi xóa sinh viên: {str(e)}")

    def onStudentSaved(self, student_data):
        self.loadStudents()
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)

    def onTableSelectionChanged(self):
        print("👉 Đã chọn dòng trong bảng")
        selected_rows = self.student_table.selectionModel().selectedRows()
        is_selected = len(selected_rows) > 0
        print(f"Số dòng được chọn: {len(selected_rows)}")
        self.edit_btn.setEnabled(is_selected)
        self.delete_btn.setEnabled(is_selected)

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

