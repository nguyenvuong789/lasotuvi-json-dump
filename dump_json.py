#!/usr/bin/env python3
import argparse
import json

from lasotuvi.App import lapDiaBan
from lasotuvi.DiaBan import diaBan
from lasotuvi.ThienBan import lapThienBan


def star_to_dict(star):
    data = dict(star)
    return data


def palace_to_dict(palace):
    return {
        "cungSo": palace.cungSo,
        "cungTen": palace.cungTen,
        "cungChu": getattr(palace, "cungChu", None),
        "hanhCung": palace.hanhCung,
        "cungThan": palace.cungThan,
        "cungDaiHan": getattr(palace, "cungDaiHan", None),
        "cungTieuHan": getattr(palace, "cungTieuHan", None),
        "tuanTrung": getattr(palace, "tuanTrung", False),
        "trietLo": getattr(palace, "trietLo", False),
        "stars": [star_to_dict(star) for star in palace.cungSao],
    }


def build_chart(ngay, thang, nam, gio, gioi_tinh, ten, duong_lich=True, time_zone=7):
    db = lapDiaBan(diaBan, ngay, thang, nam, gio, gioi_tinh, duong_lich, time_zone)
    tb = lapThienBan(ngay, thang, nam, gio, gioi_tinh, ten, db, duong_lich, time_zone)
    return tb, db


def main():
    parser = argparse.ArgumentParser(description="Dump lasotuvi JSON")
    parser.add_argument("--name", default="", help="Họ tên")
    parser.add_argument("--gender", type=int, choices=[1, -1], required=True, help="1 nam, -1 nữ")
    parser.add_argument("--day", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--hour", type=int, required=True, help="Giờ chi 1-12: Tý..Hợi")
    parser.add_argument("--solar", action="store_true", help="Nhập dương lịch")
    parser.add_argument("--timezone", type=int, default=7)
    args = parser.parse_args()

    tb, db = build_chart(
        args.day,
        args.month,
        args.year,
        args.hour,
        args.gender,
        args.name,
        duong_lich=args.solar,
        time_zone=args.timezone,
    )

    payload = {
        "thienBan": {
            "ten": tb.ten,
            "namNu": tb.namNu,
            "gioSinh": tb.gioSinh,
            "ngayDuong": tb.ngayDuong,
            "thangDuong": tb.thangDuong,
            "namDuong": tb.namDuong,
            "ngayAm": tb.ngayAm,
            "thangAm": tb.thangAm,
            "namAm": tb.namAm,
            "canNgayTen": tb.canNgayTen,
            "chiNgayTen": tb.chiNgayTen,
            "canThangTen": tb.canThangTen,
            "chiThangTen": tb.chiThangTen,
            "canNamTen": tb.canNamTen,
            "chiNamTen": tb.chiNamTen,
            "amDuongNamSinh": tb.amDuongNamSinh,
            "amDuongMenh": tb.amDuongMenh,
            "tenCuc": tb.tenCuc,
            "menhChu": tb.menhChu,
            "thanChu": tb.thanChu,
            "sinhKhac": tb.sinhKhac,
            "banMenh": tb.banMenh,
        },
        "diaBan": {
            "cungMenh": db.cungMenh,
            "cungThan": db.cungThan,
            "palaces": [palace_to_dict(palace) for palace in db.thapNhiCung[1:]],
        },
    }

    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
