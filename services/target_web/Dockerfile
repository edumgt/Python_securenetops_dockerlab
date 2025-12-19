FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir "fastapi>=0.112.0" "uvicorn[standard]>=0.30.0"

# ✅ 루트 기준 경로로 복사
COPY services/target_web/app /app/app

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
