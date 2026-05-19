FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir \
    fastapi>=0.136.0 \
    uvicorn[standard]>=0.34.0 \
    pyjwt>=2.12.0 \
    "pwdlib[argon2]>=0.3.0" \
    sqlalchemy \
    "psycopg[binary]>=3.1.0" \
    python-dotenv>=1.0.0

COPY scripts/entrypoint.py /app/entrypoint.py
COPY src/ ./src/

WORKDIR /app/src

RUN mkdir -p /app/logs \
    && useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/')" || exit 1

ENTRYPOINT ["python", "/app/entrypoint.py"]
