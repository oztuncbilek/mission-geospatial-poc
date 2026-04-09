CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

CREATE SCHEMA IF NOT EXISTS mission;

SET search_path TO mission, public;

CREATE TABLE IF NOT EXISTS mission_areas (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'planned',
    srid INTEGER DEFAULT 4326,
    geom GEOMETRY(POLYGON, 4326) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS flight_paths (
    id SERIAL PRIMARY KEY,
    mission_area_id INTEGER REFERENCES mission_areas(id) ON DELETE CASCADE,
    platform_name TEXT,
    source_type TEXT DEFAULT 'drone',
    captured_at TIMESTAMP,
    geom GEOMETRY(LINESTRING, 4326) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS observations (
    id SERIAL PRIMARY KEY,
    mission_area_id INTEGER REFERENCES mission_areas(id) ON DELETE SET NULL,
    observation_type TEXT NOT NULL,
    confidence NUMERIC(4,3),
    source_name TEXT,
    captured_at TIMESTAMP,
    properties JSONB DEFAULT '{}'::jsonb,
    geom GEOMETRY(POINT, 4326) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS no_fly_zones (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    restriction_type TEXT DEFAULT 'no-fly',
    active BOOLEAN DEFAULT TRUE,
    geom GEOMETRY(POLYGON, 4326) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS targets (
    id SERIAL PRIMARY KEY,
    mission_area_id INTEGER REFERENCES mission_areas(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    priority INTEGER DEFAULT 3,
    status TEXT DEFAULT 'unverified',
    geom GEOMETRY(POINT, 4326) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mission_areas_geom
    ON mission_areas
    USING GIST (geom);

CREATE INDEX IF NOT EXISTS idx_flight_paths_geom
    ON flight_paths
    USING GIST (geom);

CREATE INDEX IF NOT EXISTS idx_observations_geom
    ON observations
    USING GIST (geom);

CREATE INDEX IF NOT EXISTS idx_no_fly_zones_geom
    ON no_fly_zones
    USING GIST (geom);

CREATE INDEX IF NOT EXISTS idx_targets_geom
    ON targets
    USING GIST (geom);

INSERT INTO mission_areas (name, description, status, geom)
VALUES (
    'Sample Mission Area',
    'Initial sample polygon for local testing',
    'planned',
    ST_GeomFromText(
        'POLYGON((11.5400 48.1400, 11.5600 48.1400, 11.5600 48.1550, 11.5400 48.1550, 11.5400 48.1400))',
        4326
    )
)
ON CONFLICT DO NOTHING;

INSERT INTO no_fly_zones (name, restriction_type, active, geom)
VALUES (
    'Restricted Zone Alpha',
    'restricted-airspace',
    TRUE,
    ST_GeomFromText(
        'POLYGON((11.5480 48.1450, 11.5530 48.1450, 11.5530 48.1490, 11.5480 48.1490, 11.5480 48.1450))',
        4326
    )
)
ON CONFLICT DO NOTHING;

INSERT INTO flight_paths (mission_area_id, platform_name, source_type, captured_at, geom)
VALUES (
    1,
    'Drone-01',
    'drone',
    NOW(),
    ST_GeomFromText(
        'LINESTRING(11.5420 48.1410, 11.5470 48.1440, 11.5520 48.1470, 11.5580 48.1530)',
        4326
    )
)
ON CONFLICT DO NOTHING;

INSERT INTO observations (mission_area_id, observation_type, confidence, source_name, captured_at, properties, geom)
VALUES
(
    1,
    'vehicle',
    0.920,
    'drone-camera',
    NOW(),
    '{"note":"detected near road segment"}'::jsonb,
    ST_GeomFromText('POINT(11.5495 48.1468)', 4326)
),
(
    1,
    'antenna',
    0.810,
    'manual-import',
    NOW(),
    '{"note":"static infrastructure object"}'::jsonb,
    ST_GeomFromText('POINT(11.5550 48.1510)', 4326)
)
ON CONFLICT DO NOTHING;

INSERT INTO targets (mission_area_id, name, priority, status, geom)
VALUES
(
    1,
    'Target-01',
    1,
    'unverified',
    ST_GeomFromText('POINT(11.5515 48.1482)', 4326)
),
(
    1,
    'Target-02',
    2,
    'candidate',
    ST_GeomFromText('POINT(11.5570 48.1520)', 4326)
)
ON CONFLICT DO NOTHING;