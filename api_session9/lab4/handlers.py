import uuid


def v1_create_order(body):
    """Handler v1: Logic tạo đơn hàng cũ (đồng bộ, schema cũ, trả về HTTP 200)."""
    account_id = (body or {}).get("account_id", "unknown")
    items = (body or {}).get("items", [])
    return {
        "order_id": f"ord_v1_{uuid.uuid4().hex[:8]}",
        "account_id": account_id,
        "version": "v1",
        "status": "created",
        "items_count": len(items) if isinstance(items, list) else 1,
    }


def v2_create_order(body):
    """Handler v2: Logic tạo đơn hàng mới (bất đồng bộ, schema mới, trả về HTTP 201)."""
    account_id = (body or {}).get("account_id", "unknown")
    items = (body or {}).get("items", [])
    return {
        "order_id": f"ord_v2_{uuid.uuid4().hex[:8]}",
        "account_id": account_id,
        "version": "v2",
        "status": "processed",
        "items": items,
        "features": ["async_fulfillment", "realtime_tracking"],
    }
