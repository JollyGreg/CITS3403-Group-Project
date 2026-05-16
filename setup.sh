#!/bin/bash
set -e

echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Removing potential existing database...
rm -f instance/chess.db

echo "Initializing database..."
python db.py

echo "Setup complete!"   
echo
echo To run the application:
echo   python app.py
echo