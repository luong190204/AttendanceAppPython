# Hệ thống Điểm danh Sinh viên (Attendance Management System)

## 📝 Giới thiệu

Hệ thống Điểm danh Sinh viên là một ứng dụng quản lý điểm danh dựa trên giao diện người dùng đồ họa (GUI), được phát triển nhằm tự động hóa và tối ưu hóa quy trình điểm danh tại các cơ sở giáo dục. Hệ thống giúp theo dõi chính xác sự hiện diện của sinh viên trong các buổi học, cung cấp báo cáo chi tiết và hỗ trợ quản lý thông tin tài khoản người dùng (sinh viên, giáo viên, quản trị viên).

## ✨ Tính năng chính

* **Quản lý Tài khoản Người dùng:**
    * Hỗ trợ đa vai trò: Quản trị viên (Admin), Giáo viên (Teacher), Sinh viên (Student).
    * Đăng nhập và xác thực người dùng an toàn với mã hóa mật khẩu bcrypt.
    * Quản trị viên có thể thêm, sửa, xóa tài khoản người dùng và phân quyền.
* **Quản lý Sinh viên:**
    * Thêm, sửa, xóa thông tin sinh viên.
    * Tìm kiếm và lọc sinh viên theo nhiều tiêu chí.
* **Quản lý Giáo viên:**
    * Thêm, sửa, xóa thông tin giáo viên.
* **Quản lý Môn học:**
    * Đăng ký môn học và gán giáo viên phụ trách.
* **Quản lý Lớp học:**
    * Tạo và quản lý các lớp học, gán sinh viên vào lớp.
* **Chức năng Điểm danh:**
    * Giao diện thân thiện cho giáo viên thực hiện điểm danh.
    * Ghi nhận trạng thái điểm danh (Có mặt, Vắng mặt, Đi muộn...).
* **Báo cáo và Thống kê:**
    * (Dự kiến) Tạo báo cáo điểm danh theo buổi, theo lớp, theo sinh viên.
    * (Dự kiến) Thống kê tỷ lệ đi học, nghỉ học.

## 🛠️ Công nghệ sử dụng

* **Ngôn ngữ lập trình:** Python 3.9+
* **Thư viện GUI:** PyQt5
* **Hệ quản trị cơ sở dữ liệu:** MySQL (hoặc MariaDB)
* **Driver kết nối CSDL Python:** PyMySQL
* **Mã hóa mật khẩu:** bcrypt
* **Quản lý dự án/Phiên bản:** Git & GitHub

## 📂 Cấu trúc Dự án
```
AttendanceApp/
├── main.py                     # Điểm khởi chạy chính của ứng dụng
├── config.py                   # Cấu hình cơ sở dữ liệu và các hằng số
├── .gitignore                  # Các file/thư mục bị bỏ qua bởi Git
├── README.md                   # File mô tả dự án (bạn đang đọc)
├── ui/                         # Chứa các file giao diện người dùng (PyQt5)
│   ├── login_ui.py             # Giao diện đăng nhập
│   ├── main_window.py          # Cửa sổ chính của ứng dụng sau khi đăng nhập
│   └── ... (các UI khác)
├── database/                   # Chứa các lớp tương tác với cơ sở dữ liệu
│   ├── connection_manager.py   # Quản lý kết nối CSDL (Singleton)
│   ├── base_repository.py      # Lớp cơ sở cho các repository
│   ├── user_repository.py      # Quản lý dữ liệu người dùng
│   ├── student_repository.py   # Quản lý dữ liệu sinh viên
│   ├── teacher_repository.py   # Quản lý dữ liệu giáo viên
│   └── ... (các repository khác)
└── .venv/                      # Môi trường ảo của Python (bị bỏ qua bởi Git)
```
## 🚀 Hướng dẫn cài đặt và chạy

1.  **Clone repository:**
    ```bash
    git clone [https://github.com/your_github_username/AttendanceApp.git](https://github.com/your_github_username/AttendanceApp.git)
    cd AttendanceApp
    ```

