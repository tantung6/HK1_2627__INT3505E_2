from flask import Flask, jsonify, request

app = Flask(__name__)

# Dữ liệu sách mẫu
BOOKS = [
    {"id": "b1", "t": "Học Python căn bản"},
    {"id": "b2", "t": "Flask Web Development"},
    {"id": "b3", "t": "Python nâng cao"},
    {"id": "b4", "t": "JavaScript toàn tập"}
]

def find_by_id(book_id):
    for book in BOOKS:
        if book["id"] == book_id:
            return book
    return None

# 1. Path param (string)
@app.route("/books/<book_id>", methods=["GET"])
def get_book(book_id):
    book = find_by_id(book_id)
    if book is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(book), 200

# 2. Path param ép kiểu int
@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    return jsonify({"id": item_id}), 200

# 3. Query string (bộ lọc / phân trang)
@app.route("/books", methods=["GET"])
def list_books():
    limit = int(request.args.get("limit", 20))
    q = request.args.get("q", "").strip().lower()
    items = [b for b in BOOKS if q in b["t"].lower()]
    return jsonify({"items": items[:limit]}), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)