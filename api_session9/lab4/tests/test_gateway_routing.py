import pytest
from app import app
import gateway


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        # Reset V2_PERCENT về 5 trước mỗi bài test
        gateway.set_v2_percent(5)
        yield client
        gateway.set_v2_percent(5)


def test_case_1_cohort_beta_routes_to_v2(client):
    """Case 1 từ Slide: Header X-Cohort: beta có độ ưu tiên cao nhất -> v2 (HTTP 201)."""
    response = client.post(
        "/orders",
        headers={"X-Cohort": "beta"},
        json={"account_id": "any_random_account"}
    )
    assert response.status_code == 201
    assert response.headers.get("X-Order-Handler") == "v2"

    data = response.get_json()
    assert data["version"] == "v2"
    assert data["account_id"] == "any_random_account"
    assert "async_fulfillment" in data["features"]


def test_case_1_cohort_internal_routes_to_v2(client):
    """Case 1 mở rộng: Header X-Cohort: internal -> v2."""
    response = client.post(
        "/orders",
        headers={"X-Cohort": "internal"},
        json={"account_id": "user_xyz"}
    )
    assert response.status_code == 201
    assert response.headers.get("X-Order-Handler") == "v2"
    assert response.get_json()["version"] == "v2"


def test_case_2_force_account_routes_to_v2(client):
    """Case 2 từ Slide: Tài khoản nằm trong V2_FORCE_ACCOUNTS (acct_42, acct_99) -> ép vào v2."""
    for force_acct in ["acct_42", "acct_99"]:
        response = client.post("/orders", json={"account_id": force_acct})
        assert response.status_code == 201
        assert response.headers.get("X-Order-Handler") == "v2"
        assert response.get_json()["account_id"] == force_acct
        assert response.get_json()["version"] == "v2"


def test_case_3_ordinary_account_bucket_decides(client):
    """Case 3 từ Slide: Tài khoản thông thường chia bucket theo 5% hash MD5."""
    gateway.set_v2_percent(5)

    # user_38 có hash % 100 = 4 (< 5) -> lọt vào 5% của v2
    res_v2 = client.post("/orders", json={"account_id": "user_38"})
    assert res_v2.status_code == 201
    assert res_v2.headers.get("X-Order-Handler") == "v2"
    assert res_v2.get_json()["version"] == "v2"

    # user_1 có hash % 100 = 53 (>= 5) -> rơi vào 95% của v1 (HTTP 200)
    res_v1 = client.post("/orders", json={"account_id": "user_1"})
    assert res_v1.status_code == 200
    assert res_v1.headers.get("X-Order-Handler") == "v1"
    assert res_v1.get_json()["version"] == "v1"


def test_case_4_flip_v2_percent_to_100(client):
    """Case 4 từ Slide: Đẩy V2_PERCENT = 100 -> toàn bộ tài khoản thường đều sang v2."""
    gateway.set_v2_percent(100)

    # user_1 trước đây ở v1 giờ phải sang v2
    response = client.post("/orders", json={"account_id": "user_1"})
    assert response.status_code == 201
    assert response.headers.get("X-Order-Handler") == "v2"
    assert response.get_json()["version"] == "v2"


def test_case_5_flip_v2_percent_to_0_and_cohort_override(client):
    """Case 5: Khi V2_PERCENT = 0, chỉ allow-list và cohort header mới vào được v2."""
    gateway.set_v2_percent(0)

    # user_38 từng ở v2 nay về v1 do percent = 0
    res_normal = client.post("/orders", json={"account_id": "user_38"})
    assert res_normal.status_code == 200
    assert res_normal.headers.get("X-Order-Handler") == "v1"

    # Nhưng acct_42 (allow-list) vẫn luôn vào v2
    res_force = client.post("/orders", json={"account_id": "acct_42"})
    assert res_force.status_code == 201
    assert res_force.headers.get("X-Order-Handler") == "v2"

    # Và X-Cohort: beta vẫn luôn vào v2
    res_cohort = client.post(
        "/orders",
        headers={"X-Cohort": "beta"},
        json={"account_id": "user_38"}
    )
    assert res_cohort.status_code == 201
    assert res_cohort.headers.get("X-Order-Handler") == "v2"


def test_admin_rollout_api(client):
    """Kiểm tra API quản trị tỉ lệ rollout."""
    get_res = client.get("/admin/rollout")
    assert get_res.status_code == 200
    assert "v2_percent" in get_res.get_json()

    post_res = client.post("/admin/rollout", json={"v2_percent": 50})
    assert post_res.status_code == 200
    assert post_res.get_json()["v2_percent"] == 50
    assert gateway.V2_PERCENT == 50

    # Test giá trị không hợp lệ
    err_res = client.post("/admin/rollout", json={"v2_percent": 150})
    assert err_res.status_code == 400
