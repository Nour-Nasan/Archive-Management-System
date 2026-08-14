#!/usr/bin/env bash
# Render build script for Archive Management System
# Render runs this once during each deploy before starting the web service.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py seed_initial_data
