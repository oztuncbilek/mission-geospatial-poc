-- 1) Mission area içindeki tüm targets
SELECT t.*
FROM mission.targets t
JOIN mission.mission_areas a ON ST_Contains(a.geom, t.geom)
WHERE a.id = 1;

-- 2) En yakın target'i observation'a göre bul
SELECT o.id AS observation_id,
       t.id AS target_id,
       ST_Distance(o.geom, t.geom) AS distance_m
FROM mission.observations o
CROSS JOIN LATERAL (
    SELECT t2.*
    FROM mission.targets t2
    ORDER BY o.geom <-> t2.geom
    LIMIT 1
) t
WHERE o.id = 1;

-- 3) No-fly zone ile kesişen flight paths
SELECT f.*
FROM mission.flight_paths f
JOIN mission.no_fly_zones z
  ON ST_Intersects(f.geom, z.geom);

-- 4) Belli bir bounding box içindeki observations
SELECT *
FROM mission.observations
WHERE geom && ST_MakeEnvelope(11.54, 48.145, 11.56, 48.155, 4326);