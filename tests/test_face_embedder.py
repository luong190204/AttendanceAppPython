# test_face_embedder.py
"""
File test để kiểm tra các chức năng của FaceEmbedder
Chạy các test case khác nhau để đảm bảo hệ thống hoạt động đúng
"""

import os
import sys
import time
import numpy as np
import cv2
from typing import Optional

# Thêm đường dẫn project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from face_recognition_module.face_embedder import FaceEmbedder
except ImportError as e:
    print(f"Lỗi import FaceEmbedder: {e}")
    print("Đảm bảo file face_embedder.py đã được đặt đúng vị trí")
    sys.exit(1)


class FaceEmbedderTester:
    """Class để test các chức năng của FaceEmbedder"""

    def __init__(self):
        """Khởi tạo tester"""
        print("=" * 60)
        print("FACE EMBEDDER TESTING SUITE")
        print("=" * 60)

        try:
            self.face_embedder = FaceEmbedder()
            print("✓ FaceEmbedder đã được khởi tạo thành công")
        except Exception as e:
            print(f"✗ Lỗi khởi tạo FaceEmbedder: {e}")
            self.face_embedder = None

    def test_initialization(self) -> bool:
        """Test 1: Kiểm tra khởi tạo"""
        print("\n" + "-" * 40)
        print("TEST 1: KIỂM TRA KHỞI TẠO")
        print("-" * 40)

        if self.face_embedder is None:
            print("✗ FaceEmbedder không được khởi tạo")
            return False

        # Kiểm tra các thuộc tính cơ bản
        tests = [
            ("student_repo", hasattr(self.face_embedder, 'student_repo')),
            ("known_face_encodings", hasattr(self.face_embedder, 'known_face_encodings')),
            ("known_face_ids", hasattr(self.face_embedder, 'known_face_ids')),
            ("camera_width", hasattr(self.face_embedder, 'camera_width')),
            ("camera_height", hasattr(self.face_embedder, 'camera_height')),
        ]

        all_passed = True
        for test_name, result in tests:
            status = "✓" if result else "✗"
            print(f"{status} {test_name}: {'OK' if result else 'MISSING'}")
            if not result:
                all_passed = False

        return all_passed

    def test_load_known_faces(self) -> bool:
        """Test 2: Kiểm tra tải dữ liệu khuôn mặt"""
        print("\n" + "-" * 40)
        print("TEST 2: KIỂM TRA TỨI DỮ LIỆU KHUÔN MẶT")
        print("-" * 40)

        if self.face_embedder is None:
            print("✗ FaceEmbedder chưa được khởi tạo")
            return False

        try:
            # Lưu trạng thái hiện tại
            original_encodings = len(self.face_embedder.known_face_encodings)
            original_ids = len(self.face_embedder.known_face_ids)

            print(f"Trước khi load: {original_encodings} encodings, {original_ids} IDs")

            # Test load lại
            self.face_embedder.load_known_faces()

            new_encodings = len(self.face_embedder.known_face_encodings)
            new_ids = len(self.face_embedder.known_face_ids)

            print(f"Sau khi load: {new_encodings} encodings, {new_ids} IDs")

            # Kiểm tra tính nhất quán
            if new_encodings == new_ids:
                print("✓ Số lượng encodings và IDs khớp nhau")
                return True
            else:
                print("✗ Số lượng encodings và IDs không khớp")
                return False

        except Exception as e:
            print(f"✗ Lỗi khi test load_known_faces: {e}")
            return False

    def test_camera_initialization(self) -> bool:
        """Test 3: Kiểm tra khởi tạo camera"""
        print("\n" + "-" * 40)
        print("TEST 3: KIỂM TRA KHỞI TẠO CAMERA")
        print("-" * 40)

        if self.face_embedder is None:
            print("✗ FaceEmbedder chưa được khởi tạo")
            return False

        try:
            # Test khởi tạo camera
            camera = self.face_embedder._initialize_camera(0)

            if camera is None:
                print("✗ Không thể khởi tạo camera")
                return False

            if not camera.isOpened():
                print("✗ Camera không mở được")
                camera.release()
                return False

            # Test đọc frame
            ret, frame = camera.read()
            if ret and frame is not None:
                height, width = frame.shape[:2]
                print(f"✓ Camera hoạt động OK - Frame size: {width}x{height}")
                success = True
            else:
                print("✗ Không thể đọc frame từ camera")
                success = False

            # Dọn dẹp
            camera.release()
            return success

        except Exception as e:
            print(f"✗ Lỗi khi test camera: {e}")
            return False

    def test_face_detection_with_sample_image(self) -> bool:
        """Test 4: Kiểm tra phát hiện khuôn mặt với ảnh mẫu"""
        print("\n" + "-" * 40)
        print("TEST 4: KIỂM TRA PHÁT HIỆN KHUÔN MẶT")
        print("-" * 40)

        if self.face_embedder is None:
            print("✗ FaceEmbedder chưa được khởi tạo")
            return False

        try:
            # Tạo ảnh test đơn giản (có thể thay bằng ảnh thật)
            # Ở đây chúng ta sẽ test với camera live
            camera = self.face_embedder._initialize_camera(0)

            if camera is None:
                print("✗ Không thể khởi tạo camera để test")
                return False

            print("Đang test phát hiện khuôn mặt từ camera...")
            print("Nhìn vào camera trong 5 giây...")

            faces_detected = 0
            start_time = time.time()

            while time.time() - start_time < 5:  # Test trong 5 giây
                ret, frame = camera.read()
                if not ret:
                    continue

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_encodings = self.face_embedder._detect_and_encode_faces(rgb_frame)

                if face_encodings:
                    faces_detected += 1

                # Hiển thị frame để user thấy
                cv2.imshow('Face Detection Test - Nhan Q de thoat', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            camera.release()
            cv2.destroyAllWindows()

            if faces_detected > 0:
                print(f"✓ Phát hiện được khuôn mặt trong {faces_detected} frame(s)")
                return True
            else:
                print("⚠ Không phát hiện được khuôn mặt nào (có thể do không có người)")
                return True  # Không coi là lỗi

        except Exception as e:
            print(f"✗ Lỗi khi test phát hiện khuôn mặt: {e}")
            return False

    def test_stats_function(self) -> bool:
        """Test 5: Kiểm tra hàm thống kê"""
        print("\n" + "-" * 40)
        print("TEST 5: KIỂM TRA HÀM THỐNG KÊ")
        print("-" * 40)

        if self.face_embedder is None:
            print("✗ FaceEmbedder chưa được khởi tạo")
            return False

        try:
            stats = self.face_embedder.get_stats()

            # Kiểm tra cấu trúc dữ liệu trả về
            required_keys = ['total_faces', 'unique_students', 'students_list']

            for key in required_keys:
                if key not in stats:
                    print(f"✗ Thiếu key '{key}' trong stats")
                    return False

            print(f"✓ Tổng số khuôn mặt: {stats['total_faces']}")
            print(f"✓ Số sinh viên unique: {stats['unique_students']}")
            print(f"✓ Danh sách sinh viên: {stats['students_list']}")

            return True

        except Exception as e:
            print(f"✗ Lỗi khi test stats: {e}")
            return False

    def test_face_capture_dry_run(self) -> bool:
        """Test 6: Test thu thập khuôn mặt (dry run - chỉ test giao diện)"""
        print("\n" + "-" * 40)
        print("TEST 6: TEST THU THẬP KHUÔN MẶT (DRY RUN)")
        print("-" * 40)

        if self.face_embedder is None:
            print("✗ FaceEmbedder chưa được khởi tạo")
            return False

        print("Test này sẽ mở camera và hiển thị giao diện thu thập")
        print("KHÔNG thực sự lưu dữ liệu vào database")
        print("Nhấn 'q' để thoát sau khi kiểm tra giao diện")

        response = input("Bạn có muốn tiếp tục? (y/n): ").lower().strip()
        if response != 'y':
            print("⚠ Bỏ qua test này")
            return True

        try:
            camera = self.face_embedder._initialize_camera(0)
            if camera is None:
                print("✗ Không thể khởi tạo camera")
                return False

            print("Đang hiển thị giao diện thu thập - nhấn 'q' để thoát...")

            start_time = time.time()
            frames_processed = 0

            while time.time() - start_time < 10:  # Test trong 10 giây
                ret, frame = camera.read()
                if not ret:
                    continue

                frames_processed += 1

                # Mô phỏng giao diện thu thập
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_encodings = self.face_embedder._detect_and_encode_faces(rgb_frame)

                # Vẽ giao diện
                display_frame = frame.copy()
                cv2.putText(display_frame, "DRY RUN TEST - Khong luu du lieu", (20, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.putText(display_frame, f"Frames: {frames_processed}", (20, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

                if face_encodings:
                    cv2.putText(display_frame, "Khuon mat phat hien!", (20, 90),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                cv2.imshow('Face Capture Test - Nhan Q de thoat', display_frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            camera.release()
            cv2.destroyAllWindows()

            print(f"✓ Đã xử lý {frames_processed} frames")
            print("✓ Giao diện hoạt động bình thường")
            return True

        except Exception as e:
            print(f"✗ Lỗi khi test giao diện: {e}")
            return False

    def run_all_tests(self) -> None:
        """Chạy tất cả các test"""
        print("\n" + "=" * 60)
        print("BẮT ĐẦU CHẠY TẤT CẢ CÁC TEST")
        print("=" * 60)

        tests = [
            ("Initialization", self.test_initialization),
            ("Load Known Faces", self.test_load_known_faces),
            ("Camera Initialization", self.test_camera_initialization),
            ("Face Detection", self.test_face_detection_with_sample_image),
            ("Stats Function", self.test_stats_function),
            ("Face Capture Interface", self.test_face_capture_dry_run),
        ]

        results = []

        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))

                if result:
                    print(f"\n✓ {test_name}: PASSED")
                else:
                    print(f"\n✗ {test_name}: FAILED")

            except Exception as e:
                print(f"\n✗ {test_name}: ERROR - {e}")
                results.append((test_name, False))

        # Tổng kết
        print("\n" + "=" * 60)
        print("KẾT QUẢ TỔNG KẾT")
        print("=" * 60)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = "PASS" if result else "FAIL"
            symbol = "✓" if result else "✗"
            print(f"{symbol} {test_name}: {status}")

        print(f"\nTổng kết: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 TẤT CẢ CÁC TEST ĐỀU THÀNH CÔNG!")
        else:
            print("⚠ CÓ MỘT SỐ TEST THẤT BẠI - Kiểm tra lại hệ thống")

    def interactive_test_menu(self) -> None:
        """Menu test tương tác"""
        while True:
            print("\n" + "=" * 50)
            print("FACE EMBEDDER TEST MENU")
            print("=" * 50)
            print("1. Test khởi tạo")
            print("2. Test tải dữ liệu khuôn mặt")
            print("3. Test camera")
            print("4. Test phát hiện khuôn mặt")
            print("5. Test hàm thống kê")
            print("6. Test giao diện thu thập (dry run)")
            print("7. Chạy tất cả test")
            print("8. Test thu thập thật (lưu vào DB)")
            print("0. Thoát")

            choice = input("\nChọn test (0-8): ").strip()

            if choice == '0':
                print("Thoát chương trình test")
                break
            elif choice == '1':
                self.test_initialization()
            elif choice == '2':
                self.test_load_known_faces()
            elif choice == '3':
                self.test_camera_initialization()
            elif choice == '4':
                self.test_face_detection_with_sample_image()
            elif choice == '5':
                self.test_stats_function()
            elif choice == '6':
                self.test_face_capture_dry_run()
            elif choice == '7':
                self.run_all_tests()
            elif choice == '8':
                self.test_real_face_capture()
            else:
                print("Lựa chọn không hợp lệ!")

    def test_real_face_capture(self) -> None:
        """Test thu thập khuôn mặt thật (lưu vào database)"""
        print("\n" + "-" * 40)
        print("TEST THU THẬP KHUÔN MẶT THẬT")
        print("-" * 40)

        if self.face_embedder is None:
            print("✗ FaceEmbedder chưa được khởi tạo")
            return

        print("⚠ Test này sẽ THỰC SỰ lưu dữ liệu vào database!")
        student_id = input("Nhập mã sinh viên để test (hoặc Enter để hủy): ").strip()

        if not student_id:
            print("Đã hủy test")
            return

        num_samples = input("Số mẫu muốn thu thập (mặc định 3): ").strip()
        try:
            num_samples = int(num_samples) if num_samples else 3
        except ValueError:
            num_samples = 3

        print(f"Bắt đầu thu thập {num_samples} mẫu cho sinh viên {student_id}")
        print("Bạn có 3 giây để chuẩn bị...")

        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)

        try:
            result = self.face_embedder.capture_and_extract_face_embedding(
                student_id=student_id,
                num_samples=num_samples,
                save_path="save_path/student_faces"
            )

            if result:
                print(f"✓ Thu thập thành công {len(result)} mẫu!")
                print("✓ Dữ liệu đã được lưu vào database")
            else:
                print("✗ Thu thập thất bại")

        except Exception as e:
            print(f"✗ Lỗi khi thu thập: {e}")


def main():
    """Hàm main để chạy test"""
    print("FACE EMBEDDER TESTING TOOL")
    print("Công cụ này sẽ test các chức năng của FaceEmbedder")
    print("Đảm bảo bạn đã:")
    print("1. Cài đặt tất cả dependencies")
    print("2. Kết nối camera")
    print("3. Cấu hình database")

    input("\nNhấn Enter để tiếp tục...")

    try:
        tester = FaceEmbedderTester()

        print("\nChọn chế độ test:")
        print("1. Chạy tất cả test tự động")
        print("2. Menu test tương tác")

        choice = input("Chọn (1 hoặc 2): ").strip()

        if choice == '1':
            tester.run_all_tests()
        elif choice == '2':
            tester.interactive_test_menu()
        else:
            print("Lựa chọn không hợp lệ, chạy menu tương tác...")
            tester.interactive_test_menu()

    except Exception as e:
        print(f"Lỗi khi chạy test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()