FROM python:3.12-alpine

WORKDIR /app

RUN apk add --no-cache postgresql-dev gcc musl-dev libffi-dev zlib-dev make

# Install shared deps
COPY shared/ /app/shared/
RUN pip install --no-cache-dir pydantic pydantic-settings

# Install agent dependencies directly
RUN pip install --no-cache-dir \
    "langgraph>=0.2.0" \
    "langchain>=0.3.0" \
    "langchain-community>=0.3.0" \
    "langchain-ollama>=0.2.0" \
    "pydantic>=2.0" \
    "pydantic-settings>=2.0" \
    "sqlalchemy[asyncio]>=2.0" \
    "asyncpg>=0.29.0" \
    "aiokafka>=0.10" \
    "qdrant-client>=1.10" \
    "httpx>=0.27" \
    "numpy>=1.26" \
    "redis>=5.0"

# Copy source
COPY services/ml/ /app/services/ml/
COPY services/agents/ /app/services/agents/

ENV PYTHONPATH=/app
CMD ["python", "-m", "services.agents.main"]
