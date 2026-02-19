# SecureNetOps Docker Lab (WSL + Docker + Kubernetes)

SecureNetOps 실습을 **WSL2 기반 개발 환경**에서 바로 돌릴 수 있도록 정리한 레포입니다.
기존 Docker Lab 흐름을 유지하면서, 동일 서비스를 **Kubernetes(kind/minikube 등)** 에 배포하고 스모크 테스트까지 수행할 수 있게 구성했습니다.

---

## 1. 목표

- WSL2 Ubuntu 기준으로 실습 환경 빠르게 셋업
- Docker Compose 기반 네트워크 자동화/보안 도구 실행
- Kubernetes로 배포 후 핵심 기능 스모크 테스트 수행

---

## 2. WSL2 기반 권장 환경

### 필수
- Windows 11 + WSL2 (Ubuntu 22.04 이상 권장)
- Docker Desktop (WSL integration ON)
- Docker Compose plugin

### Kubernetes 실습 시 추가
- `kubectl`
- `kind` (권장) 또는 기존 K8s 클러스터 컨텍스트

---

## 3. 빠른 시작 (WSL)

### 3.1 사전 점검
```bash
bash scripts/wsl_preflight.sh
```

### 3.2 Docker Lab 기동
```bash
bash scripts/lab_up.sh
```

### 3.3 클라이언트 컨테이너 진입
```bash
docker compose exec client bash
```

컨테이너 내부에서 아래 도구를 실행할 수 있습니다.

```bash
python -m tools.netdiag --targets configs/targets.yml --report reports/netdiag.json
python -m tools.intent_apply --desired configs/desired_state.yml --report reports/intent_report.json
python -m tools.security_audit --policy configs/security_policy.yml --report reports/security_report.json
python -m tools.monitor_agent --config configs/monitor.yml
```

### 3.4 종료
```bash
bash scripts/lab_down.sh
```

---

## 4. Kubernetes 배포 및 테스트

> 아래는 `kind` 사용 기준입니다. 기존 클러스터를 쓰면 `USE_KIND=false`로 실행하세요.

### 4.1 배포
```bash
bash scripts/k8s_deploy.sh
```

실행 내용:
1. (옵션) kind 클러스터 생성
2. 컨테이너 이미지 빌드
3. kind 클러스터에 이미지 로드
4. `k8s/securenetops-lab.yaml` 적용 및 rollout 확인

### 4.2 K8s 스모크 테스트
```bash
bash scripts/k8s_smoke_test.sh
```

검증 항목:
- `controller-api /health` 응답
- `controller-api /state` 인증 포함 응답
- `target-web /health` 응답
- `target-web /` 보안 헤더(`X-Frame-Options: DENY`) 확인

---

## 5. 디렉토리

```text
services/
  controller_api/     # 모의 컨트롤러 API
  target_web/         # 테스트 대상 웹 서비스
  monitor/            # 모니터링 실행 이미지
  client/             # 실습용 컨테이너
src/core/             # config/logger/retry/http/report
tools/                # netdiag / intent_apply / security_audit / monitor_agent
configs/              # 대상/정책/의도/모니터링 설정
scripts/              # WSL/Compose/K8s 운영 스크립트
k8s/                  # Kubernetes 매니페스트
tests/                # pytest
```

---

## 6. 테스트 명령

```bash
pytest -q
bash scripts/wsl_preflight.sh
# (K8s 환경 준비 시)
bash scripts/k8s_deploy.sh
bash scripts/k8s_smoke_test.sh
```

---

## 7. 보안/운영 주의

- 본 프로젝트는 교육/검증 목적입니다.
- 스캔/점검은 반드시 승인된 대상과 범위에서만 수행하세요.
- 운영망 적용 시 인증토큰/시크릿/접근제어/감사로그 정책을 별도 적용하세요.
