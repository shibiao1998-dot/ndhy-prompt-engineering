#!/bin/bash
# Railway / Render build script
set -e

echo "=== Building frontend ==="
cd frontend && npm install && npm run build
cd ..

echo "=== Copying frontend build to backend/static ==="
rm -rf backend/static
cp -r frontend/dist backend/static

echo "=== Installing backend dependencies ==="
cd backend && pip install -r requirements.txt

echo "=== Importing dimension data ==="
python import_from_md.py

echo "=== Build complete ==="
