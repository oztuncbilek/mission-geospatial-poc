#!/usr/bin/env bash

echo "=================================================="
echo "  Starting Geospatial Pipeline..."
echo "=================================================="

# 1. Check if virtual environment exists, if not create it
if [ ! -d ".venv" ]; then
    echo "[SETUP] Creating Python virtual environment..."
    python3 -m venv .venv
fi

# 2. Activate virtual environment
echo "[SETUP] Activating virtual environment..."
source .venv/bin/activate

# 3. Install requirements
echo "[SETUP] Installing Python dependencies..."
pip install -r requirements.txt -q

# 4. Generate Dummy Data
echo "[DATA] Generating dummy flight paths and observations..."
python scripts/generate_dummy_data.py

# 5. Import Data to PostGIS
echo "[DB] Importing data into PostGIS..."
python scripts/import_data.py

# 6. Validate Data (QA Check)
echo "[QA] Validating spatial integrity of the database..."
python scripts/validate_data.py

echo "=================================================="
echo "  ✅ Python Pipeline Finished Successfully!"
echo "  You can now run the C++ client."
echo "=================================================="