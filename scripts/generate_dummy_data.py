#!/usr/bin/env python

import geopandas as gpd
from shapely.geometry import Point, LineString
from pathlib import Path

# Data klasörünün yolunu bulalım (scripts klasörünün bir üstündeki data klasörü)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True) # Data klasörü yoksa yarat

def generate_flight_paths():
    print("Generating dummy flight paths...")
    # Haritadaki konuma uygun sahte dron rotaları (LineString)
    line1 = LineString([(11.5300, 48.1400), (11.5350, 48.1420), (11.5400, 48.1480)])
    line2 = LineString([(11.5600, 48.1300), (11.5550, 48.1350), (11.5500, 48.1450)])
    
    # GeoDataFrame oluştur
    gdf_flights = gpd.GeoDataFrame(
        {'platform_id': ['Drone-Alpha', 'Drone-Bravo']}, 
        geometry=[line1, line2],
        crs="EPSG:4326" # GPS Koordinat sistemi
    )
    
    # GeoPackage olarak kaydet
    out_file = DATA_DIR / "flight_paths_sample.gpkg"
    gdf_flights.to_file(out_file, driver="GPKG")
    print(f"Saved: {out_file}")

def generate_observations():
    print("Generating dummy observations...")
    # Haritadaki konuma uygun sahte tespit edilen noktalar (Point)
    point1 = Point(11.5350, 48.1420)
    point2 = Point(11.5550, 48.1350)
    
    gdf_obs = gpd.GeoDataFrame(
        {'obs_type': ['vehicle', 'unknown_object'], 'confidence': [0.85, 0.60]}, 
        geometry=[point1, point2],
        crs="EPSG:4326"
    )
    
    out_file = DATA_DIR / "observations_sample.gpkg"
    gdf_obs.to_file(out_file, driver="GPKG")
    print(f"Saved: {out_file}")

if __name__ == "__main__":
    generate_flight_paths()
    generate_observations()
    print("Dummy data generation complete!")