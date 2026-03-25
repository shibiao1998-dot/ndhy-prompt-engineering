# Multi-stage build: Node.js for frontend + Python for backend
FROM node:20-slim AS frontend-build

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Python runtime
FROM python:3.11-slim

WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./

# Copy frontend build output to static directory
COPY --from=frontend-build /app/frontend/dist/ /app/static/

# Railway injects PORT and DATABASE_URL env vars
ENV PORT=8000
EXPOSE ${PORT}

# Start server - migration runs on startup via lifespan
CMD python -u -m uvicorn main:app --host 0.0.0.0 --port ${PORT} --timeout-keep-alive 1800