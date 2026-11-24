import logging
from datetime import datetime, timezone
from unittest.mock import patch
import pytest
from app import app
from sunset import deprecate_at


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_before_sunset_returns_200_and_deprecation_headers(client, caplog):
    """Trước Sunset: Trả về HTTP 200, các headers Sunset, Deprecation, Link và log cảnh báo."""
    with caplog.at_level(logging.WARNING, logger="sunset"):
        response = client.get("/api/v1/users/1")

    assert response.status_code == 200
    assert response.headers.get("Sunset") == "Thu, 31 Dec 2026 23:59:59 GMT"
    assert response.headers.get("Deprecation") == "true"
    assert response.headers.get("Link") == '</api/v2/users>; rel="successor-version"'

    data = response.get_json()
    assert data["id"] == 1
    assert data["full_name"] == "Nguyễn Văn A"

    # Kiểm tra server log đã ghi nhận cảnh báo
    assert any("deprecated_call /api/v1/users/1" in record.message for record in caplog.records)


def test_after_sunset_returns_410_gone(client):
    """Sau Sunset: Endpoint quá khứ trả về ngay HTTP 410 Gone kèm gợi ý thay thế."""
    response = client.get("/api/v0/users/1")
    assert response.status_code == 410

    data = response.get_json()
    assert data["error"] == "gone"
    assert data["sunset"] == "Mon, 01 Jan 2024 00:00:00 GMT"
    assert data["use_instead"] == "/api/v1/users"


def test_mocked_time_after_sunset(client):
    """Mô phỏng thời gian tương lai (sau 31/12/2026) -> v1 chuyển sang HTTP 410 Gone."""
    future_time = datetime(2027, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    with patch("sunset.datetime") as mock_dt:
        mock_dt.now.return_value = future_time
        response = client.get("/api/v1/users/1")

    assert response.status_code == 410
    data = response.get_json()
    assert data["error"] == "gone"
    assert data["use_instead"] == "/api/v2/users"
    assert data["sunset"] == "Thu, 31 Dec 2026 23:59:59 GMT"


def test_endpoint_without_replacement():
    """Kiểm tra khi decorator không truyền replacement thì không sinh header Link."""
    from flask import Flask
    test_app = Flask(__name__)
    sunset_date = datetime(2028, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    @test_app.route("/test")
    @deprecate_at(sunset_date)
    def test_route():
        return {"ok": True}

    client = test_app.test_client()
    res = client.get("/test")
    assert res.status_code == 200
    assert "Sunset" in res.headers
    assert "Deprecation" in res.headers
    assert "Link" not in res.headers


def test_v2_successor_endpoint(client):
    """Kiểm tra endpoint v2 hoạt động bình thường, không bị gắn header deprecation."""
    response = client.get("/api/v2/users/1")
    assert response.status_code == 200
    assert "Sunset" not in response.headers
    assert "Deprecation" not in response.headers

    data = response.get_json()
    assert data["id"] == 1
    assert data["first_name"] == "Văn A"
    assert data["last_name"] == "Nguyễn"
    assert data["email"] == "a@vnu.vn"
