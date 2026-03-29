FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for TensorFlow, bcrypt, Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (layer cache)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app
COPY ml ./ml
COPY run.py wsgi.py ./

# Models and data are mounted as volumes in docker-compose
# but copy them here as fallback for standalone builds
COPY models ./models
COPY data ./data

EXPOSE 5000

# Use gunicorn in production; run.py handles model/dataset loading via wsgi
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "wsgi:app"]
