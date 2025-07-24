#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r chat_project/requirments.txt

# Run collectstatic
python chat_project/manage.py collectstatic --no-input
