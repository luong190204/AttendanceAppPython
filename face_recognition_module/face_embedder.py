# face_recognition_module\face_embedder.py
import cv2
import face_recognition
import numpy as np
import os
import sys
import time
import threading
from typing import List, Optional, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Thêm đường dẫn thư mục gốc của project vào sys.path để import config và database
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from database.student_repository import StudentRepository
    from config import DB_CONFIG
except ImportError as e:
    logger.error(f"Không thể import module cần thiết: {e}")
    raise


class FaceEmbedder:
    def __init__(self):
        """Khởi tạo FaceEmbedder với các cấu hình tối ưu"""
        try:
            self.student_repo = StudentRepository()
            self.known_face_encodings = []
            self.known_face_ids = []

            # Cấu hình camera
            self.camera_width = 640
            self.camera_height = 480
            self.frame_rate = 30

            # Cấu hình face recognition
            self.face_detection_model = 'hog'  # 'hog' nhanh hơn 'cnn' nhưng ít chính xác hơn
            self.num_jitters = 1  # Giảm từ mặc định để tăng tốc độ
            self.tolerance = 0.6  # Độ chính xác nhận diện

            # Threading cho việc xử lý ảnh
            self.processing_lock = threading.Lock()

            self.load_known_faces()

        except Exception as e:
            logger.error(f"Lỗi khởi tạo FaceEmbedder: {e}")
            raise

    def load_known_faces(self):
        """
        Load tất cả embedding khuôn mặt đã lưu từ database vào bộ nhớ.
        """
        self.known_face_encodings = []
        self.known_face_ids = []

        try:
            raw_data = self.student_repo.get_all_face_embeddings()

            for student_id, embedding_blob in raw_data:
                try:
                    embedding_array = np.frombuffer(embedding_blob, dtype=np.float32)

                    if embedding_array.shape != (128,):
                        logger.warning(f"Embedding sai định dạng cho {student_id}: {embedding_array.shape}")
                        continue

                    self.known_face_encodings.append(embedding_array)
                    self.known_face_ids.append(student_id)

                except Exception as e:
                    logger.warning(f"Lỗi khi xử lý embedding cho sinh viên {student_id}: {e}")

            logger.info(f"Đã load {len(self.known_face_encodings)} khuôn mặt từ database.")

        except Exception as e:
            logger.error(f"Lỗi khi load known faces từ database: {e}")

    def _initialize_camera(self, camera_index: int = 0) -> Optional[cv2.VideoCapture]:
        """
        Khởi tạo camera với các cấu hình tối ưu
        """
        try:
            video_capture = cv2.VideoCapture(camera_index)

            if not video_capture.isOpened():
                logger.error("Không thể mở camera. Kiểm tra kết nối camera.")
                return None

            # Cấu hình camera để tối ưu hiệu suất
            video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
            video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
            video_capture.set(cv2.CAP_PROP_FPS, self.frame_rate)
            video_capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Giảm buffer để giảm độ trễ

            logger.info(f"Camera đã được khởi tạo với độ phân giải {self.camera_width}x{self.camera_height}")
            return video_capture

        except Exception as e:
            logger.error(f"Lỗi khởi tạo camera: {e}")
            return None

    def detect_and_encode_faces(self, rgb_frame: np.ndarray) -> List[np.ndarray]:
        """
        Phát hiện và mã hóa khuôn mặt từ frame RGB
        """
        try:
            # Giảm kích thước ảnh để tăng tốc độ xử lý
            small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.5, fy=0.5)

            # Tìm vị trí khuôn mặt
            face_locations = face_recognition.face_locations(
                small_frame,
                model=self.face_detection_model
            )

            if not face_locations:
                return []

            # Scale lại tọa độ về kích thước gốc
            face_locations = [(top * 2, right * 2, bottom * 2, left * 2) for (top, right, bottom, left) in
                              face_locations]

            # Mã hóa khuôn mặt
            face_encodings = face_recognition.face_encodings(
                rgb_frame,
                face_locations,
                num_jitters=self.num_jitters
            )

            return face_encodings

        except Exception as e:
            logger.error(f"Lỗi khi xử lý khuôn mặt: {e}")
            return []

    def _save_sample_image(self, frame: np.ndarray, student_id: str, sample_num: int, save_path: str) -> str:
        """
        Lưu ảnh mẫu với xử lý lỗi
        """
        try:
            if not os.path.exists(save_path):
                os.makedirs(save_path, exist_ok=True)

            timestamp = int(time.time())
            filename = f"{student_id}_{sample_num}_{timestamp}.jpg"
            image_path = os.path.join(save_path, filename)

            success = cv2.imwrite(image_path, frame)
            if success:
                logger.info(f"Đã lưu ảnh: {image_path}")
                return image_path
            else:
                logger.error(f"Không thể lưu ảnh: {image_path}")
                return ""

        except Exception as e:
            logger.error(f"Lỗi khi lưu ảnh: {e}")
            return ""

    def capture_and_extract_face_embedding(self,
                                           student_id: str,
                                           num_samples: int = 5,
                                           save_path: str = "assets/student_faces",
                                           camera_index: int = 0) -> Optional[List[np.ndarray]]:
        """
        Chụp ảnh từ camera, phát hiện và trích xuất embedding khuôn mặt của một sinh viên.
        Phiên bản tối ưu với xử lý lỗi tốt hơn và hiệu suất cải thiện.

        Args:
            student_id (str): Mã sinh viên để gán cho khuôn mặt.
            num_samples (int): Số lượng ảnh khuôn mặt muốn thu thập.
            save_path (str): Đường dẫn để lưu ảnh gốc.
            camera_index (int): Index của camera (mặc định 0).

        Returns:
            List[np.ndarray]: Danh sách các embedding đã được lưu vào CSDL.
            None nếu không trích xuất được.
        """

        # Kiểm tra input
        if not student_id or not student_id.strip():
            logger.error("Student ID không hợp lệ")
            return None

        if num_samples <= 0:
            logger.error("Số lượng mẫu phải lớn hơn 0")
            return None

        # Khởi tạo camera
        video_capture = self._initialize_camera(camera_index)
        if not video_capture:
            return None

        face_embeddings = []
        samples_collected = 0
        last_capture_time = 0
        capture_interval = 1.0  # Khoảng cách tối thiểu giữa các lần chụp (giây)

        logger.info(f"Bắt đầu thu thập {num_samples} mẫu khuôn mặt cho sinh viên {student_id}")
        print(f"\n=== THU THẬP KHUÔN MẶT ===")
        print(f"Sinh viên: {student_id}")
        print(f"Mục tiêu: {num_samples} mẫu")
        print(f"Hướng dẫn:")
        print("- Nhìn thẳng vào camera")
        print("- Giữ khuôn mặt ổn định trong khung hình")
        print("- Nhấn 'q' để thoát, 'c' để chụp thủ công")
        print("- Tự động chụp khi phát hiện khuôn mặt rõ ràng\n")

        try:
            while samples_collected < num_samples:
                ret, frame = video_capture.read()
                if not ret:
                    logger.error("Không thể đọc khung hình từ camera")
                    break

                current_time = time.time()

                # Chuyển đổi màu BGR sang RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Phát hiện và mã hóa khuôn mặt
                face_encodings = self.detect_and_encode_faces(rgb_frame)
                face_locations = face_recognition.face_locations(rgb_frame, model=self.face_detection_model)

                # Vẽ khung hình và thông tin
                display_frame = frame.copy()

                # Vẽ hình chữ nhật quanh khuôn mặt
                for (top, right, bottom, left) in face_locations:
                    cv2.rectangle(display_frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(display_frame, "Face Detected", (left, top - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # Hiển thị thông tin trạng thái
                status_text = f"Mau: {samples_collected}/{num_samples}"
                cv2.putText(display_frame, status_text, (20, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                if face_encodings and len(face_encodings) > 0:
                    cv2.putText(display_frame, "Khuon mat phat hien!", (20, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                    # Tự động chụp nếu đủ thời gian chờ
                    if current_time - last_capture_time >= capture_interval:
                        face_encoding = face_encodings[0]  # Lấy khuôn mặt đầu tiên

                        if face_encoding.size == 128:  # Kiểm tra kích thước encoding hợp lệ
                            # Lưu ảnh
                            image_path = self._save_sample_image(frame, student_id,
                                                                 samples_collected + 1, save_path)

                            if image_path:
                                # Lưu embedding vào CSDL
                                face_encoding = face_encoding.astype(np.float32)
                                embedding_blob = face_encoding.tobytes()

                                with self.processing_lock:
                                    if self.student_repo.add_face_embedding(student_id, image_path, embedding_blob):
                                        face_embeddings.append(face_encoding)
                                        samples_collected += 1
                                        last_capture_time = current_time

                                        print(f"✓ Đã thu thập mẫu {samples_collected}/{num_samples}")
                                        logger.info(f"Đã lưu embedding mẫu {samples_collected} vào CSDL")
                                    else:
                                        logger.error(f"Lỗi khi lưu embedding mẫu {samples_collected + 1} vào CSDL")
                else:
                    cv2.putText(display_frame, "Khong tim thay khuon mat", (20, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                # Hiển thị khung hình
                cv2.imshow('Thu thap khuon mat - Nhan Q de thoat', display_frame)

                # Xử lý phím bấm
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    logger.info("Người dùng đã hủy quá trình thu thập")
                    break
                elif key == ord('c') and face_encodings:  # Chụp thủ công
                    if current_time - last_capture_time >= 0.5:  # Tránh chụp liên tục
                        logger.info("Chụp thủ công được kích hoạt")

        except KeyboardInterrupt:
            logger.info("Quá trình thu thập bị ngắt bởi người dùng")
        except Exception as e:
            logger.error(f"Lỗi trong quá trình thu thập: {e}")
        finally:
            # Dọn dẹp tài nguyên
            video_capture.release()
            cv2.destroyAllWindows()

        # Báo cáo kết quả
        if samples_collected > 0:
            print(f"\n=== KẾT QUÁ ===")
            print(f"✓ Hoàn tất thu thập {samples_collected}/{num_samples} mẫu khuôn mặt cho {student_id}")
            logger.info(f"Thu thập thành công {samples_collected} mẫu khuôn mặt")

            # Cập nhật lại danh sách khuôn mặt đã biết
            self.load_known_faces()
            return face_embeddings
        else:
            print(f"\n=== THẤT BẠI ===")
            print("✗ Không thu thập được mẫu khuôn mặt nào")
            logger.warning("Không thu thập được mẫu khuôn mặt nào")
            return None

    def recognize_face(self, face_encoding: np.ndarray) -> Optional[str]:
        """
        Nhận diện khuôn mặt từ encoding

        Args:
            face_encoding: Encoding của khuôn mặt cần nhận diện

        Returns:
            str: Mã sinh viên nếu nhận diện được, None nếu không
        """
        if not self.known_face_encodings:
            logger.warning("Chưa có dữ liệu khuôn mặt nào để so sánh")
            return None

        try:
            # So sánh với tất cả khuôn mặt đã biết
            matches = face_recognition.compare_faces(
                self.known_face_encodings,
                face_encoding,
                tolerance=self.tolerance
            )

            if True in matches:
                match_index = matches.index(True)
                return self.known_face_ids[match_index]

            return None

        except Exception as e:
            logger.error(f"Lỗi trong quá trình nhận diện: {e}")
            return None

    def get_stats(self) -> dict:
        """
        Trả về thống kê về dữ liệu khuôn mặt đã lưu
        """
        return {
            'total_faces': len(self.known_face_encodings),
            'unique_students': len(set(self.known_face_ids)),
            'students_list': list(set(self.known_face_ids))
        }



# --- Phần kiểm thử (có thể xóa sau khi tích hợp vào UI) ---
if __name__ == '__main__':
    # Đảm bảo MySQL server đang chạy và DB/bảng đã được tạo, config.py đã đúng
    # Đảm bảo SV001 đã tồn tại trong bảng SinhVien (có thể thêm bằng StudentRepository)

    # Kết nối DB trước khi khởi tạo FaceEmbedder
    from database.connection_manager import ConnectionManager

    conn_manager = ConnectionManager()
    if not conn_manager.connect():
        print("Không thể kết nối CSDL, không thể chạy test FaceEmbedder.")
        sys.exit(1)

    embedder = FaceEmbedder()

    # Thử thu thập và lưu embedding cho một sinh viên
    # Thay 'SV001' bằng Mã SV thực tế của bạn
    # Bạn có thể gọi student_repo.add_student() ở đây nếu chưa có SV001
    student_repo = StudentRepository()
    if not student_repo.get_student_by_id('SV006'):
        student_repo.add_student('SV006', 'Dinh Luong', '2004-01-15', 'Nam', 'Ha Noi', 'luong@example.com',
                                 '0912345678')
        print("Đã thêm SV006 cho mục đích kiểm thử.")

    print("\nBắt đầu quá trình thu thập khuôn mặt cho SV006...")
    embeddings = embedder.capture_and_extract_face_embedding('SV006', num_samples=3)

    if embeddings:
        print(f"Đã trích xuất và lưu thành công {len(embeddings)} embedding cho SV006.")
        # Sau khi lưu, bạn có thể tải lại để kiểm tra
        embedder.load_known_faces()
        print(f"Số lượng khuôn mặt đã tải lại: {len(embedder.known_face_encodings)}")
    else:
        print("Không thể thu thập và lưu embedding cho SV006.")

    conn_manager.disconnect()
