# Carbon Travel Intelligence API - Production Docker Image
FROM python:3.11-slim

LABEL maintainer="Carbon Travel API"
LABEL description="Carbon- & Resource-Aware Travel Intelligence Platform"

# Set working directory
WORKDIR /app

# Install dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY templates/ ./templates/
COPY config.py .
COPY app.py .

# Expose port
EXPOSE 8080

# Environment variables
ENV FLASK_ENV=production
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "--access-logfile", "-", "app:create_app()"]
