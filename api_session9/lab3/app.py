import logging
from datetime import datetime, timezone
from flask import Flask, jsonify
from sunset import deprecate_at

# Cấu hình log để hiển thị cảnh báo deprecated_call rõ ràng
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

app = Flask(__name__)

# Ngày Sunset cho API v1 (cuối năm 2026)
V1_SUNSET = datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

# Ngày Sunset trong quá khứ để test tình huống 410 Gone trực tiếp
V0_SUNSET = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


@app.route("/api/v1/users/<int:uid>")
@deprecate_at(V1_SUNSET, replacement="/api/v2/users")
def get_v1(uid):
    return {"id": uid, "full_name": "Nguyễn Văn A"}


@app.route("/api/v0/users/<int:uid>")
@deprecate_at(V0_SUNSET, replacement="/api/v1/users")
def get_v0(uid):
    """Endpoint đã hết hạn hoàn toàn (quá khứ) để test HTTP 410 Gone."""
    return {"id": uid, "name": "Phiên bản cũ"}


@app.route("/api/v2/users")
def list_v2_users():
    return jsonify({
        "message": "Danh sách API Users v2 mới nhất",
        "endpoints": ["/api/v2/users/<id>"]
    })


@app.route("/api/v2/users/<int:uid>")
def get_v2(uid):
    return jsonify({
        "id": uid,
        "first_name": "Văn A",
        "last_name": "Nguyễn",
        "email": "a@vnu.vn"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
