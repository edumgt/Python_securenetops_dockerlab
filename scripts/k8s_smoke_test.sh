#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${NAMESPACE:-securenetops-lab}"
TOKEN="${CONTROLLER_API_TOKEN:-dev-token-please-change}"

if ! command -v kubectl >/dev/null 2>&1; then
  echo "[ERR] kubectl이 필요합니다."
  exit 1
fi
if ! command -v curl >/dev/null 2>&1; then
  echo "[ERR] curl이 필요합니다."
  exit 1
fi

kubectl -n "$NAMESPACE" wait --for=condition=available deploy/controller-api --timeout=180s
kubectl -n "$NAMESPACE" wait --for=condition=available deploy/target-web --timeout=180s

cleanup() {
  [[ -n "${PF1_PID:-}" ]] && kill "$PF1_PID" >/dev/null 2>&1 || true
  [[ -n "${PF2_PID:-}" ]] && kill "$PF2_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT

kubectl -n "$NAMESPACE" port-forward svc/controller-api 18000:8000 >/tmp/securenetops-pf-controller.log 2>&1 &
PF1_PID=$!
kubectl -n "$NAMESPACE" port-forward svc/target-web 18080:8080 >/tmp/securenetops-pf-target.log 2>&1 &
PF2_PID=$!
sleep 2

curl -fsS http://127.0.0.1:18000/health >/dev/null
curl -fsS -H "Authorization: Bearer $TOKEN" http://127.0.0.1:18000/state >/dev/null
curl -fsS http://127.0.0.1:18080/health >/dev/null
curl -fsS -I http://127.0.0.1:18080/ | rg -qi "x-frame-options: DENY"

echo "[DONE] Kubernetes smoke test 통과"
