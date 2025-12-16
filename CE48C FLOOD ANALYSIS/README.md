# Flood Analysis Simulation App - Kuzey 2 Regulator

A standalone Python application for flood analysis simulation using QGIS libraries, specifically designed for the Kuzey 2 regulator structure.

## Features

- **Overflow Dam Behavior**: Water accumulates behind dam until overflow elevation (412.00 m), then overflows using broad-crested weir equation
- **Actual Structure Dimensions**: Uses real dimensions from engineering drawings:
  - Spillway width: 25.0 m
  - Overflow elevation: 412.00 m
  - Weir coefficient: 1.7 (broad-crested weir)
- **Multiple Rainfall Scenarios**: Pre-defined scenarios or custom intensity
- **2D Shallow Water Equations Solver**: Physics-based flood simulation
- **Automatic Stream Channel Detection**: Extracts stream channels from DEM using flow accumulation
- **Time-Varying Flood Visualization**: Interactive time slider and animation
- **Interactive QGIS Map Display**: Real-time visualization of flood extent and depth
- **Pre-set Regulator Coordinates**: Kuzey 2 coordinates (UTM Zone 6N: 369,012 E, 4,513,388 N)
- **Export Functionality**: Export all time steps as GeoTIFF files
- **Dual Console Output**: Information displayed in both GUI and terminal

## Installation

### 1. Install QGIS

Download and install QGIS from https://qgis.org
- Standard installation path will be auto-detected
- Typical Windows paths: `C:\OSGeo4W64\apps\qgis` or `C:\Program Files\QGIS 3.x`

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install PyQt5 numpy scipy
```

### 3. GDAL

GDAL should be available with QGIS installation. If not, install using:
```bash
# Option 1: Using conda
conda install -c conda-forge gdal

# Option 2: Using OSGeo4W (if QGIS is installed)
# GDAL should already be available with QGIS
```

## Usage

### 1. Prepare DEM File

Place your DEM file (`ikinci_data.tif`) on your Desktop.

### 2. Run the Application

```bash
python flood_analysis_app.py
```

### 3. Load DEM

- Click "Load DEM from Desktop" button
- Or use File menu → Load DEM (TIF)
- The app will automatically look for `ikinci_data.tif` on Desktop

### 4. Configure Parameters

**Regulator Location:**
- Pre-set to Kuzey 2 coordinates (UTM Zone 6N: 369,012 E, 4,513,388 N)
- Coordinates are automatically transformed to match DEM's CRS

**Structure Dimensions:**
- Spillway Width: 25.0 m (pre-set from drawings)
- Overflow Elevation: 412.00 m (pre-set from drawings)
- Weir Coefficient: 1.7 (standard broad-crested weir)

**Rainfall Scenario:**
- Select from dropdown: Light (5 mm/hr), Moderate (10 mm/hr), Heavy (25 mm/hr), Very Heavy (50 mm/hr), Extreme (100 mm/hr)
- Or use "Custom Intensity" for specific values

**Simulation Parameters:**
- Duration: Total simulation time (1-48 hours)
- Time Step: Resolution of simulation (0.1-60 minutes)

**Soil Characteristics:**
- Manning's Roughness: 0.04 (default for old streambed in forest)
- Infiltration Rate: 7.5 mm/hr (default)
- SCS Curve Number: 65 (default)

**Initial Conditions:**
- Initial Water Level: 1.0 m at regulator location

### 5. Run Simulation

- Click "Run Simulation" button
- Monitor progress in progress bar and console output
- Status messages appear in both GUI and terminal

### 6. View Results

- Use time slider to navigate through time steps
- Click "Play Animation" for automatic playback
- Water depth is color-coded on map:
  - Blue shades indicate water depth
  - Transparent = no water
  - Darker blue = deeper water

### 7. Export Results

- **Export Current View**: File menu → Export Current View (PNG/JPEG)
- **Export All Time Steps**: File menu → Export All Time Steps (GeoTIFF files)

## Structure Dimensions

The application uses actual dimensions from engineering drawings:

- **Spillway Width (Crest Length)**: 25.0 meters
- **Overflow Elevation**: 412.00 meters
- **Weir Coefficient**: 1.7 (broad-crested weir)

Overflow is calculated using the broad-crested weir equation:
```
Q = C × L × H^(3/2)
```
where:
- Q = discharge (m³/s)
- C = weir coefficient (1.7)
- L = spillway width (25.0 m)
- H = head over weir (water level - 412.00 m)

## Regulator Behavior

The Kuzey 2 regulator acts as an overflow dam:

1. **Water Accumulation**: Water accumulates behind the dam from:
   - Rainfall/runoff in the catchment area
   - Initial water level at regulator

2. **Overflow**: When water level exceeds 412.00 m:
   - Overflow begins using weir equation
   - Discharge is calculated based on head over weir
   - Water flows downstream following terrain

3. **Flow Routing**: Water flows downstream using:
   - 2D shallow water equations
   - Manning's equation for velocity
   - Flow follows terrain (DEM)

## Output Files

Exported GeoTIFF files are named:
```
flood_depth_t000.00hr.tif
flood_depth_t001.00hr.tif
...
```

Each file contains:
- Water depth in meters
- Same CRS and geotransform as input DEM
- NoData value: -9999

## Technical Details

### DEM Data Type Handling

The application automatically handles BYTE data type DEMs:
- Converts BYTE (0-255) to float64
- Assumes BYTE values represent elevation in meters
- Adjust conversion if your data uses different scaling

### Coordinate Transformation

- Input coordinates: UTM Zone 6N (EPSG:32606)
- Automatic transformation to DEM's CRS
- Validation that coordinates are within DEM extent

### Flow Channel Detection

- Uses flow accumulation from DEM
- Threshold: 85th percentile (adjustable)
- Morphological operations to clean up channels

### Simulation Method

- 2D shallow water equations (simplified)
- Finite difference method
- Manning's equation for velocity
- SCS Curve Number for runoff
- Time-stepping simulation

## Troubleshooting

### QGIS Not Found

If you get "QGIS Not Found" error:
1. Install QGIS from https://qgis.org
2. Or set environment variable: `QGIS_PREFIX_PATH` to your QGIS installation path

### DEM Loading Issues

- Ensure DEM file is valid GeoTIFF
- Check that file path is correct
- Verify DEM has valid CRS information

### Coordinate Issues

- Verify regulator coordinates are within DEM extent
- Check DEM CRS matches expected coordinate system
- Coordinate transformation will fail if CRS is invalid

### Performance

- Large DEMs may take time to process
- Reduce time step for faster simulation (less accurate)
- Reduce duration for testing

## File Structure

```
CE48C FLOOD ANALYSIS/
├── flood_analysis_app.py    # Main application
├── flood_simulator.py        # Flood simulation engine
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## License

This application is developed for educational/research purposes.

## Contact

For questions or issues, refer to the project documentation or engineering team.

