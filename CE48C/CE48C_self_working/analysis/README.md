# DSİ Akım Gözlem Yıllığı Data Extractor

## Overview
This script extracts hydrological station data from DSİ annual streamflow reports (2000-2020) with high performance and memory efficiency.

## Features
- **Fast Processing**: Uses PyMuPDF for optimal performance
- **Memory Efficient**: Reads only second line for station code detection
- **Smart Filtering**: Skips irrelevant pages immediately
- **Robust Parsing**: Handles both Turkish and English coordinate notation
- **Target Stations**: Extracts data only for specified station codes
- **CSV Output**: Appends results to single CSV file

## Target Station Codes
- D22A144, D22A145, D22A065, D22A093, D22A095, D14A149, D22A158

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python extract_dsi_stations.py
```

## Configuration
Edit the `PDF_DIRECTORY` variable in the `main()` function to point to your DSİ PDF files directory.

## Output
Results are saved to `dsi_akim_verileri_2000_2020.csv` with columns:
- Year, Station_Code, Station_Name, Latitude, Longitude
- Annual_Mean_Discharge, Total_Annual_Flow, Specific_Flow

## Performance
- Processes 1000+ page PDFs efficiently
- Skips non-station pages immediately
- Memory usage optimized for large files
