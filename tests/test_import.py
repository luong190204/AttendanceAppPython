# debug_db.py - Script để debug kết nối database
import sys
import os
import logging

# Thiết lập logging chi tiết
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def debug_database_connection():
    """Debug kết nối database step by step"""

    print("=" * 50)
    print("DEBUG DATABASE CONNECTION")
    print("=" * 50)

    # 1. Kiểm tra đường dẫn project
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    print(f"1. Project root: {project_root}")
    print(f"   Current working directory: {os.getcwd()}")

    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        print(f"   Added to sys.path: {project_root}")

    # 2. Kiểm tra file database có tồn tại không
    db_files = [
        "database/__init__.py",
        "database/connection_manager.py",
        "database/user_repository.py"
    ]

    print("\n2. Kiểm tra files database:")
    for file_path in db_files:
        full_path = os.path.join(project_root, file_path)
        exists = os.path.exists(full_path)
        print(f"   {file_path}: {'✓' if exists else '✗'}")
        if not exists:
            print(f"      → File không tồn tại: {full_path}")

    # 3. Thử import các modules
    print("\n3. Thử import modules:")

    try:
        print("   Importing connection_manager...")
        from database.connection_manager import ConnectionManager
        print("   ✓ Import ConnectionManager thành công")
    except Exception as e:
        print(f"   ✗ Lỗi import ConnectionManager: {e}")
        return False

    try:
        print("   Importing user_repository...")
        from database.user_repository import UserRepository
        print("   ✓ Import UserRepository thành công")
    except Exception as e:
        print(f"   ✗ Lỗi import UserRepository: {e}")
        return False

    # 4. Kiểm tra các dependencies
    print("\n4. Kiểm tra dependencies:")
    required_packages = ['mysql-connector-python', 'bcrypt']

    for package in required_packages:
        try:
            if package == 'mysql-connector-python':
                import mysql.connector
                print(f"   ✓ {package} đã cài đặt")
            elif package == 'bcrypt':
                import bcrypt
                print(f"   ✓ {package} đã cài đặt")
        except ImportError:
            print(f"   ✗ {package} chưa được cài đặt")
            print(f"      → Chạy: pip install {package}")

    # 5. Thử khởi tạo ConnectionManager
    print("\n5. Thử khởi tạo ConnectionManager:")
    try:
        conn_manager = ConnectionManager()
        print("   ✓ Khởi tạo ConnectionManager thành công")

        # Kiểm tra config
        if hasattr(conn_manager, 'config'):
            print(f"   Config: {conn_manager.config}")

    except Exception as e:
        print(f"   ✗ Lỗi khởi tạo ConnectionManager: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 6. Thử kết nối database
    print("\n6. Thử kết nối database:")
    try:
        print("   Đang gọi conn_manager.connect()...")
        result = conn_manager.connect()
        print(f"   Kết quả: {result}")

        if result:
            print("   ✓ Kết nối database thành công!")

            # Thử một số operations cơ bản
            if hasattr(conn_manager, 'connection') and conn_manager.connection:
                cursor = conn_manager.connection.cursor()
                cursor.execute("SELECT 1")
                test_result = cursor.fetchone()
                print(f"   Test query result: {test_result}")
                cursor.close()
        else:
            print("   ✗ Kết nối database thất bại")
            return False

    except Exception as e:
        print(f"   ✗ Lỗi khi kết nối database: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 7. Thử khởi tạo UserRepository
    print("\n7. Thử khởi tạo UserRepository:")
    try:
        user_repo = UserRepository()
        print("   ✓ Khởi tạo UserRepository thành công")

        # Thử một operation đơn giản
        try:
            result = user_repo.get_lecturer_by_id("test")
            print(f"   Test query result: {result}")
        except Exception as e:
            print(f"   Lỗi test query: {e}")

    except Exception as e:
        print(f"   ✗ Lỗi khởi tạo UserRepository: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 50)
    print("DEBUG HOÀN TẤT - TẤT CẢ OK!")
    print("=" * 50)
    return True


def check_mysql_service():
    """Kiểm tra MySQL service có đang chạy không"""
    print("\n8. Kiểm tra MySQL Service:")

    import subprocess
    import platform

    system = platform.system().lower()

    try:
        if system == "windows":
            # Windows
            result = subprocess.run(
                ['sc', 'query', 'mysql'],
                capture_output=True, text=True, timeout=10
            )
            if "RUNNING" in result.stdout:
                print("   ✓ MySQL service đang chạy (Windows)")
            else:
                print("   ✗ MySQL service không chạy (Windows)")
                print("   → Khởi động: net start mysql")

        elif system == "linux":
            # Linux
            result = subprocess.run(
                ['systemctl', 'is-active', 'mysql'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                print("   ✓ MySQL service đang chạy (Linux)")
            else:
                print("   ✗ MySQL service không chạy (Linux)")
                print("   → Khởi động: sudo systemctl start mysql")

        elif system == "darwin":
            # macOS
            result = subprocess.run(
                ['brew', 'services', 'list'],
                capture_output=True, text=True, timeout=10
            )
            if "mysql" in result.stdout and "started" in result.stdout:
                print("   ✓ MySQL service đang chạy (macOS)")
            else:
                print("   ✗ MySQL service không chạy (macOS)")
                print("   → Khởi động: brew services start mysql")

    except Exception as e:
        print(f"   Không thể kiểm tra MySQL service: {e}")


if __name__ == "__main__":
    print("Chạy debug database connection...")

    # Kiểm tra MySQL service trước
    check_mysql_service()

    # Debug database connection
    success = debug_database_connection()

    if success:
        print("\n🎉 Database connection OK! Bạn có thể chạy ứng dụng chính.")
    else:
        print("\n❌ Có lỗi với database connection. Vui lòng kiểm tra các bước trên.")

    input("\nNhấn Enter để thoát...")