#!/usr/bin/env python

import os
from pathlib import Path

import geopandas as gpd
from sqlalchemy import create_engine, text


DB_USER = os.getenv("DB_USER", "mission_user")
DB_PASS = os.getenv("DB_PASS", "mission_pass")
DB_NAME = os.getenv("DB_NAME", "mission_geo")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def get_engine():
    url = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url)


def load_geodata(file_path: Path) -> gpd.GeoDataFrame:
    print(f"[import] Reading file: {file_path}")
    gdf = gpd.read_file(file_path)
    if gdf.empty:
        raise ValueError(f"No features found in {file_path}")
    if gdf.crs is None:
        raise ValueError(f"CRS is missing for {file_path}")
    if gdf.crs.to_epsg() != 4326:
        print(f"[import] Reprojecting {file_path.name} from {gdf.crs} to EPSG:4326")
        gdf = gdf.to_crs(epsg=4326)
    gdf = gdf[~gdf.geometry.is_empty & gdf.geometry.notnull()]
    return gdf


def import_flight_paths(file_path: Path):
    gdf = load_geodata(file_path)
    gdf["mission_area_id"] = 1
    gdf["platform_name"] = "Drone-Imported"
    gdf["source_type"] = "drone"
    gdf["captured_at"] = None
    
    # GeoPandas'ın geometry sütununu SQL'deki geom ile eşleştiriyoruz
    gdf = gdf.rename_geometry("geom")
    keep_cols = ["mission_area_id", "platform_name", "source_type", "captured_at", "geom"]
    gdf = gdf[keep_cols]

    engine = get_engine()
    print("[import] Writing features into mission.flight_paths")
    gdf.to_postgis(
        name="flight_paths",
        con=engine,
        schema="mission",
        if_exists="append",
        index=False,
    )
    print("[import] Done.")


def import_observations(file_path: Path, observation_type: str = "detected-object"):
    gdf = load_geodata(file_path)
    gdf["mission_area_id"] = 1
    gdf["observation_type"] = observation_type
    gdf["confidence"] = 0.9
    gdf["source_name"] = "import-script"
    gdf["captured_at"] = None
    gdf["properties"] = None

    # GeoPandas'ın geometry sütununu SQL'deki geom ile eşleştiriyoruz
    gdf = gdf.rename_geometry("geom")
    keep_cols = [
        "mission_area_id",
        "observation_type",
        "confidence",
        "source_name",
        "captured_at",
        "properties",
        "geom",
    ]
    gdf = gdf[keep_cols]

    engine = get_engine()
    print("[import] Writing features into mission.observations")
    gdf.to_postgis(
        name="observations",
        con=engine,
        schema="mission",
        if_exists="append",
        index=False,
    )
    print("[import] Done.")


def main():
    print("[import] Starting import pipeline")
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("SET search_path TO mission, public;"))
    print(f"[import] Connected to {DB_NAME} at {DB_HOST}:{DB_PORT}")

    flight_file = DATA_DIR / "flight_paths_sample.gpkg"
    obs_file = DATA_DIR / "observations_sample.gpkg"

    if flight_file.exists():
        import_flight_paths(flight_file)
    else:
        print(f"[import] Flight path file not found: {flight_file}")

    if obs_file.exists():
        import_observations(obs_file, observation_type="drone-detection")
    else:
        print(f"[import] Observation file not found: {obs_file}")

    print("[import] Import pipeline finished")


if __name__ == "__main__":
    main()