FROM python:3.10-slim

WORKDIR /app

# System dependencies for audio/image processing/DB
RUN apt-get update && apt-get install -y gcc libsndfile1 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend directory
COPY backend/ ./backend/

# Set env
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
