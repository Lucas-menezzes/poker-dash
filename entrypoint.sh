#!/bin/bash

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating superuser..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | python manage.py shell || true

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
gunicorn poker_dashboard.wsgi --bind 0.0.0.0:$PORT
