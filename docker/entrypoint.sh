#!/bin/bash
set -e

echo "Running migrations..."
python src/manage.py migrate --no-input

echo "Starting server..."
exec "$@"
