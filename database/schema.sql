-- schema.sql

CREATE TABLE IF NOT EXISTS SinhVien (
    MaSV VARCHAR(10) PRIMARY KEY,
    TenSV VARCHAR(100) NOT NULL,
    NgaySinh DATE,
    GioiTinh VARCHAR(10),
    DiaChi VARCHAR(255),
    Email VARCHAR(100),
    SDT VARCHAR(15)
);

CREATE TABLE IF NOT EXISTS LopHoc (
    MaLop VARCHAR(10) PRIMARY KEY,
    TenLop VARCHAR(100) NOT NULL,
    Khoa VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS MonHoc (
    MaMon VARCHAR(10) PRIMARY KEY,
    TenMon VARCHAR(100) NOT NULL,
    SoTinChi INT
);

CREATE TABLE IF NOT EXISTS GiangVien (
    MaGV VARCHAR(10) PRIMARY KEY,
    TenGV VARCHAR(100) NOT NULL,
    Email VARCHAR(100),
    SDT VARCHAR(15)
);

CREATE TABLE IF NOT EXISTS TaiKhoan (
    TenDangNhap VARCHAR(50) PRIMARY KEY,
    MatKhau VARCHAR(255) NOT NULL, -- Nên lưu mật khẩu đã hash
    LoaiTaiKhoan VARCHAR(20) NOT NULL, -- 'admin', 'giangvien'
    MaGV_FK VARCHAR(10),
    FOREIGN KEY (MaGV_FK) REFERENCES GiangVien(MaGV)
);

CREATE TABLE IF NOT EXISTS KhuonMat (
    ID_KhuonMat INT AUTO_INCREMENT PRIMARY KEY,
    MaSV_FK VARCHAR(10) NOT NULL,
    DuongDanAnh VARCHAR(255), -- Đường dẫn đến file ảnh gốc
    DuLieuMaHoa BLOB, -- Dữ liệu vector đặc trưng (binary large object)
    FOREIGN KEY (MaSV_FK) REFERENCES SinhVien(MaSV)
);

CREATE TABLE IF NOT EXISTS Lop_Mon_SinhVien (
    MaLop_FK VARCHAR(10) NOT NULL,
    MaMon_FK VARCHAR(10) NOT NULL,
    MaSV_FK VARCHAR(10) NOT NULL,
    PRIMARY KEY (MaLop_FK, MaMon_FK, MaSV_FK),
    FOREIGN KEY (MaLop_FK) REFERENCES LopHoc(MaLop),
    FOREIGN KEY (MaMon_FK) REFERENCES MonHoc(MaMon),
    FOREIGN KEY (MaSV_FK) REFERENCES SinhVien(MaSV)
);

CREATE TABLE IF NOT EXISTS DiemDanh (
    ID_DiemDanh INT AUTO_INCREMENT PRIMARY KEY,
    MaBuoiHoc_FK VARCHAR(10) NOT NULL,
    MaSV_FK VARCHAR(10) NOT NULL,
    ThoiGian DATETIME NOT NULL,
    TrangThai VARCHAR(20) NOT NULL,  -- Ví dụ: 'Có mặt', 'Muộn 15 phút', 'Vắng mặt'
    HinhAnh VARCHAR(255),            -- Đường dẫn đến file ảnh lưu trên máy
    FOREIGN KEY (MaBuoiHoc_FK) REFERENCES BuoiHoc(MaBuoiHoc),
    FOREIGN KEY (MaSV_FK) REFERENCES SinhVien(MaSV)
);

CREATE TABLE BuoiHoc (
    MaBuoiHoc VARCHAR(10) PRIMARY KEY,
    GioBatDau TIME NOT NULL,
    GioKetThuc TIME NOT NULL,
    NgayHoc DATE NOT NULL,
    MaGV_FK VARCHAR(10) NOT NULL,
    MaMonHoc_FK VARCHAR(10) NOT NULL,
    PhongHoc VARCHAR(20),
    MaLop_FK VARCHAR(20),
    TrangThaiBuoiHoc VARCHAR(20) DEFAULT 'Scheduled',
    FOREIGN KEY (MaGV_FK) REFERENCES GiaoVien(MaGV),
    FOREIGN KEY (MaMonHoc_FK) REFERENCES MonHoc(MaMon),
    FOREIGN KEY (MaLop_FK) REFERENCES LopHoc(MaLop)
);