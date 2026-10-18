FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY backend/requirements.lock backend/requirements.lock
RUN pip install --no-cache-dir -r backend/requirements.lock
COPY backend backend
COPY patterns patterns
RUN useradd --create-home appuser
USER appuser
EXPOSE 8100
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8100"]
