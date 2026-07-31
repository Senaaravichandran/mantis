#!/bin/bash
set -e

echo "=========================================="
echo "  MANTIS - Demo Data Seeder"
echo "=========================================="

API_URL="${API_URL:-http://localhost:8000}"

# Wait for API to be ready
echo "[1/3] Waiting for API server..."
MAX_RETRIES=30
RETRY=0
until curl -sf "$API_URL/health" > /dev/null 2>&1; do
  RETRY=$((RETRY + 1))
  if [ $RETRY -ge $MAX_RETRIES ]; then
    echo "ERROR: API server not ready after $MAX_RETRIES attempts"
    exit 1
  fi
  echo "  Waiting... ($RETRY/$MAX_RETRIES)"
  sleep 2
done
echo "  API server is ready!"

# Run the seed script
echo "[2/3] Seeding database with demo data..."
docker compose exec -T api python -m seed
echo "  Seed data loaded!"

# Verify
echo "[3/3] Verifying seed data..."
ASSETS=$(curl -sf "$API_URL/api/v1/assets" | python3 -c "import sys,json; print(json.load(sys.stdin).get('total',0))" 2>/dev/null || echo "0")
ALERTS=$(curl -sf "$API_URL/api/v1/alerts" | python3 -c "import sys,json; print(json.load(sys.stdin).get('total',0))" 2>/dev/null || echo "0")

echo ""
echo "=========================================="
echo "  Seed Complete!"
echo "  Assets: $ASSETS"
echo "  Alerts: $ALERTS"
echo "=========================================="
echo ""
echo "  Dashboard:  http://localhost:3000"
echo "  API Docs:   http://localhost:8000/docs"
echo "  Qdrant UI:  http://localhost:6333/dashboard"
echo "  MinIO:      http://localhost:9001"
echo "=========================================="

# Ensure simulation data is clean
