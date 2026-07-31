# MANTIS - Vigilant Infrastructure Guardian with Intelligent Lifecycle Management

An open-source multi-agent AI platform for predictive municipal infrastructure intelligence. MANTIS uses 6 LLM-powered agents orchestrated by LangGraph to monitor bridges, water mains, roads, and other infrastructure assets — generating alerts, work orders, compliance filings, and maintenance schedules autonomously.

## Architecture

```
                     +-------------------+
                     |   Next.js 14 UI   |
                     |   (Dashboard)     |
                     +--------+----------+
                              |
                     +--------v----------+
                     |   FastAPI Backend  |
                     |   REST + WebSocket |
                     +--------+----------+
                              |
          +-------------------+-------------------+
          |                   |                   |
+---------v------+  +---------v------+  +--------v--------+
| Agent Service  |  |  ML Service    |  | Ingestion Svc   |
| (LangGraph)    |  | (PyOD/Prophet) |  | (Kafka + APIs)  |
+----------------+  +----------------+  +-----------------+
          |                   |                   |
+---------v-------------------v-------------------v--------+
|                    Infrastructure                         |
| PostgreSQL+TimescaleDB | Redis | Kafka | Qdrant | MinIO  |
+----------------------------------------------------------+
```

## 6 AI Agents

| Agent | Role | Capabilities |
|-------|------|-------------|
| **Sentinel** | Anomaly Detection | Monitors sensors, flags deviations > 2 sigma, correlates weather |
| **Analyst** | Risk Scoring | Root cause analysis, multi-factor risk assessment, failure prediction |
| **Planner** | Maintenance Planning | Work order drafting, cost estimation, priority scheduling |
| **Reporter** | Communication | Report generation, Slack/email notifications, executive summaries |
| **Contractor** | Procurement | RFQ drafting, bid comparison, contractor matching |
| **Regulator** | Compliance | Inspection cycle tracking, regulatory filing, deadline monitoring |

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy 2.x (async), Pydantic 2.x
- **Database**: PostgreSQL 16 + TimescaleDB + PostGIS
- **AI/ML**: LangGraph, Ollama (LLaMA 3 + Mistral), PyOD, NeuralProphet, XGBoost
- **Vector DB**: Qdrant (RAG over infrastructure documents)
- **Streaming**: Apache Kafka (sensor data + agent events)
- **Task Queue**: Celery + Redis
- **Frontend**: Next.js 14, TanStack Query, Zustand, Recharts, Tailwind CSS
- **Storage**: MinIO (S3-compatible)
- **Infrastructure**: Docker Compose

## Quick Start

### Prerequisites

- Docker & Docker Compose
- 16GB+ RAM recommended
- NVIDIA GPU (optional, for Ollama acceleration)

### 1. Clone and configure

```bash
cd mantis
cp .env.example .env
```

### 2. Start all services

```bash
make up
```

This starts: PostgreSQL/TimescaleDB, Redis, Kafka, Qdrant, MinIO, Ollama, and all MANTIS services.

### 3. Seed demo data

```bash
make seed
```

Loads 2 municipalities, 20+ infrastructure assets (Pittsburgh, PA), 30 days of sensor data, alerts, and work orders.

### 4. Pull LLM models (first time only)

```bash
make ollama-setup
```

Downloads LLaMA 3 and Mistral models for local inference.

### 5. Access the platform

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:3000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Qdrant UI | http://localhost:6333/dashboard |
| MinIO Console | http://localhost:9001 |

## Development

### Run services individually (hot reload)

```bash
make dev-api    # FastAPI with uvicorn --reload
make dev-web    # Next.js dev server
```

### Run tests

```bash
make test
```

### View logs

```bash
make logs            # All services
make logs s=api      # Single service
```

## Project Structure

```
mantis/
├── docker-compose.yml        # Full dev stack
├── Makefile                  # Dev shortcuts
├── .env.example              # Environment template
├── shared/                   # Shared Python library
│   └── mantis_shared/        # Constants, config, models
├── services/
│   ├── api/                  # FastAPI REST backend
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── routers/         # API endpoints
│   │   ├── database/        # DB connection + init SQL
│   │   ├── middleware/      # Audit log, request ID
│   │   ├── auth/            # JWT auth (optional)
│   │   └── seed.py          # Demo data seeder
│   ├── agents/               # LangGraph agent service
│   │   ├── agents/          # 6 agent implementations
│   │   ├── graph/           # StateGraph + routing
│   │   ├── tools/           # Agent tools (DB, vector, weather)
│   │   ├── llm/             # Ollama provider + prompts
│   │   ├── rag/             # Document indexer + retriever
│   │   └── memory/          # Episodic + working memory
│   ├── ml/                   # ML service
│   │   ├── anomaly/         # PyOD + River detectors
│   │   ├── forecasting/     # NeuralProphet + XGBoost
│   │   └── vision/          # Satellite + crack detection
│   ├── ingestion/            # Data ingestion service
│   │   ├── connectors/      # Simulator, NOAA, USGS, SCADA
│   │   └── schemas/         # Event schemas
│   └── worker/               # Celery worker service
│       └── tasks/           # Scheduled scans, reports
├── web/                      # Next.js 14 dashboard
│   ├── app/                 # Pages (App Router)
│   ├── components/          # UI + chart + map components
│   └── lib/                 # API client, store, utils
└── scripts/                  # Utility scripts
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/assets` | List all infrastructure assets |
| GET | `/api/v1/assets/{id}` | Get asset details |
| POST | `/api/v1/sensors/readings` | Ingest sensor data |
| GET | `/api/v1/sensors/{asset_id}/history` | Sensor history |
| GET | `/api/v1/alerts` | List alerts |
| POST | `/api/v1/alerts/{id}/acknowledge` | Acknowledge alert |
| POST | `/api/v1/alerts/{id}/resolve` | Resolve alert |
| GET | `/api/v1/workorders` | List work orders |
| POST | `/api/v1/workorders/{id}/approve` | Approve work order |
| GET | `/api/v1/analytics/dashboard` | Dashboard stats |
| POST | `/api/v1/agents/trigger` | Trigger agent run |
| GET | `/api/v1/agents/runs` | Agent run history |

## Infrastructure Assets Supported

- Bridges
- Water mains
- Roads
- Tunnels
- Pump stations
- Culverts
- Retention basins
- Sewer lines

## Sensor Types

Vibration, strain, temperature, water level, flow rate, pressure, displacement, corrosion, humidity, pH

## License

Apache License 2.0 - see [LICENSE](LICENSE)
