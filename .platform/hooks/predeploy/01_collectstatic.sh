#!/bin/bash
set -e
cd /var/app/staging
python manage.py collectstatic --noinput
