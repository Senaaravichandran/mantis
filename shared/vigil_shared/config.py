"""MANTIS application configuration via environment variables."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # General
    mantis_env: str = "development"
    mantis_debug: bool = True
    mantis_secret_key: str = "change-me-in-production"

    # PostgreSQL
    database_url: str = "postgresql+asyncpg://mantis:mantis_dev_password@localhost:5432/mantis"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "mantis_documents"

    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "mantis_minio"
    minio_secret_key: str = "mantis_minio_secret"
    minio_bucket: str = "mantis-assets"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3:70b-instruct-q4_K_M"
    ollama_fast_model: str = "mistral:7b-instruct-v0.3"
    ollama_embedding_model: str = "bge-m3"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://localhost:3001"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Auth
    auth_enabled: bool = False
    keycloak_url: str = "http://localhost:8080"
    keycloak_realm: str = "mantis"
    keycloak_client_id: str = "mantis-api"

    # External APIs
    noaa_api_base: str = "https://api.weather.gov"
    usgs_api_base: str = "https://waterservices.usgs.gov/nwis"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
