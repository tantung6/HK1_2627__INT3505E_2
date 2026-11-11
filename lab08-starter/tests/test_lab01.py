"""LAB 1 — add your five tests here. Do not delete the smoke tests.

A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. Validate a Book response using JSON Schema; add an unknown
       field to a *copy* of the response and assert ValidationError.

Useful imports:
    from jsonschema import validate, ValidationError
    import pytest
    from tools import get_book_schema

Do not depend on test execution order. Fixtures: client, app, sample_book.
"""


def test_get_books_empty_database(client):
    """A. GET /books khi CSDL rỗng trả về mảng rỗng (không phải null)."""
    response = client.get("/books")
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert isinstance(data, list)
    assert data == []


def test_get_book_not_found(client):
    """B. GET /books/<id> với id không tồn tại trả về 404 + JSON chứa "code": "NOT_FOUND"."""
    response = client.get("/books/9999")
    assert response.status_code == 404
    data = response.get_json()
    assert data is not None
    assert data.get("code") == "NOT_FOUND"


def test_create_book_missing_title(client):
    """C. POST /books thiếu title trả về 400 + trong errors có field "title"."""
    response = client.post("/books", json={"author": "J.K. Rowling"})
    assert response.status_code == 400
    data = response.get_json()
    assert "errors" in data
    fields = [err.get("field") for err in data["errors"]]
    assert "title" in fields


def test_delete_then_get_same_id(client):
    """D. Xoá rồi GET cùng id — phải trả về 404."""
    # Tạo một sách hợp lệ
    create_res = client.post("/books", json={"title": "Clean Code", "author": "Robert C. Martin"})
    assert create_res.status_code == 201
    book_id = create_res.get_json()["id"]

    # Xoá sách vừa tạo
    delete_res = client.delete(f"/books/{book_id}")
    assert delete_res.status_code == 204

    # GET lại cùng id -> trả về 404
    get_res = client.get(f"/books/{book_id}")
    assert get_res.status_code == 404
    assert get_res.get_json().get("code") == "NOT_FOUND"
