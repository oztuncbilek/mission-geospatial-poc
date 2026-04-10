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