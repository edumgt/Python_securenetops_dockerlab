from __future__ import annotations
import argparse
from typing import Any, Dict, List

from src.core.config import load_yaml, env
from src.core.http import HttpClient, HttpError
from src.core.logger import get_logger
from src.core.report import Report, utcnow_iso, write_json

log = get_logger(__name__)

def main():
    ap = argparse.ArgumentParser(description="Apply desired state (intent) via controller API (lab)")
    ap.add_argument("--desired", default="configs/desired_state.yml")
    ap.add_argument("--report", default="reports/intent_report.json")
    args = ap.parse_args()

    token = env("CONTROLLER_API_TOKEN", "dev-token-please-change")
    desired = load_yaml(args.desired).get("desired_state", {})
    cli = HttpClient(base_url="http://172.30.0.10:8000", token=token, timeout_s=3)

    items: List[Dict[str, Any]] = []

    try:
        current = cli.request("GET", "/state", timeout_s=2)
        items.append({"step": "get_current", "ok": True, "current": current})
    except Exception as e:
        items.append({"step": "get_current", "ok": False, "error": str(e)})
        write_json(args.report, Report("intent_apply", utcnow_iso(), False, {"reason": "cannot read current"}, items).to_dict())
        raise

    # Compute diff (simple)
    diff: Dict[str, Any] = {}
    for k, v in desired.items():
        if current.get(k) != v:
            diff[k] = {"from": current.get(k), "to": v}

    items.append({"step": "diff", "ok": True, "diff": diff})

    if diff:
        try:
            res = cli.request("POST", "/state", json=desired, timeout_s=3)
            items.append({"step": "apply", "ok": True, "result": res})
        except HttpError as e:
            items.append({"step": "apply", "ok": False, "status_code": e.status_code, "payload": e.payload})
        except Exception as e:
            items.append({"step": "apply", "ok": False, "error": str(e)})
    else:
        items.append({"step": "apply", "ok": True, "result": "already converged"})

    # Verify converge
    try:
        after = cli.request("GET", "/state", timeout_s=2)
        ok = True
        for k, v in desired.items():
            if after.get(k) != v:
                ok = False
        items.append({"step": "verify", "ok": ok, "state": after})
    except Exception as e:
        items.append({"step": "verify", "ok": False, "error": str(e)})
        ok = False

    summary = {"desired_keys": list(desired.keys()), "changed": bool(diff)}
    rep = Report("intent_apply", utcnow_iso(), ok, summary, items)
    write_json(args.report, rep.to_dict())
    log.info(f"Wrote report: {args.report} (ok={ok})")

if __name__ == "__main__":
    main()
