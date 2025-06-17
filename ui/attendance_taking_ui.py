# python -m ui.attendance_taking_ui

from PyQt5 import QtWidgets, QtGui, QtCore
import cv2
import sys
import datetime
from PIL import Image, ImageQt

from face_recognition_module.face_recognizer import FaceRecognizer
from database.attendance_repository import AttendanceRepository
from database.session_repository import SessionRepository


class AttendanceUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎓 Hệ thống điểm danh khuôn mặt")
        self.setGeometry(100, 100, 1200, 700)
        self.face_recognizer = FaceRecognizer()
        self.attendance = AttendanceRepository()
        self.session = SessionRepository()
        self.camera_running = False
        self.cap = None
        self.timer = None
        self.current_student = None  # Lưu thông tin sinh viên hiện tại

        # Thiết lập style cho toàn bộ ứng dụng
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }

            QLabel {
                color: #333;
                font-size: 12px;
                padding: 2px;
            }

            QComboBox {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                min-height: 20px;
            }

            QComboBox:focus {
                border-color: #4CAF50;
            }

            QComboBox::drop-down {
                border: none;
                width: 20px;
            }

            QComboBox::down-arrow {
                image: none;
                border: 3px solid #666;
                border-top-color: transparent;
                border-left-color: transparent;
                border-right-color: transparent;
            }

            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }

            QPushButton:hover {
                background-color: #45a049;
                transform: translateY(-1px);
            }

            QPushButton:pressed {
                background-color: #3d8b40;
            }

            QPushButton#closeBtn {
                background-color: #f44336;
            }

            QPushButton#closeBtn:hover {
                background-color: #da190b;
            }

            QGroupBox {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                margin: 10px;
                padding-top: 15px;
                font-weight: bold;
                font-size: 14px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px 0 10px;
                color: #4CAF50;
            }
        """)

        self.setup_ui()
        self.load_sessions()
        self.session_combo.currentIndexChanged.connect(self.load_session_time)

    def setup_ui(self):
        # Layout tổng
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # === VÙNG BÊN TRÁI ===
        left_widget = QtWidgets.QWidget()
        left_widget.setFixedWidth(600)
        left_layout = QtWidgets.QVBoxLayout(left_widget)

        # Group box cho phần chọn buổi học
        selection_group = QtWidgets.QGroupBox("📚 Thông tin buổi học")
        selection_layout = QtWidgets.QVBoxLayout(selection_group)

        # Form chọn buổi học
        form_layout = QtWidgets.QFormLayout()

        self.session_combo = QtWidgets.QComboBox()
        self.session_combo.setMinimumHeight(35)

        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(["🔵 Vào", "🔴 Ra"])
        self.type_combo.setMinimumHeight(35)

        form_layout.addRow("📖 Môn học / Buổi học:", self.session_combo)
        form_layout.addRow("⏰ Loại điểm danh:", self.type_combo)

        selection_layout.addLayout(form_layout)

        # Group box cho camera
        camera_group = QtWidgets.QGroupBox("📷 Camera điểm danh")
        camera_layout = QtWidgets.QVBoxLayout(camera_group)

        # Camera view với border đẹp
        self.camera_label = QtWidgets.QLabel("📷 Camera chưa khởi động\n\nBấm 'Mở Camera' để bắt đầu")
        self.camera_label.setFixedSize(550, 350)
        self.camera_label.setAlignment(QtCore.Qt.AlignCenter)
        self.camera_label.setStyleSheet("""
            QLabel {
                background-color: #263238;
                color: #fff;
                border: 3px solid #37474f;
                border-radius: 12px;
                font-size: 16px;
            }
        """)

        # Nút điều khiển với spacing đẹp
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(15)

        self.open_btn = QtWidgets.QPushButton("📷 Mở Camera")
        self.close_btn = QtWidgets.QPushButton("⏹️ Đóng Camera")
        self.close_btn.setObjectName("closeBtn")

        # Thêm nút điểm danh
        self.attendance_btn = QtWidgets.QPushButton("✅ Điểm Danh")
        self.attendance_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.attendance_btn.setEnabled(False)  # Bắt đầu với trạng thái disabled

        button_layout.addWidget(self.open_btn)
        button_layout.addWidget(self.close_btn)
        button_layout.addWidget(self.attendance_btn)
        button_layout.addStretch()

        self.open_btn.clicked.connect(self.start_camera)
        self.close_btn.clicked.connect(self.stop_camera)
        self.attendance_btn.clicked.connect(self.confirm_attendance)

        camera_layout.addWidget(self.camera_label)
        camera_layout.addSpacing(10)
        camera_layout.addLayout(button_layout)

        # Thêm vào layout trái
        left_layout.addWidget(selection_group)
        left_layout.addWidget(camera_group)
        left_layout.addStretch()

        # === VÙNG BÊN PHẢI ===
        right_widget = QtWidgets.QWidget()
        right_widget.setFixedWidth(400)
        right_layout = QtWidgets.QVBoxLayout(right_widget)

        # Group box cho thông tin sinh viên
        student_group = QtWidgets.QGroupBox("👤 Thông tin sinh viên")
        student_layout = QtWidgets.QVBoxLayout(student_group)

        # Ảnh khuôn mặt
        self.face_image_label = QtWidgets.QLabel("📸 Chưa có ảnh")
        self.face_image_label.setFixedSize(200, 200)
        self.face_image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.face_image_label.setStyleSheet("""
            QLabel {
                background-color: #eceff1;
                border: 3px dashed #90a4ae;
                border-radius: 12px;
                color: #90a4ae;
                font-size: 14px;
            }
        """)

        # Thông tin sinh viên với style đẹp
        info_widget = QtWidgets.QWidget()
        info_layout = QtWidgets.QVBoxLayout(info_widget)
        info_layout.setSpacing(8)

        self.student_id_label = QtWidgets.QLabel("🆔 ID Sinh Viên: --")
        self.student_name_label = QtWidgets.QLabel("👤 Tên Sinh Viên: --")
        self.time_label = QtWidgets.QLabel("🕐 Thời gian: --")

        # Style cho các label thông tin
        info_style = """
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                color: #495057;
            }
        """

        for label in [self.student_id_label, self.student_name_label, self.time_label]:
            label.setStyleSheet(info_style)

        info_layout.addWidget(self.student_id_label)
        info_layout.addWidget(self.student_name_label)
        info_layout.addWidget(self.time_label)

        student_layout.addWidget(self.face_image_label, alignment=QtCore.Qt.AlignCenter)
        student_layout.addSpacing(10)
        student_layout.addWidget(info_widget)

        # Group box cho thông tin buổi học
        session_info_group = QtWidgets.QGroupBox("📋 Chi tiết buổi học")
        session_info_layout = QtWidgets.QVBoxLayout(session_info_group)

        self.class_label = QtWidgets.QLabel("🏫 Phòng học: --")
        self.subject_label = QtWidgets.QLabel("📚 Môn học: --")
        self.session_time_label = QtWidgets.QLabel("⏰ Thời gian buổi học: --")

        for label in [self.class_label, self.subject_label, self.session_time_label]:
            label.setStyleSheet(info_style)

        session_info_layout.addWidget(self.class_label)
        session_info_layout.addWidget(self.subject_label)
        session_info_layout.addWidget(self.session_time_label)

        # Thêm vào layout phải
        right_layout.addWidget(student_group)
        right_layout.addWidget(session_info_group)
        right_layout.addStretch()

        # Gộp hai vùng
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)

    def load_sessions(self):
        """Load dữ liệu buổi học từ database vào combo box"""
        try:
            if not self.session:
                return

            sessions = self.session.get_all_sessions()
            self.session_combo.clear()
            self.session_combo.addItem("-- Chọn buổi học --", "")

            if not sessions:
                QtWidgets.QMessageBox.warning(self, "⚠️ Thông báo", "Không tìm thấy buổi học nào!")
                return

            for session in sessions:
                if isinstance(session, tuple):
                    ma_buoi = session[0]
                    ten_mon = session[1]
                else:
                    ma_buoi = session.get("MaBuoiHoc")
                    ten_mon = session.get("TenMon")

                display_text = f"{ten_mon} / {ma_buoi}"
                self.session_combo.addItem(display_text, ma_buoi)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "❌ Lỗi", f"Không thể tải danh sách buổi học: {str(e)}")

    def load_session_time(self):
        """Load thời gian của buổi học"""
        try:
            ma_buoi_hoc = self.session_combo.currentData()
            if not ma_buoi_hoc:
                self.session_time_label.setText("⏰ Thời gian buổi học: --")
                self.subject_label.setText("📚 Môn học: --")
                self.class_label.setText("🏫 Phòng học: --")
                return

            session_info = self.session.get_session_by_id(ma_buoi_hoc)
            if session_info:
                bat_dau = session_info.get("GioBatDau", "??:??:??")
                ket_thuc = session_info.get("GioKetThuc", "??:??:??")
                ten_mon = session_info.get("TenMon", "Không rõ")
                phong_hoc = session_info.get("PhongHoc", "Không rõ")
                self.session_time_label.setText(f"⏰ Thời gian buổi học: {bat_dau} - {ket_thuc}")
                self.subject_label.setText(f"📚 Môn học: {ten_mon}")
                self.class_label.setText(f"🏫 Phòng học:  {phong_hoc}")
            else:
                self.session_time_label.setText("⏰ Thời gian buổi học: Không tìm thấy")
                self.subject_label.setText("📚 Môn học: Không rõ")
        except Exception as e:
            self.session_time_label.setText("⏰ Thời gian buổi học: Lỗi tải dữ liệu")

    def start_camera(self):
        """Khởi động camera"""
        try:
            if not self.camera_running:
                self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    QtWidgets.QMessageBox.critical(self, "❌ Lỗi Camera",
                                                   "Không thể mở camera!\nVui lóng kiểm tra:\n"
                                                   "• Camera có được kết nối?\n"
                                                   "• Ứng dụng khác có đang sử dụng camera?")
                    return

                # Thiết lập độ phân giải camera
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

                self.camera_running = True
                self.timer = QtCore.QTimer()
                self.timer.timeout.connect(self.update_frame)
                self.timer.start(30)  # 30ms = ~33 FPS

                self.camera_label.setText("📷 Camera đang hoạt động...")
                self.open_btn.setEnabled(False)
                self.close_btn.setEnabled(True)
                self.attendance_btn.setEnabled(False)  # Reset nút điểm danh
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "❌ Lỗi", f"Không thể khởi động camera: {str(e)}")

    def update_frame(self):
        """Cập nhật frame từ camera"""
        try:
            if not self.cap or not self.camera_running:
                return

            ret, frame = self.cap.read()
            if not ret:
                return

            # Lật frame theo chiều ngang (mirror effect)
            frame = cv2.flip(frame, 1)

            # Nhận diện khuôn mặt
            recognized_faces = self.face_recognizer.recognize_faces_in_frame(frame)

            # Vẽ khung cho các khuôn mặt được nhận diện
            for student_id, student_name, face_location, confidence, face_img in recognized_faces:
                top, right, bottom, left = face_location

                if student_id and confidence > 70:  # Độ tin cậy cao
                    print(f"Đã nhận diện: {student_id} - {student_name} ({confidence}%)")

                    # Vẽ khung xanh cho khuôn mặt được nhận diện
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, f"{student_name} ({confidence}%)",
                                (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                    # Chỉ hiển thị thông tin mà không tắt camera
                    self.display_student_info(student_id, student_name, face_img, confidence)

                elif student_id:  # Nhận diện được nhưng độ tin cậy thấp
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 255), 2)
                    cv2.putText(frame, f"{student_name} ({confidence}%)",
                                (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                else:
                    # Vẽ khung đỏ cho khuôn mặt chưa nhận diện được
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.putText(frame, "Unknown",
                                (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            # Hiển thị frame lên giao diện
            self.display_frame(frame)

        except Exception as e:
            print(f"Lỗi update_frame: {str(e)}")

    def display_frame(self, frame):
        """Hiển thị frame lên label"""
        try:
            # Chuyển đổi từ BGR sang RGB
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w

            # Tạo QImage
            qt_image = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)

            # Scale để fit với label
            pixmap = QtGui.QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(self.camera_label.size(),
                                          QtCore.Qt.KeepAspectRatio,
                                          QtCore.Qt.SmoothTransformation)

            self.camera_label.setPixmap(scaled_pixmap)
        except Exception as e:
            print(f"Lỗi display_frame: {str(e)}")

    def display_student_info(self, student_id, student_name, face_img, confidence):
        """Hiển thị thông tin sinh viên lên giao diện mà không tắt camera"""
        try:
            student_info = self.face_recognizer.get_student_info(student_id)
            now = datetime.datetime.now()

            # Format thời gian: giờ -> ngày
            time_str = now.strftime("%H:%M:%S %d/%m/%Y")

            # Lưu thông tin sinh viên hiện tại
            self.current_student = {
                'student_id': student_id,
                'student_name': student_name,
                'face_img': face_img,
                'student_info': student_info,
                'time_str': time_str
            }

            # Hiển thị thông tin
            self.student_id_label.setText(f"🆔 ID Sinh Viên: {student_info.get('MaSV', student_id)}")
            self.student_name_label.setText(
                f"👤 Tên Sinh Viên: {student_info.get('TenSV', student_name)} ({confidence}%)")
            self.time_label.setText(f"🕐 Thời gian: {time_str}")

            # Enable nút điểm danh
            self.attendance_btn.setEnabled(True)

            # Hiển thị ảnh khuôn mặt nếu có
            if face_img is not None:
                try:
                    face_img_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
                    h, w, ch = face_img_rgb.shape
                    bytes_per_line = ch * w
                    qt_image = QtGui.QImage(face_img_rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
                    pixmap = QtGui.QPixmap.fromImage(qt_image).scaled(200, 200, QtCore.Qt.KeepAspectRatio,
                                                                      QtCore.Qt.SmoothTransformation)
                    self.face_image_label.setPixmap(pixmap)
                except Exception as e:
                    print(f"Lỗi hiển thị ảnh khuôn mặt: {str(e)}")

        except Exception as e:
            print(f"Lỗi display_student_info: {str(e)}")

    def confirm_attendance(self):
        """Xác nhận điểm danh khi người dùng bấm nút"""
        if self.current_student:
            self.process_attendance(
                self.current_student['student_id'],
                self.current_student['student_name'],
                self.current_student['face_img']
            )
            # Reset thông tin sinh viên và disable nút
            self.current_student = None
            self.attendance_btn.setEnabled(False)

    def process_attendance(self, student_id, student_name, face_img):
        """Xử lý điểm danh cho sinh viên - chỉ được gọi khi người dùng xác nhận"""
        try:
            student_info = self.face_recognizer.get_student_info(student_id)
            now = datetime.datetime.now()

            # Format thời gian: giờ -> ngày
            time_str = now.strftime("%H:%M:%S %d/%m/%Y")
            datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")

            session_id = self.session_combo.currentData()
            status = self.type_combo.currentText().replace("🔵 ", "").replace("🔴 ", "")

            if not session_id:
                QtWidgets.QMessageBox.warning(self, "⚠️ Thông báo", "Vui lòng chọn buổi học trước khi điểm danh!")
                return

            # Lưu điểm danh
            self.attendance.add_attendance_record(session_id, student_id, datetime_str, status)

            # Thông báo thành công
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setWindowTitle("✅ Điểm danh thành công")
            msg.setText(f"Sinh viên {student_info.get('TenSV', student_name)} đã điểm danh thành công!")
            msg.setDetailedText(f"Thời gian: {time_str}\nLoại: {status}")
            msg.exec_()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "❌ Lỗi", f"Không thể xử lý điểm danh: {str(e)}")

    def stop_camera(self):
        """Dừng camera"""
        try:
            if self.camera_running and self.timer:
                self.timer.stop()
                self.timer = None

            if self.cap:
                self.cap.release()
                self.cap = None

            self.camera_label.clear()
            self.camera_label.setText("📷 Camera đã dừng\n\nBấm 'Mở Camera' để bắt đầu lại")
            self.camera_running = False

            self.open_btn.setEnabled(True)
            self.close_btn.setEnabled(False)
            self.attendance_btn.setEnabled(False)  # Disable nút điểm danh
            self.current_student = None  # Reset thông tin sinh viên
        except Exception as e:
            print(f"Lỗi stop_camera: {str(e)}")

    def closeEvent(self, event):
        """Xử lý khi đóng ứng dụng"""
        self.stop_camera()
        event.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    # Thiết lập icon cho ứng dụng (nếu có)
    app.setApplicationName("Hệ thống điểm danh khuôn mặt")
    app.setOrganizationName("Your Organization")

    window = AttendanceUI()
    window.show()
    sys.exit(app.exec_())