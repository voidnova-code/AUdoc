#!/usr/bin/env bash
set -o errexit

cd AUdoc_back
python manage.py migrate --noinput
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='sayan').exists() or User.objects.create_superuser('sayan', 'admin@example.com', 'sayan')"
gunicorn AUdoc_back.wsgi:application --bind 0.0.0.0:$PORT
