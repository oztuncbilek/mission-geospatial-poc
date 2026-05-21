#!/usr/bin/env python
"""
Gerçek OSM verisi indirir - Nominatim API kullanarak.
- POI'lar (amenities) → observations_sample.gpkg
- Nominatim geocoding → locations
Munich bbox (seed datamızla aynı alan).
"""

import time
from pathlib import Path

import geopandas as gpd
import requests
from shapely.geometry import Point

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Munich test bbox - seed datamızla aynı (south, west, north, east)
BBOX = (48.130, 11.530, 48.165, 11.575)
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

HEADERS = {
    "User-Agent": "MissionGeoBot/1.0 (+http://example.com/bot)",
}


def search_amenities(amenity_type: str = "restaurant") -> list:
    """Nominatim'den amenity tipini ara."""
    print(f"[download] Nominatim'den '{amenity_type}' aranıyor...")
    
    params = {
        "q": f"{amenity_type} Munich",
        "format": "json",
        "limit": 50,
        "bbox": f"{BBOX[1]},{BBOX[0]},{BBOX[3]},{BBOX[2]}",  # west, south, east, north
    }
    
    try:
        resp = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"[download] Hata: {e}")
        return []


def download_observations():
    """OSM amenity verilerini observation olarak indirir."""
    features = []
    amenity_types = ["restaurant", "hospital", "police", "pharmacy", "fire_station"]
    
    for amenity in amenity_types:
        results = search_amenities(amenity)
        
        for result in results:
            try:
                lon = float(result.get("lon"))
                lat = float(result.get("lat"))
                
                # bbox içinde mi kontrol et
                if BBOX[0] <= lat <= BBOX[2] and BBOX[1] <= lon <= BBOX[3]:
                    features.append({
                        "osm_id": result.get("osm_id"),
                        "name": result.get("name", "unnamed"),
                        "amenity": amenity,
                        "type": result.get("type", "unknown"),
                        "geometry": Point(lon, lat),
                    })
            except (ValueError, TypeError):
                continue
        
        time.sleep(1)  # Rate limiting
    
    if not features:
        print("[download] Observation verisi bulunamadı.")
        return
    
    gdf = gpd.GeoDataFrame(features, crs="EPSG:4326")
    out_path = DATA_DIR / "observations_sample.gpkg"
    gdf.to_file(out_path, driver="GPKG")
    print(f"[download] {len(gdf)} observation kaydedildi → {out_path}")
    print(f"[download] Amenity türleri: {gdf['amenity'].unique().tolist()}")


def create_flight_paths_mock():
    """Mock flight path verileri oluştur (real GPS track simulation)."""
    from shapely.geometry import LineString
    
    print("[download] Mock flight paths oluşturuluyor...")
    
    # Basit drone uçuş yolları (önceden tanımlanmış rota)
    flight_paths = [
        {
            "osm_id": 1,
            "name": "Drone-Route-Alpha",
            "platform": "Drone-01",
            "geometry": LineString([
                (11.540, 48.135),
                (11.550, 48.140),
                (11.560, 48.145),
                (11.565, 48.160),
            ]),
        },
        {
            "osm_id": 2,
            "name": "Drone-Route-Beta",
            "platform": "Drone-02",
            "geometry": LineString([
                (11.535, 48.150),
                (11.545, 48.155),
                (11.555, 48.162),
                (11.570, 48.155),
            ]),
        },
    ]
    
    gdf = gpd.GeoDataFrame(flight_paths, crs="EPSG:4326")
    out_path = DATA_DIR / "flight_paths_sample.gpkg"
    gdf.to_file(out_path, driver="GPKG")
    print(f"[download] {len(gdf)} flight path kaydedildi → {out_path}")


if __name__ == "__main__":
    print("[download] Gerçek OSM verisi indiriliyor...")
    print(f"[download] BBox: {BBOX}")
    
    download_observations()
    print("[download] 2 saniye bekleniyor...")
    time.sleep(2)
    create_flight_paths_mock()
    
    print("[download] ✓ Tamamlandı. data/ klasörünü kontrol et.")
