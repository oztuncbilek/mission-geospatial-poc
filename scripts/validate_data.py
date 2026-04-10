#!/usr/bin/env python
"""
PostGIS'teki tüm tabloları validate eder.
Kontroller: null geom, invalid geom, yanlış SRID, boş tablo.
"""

import os
from sqlalchemy import create_engine, text

DB_USER = os.getenv("DB_USER", "mission_user")
DB_PASS = os.getenv("DB_PASS", "mission_pass")
DB_NAME = os.getenv("DB_NAME", "mission_geo")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")


def get_engine():
    url = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url)


TABLES = {
    "mission_areas": "POLYGON",
    "flight_paths": "LINESTRING",
    "observations": "POINT",
    "no_fly_zones": "POLYGON",
    "targets": "POINT",
}


def run_checks():
    engine = get_engine()
    all_ok = True

    with engine.connect() as conn:
        conn.execute(text("SET search_path TO mission, public;"))

        for table, expected_type in TABLES.items():
            print(f"\n[validate] mission.{table}")
            print(f"  {'─' * 40}")

            total = conn.execute(
                text(f"SELECT COUNT(*) FROM mission.{table}")
            ).scalar()
            print(f"  Toplam satır : {total}")

            if total == 0:
                print(f"  [WARN] Tablo boş")
                continue

            nulls = conn.execute(
                text(f"SELECT COUNT(*) FROM mission.{table} WHERE geom IS NULL")
            ).scalar()
            status = "[OK]  " if nulls == 0 else "[FAIL]"
            print(f"  {status} Null geometri  : {nulls}")
            if nulls > 0:
                all_ok = False

            invalid = conn.execute(
                text(f"SELECT COUNT(*) FROM mission.{table} WHERE NOT ST_IsValid(geom)")
            ).scalar()
            status = "[OK]  " if invalid == 0 else "[FAIL]"
            print(f"  {status} Invalid geom   : {invalid}")
            if invalid > 0:
                all_ok = False

            row = conn.execute(
                text(f"SELECT ST_SRID(geom) FROM mission.{table} LIMIT 1")
            ).fetchone()
            if row:
                srid = row[0]
                status = "[OK]  " if srid == 4326 else "[FAIL]"
                print(f"  {status} SRID           : {srid}")
                if srid != 4326:
                    all_ok = False

            geom_type = conn.execute(
                text(f"SELECT GeometryType(geom) FROM mission.{table} LIMIT 1")
            ).scalar()
            match = expected_type.upper() in (geom_type or "").upper()
            status = "[OK]  " if match else "[WARN]"
            print(f"  {status} Geometry type  : {geom_type}")

    print(f"\n{'=' * 45}")
    if all_ok:
        print("  Tüm kontroller geçti.")
    else:
        print("  Bazı kontroller başarısız. Yukarıdaki çıktıya bak.")

    return all_ok


if __name__ == "__main__":
    print("[validate] Validasyon başladı")
    run_checks()