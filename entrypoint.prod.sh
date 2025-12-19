#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static..."
python manage.py collectstatic --noinput

# Iniciar django-q worker em background
echo "Starting django-q worker..."
python manage.py qcluster &
QCluster_PID=$!

echo "Starting Gunicorn..."
exec gunicorn core.wsgi:application \
  --bind 0.0.0.0:8080 \
  --log-level debug \
  --access-logfile - \
  --error-logfile -

