from datetime import datetime, timezone
from email.utils import format_datetime
from functools import wraps
from flask import request, jsonify
import logging

log = logging.getLogger("sunset")


def http_date(dt):
    """Format đối tượng datetime UTC thành chuỗi HTTP-date (RFC 7231 / RFC 8594)."""
    return format_datetime(dt, usegmt=True)


def deprecate_at(sunset_date, replacement=None):
    """Decorator áp dụng chính sách Deprecation & Sunset theo RFC 8594.

    - Nếu thời gian hiện tại >= sunset_date:
        Trả về HTTP 410 Gone và gợi ý phiên bản thay thế qua thuộc tính use_instead.
    - Nếu trước sunset_date:
        Trả về kết quả bình thường nhưng bổ sung các response headers:
        + Sunset: <HTTP-date>
        + Deprecation: true
        + Link: <{replacement}>; rel="successor-version" (nếu có replacement)
        Đồng thời ghi log warning phục vụ việc audit / telemetry giám sát lưu lượng client cũ.
    """
    def wrap(fn):
        @wraps(fn)
        def inner(*a, **kw):
            now = datetime.now(timezone.utc)
            if now >= sunset_date:
                return jsonify({
                    "error": "gone",
                    "sunset": http_date(sunset_date),
                    "use_instead": replacement,
                }), 410
            result = fn(*a, **kw)
            body, status = result if isinstance(result, tuple) else (result, 200)
            r = jsonify(body)
            r.status_code = status
            r.headers["Sunset"] = http_date(sunset_date)
            r.headers["Deprecation"] = "true"
            if replacement:
                r.headers["Link"] = f'<{replacement}>; rel="successor-version"'
            log.warning("deprecated_call %s %s", request.path, request.remote_addr)
            return r
        return inner
    return wrap
