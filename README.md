# SecureNetOps Docker Lab (Python examples)

Docker 네트워크 중심으로 구성된 **네트워크 운영 자동화 + 시큐어 코딩** 예제 프로젝트입니다.
교육 과정(네트웍 기초 → GitHub → 파이썬 → Ansible → 기타)을 **Docker Lab**에서 재현 가능하게 만들었습니다.

## 0) 빠른 시작

### 요구사항
- Docker Desktop / Docker Engine + docker compose
- (선택) Python 3.11+ 로컬 실행

### 1) 환경변수 설정
```bash
cp .env.example .env
# 토큰은 교육용(로컬) 값이므로 그대로 써도 됩니다.
```

### 2) 컨테이너 기동
```bash
docker compose up -d --build
docker compose ps
```

### 3) 클라이언트 컨테이너로 들어가기(실습용)
```bash
docker compose exec client bash
```

컨테이너 안에서 아래처럼 실행합니다.

## 1) 네트워크 진단 도구(netdiag)
```bash
python -m tools.netdiag --help
python -m tools.netdiag --targets configs/targets.yml --report reports/netdiag.json
```

## 2) 목적 중심 네트워킹(intent) 적용
```bash
python -m tools.intent_apply --desired configs/desired_state.yml --report reports/intent_report.json
```

## 3) 보안 점검(security_audit)
> **허용 목록(allowlist)** 기반 점검만 포함합니다(범용 포트 스캐너 아님).
```bash
python -m tools.security_audit --policy configs/security_policy.yml --report reports/security_report.json
```

## 4) 모니터링 에이전트(monitor_agent)
```bash
python -m tools.monitor_agent --config configs/monitor.yml
# metrics는 /data/metrics.jsonl 로 쌓입니다.
```

## 5) 테스트(pytest)
```bash
pytest -q
```

---

## 6) Docker 네트워크 구조(고정 IP)
- subnet: `172.30.0.0/24`
- controller_api: `172.30.0.10:8000`
- target_web: `172.30.0.20:8080`
- monitor: `172.30.0.30`
- client: `172.30.0.40`

---

## 7) 디렉토리 구조
```
services/
  controller_api/     # 모의 컨트롤러(API) - 상태 수렴용
  target_web/         # 점검/모니터링 대상 서비스
  monitor/            # 모니터링 에이전트 실행 컨테이너(동일 코드 사용)
  client/             # 실습용(쉘 + 파이썬 실행)
src/
  core/               # config/logger/retry/http/report 등 공통
tools/                # netdiag / intent_apply / security_audit / monitor_agent
configs/              # 대상/정책/의도/모니터링 설정
tests/                # pytest
reports/              # 결과물(JSON) (git에는 비워둬도 OK)
data/                 # 런타임 데이터(모니터링 metrics)
```

---

## 8) 안전/보안 메모
이 프로젝트는 **교육/테스트용**이며, 스캐닝은 **정해진 대상 + 허용 포트**에 대해서만 수행합니다.
실제 운영망에는 반드시 승인된 절차(권한/점검 범위/기록)를 갖춘 뒤 적용하세요.
