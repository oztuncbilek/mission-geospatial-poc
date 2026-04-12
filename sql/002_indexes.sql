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

