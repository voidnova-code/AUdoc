#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
cd AUdoc_back
python manage.py collectstatic --noinput
