from __future__ import annotations
import argparse
import socket
import time
from typing import Any, Dict, List, Tuple
import requests

from src.core.config import load_yaml, env
from src.core.logger import get_logger
from src.core.report import Report, utcnow_iso, write_json

log = get_logger(__name__)

def check_tcp(host: str, port: int, timeout_s: float) -> Dict[str, Any]:
    t0 = time.time()
    try:
        with socket.create_connection((host, port), timeout=timeout_s):
            ms = int((time.time() - t0) * 1000)
            return {"type": "tcp", "host": host, "port": port, "ok": True, "latency_ms": ms}
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        return {"type": "tcp", "host": host, "port": port, "ok": False, "latency_ms": ms, "error": str(e)}

def check_dns(hostname: str) -> Dict[str, Any]:
    try:
        ip = socket.gethostbyname(hostname)
        return {"type": "dns", "hostname": hostname, "ok": True, "ip": ip}
    except Exception as e:
        return {"type": "dns", "hostname": hostname, "ok": False, "error": str(e)}

def check_http(url: str, timeout_s: float) -> Dict[str, Any]:
    t0 = time.time()
    try:
        r = requests.get(url, timeout=timeout_s)
        ms = int((time.time() - t0) * 1000)
        return {
            "type": "http",
            "url": url,
            "ok": r.status_code < 400,
            "status_code": r.status_code,
            "latency_ms": ms,
            "headers": {k.lower(): v for k, v in r.headers.items()},
        }
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        return {"type": "http", "url": url, "ok": False, "latency_ms": ms, "error": str(e)}

def main():
    ap = argparse.ArgumentParser(description="Safe network diagnostics (Docker lab)")
    ap.add_argument("--targets", default="configs/targets.yml", help="YAML config with allowlisted checks")
    ap.add_argument("--report", default="reports/netdiag.json", help="Where to write report JSON")
    args = ap.parse_args()

    cfg = load_yaml(args.targets)
    items: List[Dict[str, Any]] = []

    for it in cfg.get("checks", {}).get("dns", []) or []:
        items.append(check_dns(it["hostname"]))

    for it in cfg.get("checks", {}).get("tcp", []) or []:
        items.append(check_tcp(it["host"], int(it["port"]), float(it.get("timeout_s", 1))))

    for it in cfg.get("checks", {}).get("http", []) or []:
        items.append(check_http(it["url"], float(it.get("timeout_s", 2))))

    ok = all(x.get("ok") for x in items) if items else False
    summary = {
        "total": len(items),
        "ok": sum(1 for x in items if x.get("ok")),
        "fail": sum(1 for x in items if not x.get("ok")),
    }
    rep = Report(name="netdiag", generated_at=utcnow_iso(), ok=ok, summary=summary, items=items)
    write_json(args.report, rep.to_dict())
    log.info(f"Wrote report: {args.report} (ok={ok})")

if __name__ == "__main__":
    main()
