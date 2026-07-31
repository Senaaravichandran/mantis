FROM python:3.12-alpine

WORKDIR /app

# System dependencies for PostGIS and async
RUN apk add --no-cache \
    postgresql-dev gcc musl-dev geos-dev proj-dev gdal curl libffi-dev zlib-dev make

# Install shared library deps
COPY shared/ /app/shared/
RUN pip install --no-cache-dir pydantic pydantic-settings

# Install API dependencies directly
RUN pip install --no-cache-dir \
    "fastapi>=0.115.0" \
    "uvicorn[standard]>=0.30.0" \
    "sqlalchemy[asyncio]>=2.0" \
    "asyncpg>=0.29.0" \
    "alembic>=1.13" \
    "pydantic>=2.0" \
    "pydantic-settings>=2.0" \
    "redis>=5.0" \
    "aiokafka>=0.10" \
    "python-multipart>=0.0.9" \
    "geoalchemy2>=0.15" \
    "python-jose[cryptography]>=3.3" \
    "passlib[bcrypt]>=1.7" \
    "httpx>=0.27"

# Copy all source
COPY services/api/ /app/services/api/

ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["uvicorn", "services.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
