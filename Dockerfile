# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 – Build dependencies
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /install

# Copy both requirements files
COPY requirements-backend.txt .
COPY frontend/requirements-frontend.txt ./frontend-requirements.txt

RUN pip install --upgrade pip \
 && pip install --prefix=/install/deps --no-cache-dir -r requirements-backend.txt -r frontend-requirements.txt

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 – Runtime image
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install curl for the start.sh healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install/deps /usr/local

# Copy source code and scripts
COPY app/      ./app/
COPY data/     ./data/
COPY frontend/ ./frontend/
COPY start.sh  ./start.sh

# Make start script executable and fix line endings (for Windows hosts)
RUN chmod +x start.sh && sed -i 's/\r$//' start.sh

# Non-root user for security
RUN adduser --disabled-password --gecos "" appuser \
 && chown -R appuser /app
USER appuser

EXPOSE 8000 8501

CMD ["./start.sh"]
