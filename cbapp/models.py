from enum import Enum

# models.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON, Date, DateTime
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime, timedelta

from cbapp import app, db, create_db


class VaiTro(Enum):
    QUANTRI = 'Quản trị'
    BANVE = 'Bán vé'

class KhachHang(db.Model, UserMixin):
    __tablename__ = 'khachhang'
    maKhachHang = Column(Integer, primary_key=True, autoincrement=True)
    hoVaTen = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    soDienThoai = Column(String(12), nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    taiKhoan = Column(String(30), unique=True, nullable=False)
    matKhau = Column(String(255), nullable=False)

    def set_password(self, password):
        self.matKhau = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.matKhau, password)

    def get_id(self):
        return str(self.maKhachHang)

    def get_username(self):
        return self.hoVaTen


class NhanVien(db.Model, UserMixin):
    __tablename__ = 'nhanvien'
    maNhanVien = Column(Integer, primary_key=True, autoincrement=True)
    tenNhanVien = Column(String(50), nullable=False)
    soDienThoai = Column(String(12), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    vaiTro = Column(String(50), nullable=False)
    taiKhoan = Column(String(30), unique=True, nullable=False)
    matKhau = Column(String(255), nullable=False)

    def set_password(self, password):
        self.matKhau = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.matKhau, password)

    def get_id(self):
        return str(self.maNhanVien)

    def get_username(self):
        return self.tenNhanVien


class SanBay(db.Model):
    __tablename__ = 'sanbay'
    maSanBay = db.Column(db.String(10), primary_key=True)
    tenSanBay = db.Column(db.String(100), nullable=False)


class TuyenBay(db.Model):
    __tablename__ = 'tuyenbay'

    maTuyenBay = db.Column(Integer, primary_key=True, autoincrement=True)
    tenTuyenBay = db.Column(db.String(50), nullable=False)
    maSanBayTrungGian1 = db.Column(db.String(10), db.ForeignKey('sanbay.maSanBay'), nullable=True)
    thoiGianDung1 = db.Column(Integer, nullable=True)
    maSanBayTrungGian2 = db.Column(db.String(10), db.ForeignKey('sanbay.maSanBay'), nullable=True)
    thoiGianDung2 = db.Column(Integer, nullable=True)
    giaCoBan = db.Column(Integer, nullable=False)
    maSanBayDi = db.Column(db.String(10), db.ForeignKey('sanbay.maSanBay'), nullable=False)
    maSanBayDen = db.Column(db.String(10), db.ForeignKey('sanbay.maSanBay'), nullable=False)


    sanBayDi = db.relationship('SanBay', foreign_keys=[maSanBayDi], backref='sanbay_di', lazy='select')
    sanBayDen = db.relationship('SanBay', foreign_keys=[maSanBayDen], backref='sanbay_den', lazy='select')


    sanBayTrungGian1 = db.relationship(  'SanBay', foreign_keys=[maSanBayTrungGian1],   backref='sanbay_trunggian1', lazy='select'  )
    sanBayTrungGian2 = db.relationship(    'SanBay',  foreign_keys=[maSanBayTrungGian2], backref='sanbay_trunggian2',   lazy='select'  )


class MayBay(db.Model):
    __tablename__ = 'maybay'
    maMayBay = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenMayBay = db.Column(db.String(50), nullable=False)
    tongSoGhe = db.Column(db.Integer, nullable=False)
    gheHang1 = db.Column(db.Integer, nullable=False)
    gheHang2 = db.Column(db.Integer, nullable=False)

class Ghe(db.Model):
    __tablename__ = 'ghe'
    maGhe = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenGhe = db.Column(db.String(50), nullable=False)
    trangThai = db.Column(db.Boolean, nullable=False)  # Status of the seat (available or booked)
    hangGhe = db.Column(db.String(50), nullable=False)  # Class of seat (economy, business, etc.)
    maMayBay = db.Column(db.Integer, db.ForeignKey('maybay.maMayBay'), nullable=False)

    mayBay = db.relationship('MayBay', backref=db.backref('ghe', lazy=True))




class ChuyenBay(db.Model):
    __tablename__ = 'chuyenbay'
    maChuyenBay = Column(Integer, primary_key=True, autoincrement=True)
    gioDi = Column(DateTime, nullable=False, default=datetime.today)
    gioDen = Column(DateTime, nullable=False)

    maTuyenBay = Column(Integer, ForeignKey('tuyenbay.maTuyenBay'), nullable=False)
    maMayBay = Column(Integer, ForeignKey('maybay.maMayBay'), nullable=False)

    tuyenBay = db.relationship('TuyenBay',foreign_keys=[maTuyenBay], backref='tentb', lazy='select')
    mayBay = db.relationship('MayBay',foreign_keys=[maMayBay], backref='tenmb', lazy='select')

    ves = relationship('Ve', backref='chuyenBay', cascade="all, delete-orphan")


    def tinh_gia_ve(self, loai_ve, ngay_dat):
        gia_ve = self.tuyenBay.giaCoBan

        if loai_ve == 'ThuongGia':
            gia_ve *= 2  # Giá vé thương gia gấp đôi

        ngay_dat = datetime.strptime(ngay_dat, "%d/%m/%Y %H:%M")
        so_ngay_truoc_bay = (self.gioDi - ngay_dat).days

        if so_ngay_truoc_bay > 30:
            pass  # Không có phụ thu
        elif 15 < so_ngay_truoc_bay <= 30:
            gia_ve *= 1.2  # Phụ thu 20%
        elif 5 < so_ngay_truoc_bay <= 15:
            gia_ve *= 1.1  # Phụ thu 10%
        else:
            gia_ve *= 1.3  # Phụ thu 30%

        if self.gioDi - ngay_dat <= timedelta(days=1) and self.gioDi - ngay_dat >= timedelta(hours=12):
            gia_ve *= 0.7  # Giảm 30% nếu đặt trong vòng 12-24 giờ trước giờ bay

        return gia_ve



