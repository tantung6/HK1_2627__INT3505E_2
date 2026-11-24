import hashlib
import logging
from flask import request
from handlers import v1_create_order, v2_create_order

log = logging.getLogger("gateway")

# Config: flip V2_PERCENT through dashboard / admin
V2_PERCENT = 5
V2_COHORTS = {"beta", "internal"}
V2_FORCE_ACCOUNTS = {"acct_42", "acct_99"}


def set_v2_percent(percent: int):
    """Cập nhật tỉ lệ phần trăm traffic vào handler v2 (0 -> 100)."""
    global V2_PERCENT
    V2_PERCENT = max(0, min(100, int(percent)))


def route_to_v2(body):
    """Hệ thống điều hướng 3 tầng (3-tier routing) theo Slide 23:
    1. Explicit cohort (X-Cohort header) có độ ưu tiên cao nhất.
    2. Account nằm trong danh sách ép buộc (Allow-list).
    3. Phân bổ theo phần trăm xác định (Deterministic percentage hash bucket).
    """
    # 1. Explicit cohort has highest priority
    cohort = request.headers.get("X-Cohort", "").lower()
    if cohort in V2_COHORTS:
        return True

    # 2. Allow-listed account
    acct = (body or {}).get("account_id", "")
    if acct in V2_FORCE_ACCOUNTS:
        return True

    # 3. Deterministic percentage bucket
    if V2_PERCENT == 0:
        return False
    h = int(hashlib.md5(acct.encode()).hexdigest(), 16)
    return h % 100 < V2_PERCENT


def dispatch(body):
    """Điều hướng request tới handler tương ứng và trả về version cùng kết quả."""
    if route_to_v2(body):
        return "v2", v2_create_order(body)
    return "v1", v1_create_order(body)
