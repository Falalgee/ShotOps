FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    NO_GCE_CHECK=true \
    GEMINI_MODEL=gemini-flash-lite-latest

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt* pyproject.toml* ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    if [ -f pyproject.toml ]; then pip install --no-cache-dir .; fi && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi && \
    pip install --no-cache-dir uvicorn httpx pydantic fastapi google-genai

COPY . .

EXPOSE 8000

CMD ["python3", "-m", "uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]
