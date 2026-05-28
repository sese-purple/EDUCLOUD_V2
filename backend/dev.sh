#!/usr/bin/env bash
# Activate venv and run Django dev server
DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/venv/Scripts/activate"
python "$DIR/manage.py" runserver
