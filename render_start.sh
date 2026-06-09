#!/usr/bin/env bash
set -o errexit

cd AUdoc_back
python manage.py migrate --noinput
gunicorn AUdoc_back.wsgi:application --bind 0.0.0.0:$PORT
