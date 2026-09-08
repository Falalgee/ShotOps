FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY agent/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY agent/backend/ /app/

ENV PYTHONUNBUFFERED=1

CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
