#!/usr/bin/env bash
set -euo pipefail

if ! grep -qiE "microsoft|wsl" /proc/version 2>/dev/null; then
  echo "[WARN] WSL 환경이 아닌 것으로 보입니다. (Linux 네이티브면 무시 가능)"
else
  echo "[OK] WSL 환경 감지"
fi

required_cmds=(docker)
for cmd in "${required_cmds[@]}"; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "[ERR] '$cmd' 명령을 찾을 수 없습니다. 설치 후 다시 시도하세요."
    exit 1
  fi
  echo "[OK] $cmd 확인"
done

if docker compose version >/dev/null 2>&1; then
  echo "[OK] docker compose 확인"
else
  echo "[ERR] docker compose plugin이 필요합니다."
  exit 1
fi

if command -v kubectl >/dev/null 2>&1; then
  echo "[OK] kubectl 확인"
else
  echo "[WARN] kubectl 없음 (Kubernetes 테스트는 건너뜀)"
fi

if command -v kind >/dev/null 2>&1; then
  echo "[OK] kind 확인"
else
  echo "[WARN] kind 없음 (로컬 클러스터 자동 구성 기능은 비활성)"
fi

echo "[DONE] 사전 점검 완료"
