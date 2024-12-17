#!/bin/bash
source venv/bin/activate
# flask db upgrade
# flask translate compile
exec gunicorn -b :5000 --timeout 120 --access-logfile - --error-logfile - start:app