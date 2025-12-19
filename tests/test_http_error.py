from src.core.http import HttpError

def test_http_error_fields():
    e = HttpError("x", status_code=400, payload={"a": 1})
    assert e.status_code == 400
    assert e.payload["a"] == 1
