FROM python:3.12-alpine

WORKDIR /app

RUN apk add --no-cache postgresql-dev gcc musl-dev

# Install shared deps
COPY shared/ /app/shared/
RUN pip install --no-cache-dir pydantic pydantic-settings

# Install worker dependencies
RUN pip install --no-cache-dir celery redis

# Copy source
COPY services/worker/ /app/services/worker/

ENV PYTHONPATH=/app
CMD ["celery", "-A", "services.worker.celery_app", "worker", "--loglevel=info", "-B"]
