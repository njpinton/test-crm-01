# Use official Python runtime as base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/production.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files - MUST succeed or build fails
# Note: Requires DJANGO_SECRET_KEY to be set as build arg
ARG DJANGO_SECRET_KEY=build-time-only-key
ENV DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
RUN python manage.py collectstatic --noinput --settings=config.settings.production

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port (Cloud Run uses PORT env variable)
EXPOSE 8080

# Run gunicorn
CMD exec gunicorn config.wsgi:application \
    --bind :$PORT \
    --workers 2 \
    --threads 4 \
    --timeout 0 \
    --access-logfile - \
    --error-logfile -
