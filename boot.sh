#!/bin/bash
source venv/bin/activate
# flask db upgrade
# flask translate compile
exec gunicorn -b :5000 --timeout 300 --access-logfile - --error-logfile - start:app