class HangVe(db.Model):
    __tablename__ = 'hangve'
    maHangVe = Column(Integer, primary_key=True, autoincrement=True)
    tenHangVe = Column(String(50), nullable=False)

    ves = relationship('Ve', backref='hangVe', cascade="all, delete-orphan")


class GiaVe(db.Model):
    __tablename__ = 'giave'
    maGiaVe = Column(Integer, primary_key=True, autoincrement=True)
    tenGiaVe = Column(String(50), nullable=False)

    ves = relationship('Ve', backref='giaVe', cascade="all, delete-orphan")


class Ve(db.Model):
    __tablename__ = 've'
    maVe = Column(Integer, primary_key=True, autoincrement=True)
    tinhTrangVe = Column(String(50), nullable=False)
    maChuyenBay = Column(Integer, ForeignKey('chuyenbay.maChuyenBay'), nullable=False)
    maKhachHang = Column(Integer, ForeignKey('khachhang.maKhachHang'), nullable=False)
    maGhe = Column(Integer, ForeignKey('ghe.maGhe'), nullable=False)
    maHangVe = Column(Integer, ForeignKey('hangve.maHangVe'), nullable=False)
    maGiaVe = Column(Integer, ForeignKey('giave.maGiaVe'), nullable=True)
    maNhanVien = Column(Integer, ForeignKey('nhanvien.maNhanVien'), nullable=True)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        haNoi = SanBay(maSanBay="HAN", tenSanBay="Sân bay Nội Bài, Hà Nội")
        saiGon = SanBay(maSanBay="SGN", tenSanBay="Sân bay Tân Sơn Nhất, TP. HCM")
        daNang = SanBay(maSanBay="DAD", tenSanBay="Sân bay Quốc tế Đà Nẵng")
        phuQuoc = SanBay(maSanBay="PQC", tenSanBay="Sân bay Phú Quốc")
        hue = SanBay(maSanBay="HUI", tenSanBay="Sân bay Phú Bài, Huế")
        caMau = SanBay(maSanBay="CAH", tenSanBay="Sân bay Cà Mau")
        db.session.add_all([haNoi, saiGon, daNang, phuQuoc, hue, caMau])


        khachHang1 = KhachHang(hoVaTen="Nguyễn Văn A", email="nguyenvana@example.com",
                               soDienThoai="0912345678", taiKhoan="user01", active=True)
        khachHang1.set_password("123456")

        khachHang2 = KhachHang(hoVaTen="Trần Thị B", email="tranthib@example.com",
                               soDienThoai="0987654321", taiKhoan="user02", active=True)
        khachHang2.set_password("123456")

        khachHang3 = KhachHang(hoVaTen="Lê Minh C", email="leminhc@example.com",
                               soDienThoai="0976543210", taiKhoan="user03", active=False)
        khachHang3.set_password("123456")

        db.session.add_all([khachHang1, khachHang2, khachHang3])


        nhanVien1 = NhanVien(tenNhanVien="Trần Huỳnh Sang", soDienThoai="0901234567",
                             email="lequangd@example.com", vaiTro="QUANTRI", taiKhoan="admin01")
        nhanVien1.set_password("123456")

        nhanVien2 = NhanVien(tenNhanVien="Phạm Thu E", soDienThoai="0932123456",
                             email="phamthue@example.com", vaiTro="BANVE", taiKhoan="admin02")
        nhanVien2.set_password("123456")

        nhanVien3 = NhanVien(tenNhanVien="Nguyễn Duy F", soDienThoai="0943234567",
                             email="nguyenduyf@example.com", vaiTro="BANVE", taiKhoan="admin03")
        nhanVien3.set_password("123456")

        db.session.add_all([nhanVien1, nhanVien2, nhanVien3])


        tb = TuyenBay(tenTuyenBay="Hà Nội - TP. HCM", maSanBayDi="HAN", maSanBayDen="SGN", giaCoBan="1000000")
        db.session.add(tb)

        mb = MayBay(tenMayBay="VN01", tongSoGhe=300, gheHang1=50, gheHang2=200)
        db.session.add(mb)


        db.session.commit()



