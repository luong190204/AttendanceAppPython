# config.py

DB_CONFIG = {
    'host': 'localhost',  # Địa chỉ MySQL server, thường là 'localhost'
    'user': 'root',       # Username mặc định của MySQL
    'password': '', # Thay bằng mật khẩu MySQL của bạn
    'database': 'attendance_app_python', # Tên cơ sở dữ liệu bạn đã tạo
    'port': 3306 # Cổng mặc định của MySQL,
}

# Các cấu hình khác có thể thêm sau này
# FACE_RECOGNITION_THRESHOLD = 0.6 # Ngưỡng nhận diện khuôn mặt
# DEFAULT_IMAGE_DIR = "assets/student_faces"