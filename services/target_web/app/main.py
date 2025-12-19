from __future__ import annotations
import time
from fastapi import FastAPI, Response

app = FastAPI(title="Target Web (Lab)", version="0.1")

@app.get("/health")
def health():
    return {"ok": True, "service": "target_web"}

@app.get("/slow")
def slow(ms: int = 200):
    # latency 테스트용 endpoint
    time.sleep(ms / 1000.0)
    return {"ok": True, "slept_ms": ms}

@app.get("/")
def root(resp: Response):
    # 보안 헤더(교육용 예시) - security_audit가 점검함
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    return {"message": "Hello from target_web"}
