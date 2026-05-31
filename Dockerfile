# syntax=docker/dockerfile:1
# Python 3.10 is required: the pinned numpy/pandas/scikit-learn versions have no
# wheels for newer Python releases.
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

# Install runtime dependencies first to leverage Docker layer caching.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Application code and the dataset the model trains from at startup.
COPY challenge/ ./challenge/
COPY data/ ./data/

EXPOSE 8080

# Cloud Run injects $PORT (defaults to 8080); bind to it on all interfaces.
CMD ["sh", "-c", "uvicorn challenge.api:app --host 0.0.0.0 --port ${PORT}"]
