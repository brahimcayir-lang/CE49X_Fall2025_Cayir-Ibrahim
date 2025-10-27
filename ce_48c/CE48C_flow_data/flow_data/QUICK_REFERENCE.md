# Quick Reference: Derived Metrics & Analysis

## 📊 Files Generated

1. **dsi_final_with_derived_metrics.csv** - Enhanced dataset with 24 new computed columns
2. **charts/derived_annual_trends.png** - Long-term trends
3. **charts/derived_seasonality.png** - Monthly patterns
4. **charts/derived_flow_distribution.png** - Catchment characteristics
5. **charts/derived_extreme_events.png** - Flood/drought analysis
6. **charts/derived_station_comparison.png** - Station comparisons

---

## 🔢 Key Metrics Explained

| Metric | What It Shows | High Value | Low Value |
|--------|---------------|------------|-----------|
| **Flow Variability Index** | How flashy/stable the river is | Flashy, unstable flow | Stable, predictable |
| **Baseflow Index** | Groundwater contribution | Permanent river | Ephemeral stream |
| **Annual Yield (mm)** | Water productivity | High runoff | Low runoff |
| **Runoff Coefficient** | Season distribution | Seasonal peak | Uniform year-round |

---

## 🎯 What Each Visualization Tells You

### Derived Annual Trends
- **Are flows increasing/decreasing?** → Climate change signals
- **Is variability changing?** → Ecosystem impacts
- **Is baseflow degrading?** → Groundwater depletion

### Derived Seasonality  
- **Which months are wettest?** → Agriculture planning
- **When do floods occur?** → Risk management
- **How uniform is the year?** → Water storage needs

### Derived Flow Distribution
- **What type of catchments?** → Flashy vs stable
- **Which basins are different?** → Regional patterns
- **How variable are flows?** → Supply reliability

### Derived Extreme Events
- **Flood patterns over time** → Infrastructure design
- **Drought frequency** → Water security
- **Peak-base relationships** → Ecosystem requirements

### Derived Station Comparison
- **Top performers** → Water resource potential
- **Catchment efficiency** → Yield analysis
- **Spatial patterns** → Regional hydrology

---

## 💡 Interpretation Guide

### Flow Variability Index (Your Data: 0.5 - 427)
```python
< 5   = Very stable (reservoirs, lakes)
5-15  = Moderately variable (typical river)
15-30 = Flashy (small catchments)
> 30  = Highly flashy (arid/wet regions)
```

### Baseflow Index (Your Data: 0.0 - 0.57)
```python
> 0.3  = Permanent river (strong groundwater)
0.1-0.3 = Semi-permanent
0.05-0.1 = Ephemeral in dry season
< 0.05 = Highly ephemeral or intermittent
```

### Annual Yield (Your Data: 1 - 1,566 mm)
```python
< 100 mm  = Arid catchment
100-300   = Semi-arid
300-600   = Moderate
600-1000  = Productive
> 1000    = Very high yield (humid)
```

---

## 📈 Statistical Summary (Your Data)

**Flow Variability Index**:
- Mean: 25x (moderately flashy on average)
- Median: 14x 
- Range: 0.5x (stable) to 427x (extremely flashy)

**Baseflow Index**:
- Mean: 0.072 (generally low baseflow)
- Median: 0.047
- Most stations: Ephemeral or highly seasonal

**Annual Yield**:
- Mean: 423 mm/year
- Median: 325 mm/year
- Range: 1 to 1,566 mm (highly diverse)

**Flow Concentration**:
- Mean: 1.003 (uniform distribution)
- Most catchments: Balanced annual runoff

---

## 🛠️ Usage Examples

### Find Flashy Catchments (High Flood Risk)
```python
df[df['flow_variability_index'] > 30]
# These need flood protection infrastructure
```

### Find Permanent Rivers (Water Security)
```python
df[df['baseflow_index'] > 0.2]
# These have reliable water supply year-round
```

### Find High-Yielding Catchments (Water Potential)
```python
df[df['annual_mm'] > 500]
# High productivity for water resources
```

### Identify Wet Season
```python
# Check which months have coefficient > 0.15
coef_cols = [f'{m}_coefficient' for m in ['oct','nov','dec','jan','feb','mar',
                                            'apr','may','jun','jul','aug','sep']]
df[coef_cols].mean() > 0.15
```

---

## 🔍 Quality Indicators

### Good Data Quality:
✅ Flow variability index < 1000  
✅ Baseflow index between 0 and 1  
✅ Runoff coefficients sum to ~1.0  
✅ Annual mm matches sum of monthly mm

### Potential Issues:
⚠️ Flow variability > 100 → Check for data errors  
⚠️ Baseflow index > 0.8 → Unrealistically high baseflow  
⚠️ Negative flow values → Data collection error

---

## 📝 Column Reference (dsi_final_with_derived_metrics.csv)

### New Metrics Added:
- `max_flow` - Maximum monthly flow (m³/s)
- `min_flow` - Minimum monthly flow (m³/s)  
- `mean_flow` - Average monthly flow (m³/s)
- `flow_variability_index` - Max / mean flow
- `baseflow_index` - Min / mean flow
- `flow_concentration_index` - Seasonality measure
- `mean_monthly_mm` - Average monthly runoff
- `oct_coefficient` through `sep_coefficient` - Monthly proportions

---

## 🎓 Further Analysis Ideas

1. **Correlation Analysis**: Which factors drive variability?
2. **Cluster Analysis**: Group similar catchments
3. **Trend Detection**: Significant changes over time?
4. **Region Comparison**: Basin differences
5. **Extreme Events**: Frequency analysis
6. **Water Balance**: Add rainfall data to compute R/P ratios
7. **Specific Discharge Maps**: GIS visualization
8. **Flow Duration Curves**: Percentile-based analysis

---

## 📚 References

- **Flow Regime Classification**: Poff et al. (1997) - "The Natural Flow Regime"
- **Baseflow Index**: BFIHOST standard (Boorman et al., 1995)
- **Runoff Coefficients**: Singh et al. (2013) - "Hydrological Modeling"
- **Seasonality Measures**: Markham (1970) - Concentration Index

---

**Generated by**: Hydrological Analysis Script  
**Date**: 2024  
**Source**: DSI Flow Observation Yearbooks

