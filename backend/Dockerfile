# ---------- Base: runtime dependencies ----------
FROM python:3.11-slim AS base

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python deps
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Test stage (CI only: docker build --target test) ----------
FROM base AS test

COPY backend/requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY backend/app ./app
COPY backend/tests ./tests

CMD ["python", "-m", "pytest", "-q"]

# ---------- Production stage (default target, no tests or pytest) ----------
FROM base AS production

# Copy backend app
COPY backend/app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
