FROM node:22-alpine AS frontend-build
WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install --include=dev --no-audit --no-fund
COPY frontend/ ./
# Empty API URL makes the browser use the same origin as the frontend.
ENV VITE_API_URL=""
RUN npm run build

FROM python:3.11.2-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    FRONTEND_DIST=/app/static \
    PORT=10000
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app
COPY --from=frontend-build /build/frontend/dist ./static
EXPOSE 10000
CMD ["sh", "-c", "exec uvicorn app.render:app --host 0.0.0.0 --port \"${PORT:-10000}\""]
