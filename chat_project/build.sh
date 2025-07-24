#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r chat_project/requirements.txt

# Run collectstatic
python manage.py chat_project/collectstatic --no-input
