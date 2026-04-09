# mission-geospatial-poc

A small private proof-of-concept for a geospatial backend inspired by real-world mission support workflows.

The project demonstrates how to build a lightweight spatial data backend using Docker, PostgreSQL/PostGIS, Python-based ingestion scripts and a small C++ integration layer. The focus is on geodata ingestion, coordinate consistency, validation, indexing and application-oriented spatial queries.

## Goals

- Set up a reproducible local geospatial stack with Docker.
- Store mission-style geospatial entities in PostGIS.
- Import and validate external geodata formats such as GeoPackage, Shapefile or GeoJSON.
- Normalize coordinate reference systems and ensure geometry validity.
- Run practical spatial queries for mission support scenarios.
- Integrate a small C++ component that reads from the spatial database.

## Tech stack

- Docker Compose
- PostgreSQL 16 + PostGIS
- SQL
- Python
- GeoPandas / Shapely / GDAL
- C++17
- libpqxx
- CMake

## Project structure

```text
mission-geospatial-poc/
├── cpp/
├── data/
├── docs/
├── scripts/
├── sql/
├── docker-compose.yml
└── README.md
```

## Initial data model

The first version of the schema includes:

- `mission_areas`: operational polygon boundaries
- `flight_paths`: captured drone or platform routes
- `observations`: detected objects or events
- `no_fly_zones`: restricted polygons
- `targets`: mission-relevant points of interest

## Quick start

### 1. Start the database

```bash
docker compose up -d
```

### 2. Check if the container is running

```bash
docker ps
```

### 3. Connect to PostgreSQL

```bash
docker exec -it mission-postgis psql -U mission_user -d mission_geo
```

### 4. Verify PostGIS

Inside `psql`:

```sql
SELECT PostGIS_Version();
SELECT COUNT(*) FROM mission.mission_areas;
```

## Planned features

- Import pipeline for GeoPackage / Shapefile / GeoJSON
- Geometry validation and SRID normalization
- Spatial indexing and query benchmarking
- C++ query client using libpqxx
- Example mission queries such as:
  - objects inside a bounding box
  - nearest target to an observation
  - flight paths intersecting restricted areas
  - observations within a mission area

## Status

In progress.