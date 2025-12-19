from __future__ import annotations
import argparse
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import os
import requests

from src.core.config import load_yaml
from src.core.logger import get_logger

log = get_logger(__name__)

@dataclass
class Target:
    name: str
    type: str
    url: str
    timeout_s: float
    warn_ms: int
    crit_ms: int

def post_webhook(url: str, payload: Dict[str, Any]) -> None:
    try:
        requests.post(url, json=payload, timeout=2.5)
    except Exception as e:
        log.warning(f"webhook post failed: {e}")

def measure_http(url: str, timeout_s: float) -> Dict[str, Any]:
    t0 = time.time()
    try:
        r = requests.get(url, timeout=timeout_s)
        ms = int((time.time() - t0) * 1000)
        return {"ok": r.status_code < 500, "status_code": r.status_code, "latency_ms": ms}
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        return {"ok": False, "latency_ms": ms, "error": str(e)}

def main():
    ap = argparse.ArgumentParser(description="Simple monitoring agent (Docker lab)")
    ap.add_argument("--config", default="configs/monitor.yml")
    args = ap.parse_args()

    cfg = load_yaml(args.config).get("monitor", {})
    interval_s = int(cfg.get("interval_s", 5))
    metrics_path = cfg.get("metrics_path", "/data/metrics.jsonl")
    webhook_url = os.getenv("ALERT_WEBHOOK_URL", "").strip()
    alert_enabled = bool(cfg.get("alert", {}).get("enabled", True))

    targets: List[Target] = []
    for t in cfg.get("targets", []) or []:
        targets.append(Target(
            name=t["name"], type=t["type"], url=t["url"],
            timeout_s=float(t.get("timeout_s", 2)),
            warn_ms=int(t.get("warn_ms", 250)),
            crit_ms=int(t.get("crit_ms", 600)),
        ))

    os.makedirs(os.path.dirname(metrics_path), exist_ok=True)

    log.info(f"Monitoring started: interval={interval_s}s, targets={len(targets)} metrics={metrics_path}")
    while True:
        now = time.time()
        for t in targets:
            if t.type != "http":
                continue
            res = measure_http(t.url, t.timeout_s)
            sev = "ok"
            if not res.get("ok"):
                sev = "crit"
            else:
                ms = int(res.get("latency_ms", 0))
                if ms >= t.crit_ms:
                    sev = "crit"
                elif ms >= t.warn_ms:
                    sev = "warn"

            event = {
                "ts": int(now),
                "name": t.name,
                "type": t.type,
                "url": t.url,
                "severity": sev,
                **res,
            }

            with open(metrics_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")

            if alert_enabled and sev in ("warn", "crit"):
                msg = {"text": f"[{sev.upper()}] {t.name} latency={event.get('latency_ms')}ms ok={event.get('ok')} url={t.url}", "event": event}
                log.warning(msg["text"])
                if webhook_url:
                    post_webhook(webhook_url, msg)
        time.sleep(interval_s)

if __name__ == "__main__":
    main()
