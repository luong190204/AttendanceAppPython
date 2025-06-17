# face_recognition_module\face_recognizer.py
import cv2
import face_recognition
import numpy as np
import os
import sys

# Thêm đường dẫn thư mục gốc của project vào sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from database.student_repository import StudentRepository
from config import DB_CONFIG


class FaceRecognizer:
    def __init__(self, recognition_threshold=0.6):
        """
        Khởi tạo Face Recognizer

        Args:
            recognition_threshold (float): Ngưỡng nhận diện (0.0-1.0, càng nhỏ càng nghiêm ngặt)
        """
        self.student_repo = StudentRepository()
        self.known_face_encodings = []
        self.known_face_ids = []
        self.known_student_names = []
        self.recognition_threshold = recognition_threshold
        self.load_known_faces()

    def load_known_faces(self):
        """
        Tải dữ liệu khuôn mặt đã mã hóa từ DB và lưu vào bộ nhớ.
        """
        print("Đang tải dữ liệu khuôn mặt từ cơ sở dữ liệu...")

        try:
            embeddings_from_db = self.student_repo.get_all_face_embeddings()

            if not embeddings_from_db:
                print("⚠️ Không có dữ liệu khuôn mặt trong CSDL.")
                return

            # Reset bộ nhớ
            self.known_face_encodings = []
            self.known_face_ids = []
            self.known_student_names = []

            successful = 0
            failed = 0

            for row in embeddings_from_db:
                # row có thể là tuple hoặc dict
                if isinstance(row, dict):
                    ma_sv = row["MaSV_FK"]
                    encoding_blob = row["DuLieuMaHoa"]
                else:
                    ma_sv, encoding_blob = row

                try:
                    if encoding_blob is None:
                        raise ValueError("encoding_blob is None")

                    face_encoding = np.frombuffer(encoding_blob, dtype=np.float32)

                    if face_encoding.shape != (128,):
                        raise ValueError(f"Invalid shape: {face_encoding.shape}")

                    student = self.student_repo.get_student_by_id(ma_sv)
                    if not student:
                        raise ValueError(f"Không tìm thấy sinh viên {ma_sv}")

                    name = student["TenSV"]  # hoặc student["TenSV"] nếu là dict

                    self.known_face_encodings.append(face_encoding)
                    self.known_face_ids.append(ma_sv)
                    self.known_student_names.append(name)

                    successful += 1

                except Exception as e:
                    import traceback
                    print(f"⚠️ Lỗi xử lý sinh viên {ma_sv}: {type(e).__name__} - {e}")
                    traceback.print_exc()
                    failed += 1

            print(f"✅ Tải xong: {successful} thành công, {failed} lỗi.")

        except Exception as e:
            print(f"❌ Lỗi tổng khi tải dữ liệu khuôn mặt: {e}")

    def recognize_face_from_image(self, image_path):
        """
        Nhận diện khuôn mặt từ một ảnh

        Args:
            image_path (str): Đường dẫn đến ảnh

        Returns:
            list: Danh sách các sinh viên được nhận diện [(ma_sv, ten_sv, confidence), ...]
        """
        if not os.path.exists(image_path):
            print(f"Không tìm thấy ảnh: {image_path}")
            return []

        try:
            # Đọc ảnh
            image = face_recognition.load_image_file(image_path)

            # Tìm khuôn mặt trong ảnh
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)

            if not face_encodings:
                print("Không tìm thấy khuôn mặt nào trong ảnh.")
                return []

            results = []
            for face_encoding in face_encodings:
                recognized_student = self._compare_face_with_database(face_encoding)
                if recognized_student:
                    results.append(recognized_student)

            return results

        except Exception as e:
            print(f"Lỗi khi xử lý ảnh {image_path}: {e}")
            return []

    def recognize_faces_in_frame(self, frame):
        """
        Nhận diện khuôn mặt trong một khung hình video (frame)

        Args:
            frame (numpy.array): Khung hình từ camera (BGR format)

        Returns:
            list: Danh sách [(ma_sv, ten_sv, face_location, confidence, face_img), ...]
                  face_location: (top, right, bottom, left)
                  face_img: ảnh khuôn mặt được cắt từ frame (dạng numpy)
        """
        if not self.known_face_encodings:
            return []

        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)

            if not face_locations:
                return []

            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            results = []
            for face_encoding, face_location in zip(face_encodings, face_locations):
                recognized_student = self._compare_face_with_database(face_encoding)

                (top, right, bottom, left) = face_location
                # Cắt ảnh khuôn mặt từ frame gốc (vì frame gốc đang là BGR để hiển thị được bằng Qt)
                face_img = frame[top:bottom, left:right]

                if recognized_student:
                    ma_sv, ten_sv, confidence = recognized_student
                    results.append((ma_sv, ten_sv, face_location, confidence, face_img))
                else:
                    results.append((None, "Unknown", face_location, 0.0, face_img))

            return results

        except Exception as e:
            print(f"Lỗi khi nhận diện khuôn mặt trong frame: {e}")
            return []

    def _compare_face_with_database(self, face_encoding):
        """
        So sánh một khuôn mặt với tất cả khuôn mặt trong database

        Args:
            face_encoding (numpy.array): Mã hóa khuôn mặt cần so sánh

        Returns:
            tuple: (ma_sv, ten_sv, confidence) hoặc None nếu không nhận diện được
        """
        if not self.known_face_encodings:
            return None

        try:
            # Tính khoảng cách với tất cả khuôn mặt đã biết
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)

            # Tìm khuôn mặt gần nhất
            best_match_index = np.argmin(face_distances)
            best_distance = face_distances[best_match_index]

            # Kiểm tra xem có đạt ngưỡng nhận diện không
            if best_distance < self.recognition_threshold:
                confidence = (1.0 - best_distance) * 100  # Chuyển thành phần trăm

                ma_sv = self.known_face_ids[best_match_index]
                ten_sv = self.known_student_names[best_match_index]

                return (ma_sv, ten_sv, round(confidence, 2))

            return None

        except Exception as e:
            print(f"Lỗi khi so sánh khuôn mặt: {e}")
            return None

    def get_student_info(self, ma_sv):
        """
        Lấy thông tin chi tiết sinh viên theo mã số

        Args:
            ma_sv (str): Mã số sinh viên

        Returns:
            tuple: Thông tin sinh viên hoặc None
        """
        try:
            return self.student_repo.get_student_by_id(ma_sv)
        except Exception as e:
            print(f"Lỗi khi lấy thông tin sinh viên {ma_sv}: {e}")
            return None

    def update_recognition_threshold(self, new_threshold):
        """
        Cập nhật ngưỡng nhận diện

        Args:
            new_threshold (float): Ngưỡng mới (0.0-1.0)
        """
        if 0.0 <= new_threshold <= 1.0:
            self.recognition_threshold = new_threshold
            print(f"Đã cập nhật ngưỡng nhận diện: {new_threshold}")
        else:
            print("Ngưỡng nhận diện phải nằm trong khoảng 0.0-1.0")

    def reload_known_faces(self):
        """
        Tải lại dữ liệu khuôn mặt từ database
        """
        print("Đang tải lại dữ liệu khuôn mặt...")
        self.load_known_faces()

    def get_statistics(self):
        """
        Lấy thống kê về dữ liệu nhận diện

        Returns:
            dict: Thống kê
        """
        return {
            'total_known_faces': len(self.known_face_encodings),
            'recognition_threshold': self.recognition_threshold,
            'known_students': list(zip(self.known_face_ids, self.known_student_names))
        }


