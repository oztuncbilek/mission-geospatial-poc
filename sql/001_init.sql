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

