FROM python:3.12-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev libffi-dev zlib-dev make

# Install shared deps
COPY shared/ /app/shared/
RUN pip install --no-cache-dir pydantic pydantic-settings

# Install ingestion dependencies directly
RUN pip install --no-cache-dir \
    "aiokafka>=0.10" \
    "pydantic>=2.0" \
    "pydantic-settings>=2.0" \
    "httpx>=0.27" \
    "numpy>=1.26"

# Copy source
COPY services/ingestion/ /app/services/ingestion/

ENV PYTHONPATH=/app
CMD ["python", "-m", "services.ingestion.main"]
