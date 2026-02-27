# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 – Build dependencies
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /install

COPY frontend/requirements-frontend.txt .

RUN pip install --upgrade pip \
 && pip install --prefix=/install/deps --no-cache-dir -r requirements-frontend.txt

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 – Runtime image
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /install/deps /usr/local

COPY frontend/streamlit_app.py ./streamlit_app.py

# Non-root user
RUN adduser --disabled-password --gecos "" streamlit_user \
 && chown -R streamlit_user /app
USER streamlit_user

EXPOSE 8501

# headless disables browser auto-launch, CORS allowed for any origin
CMD ["streamlit", "run", "streamlit_app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