2.  **Tạo và kích hoạt môi trường ảo:**
    ```bash
    python -m venv .venv
    # Trên Windows:
    .\.venv\Scripts\activate
    # Trên macOS/Linux:
    source ./.venv/bin/activate
    ```

3.  **Cài đặt các thư viện cần thiết:**
    ```bash
    pip install PyQt5 PyMySQL bcrypt
    ```

4.  **Cấu hình Cơ sở dữ liệu MySQL/MariaDB:**
    * Đảm bảo MySQL/MariaDB Server đang chạy.
    * Tạo một cơ sở dữ liệu mới (ví dụ: `attendance_app_python`).
    * Thực hiện các lệnh SQL để tạo các bảng cần thiết (ví dụ: `TaiKhoan`, `SinhVien`, `GiaoVien`, `MonHoc`, `LopHoc`, `DiemDanh`, v.v.). Dưới đây là ví dụ cấu trúc bảng `TaiKhoan` cơ bản, bạn cần bổ sung các bảng khác theo thiết kế của mình:
        ```sql
        CREATE TABLE TaiKhoan (
            TenDangNhap VARCHAR(50) PRIMARY KEY,
            MatKhau VARCHAR(255) NOT NULL, -- Để lưu mật khẩu băm (hashed password)
            LoaiTaiKhoan ENUM('admin', 'teacher', 'student') NOT NULL,
            MaGV_FK VARCHAR(10), -- Khóa ngoại liên kết với bảng GiaoVien (NULL nếu không phải giáo viên)
            MaSV_FK VARCHAR(10), -- Khóa ngoại liên kết với bảng SinhVien (NULL nếu không phải sinh viên)
            -- Thêm các ràng buộc FOREIGN KEY nếu cần thiết
            -- Ví dụ: FOREIGN KEY (MaGV_FK) REFERENCES GiaoVien(MaGV) ON DELETE SET NULL,
            --         FOREIGN KEY (MaSV_FK) REFERENCES SinhVien(MaSV) ON DELETE SET NULL
            -- Đảm bảo các cột khóa ngoại có thể NULL hoặc có giá trị mặc định phù hợp
        );
        ```
    * Tạo file `config.py` trong thư mục gốc của dự án với nội dung:
        ```python
        # config.py
        DB_CONFIG = {
            'host': 'localhost',             # Hoặc địa chỉ IP của MySQL Server
            'user': 'root',   # Thay thế bằng username MySQL của bạn
            'password': '', # Thay thế bằng password MySQL của bạn
            'database': 'attendance_app_python', # Tên database bạn đã tạo
            'port': 3306                     # Cổng MySQL mặc định
        }
        ```
        *(Hãy thay thế các giá trị `your_mysql_username` và `your_mysql_password` bằng thông tin đăng nhập MySQL của bạn.)*

5.  **Chạy ứng dụng:**
    ```bash
    python main.py
    ```

## 🔑 Sử dụng

* Ứng dụng sẽ hiển thị một hộp thoại chờ trong quá trình kết nối CSDL, sau đó là cửa sổ đăng nhập.
* **Tài khoản demo:**
    * **Username:** `admin`
    * **Password:** `123456`
    * *(Tài khoản này sẽ tự động được tạo nếu chưa tồn tại trong CSDL khi ứng dụng khởi chạy lần đầu. Đảm bảo hàm tạo tài khoản trong `main.py` và `user_repository.py` được cấu hình đúng để tạo tài khoản `admin` phù hợp với cấu trúc bảng `TaiKhoan` của bạn, đặc biệt là các cột khóa ngoại như `MaGV_FK`.)*

## 🤝 Đóng góp

Mọi đóng góp để cải thiện hệ thống đều được chào đón. Vui lòng fork repository, tạo nhánh mới với các thay đổi của bạn và gửi pull request. Hãy đảm bảo tuân thủ các quy tắc mã hóa và kiểm thử.

## 📄 Giấy phép

Dự án này được cấp phép dưới Giấy phép MIT. 

## 📞 Liên hệ

* **Tên của bạn:** Nguyễn Đình Lượng
* **Email:** dinhluong19002004@gmail.com
* **GitHub:** `https://github.com/luong190204`

---