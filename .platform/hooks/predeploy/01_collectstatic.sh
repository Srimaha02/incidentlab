#!/bin/bash
set -e
cd /var/app/staging
PYTHON="$(printf '%s\n' /var/app/venv/staging-*/bin/python3 | head -n 1)"
if [ ! -x "$PYTHON" ]; then
  echo "Application Python executable not found: $PYTHON" >&2
  exit 1
fi
"$PYTHON" manage.py collectstatic --noinput
