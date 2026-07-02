#!/usr/bin/env python3
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from dump_json import build_chart, palace_to_dict


ROOT = Path(__file__).resolve().parent


def make_payload(body):
    tb, db = build_chart(
        body["day"],
        body["month"],
        body["year"],
        body["hour"],
        body["gender"],
        body.get("name", ""),
        duong_lich=body.get("solar", True),
        time_zone=body.get("timezone", 7),
    )
    return {
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


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, payload, content_type="application/json; charset=utf-8"):
        raw = payload if isinstance(payload, bytes) else payload.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self):
        self._send(204, b"", "text/plain")

    def do_GET(self):
        if self.path in ["/", "/index.html"]:
            self._send(200, (ROOT / "index.html").read_text(encoding="utf-8"), "text/html; charset=utf-8")
            return
        self._send(404, json.dumps({"error": "not found"}, ensure_ascii=False))

    def do_POST(self):
        if self.path != "/chart":
            self._send(404, json.dumps({"error": "not found"}, ensure_ascii=False))
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(length).decode("utf-8"))
        try:
            payload = make_payload(body)
        except Exception as exc:
            self._send(400, json.dumps({"error": str(exc)}, ensure_ascii=False))
            return
        self._send(200, json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    print("Open http://127.0.0.1:8000")
    server.serve_forever()
