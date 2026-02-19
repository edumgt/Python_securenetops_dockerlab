#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "[INFO] .env 파일이 없어 .env.example로 생성했습니다."
fi

docker compose up -d --build

echo "[DONE] Docker Lab 기동 완료"
docker compose ps
