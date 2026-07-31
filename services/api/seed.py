"""MANTIS Demo Data Seeder — creates realistic sample data for development."""

import asyncio
import sys
import os
import random
from datetime import datetime, timedelta, timezone, date
from uuid import uuid4

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))

from sqlalchemy import text
from services.api.database.connection import engine, async_session

# Fixed UUIDs for deterministic seeding
MUNICIPALITY_1 = uuid4()
MUNICIPALITY_2 = uuid4()
USER_1 = uuid4()
USER_2 = uuid4()

# Sample infrastructure assets with realistic coordinates (Pittsburgh, PA area)
ASSETS = [
    # Bridges
    {"name": "Highland Park Bridge", "type": "bridge", "lat": 40.4856, "lng": -79.9185, "material": "Steel", "span_m": 278, "year": 1957, "health": 62, "risk": "medium"},
    {"name": "Smithfield Street Bridge", "type": "bridge", "lat": 40.4341, "lng": -79.9984, "material": "Steel truss", "span_m": 366, "year": 1883, "health": 45, "risk": "high"},
    {"name": "Fort Pitt Bridge", "type": "bridge", "lat": 40.4360, "lng": -80.0075, "material": "Steel arch", "span_m": 228, "year": 1959, "health": 71, "risk": "medium"},
    {"name": "Roberto Clemente Bridge", "type": "bridge", "lat": 40.4456, "lng": -80.0006, "material": "Steel", "span_m": 228, "year": 1928, "health": 55, "risk": "high"},
    {"name": "Liberty Bridge", "type": "bridge", "lat": 40.4295, "lng": -79.9963, "material": "Steel", "span_m": 470, "year": 1928, "health": 38, "risk": "critical"},
    # Water Mains
    {"name": "Forbes Ave Main - Section A", "type": "water_main", "lat": 40.4400, "lng": -79.9580, "material": "Cast iron", "diameter_mm": 300, "year": 1965, "health": 52, "risk": "high"},
    {"name": "Fifth Ave Main - Section B", "type": "water_main", "lat": 40.4420, "lng": -79.9540, "material": "Ductile iron", "diameter_mm": 450, "year": 1982, "health": 75, "risk": "low"},
    {"name": "Murray Ave Main", "type": "water_main", "lat": 40.4310, "lng": -79.9250, "material": "Cast iron", "diameter_mm": 200, "year": 1952, "health": 35, "risk": "critical"},
    {"name": "Beechwood Blvd Main", "type": "water_main", "lat": 40.4380, "lng": -79.9200, "material": "PVC", "diameter_mm": 250, "year": 1998, "health": 88, "risk": "low"},
    {"name": "Carson St Main", "type": "water_main", "lat": 40.4280, "lng": -79.9700, "material": "Cast iron", "diameter_mm": 350, "year": 1958, "health": 48, "risk": "high"},
    # Roads
    {"name": "Penn Ave - Oakland Segment", "type": "road", "lat": 40.4440, "lng": -79.9530, "material": "Asphalt", "year": 2015, "health": 82, "risk": "low"},
    {"name": "Bigelow Blvd", "type": "road", "lat": 40.4490, "lng": -79.9510, "material": "Asphalt", "year": 2008, "health": 61, "risk": "medium"},
    {"name": "Boulevard of the Allies", "type": "road", "lat": 40.4370, "lng": -79.9620, "material": "Asphalt", "year": 2005, "health": 55, "risk": "medium"},
    # Tunnels
    {"name": "Liberty Tunnel", "type": "tunnel", "lat": 40.4180, "lng": -79.9890, "material": "Concrete lined", "year": 1924, "health": 58, "risk": "medium"},
    {"name": "Squirrel Hill Tunnel", "type": "tunnel", "lat": 40.4310, "lng": -79.9080, "material": "Concrete", "year": 1953, "health": 64, "risk": "medium"},
    # Pump Stations
    {"name": "Aspinwall Pump Station", "type": "pump_station", "lat": 40.4870, "lng": -79.9050, "material": "Concrete/Steel", "year": 1978, "health": 70, "risk": "low"},
    {"name": "Hays Pump Station", "type": "pump_station", "lat": 40.4050, "lng": -79.9340, "material": "Concrete", "year": 1985, "health": 65, "risk": "medium"},
    # Culverts
    {"name": "Four Mile Run Culvert", "type": "culvert", "lat": 40.4350, "lng": -79.9350, "material": "Corrugated steel", "diameter_mm": 1200, "year": 1970, "health": 42, "risk": "high"},
    {"name": "Nine Mile Run Culvert", "type": "culvert", "lat": 40.4240, "lng": -79.9100, "material": "Concrete box", "diameter_mm": 2400, "year": 1968, "health": 50, "risk": "high"},
    # Retention Basins
    {"name": "Panther Hollow Retention Basin", "type": "retention_basin", "lat": 40.4350, "lng": -79.9470, "material": "Earth/concrete", "year": 1990, "health": 78, "risk": "low"},
]

