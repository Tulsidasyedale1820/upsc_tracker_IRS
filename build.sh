#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Install all python modules listed in your requirements file
pip install -r requirements.txt

# 2. Gather all administrative CSS/JS files into one central production folder
python manage.py collectstatic --no-input

# 3. Apply structural data table changes to the cloud database automatically
python manage.py migrate
