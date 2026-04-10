#!/usr/bin/env python
"""
Gerçek OSM verisi indirir (Overpass API).
- Yollar / paths → flight_paths_sample.gpkg
- Amenity POI'lar → observations_sample.gpkg
Munich bbox (seed datamızla aynı alan).
"""

import json
import time
from pathlib import Path

import geopandas as gpd
import requests
from shapely.geometry import LineString, Point

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Munich test bbox - seed datamızla aynı (south, west, north, east)
BBOX = (48.130, 11.530, 48.165, 11.575)
OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def query_overpass(query: str) -> dict:
    print("[download] Overpass API sorgulanıyor...")
    resp = requests.post(OVERPASS_URL, data={"data": query}, timeout=60)
    resp.raise_for_status()
    return resp.json()


def download_flight_paths():
    """OSM yollarını drone flight path olarak indirir."""
    query = f"""
    [out:json][timeout:30];
    way["highway"]["highway"~"residential|secondary|primary|service|path|track|footway"]
    ({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]});
    out geom;
    """
    data = query_overpass(query)
    features = []

    for elem in data.get("elements", []):
        if elem["type"] == "way" and "geometry" in elem:
            coords = [(pt["lon"], pt["lat"]) for pt in elem["geometry"]]
            if len(coords) >= 2:
                tags = elem.get("tags", {})
                features.append({
                    "osm_id": elem["id"],
                    "name": tags.get("name", "unnamed"),
                    "highway": tags.get("highway", "unknown"),
                    "geometry": LineString(coords),
                })

    if not features:
        print("[download] Yol verisi bulunamadı.")
        return

    gdf = gpd.GeoDataFrame(features, crs="EPSG:4326")
    out_path = DATA_DIR / "flight_paths_sample.gpkg"
    gdf.to_file(out_path, driver="GPKG")
    print(f"[download] {len(gdf)} flight path kaydedildi → {out_path}")


def download_observations():
    """OSM amenity node'larını drone observation olarak indirir."""
    query = f"""
    [out:json][timeout:30];
    node["amenity"]
    ({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]});
    out body;
    """
    data = query_overpass(query)
    features = []

    for elem in data.get("elements", []):
        if elem["type"] == "node" and "lat" in elem and "lon" in elem:
            tags = elem.get("tags", {})
            features.append({
                "osm_id": elem["id"],
                "name": tags.get("name", "unnamed"),
                "amenity": tags.get("amenity", "unknown"),
                "geometry": Point(elem["lon"], elem["lat"]),
            })

    if not features:
        print("[download] Observation verisi bulunamadı.")
        return

    gdf = gpd.GeoDataFrame(features, crs="EPSG:4326")
    out_path = DATA_DIR / "observations_sample.gpkg"
    gdf.to_file(out_path, driver="GPKG")
    print(f"[download] {len(gdf)} observation kaydedildi → {out_path}")


if __name__ == "__main__":
    print("[download] OpenStreetMap'ten gerçek veri indiriliyor...")
    download_flight_paths()
    time.sleep(2)  # Overpass API'ye nazik ol
    download_observations()
    print("[download] Tamamlandı. data/ klasörünü kontrol et.")