# --- Demo và Test ---
if __name__ == '__main__':
    from database.connection_manager import ConnectionManager

    # Kiểm tra kết nối database
    conn_manager = ConnectionManager()
    if not conn_manager.connect():
        print("Không thể kết nối đến cơ sở dữ liệu.")
        sys.exit(1)

    # Khởi tạo Face Recognizer
    recognizer = FaceRecognizer(recognition_threshold=0.6)

    # Kiểm tra dữ liệu
    stats = recognizer.get_statistics()
    print(f"\n=== THỐNG KÊ ===")
    print(f"Tổng số khuôn mặt đã biết: {stats['total_known_faces']}")
    print(f"Ngưỡng nhận diện: {stats['recognition_threshold']}")

    if stats['total_known_faces'] == 0:
        print("\nKhông có dữ liệu khuôn mặt để nhận diện.")
        print("Vui lòng chạy face_embedder.py trước để thêm dữ liệu khuôn mặt.")
        conn_manager.disconnect()
        sys.exit(0)

    print(f"\nDanh sách sinh viên có khuôn mặt:")
    for ma_sv, ten_sv in stats['known_students']:
        print(f"  - {ma_sv}: {ten_sv}")

    # Test với camera
    print(f"\n=== DEMO NHẬN DIỆN THỜI GIAN THỰC ===")
    video_capture = cv2.VideoCapture(0)

    if not video_capture.isOpened():
        print("Không thể mở camera.")
        conn_manager.disconnect()
        sys.exit(1)

    print("\nBắt đầu nhận diện khuôn mặt từ camera...")
    print("Nhấn 'q' để thoát, 'r' để reload dữ liệu")

    try:
        while True:
            ret, frame = video_capture.read()
            if not ret:
                print("Không thể đọc frame từ camera.")
                break

            # Nhận diện khuôn mặt trong frame
            recognition_results = recognizer.recognize_faces_in_frame(frame)

            # Hiển thị kết quả trên frame
            for result in recognition_results:
                if len(result) == 4:  # (ma_sv, ten_sv, face_location, confidence)
                    ma_sv, ten_sv, (top, right, bottom, left), confidence = result

                    # Chọn màu dựa trên việc nhận diện
                    color = (0, 255, 0) if ma_sv else (0, 0, 255)  # Xanh lá nếu nhận diện được

                    # Vẽ khung bao quanh khuôn mặt
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

                    # Hiển thị thông tin
                    if ma_sv:
                        label = f"{ten_sv} ({ma_sv})"
                        confidence_text = f"{confidence}%"
                    else:
                        label = "Unknown"
                        confidence_text = ""

                    # Vẽ nền cho text
                    label_height = 35 if confidence_text else 25
                    cv2.rectangle(frame, (left, bottom), (right, bottom + label_height), color, cv2.FILLED)

                    # Hiển thị tên
                    cv2.putText(frame, label, (left + 5, bottom + 15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                    # Hiển thị confidence nếu có
                    if confidence_text:
                        cv2.putText(frame, confidence_text, (left + 5, bottom + 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            # Hiển thị frame
            cv2.imshow('Face Recognition System', frame)

            # Xử lý phím nhấn
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                print("Đang tải lại dữ liệu khuôn mặt...")
                recognizer.reload_known_faces()
                new_stats = recognizer.get_statistics()
                print(f"Đã tải lại {new_stats['total_known_faces']} khuôn mặt.")

    except KeyboardInterrupt:
        print("\nĐã dừng chương trình.")

    finally:
        video_capture.release()
        cv2.destroyAllWindows()
        conn_manager.disconnect()
        print("Đã giải phóng tài nguyên.")