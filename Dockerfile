# ---- SupportX AI Assist — Streamlit container ----
# Build:  docker build -t supportx-ai .
# Run:    docker run --rm -p 8000:8000 --env-file .env supportx-ai
# Open:   http://localhost:8000

FROM python:3.12-slim

# 1. Workdir
WORKDIR /app

# 2. Minimal system deps (CA certs for HTTPS to Azure OpenAI / Azure Search)
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 3. Install Python deps first so this layer is cached when only code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 4. Copy source. .dockerignore keeps .env, venv/, __pycache__/, .git/ out.
COPY . .

# 5. Make sure the logs dir exists (utility/guardrails.py writes into it).
RUN mkdir -p logs

# 6. Streamlit config via env vars (mirrors what startup.txt passes on CLI).
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=8000 \
    STREAMLIT_SERVER_ENABLE_CORS=false \
    STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# 7. Network
EXPOSE 8000

# 8. Healthcheck — Streamlit exposes /_stcore/health
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; \
        sys.exit(0) if urllib.request.urlopen('http://localhost:8000/_stcore/health', timeout=3).status == 200 else sys.exit(1)" \
        || exit 1

# 9. Launch
CMD ["python", "-m", "streamlit", "run", "app.py"]
