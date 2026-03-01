# This is a Dockerfile for the Django web application. It sets up a 
# Python environment, installs dependencies, and runs the app.


FROM python:3.12-slim

# Set working directory inside container.
WORKDIR /app

# Install system dependencies required to build some Python packages.
RUN apt update && \
    apt install -y --no-install-recommends \
        build-essential \
        python3-dev \
        gcc \
        libffi-dev \
        libsystemd-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy everything (project files, app packages, templates, etc.).
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Run migrations and optionally create a superuser (can fail).
ARG DJANGO_SUPERUSER_USERNAME=admin
ARG DJANGO_SUPERUSER_EMAIL=admin@example.com
ARG DJANGO_SUPERUSER_PASSWORD=admin
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate
RUN python3 manage.py createsuperuser --noinput \
    --username "$DJANGO_SUPERUSER_USERNAME" \
    --email "$DJANGO_SUPERUSER_EMAIL" || true

# Django runs on port 8000 by default.
EXPOSE 8000

# runserver listens on all interfaces so the port can be mapped
# to the host. Without the binding the development server only
# accepts connections from inside the container (127.0.0.1).
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]