SENSOR_TYPES = {
    "bridge": [("vibration", "mm/s", 0.1, 5.0), ("strain", "microstrain", 50, 500), ("tilt", "degrees", 0.0, 0.5), ("temperature", "celsius", -10, 45)],
    "water_main": [("pressure", "psi", 30, 80), ("flow", "gpm", 100, 2000), ("temperature", "celsius", 5, 25), ("corrosion", "mils", 0, 50)],
    "road": [("temperature", "celsius", -15, 55), ("displacement", "mm", 0, 10)],
    "tunnel": [("vibration", "mm/s", 0.05, 2.0), ("humidity", "percent", 30, 95), ("temperature", "celsius", 5, 35)],
    "pump_station": [("pressure", "psi", 20, 100), ("flow", "gpm", 500, 5000), ("vibration", "mm/s", 0.1, 3.0)],
    "culvert": [("water_level", "meters", 0, 3.0), ("flow", "cfs", 0, 500)],
    "retention_basin": [("water_level", "meters", 0, 5.0)],
}


async def seed():
    async with engine.begin() as conn:
        # Check if already seeded
        result = await conn.execute(text("SELECT COUNT(*) FROM municipalities"))
        if result.scalar() > 0:
            print("Database already seeded. Skipping.")
            return

    async with async_session() as session:
        # Municipalities
        await session.execute(text("""
            INSERT INTO municipalities (id, name, state, country, population, area_sq_km, timezone)
            VALUES
                (:m1, 'City of Pittsburgh', 'Pennsylvania', 'US', 302971, 151.1, 'America/New_York'),
                (:m2, 'Allegheny County', 'Pennsylvania', 'US', 1250578, 1930.6, 'America/New_York')
        """), {"m1": MUNICIPALITY_1, "m2": MUNICIPALITY_2})

        # Users
        await session.execute(text("""
            INSERT INTO users (id, municipality_id, email, full_name, role)
            VALUES
                (:u1, :m1, 'sarah.chen@pittsburgh.gov', 'Sarah Chen', 'admin'),
                (:u2, :m1, 'mike.johnson@pittsburgh.gov', 'Mike Johnson', 'engineer')
        """), {"u1": USER_1, "u2": USER_2, "m1": MUNICIPALITY_1})

        # Assets
        asset_ids = []
        for asset in ASSETS:
            aid = uuid4()
            asset_ids.append((aid, asset))
            await session.execute(text("""
                INSERT INTO assets (id, municipality_id, name, asset_type, geom,
                    installation_date, material, diameter_mm, span_m,
                    current_health_score, risk_level, metadata)
                VALUES (:id, :mid, :name, :type, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326),
                    :install_date, :material, :diameter, :span,
                    :health, :risk, :meta)
            """), {
                "id": aid, "mid": MUNICIPALITY_1,
                "name": asset["name"], "type": asset["type"],
                "lat": asset["lat"], "lng": asset["lng"],
                "install_date": date(asset["year"], 1, 1),
                "material": asset["material"],
                "diameter": asset.get("diameter_mm"),
                "span": asset.get("span_m"),
                "health": asset["health"],
                "risk": asset["risk"],
                "meta": "{}",
            })

        # Sensor readings (30 days of data for each asset)
        now = datetime.now(timezone.utc)
        readings_count = 0
        for aid, asset in asset_ids:
            sensor_configs = SENSOR_TYPES.get(asset["type"], [])
            for sensor_type, unit, min_val, max_val in sensor_configs:
                sensor_id = f"{asset['name'][:10].replace(' ', '_').lower()}_{sensor_type}"
                base_value = (min_val + max_val) / 2
                for day in range(30):
                    for hour in [0, 6, 12, 18]:
                        ts = now - timedelta(days=day, hours=hour)
                        # Add some noise and trend
                        noise = random.gauss(0, (max_val - min_val) * 0.05)
                        trend = (30 - day) * (max_val - min_val) * 0.001
                        value = max(min_val, min(max_val, base_value + noise + trend))

                        await session.execute(text("""
                            INSERT INTO sensor_readings (time, asset_id, sensor_id, sensor_type, value, unit, quality_flag)
                            VALUES (:time, :asset_id, :sensor_id, :sensor_type, :value, :unit, 'good')
                        """), {
                            "time": ts, "asset_id": aid, "sensor_id": sensor_id,
                            "sensor_type": sensor_type, "value": round(value, 3), "unit": unit,
                        })
                        readings_count += 1

        # Sample alerts
        alert_assets = [(aid, a) for aid, a in asset_ids if a["risk"] in ("high", "critical")]
        for i, (aid, asset) in enumerate(alert_assets[:6]):
            severity = "critical" if asset["risk"] == "critical" else "warning"
            await session.execute(text("""
                INSERT INTO alerts (id, asset_id, municipality_id, severity, anomaly_type,
                    title, description, confidence_score, risk_score, detected_at)
                VALUES (:id, :aid, :mid, :sev, :atype, :title, :desc, :conf, :risk, :detected)
            """), {
                "id": uuid4(), "aid": aid, "mid": MUNICIPALITY_1,
                "sev": severity,
                "atype": "statistical_deviation",
                "title": f"Anomaly detected on {asset['name']}",
                "desc": f"Sensor readings on {asset['name']} show deviation >2 sigma from 30-day baseline. "
                        f"Health score: {asset['health']}/100. Immediate investigation recommended.",
                "conf": round(random.uniform(0.75, 0.98), 2),
                "risk": float(100 - asset["health"]),
                "detected": now - timedelta(days=random.randint(0, 7)),
            })

        # Sample work orders
        for i, (aid, asset) in enumerate(alert_assets[:3]):
            await session.execute(text("""
                INSERT INTO work_orders (id, asset_id, municipality_id, status, priority,
                    title, scope_of_work, estimated_cost, generated_by, scheduled_date)
                VALUES (:id, :aid, :mid, :status, :priority, :title, :scope, :cost, 'agent', :sched)
            """), {
                "id": uuid4(), "aid": aid, "mid": MUNICIPALITY_1,
                "status": ["draft", "pending_approval", "approved"][i],
                "priority": random.randint(1, 3),
                "title": f"Maintenance required: {asset['name']}",
                "scope": f"Inspect and repair {asset['name']}. {asset['material']} structure showing signs of degradation. "
                         f"Current health score: {asset['health']}/100.",
                "cost": round(random.uniform(15000, 250000), 2),
                "sched": (now + timedelta(days=random.randint(7, 45))).date(),
            })

        # Sample contractors
        contractors = [
            ("Allegheny Bridge Solutions", "Bridge repair and rehabilitation", "Pittsburgh, PA", 4.5),
            ("PennWater Services Inc.", "Water main repair and replacement", "Pittsburgh, PA", 4.2),
            ("Three Rivers Paving Co.", "Road resurfacing and repair", "Pittsburgh, PA", 4.0),
            ("Steel City Infrastructure", "General infrastructure maintenance", "Pittsburgh, PA", 3.8),
        ]
        for name, spec, loc, rating in contractors:
            await session.execute(text("""
                INSERT INTO contractors (id, name, specialty, location, rating, is_active)
                VALUES (:id, :name, :spec, :loc, :rating, true)
            """), {"id": uuid4(), "name": name, "spec": spec, "loc": loc, "rating": rating})

        # Sample agent runs
        for i in range(3):
            await session.execute(text("""
                INSERT INTO agent_runs (id, municipality_id, agent_type, trigger_type, status,
                    thought_chain, model_used, tokens_used, started_at, completed_at)
                VALUES (:id, :mid, :agent, :trigger, :status, :thoughts, :model, :tokens, :started, :completed)
            """), {
                "id": uuid4(), "mid": MUNICIPALITY_1,
                "agent": ["sentinel", "analyst", "planner"][i],
                "trigger": "sensor_anomaly",
                "status": "completed",
                "thoughts": '[{"step": "Analyzing sensor data", "result": "Anomaly detected"}, '
                           '{"step": "Cross-referencing historical data", "result": "Pattern matches known failure mode"}]',
                "model": "llama3:70b-instruct-q4_K_M",
                "tokens": random.randint(2000, 8000),
                "started": now - timedelta(hours=random.randint(1, 48)),
                "completed": now - timedelta(hours=random.randint(0, 1)),
            })

        await session.commit()
        print(f"Seeded successfully:")
        print(f"  - 2 municipalities")
        print(f"  - 2 users")
        print(f"  - {len(ASSETS)} infrastructure assets")
        print(f"  - {readings_count} sensor readings (30 days)")
        print(f"  - {min(6, len(alert_assets))} alerts")
        print(f"  - {min(3, len(alert_assets))} work orders")
        print(f"  - 4 contractors")
        print(f"  - 3 agent runs")


if __name__ == "__main__":
    asyncio.run(seed())
