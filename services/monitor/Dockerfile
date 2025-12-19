FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY ../../pyproject.toml /app/pyproject.toml
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir "requests>=2.32.0" "PyYAML>=6.0.2" "pydantic>=2.8.0" "tenacity>=9.0.0"

COPY ../../src /app/src
COPY ../../tools /app/tools
COPY ../../configs /app/configs

CMD ["python", "-m", "tools.monitor_agent", "--config", "configs/monitor.yml"]
