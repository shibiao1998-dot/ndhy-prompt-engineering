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

# Copy frontend build output (includes ai-employee-demo.html)
COPY --from=frontend-build /app/frontend/dist/ ./static/

# Create data directory for database
RUN mkdir -p /app/data

# Import 111 dimensions into database
RUN python migrate_111_dimensions.py || true

# Railway injects PORT env var
ENV PORT=8000
# Use /app/data for database (persistent volume)
ENV DATABASE_URL=/app/data/prompt_engineering.db
EXPOSE ${PORT}

# Start server with 30min keep-alive for long SSE streams
# Use shell form so $PORT is expanded at runtime
CMD python -u -m uvicorn main:app --host 0.0.0.0 --port ${PORT} --timeout-keep-alive 1800
