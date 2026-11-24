from flask import Flask, request, jsonify
from gateway import dispatch, set_v2_percent, V2_PERCENT

app = Flask(__name__)


@app.route("/orders", methods=["POST"])
def create_order():
    """Endpoint tạo đơn hàng duy nhất, tự động định tuyến Blue-Green."""
    body = request.get_json(silent=True) or {}
    which, result = dispatch(body)
    resp = jsonify(result)
    resp.headers["X-Order-Handler"] = which
    return resp, (201 if which == "v2" else 200)


@app.route("/admin/rollout", methods=["POST", "GET"])
def handle_rollout():
    """Endpoint mô phỏng dashboard cập nhật tỉ lệ rollout động."""
    import gateway
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        percent = data.get("v2_percent")
        if percent is None or not (0 <= int(percent) <= 100):
            return jsonify({"error": "v2_percent must be between 0 and 100"}), 400
        set_v2_percent(int(percent))
        return jsonify({
            "message": f"Updated V2_PERCENT to {gateway.V2_PERCENT}%",
            "v2_percent": gateway.V2_PERCENT
        }), 200
    return jsonify({"v2_percent": gateway.V2_PERCENT}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
