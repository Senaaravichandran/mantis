-- ============================================================
-- MANTIS DATABASE INITIALIZATION
-- PostgreSQL 16 + TimescaleDB + PostGIS
-- ============================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "timescaledb";

-- ============================================================
-- ENUM TYPES
-- ============================================================
CREATE TYPE asset_type AS ENUM (
  'bridge', 'water_main', 'road', 'power_line',
  'tunnel', 'pump_station', 'culvert', 'retention_basin'
);

CREATE TYPE risk_level AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE alert_severity AS ENUM ('info', 'warning', 'critical', 'emergency');
CREATE TYPE work_order_status AS ENUM (
  'draft', 'pending_approval', 'approved', 'in_progress',
  'completed', 'cancelled', 'on_hold'
);

-- ============================================================
-- MUNICIPALITIES
-- ============================================================
CREATE TABLE municipalities (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name          VARCHAR(255) NOT NULL,
  state         VARCHAR(100),
  country       VARCHAR(100) DEFAULT 'US',
  population    INT,
  area_sq_km    FLOAT,
  timezone      VARCHAR(50) DEFAULT 'America/New_York',
  geom          GEOMETRY(Point, 4326),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- USERS
-- ============================================================
CREATE TABLE users (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  municipality_id UUID REFERENCES municipalities(id),
  email         VARCHAR(255) UNIQUE NOT NULL,
  full_name     VARCHAR(255) NOT NULL,
  role          VARCHAR(50) NOT NULL DEFAULT 'engineer',
  keycloak_id   VARCHAR(255),
  is_active     BOOLEAN DEFAULT TRUE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- INFRASTRUCTURE ASSETS
-- ============================================================
CREATE TABLE assets (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  municipality_id       UUID NOT NULL REFERENCES municipalities(id),
  name                  VARCHAR(255) NOT NULL,
  asset_type            asset_type NOT NULL,
  geom                  GEOMETRY(Geometry, 4326) NOT NULL,
  installation_date     DATE,
  design_life_years     INT,
  material              VARCHAR(100),
  manufacturer          VARCHAR(255),
  diameter_mm           INT,
  span_m                FLOAT,
  last_inspection_date  DATE,
  next_inspection_date  DATE,
  current_health_score  FLOAT CHECK (current_health_score BETWEEN 0 AND 100),
  risk_level            risk_level NOT NULL DEFAULT 'low',
  fhwa_id               VARCHAR(50),
  epa_id                VARCHAR(50),
  metadata              JSONB DEFAULT '{}',
  created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_assets_geom ON assets USING GIST(geom);
CREATE INDEX idx_assets_municipality ON assets(municipality_id);
CREATE INDEX idx_assets_risk ON assets(risk_level);
CREATE INDEX idx_assets_type ON assets(asset_type);

-- ============================================================
-- SENSOR READINGS (TimescaleDB Hypertable)
-- ============================================================
CREATE TABLE sensor_readings (
  time          TIMESTAMPTZ NOT NULL,
  asset_id      UUID NOT NULL REFERENCES assets(id),
  sensor_id     VARCHAR(100) NOT NULL,
  sensor_type   VARCHAR(100) NOT NULL,
  value         DOUBLE PRECISION NOT NULL,
  unit          VARCHAR(50),
  quality_flag  VARCHAR(20) DEFAULT 'good',
  raw_payload   JSONB
);

SELECT create_hypertable('sensor_readings', 'time', chunk_time_interval => INTERVAL '1 day');

-- Compression policy for data older than 7 days
ALTER TABLE sensor_readings SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'asset_id, sensor_type'
);
SELECT add_compression_policy('sensor_readings', INTERVAL '7 days');

-- Continuous aggregate for hourly rollups
CREATE MATERIALIZED VIEW sensor_hourly
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 hour', time) AS bucket,
       asset_id, sensor_type,
       avg(value) AS avg_val,
       max(value) AS max_val,
       min(value) AS min_val,
       count(*) AS reading_count
FROM sensor_readings
GROUP BY bucket, asset_id, sensor_type;

-- Retention: keep raw data 2 years
SELECT add_retention_policy('sensor_readings', INTERVAL '2 years');

-- ============================================================
-- AGENT RUNS (Audit Trail)
-- ============================================================
CREATE TABLE agent_runs (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  municipality_id UUID NOT NULL REFERENCES municipalities(id),
  agent_type      VARCHAR(50) NOT NULL,
  trigger_type    VARCHAR(50),
  trigger_ref     UUID,
  status          VARCHAR(20) NOT NULL DEFAULT 'running',
  input_context   JSONB,
  thought_chain   JSONB DEFAULT '[]',
  output          JSONB,
  model_used      VARCHAR(100),
  tokens_used     INT,
  cost_estimate   DECIMAL(8, 4),
  error_message   TEXT,
  started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at    TIMESTAMPTZ
);

CREATE INDEX idx_agent_runs_municipality ON agent_runs(municipality_id);
CREATE INDEX idx_agent_runs_status ON agent_runs(status);

-- ============================================================
-- ALERTS
-- ============================================================
CREATE TABLE alerts (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_id          UUID NOT NULL REFERENCES assets(id),
  municipality_id   UUID NOT NULL REFERENCES municipalities(id),
  severity          alert_severity NOT NULL,
  anomaly_type      VARCHAR(100),
  title             VARCHAR(255) NOT NULL,
  description       TEXT NOT NULL,
  agent_reasoning   TEXT,
  confidence_score  FLOAT,
  risk_score        FLOAT,
  affected_sensors  JSONB,
  weather_context   JSONB,
  agent_run_id      UUID REFERENCES agent_runs(id),
  detected_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  acknowledged_at   TIMESTAMPTZ,
  acknowledged_by   UUID REFERENCES users(id),
  resolved_at       TIMESTAMPTZ,
  is_false_positive BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_alerts_asset ON alerts(asset_id);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_detected ON alerts(detected_at DESC);

-- ============================================================
-- CONTRACTORS
-- ============================================================
CREATE TABLE contractors (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name            VARCHAR(255) NOT NULL,
  specialty       VARCHAR(255),
  location        VARCHAR(255),
  phone           VARCHAR(50),
  email           VARCHAR(255),
  rating          FLOAT CHECK (rating BETWEEN 0 AND 5),
  sam_uei         VARCHAR(50),
  is_active       BOOLEAN DEFAULT TRUE,
  metadata        JSONB DEFAULT '{}',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- WORK ORDERS
-- ============================================================
CREATE TABLE work_orders (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  alert_id          UUID REFERENCES alerts(id),
  asset_id          UUID NOT NULL REFERENCES assets(id),
  municipality_id   UUID NOT NULL REFERENCES municipalities(id),
  status            work_order_status NOT NULL DEFAULT 'draft',
  priority          INT CHECK (priority BETWEEN 1 AND 5),
  title             VARCHAR(255) NOT NULL,
  scope_of_work     TEXT NOT NULL,
  estimated_cost    DECIMAL(12, 2),
  actual_cost       DECIMAL(12, 2),
  generated_by      VARCHAR(20) DEFAULT 'agent',
  agent_run_id      UUID REFERENCES agent_runs(id),
  approved_by       UUID REFERENCES users(id),
  approved_at       TIMESTAMPTZ,
  contractor_id     UUID REFERENCES contractors(id),
  scheduled_date    DATE,
  completed_date    DATE,
  regulatory_refs   JSONB,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_workorders_asset ON work_orders(asset_id);
CREATE INDEX idx_workorders_status ON work_orders(status);

-- ============================================================
-- DOCUMENTS (RAG Corpus)
-- ============================================================
CREATE TABLE documents (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_id        UUID REFERENCES assets(id),
  municipality_id UUID REFERENCES municipalities(id),
  doc_type        VARCHAR(100),
  title           VARCHAR(255),
  source_path     VARCHAR(500),
  content_text    TEXT,
  qdrant_point_id VARCHAR(100),
  page_count      INT,
  file_size_bytes BIGINT,
  inspection_date DATE,
  inspector_name  VARCHAR(255),
  processed       BOOLEAN DEFAULT FALSE,
  uploaded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_documents_asset ON documents(asset_id);

-- ============================================================
-- COMPLIANCE FILINGS
-- ============================================================
CREATE TABLE compliance_filings (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  municipality_id UUID NOT NULL REFERENCES municipalities(id),
  asset_id        UUID REFERENCES assets(id),
  filing_type     VARCHAR(100) NOT NULL,
  agency          VARCHAR(100) NOT NULL,
  due_date        DATE NOT NULL,
  filed_date      DATE,
  status          VARCHAR(50) DEFAULT 'pending',
  filing_data     JSONB,
  agent_run_id    UUID REFERENCES agent_runs(id),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_compliance_due ON compliance_filings(due_date);
