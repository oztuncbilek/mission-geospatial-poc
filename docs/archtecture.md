# System Architecture

The Geospatial PoC is designed to simulate the backend of a MUM-T environment. The architecture prioritizes high-speed spatial data processing, robust storage, and a low-latency query engine.

## High-Level Data Flow

1. **Data Generation/Ingestion (Python):** Simulates external data feeds (e.g., drone telemetry, target observations). Uses `GeoPandas` to validate geometries, normalize SRIDs to EPSG:4326, and write directly to the database.
2. **Spatial Storage (PostgreSQL + PostGIS):** Acts as the single source of truth. Uses `GiST` indexes on all geometry columns to allow millisecond-level spatial lookups.
3. **Autonomous Engine (C++):** A lightweight client mimicking the drone's decision-making unit. Connects via `libpqxx` to perform real-time proximity and intersection checks.

## Component Breakdown

### 1. Database Layer
- **Engine:** PostgreSQL 16
- **Extension:** PostGIS
- **Deployment:** Docker container (`docker-compose.yml`)
- **Key Optimizations:** `GiST` spatial indexing, structured schemas (`mission` vs `public`), and constraint-based relationships.

### 2. Data Pipeline (Python)
- **Libraries:** `geopandas`, `shapely`, `sqlalchemy`
- **Responsibility:** Reading standardized formats (.gpkg, .shp), handling Coordinate Reference System (CRS) transformations, and bulk-inserting features safely into the operational schema.

### 3. Query Client (C++17)
- **Libraries:** `libpqxx` (PostgreSQL C++ API)
- **Responsibility:** Executing complex spatial logic securely with robust exception handling (`try-catch`).
- **Core Spatial Queries:**
  - `ST_Intersects`: Collision detection against restricted airspace (No-Fly Zones).
  - `<->` (KNN Operator): Nearest neighbor distance calculation, optimizing index usage instead of full table scans.
  - `ST_Contains` / `&&`: Bounding box and regional filtering to reduce cognitive load on the UI.
  - `ST_Transform`: On-the-fly metric distance calculation (e.g., WGS84 to UTM Zone 32N) for accurate ground-truth measurements.