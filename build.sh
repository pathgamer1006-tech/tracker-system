#!/usr/bin/env bash
# Build script for Render

set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput

python manage.py migrate

# Create admin user if it doesn't exist
python manage.py create_admin --username admin --email admin@fitness.com --password admin123
