FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml /app/pyproject.toml
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir "requests>=2.32.0" "PyYAML>=6.0.2" "pydantic>=2.8.0" "tenacity>=9.0.0" "fastapi>=0.112.0" "uvicorn[standard]>=0.30.0"

COPY src /app/src
# ✅ 루트 기준 경로로 복사
COPY services/controller_api/app /app/app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
