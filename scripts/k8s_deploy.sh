#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

NAMESPACE="${NAMESPACE:-securenetops-lab}"
CLUSTER_NAME="${KIND_CLUSTER_NAME:-securenetops-lab}"
USE_KIND="${USE_KIND:-true}"

if [[ "$USE_KIND" == "true" ]]; then
  if ! command -v kind >/dev/null 2>&1; then
    echo "[ERR] USE_KIND=true 인데 kind가 설치되어 있지 않습니다."
    exit 1
  fi
  if ! kind get clusters | rg -x "$CLUSTER_NAME" >/dev/null 2>&1; then
    kind create cluster --name "$CLUSTER_NAME"
  fi
fi

if ! command -v kubectl >/dev/null 2>&1; then
  echo "[ERR] kubectl이 필요합니다."
  exit 1
fi

docker build -t securenetops/controller-api:local -f services/controller_api/Dockerfile .
docker build -t securenetops/target-web:local -f services/target_web/Dockerfile .

if [[ "$USE_KIND" == "true" ]]; then
  kind load docker-image securenetops/controller-api:local --name "$CLUSTER_NAME"
  kind load docker-image securenetops/target-web:local --name "$CLUSTER_NAME"
fi

kubectl apply -f k8s/securenetops-lab.yaml
kubectl -n "$NAMESPACE" rollout status deploy/controller-api --timeout=180s
kubectl -n "$NAMESPACE" rollout status deploy/target-web --timeout=180s

echo "[DONE] Kubernetes 배포 완료"
