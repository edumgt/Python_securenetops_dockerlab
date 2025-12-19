from __future__ import annotations
import argparse
import socket
import time
import re
from typing import Any, Dict, List

import requests

from src.core.config import load_yaml, env
from src.core.logger import get_logger
from src.core.report import Report, utcnow_iso, write_json

log = get_logger(__name__)

def tcp_connect(host: str, port: int, timeout_s: float = 1.0) -> Dict[str, Any]:
    t0 = time.time()
    try:
        with socket.create_connection((host, port), timeout=timeout_s):
            ms = int((time.time() - t0) * 1000)
            return {"host": host, "port": port, "ok": True, "latency_ms": ms}
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        return {"host": host, "port": port, "ok": False, "latency_ms": ms, "error": str(e)}

def get_headers(url: str, timeout_s: float = 2.0) -> Dict[str, Any]:
    try:
        r = requests.get(url, timeout=timeout_s)
        headers = {k.lower(): v for k, v in r.headers.items()}
        return {"url": url, "ok": r.status_code < 500, "status_code": r.status_code, "headers": headers}
    except Exception as e:
        return {"url": url, "ok": False, "error": str(e)}

def main():
    ap = argparse.ArgumentParser(description="Security audit (allowlist-based, for lab)")
    ap.add_argument("--policy", default="configs/security_policy.yml")
    ap.add_argument("--report", default="reports/security_report.json")
    args = ap.parse_args()

    policy = load_yaml(args.policy).get("policy", {})
    items: List[Dict[str, Any]] = []

    # 1) Allowlisted endpoint port checks
    endpoints = policy.get("allowlisted_endpoints", []) or []
    for ep in endpoints:
        host = ep["host"]
        for port in ep.get("ports", []):
            items.append({"check": "allowlisted_port", "name": ep["name"], **tcp_connect(host, int(port), 1.0)})

    # 2) HTTP security headers (basic)
    required_headers = [h.lower() for h in (policy.get("http_headers_required", []) or [])]
    # For demo: check target_web root & health
    for url in ["http://172.30.0.20:8080/", "http://172.30.0.20:8080/health"]:
        res = get_headers(url, 2.0)
        missing = []
        if res.get("ok") and "headers" in res:
            for h in required_headers:
                if h not in res["headers"]:
                    missing.append(h)
        res["missing_required_headers"] = missing
        res["check"] = "http_headers"
        items.append(res)

    # 3) Secret leakage pattern check (reporting discipline)
    forbid_patterns = policy.get("secrets_rules", {}).get("forbid_patterns", []) or []
    sample_texts = [
        f"controller token={env('CONTROLLER_API_TOKEN', '')}",
        "this is a sample log line",
    ]
    leaks = []
    for p in forbid_patterns:
        rx = re.compile(re.escape(p))
        for t in sample_texts:
            if rx.search(t):
                leaks.append({"pattern": p, "text": t})
    items.append({"check": "secret_leak_guard", "ok": len(leaks) == 0, "leaks": leaks})

    ok = True
    for it in items:
        # allowlisted_port: ok must be True
        if it.get("check") == "allowlisted_port" and not it.get("ok"):
            ok = False
        if it.get("check") == "http_headers" and it.get("missing_required_headers"):
            # 권장 기준 미충족은 fail로 강제하지 않고 "warning" 처리
            it["severity"] = "warning"
        if it.get("check") == "secret_leak_guard" and not it.get("ok"):
            ok = False

    summary = {
        "allowlisted_endpoints": [e["name"] for e in endpoints],
        "required_headers": required_headers,
    }
    rep = Report("security_audit", utcnow_iso(), ok, summary, items)
    write_json(args.report, rep.to_dict())
    log.info(f"Wrote report: {args.report} (ok={ok})")

if __name__ == "__main__":
    main()
