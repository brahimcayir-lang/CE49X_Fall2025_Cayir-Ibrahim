# Hydrological Derived Metrics - Summary

## Overview
This analysis computed several derived hydrological metrics from your flow data dataset and generated comprehensive visualizations to help understand temporal trends, seasonality, and catchment characteristics.

## Computed Metrics

### 1. **Flow Variability Index** (max_flow / mean_flow)
**Purpose**: Measures how much flow fluctuates compared to average conditions.

**Formula**: `Flow Variability Index = Maximum Monthly Flow / Average Monthly Flow`

**Interpretation**:
- **High values** (>20): Highly variable rivers with significant seasonal differences (flashy response to precipitation)
- **Low values** (<10): Stable rivers with consistent flow throughout the year
- **Your data**: Mean = 24.97, Median = 13.94, Range = 0.54 - 426.67

**Physical meaning**: 
- Flashy catchments respond quickly to rainfall
- Stable catchments have more groundwater contribution or larger storage

---

### 2. **Baseflow Index** (min_flow / mean_flow)
**Purpose**: Indicates river permanence and groundwater contribution.

**Formula**: `Baseflow Index = Minimum Monthly Flow / Average Monthly Flow`

**Interpretation**:
- **High values** (>0.3): Permanent rivers with strong baseflow (groundwater-fed)
- **Low values** (<0.1): Intermittent or ephemeral streams, minimal baseflow
- **Your data**: Mean = 0.072, Median = 0.047, Range = 0.000 - 0.571

**Physical meaning**:
- Baseflow represents sustained groundwater discharge
- Low baseflow indicates limited aquifer contribution or highly seasonal flows
- This helps identify water security risks during dry periods

---

### 3. **Hydrological Yield** (annual_total_m3 / catchment_area_km2)
**Purpose**: Measures water productivity per unit catchment area.

**Formula**: `Hydrological Yield = Annual Runoff Volume (mm)`

**Already in your data**: The `annual_mm` column represents this directly.

**Interpretation**:
- **High yield** (>500 mm/yr): High precipitation, low evaporation, efficient runoff
- **Low yield** (<100 mm/yr): Arid or highly permeable catchments
- **Your data**: Mean = 422.88 mm, Median = 325 mm, Range = 1 - 1,566 mm

**Physical meaning**:
- Combines climate (precipitation), catchment characteristics, and land use
- Useful for water resource planning and agricultural water management

---

### 4. **Monthly Runoff Coefficients**
**Purpose**: Shows the proportion of annual runoff occurring in each month.

**Formula**: `Monthly Coefficient = Monthly Runoff (mm) / Annual Runoff (mm)`

**Computed for**: All 12 months (oct_coefficient through sep_coefficient)

**Interpretation**:
- Uniform distribution: 1/12 ≈ 0.083 per month
- **Values > 0.15**: Wet season months (above average runoff)
- **Values < 0.05**: Dry season months (below average runoff)
- Identifies seasonal water balance patterns

**Physical meaning**:
- Reveals timing of peak flows relative to annual distribution
- Helps understand rainfall seasonality and snowmelt contributions
- Critical for irrigation planning and flood risk assessment

---

### 5. **Flow Concentration Index**
**Purpose**: Measures how seasonal the runoff is (concentration of flow in certain months).

**Formula**: `Flow Concentration Index = Annual Runoff / (12 × Mean Monthly Runoff)`

**Interpretation**:
- **Near 1.0**: Relatively uniform flow throughout year
- **> 1.1**: Highly seasonal, concentrated runoff
- **Your data**: Mean = 1.003, suggesting relatively uniform annual distribution

**Physical meaning**:
- Low concentration: Well-distributed rainfall, groundwater buffering, or large catchment storage
- High concentration: Pronounced wet/dry seasons, snowmelt-dominated, or small reactive catchments

---

## Visualizations Generated

### 1. **charts/derived_annual_trends.png**
Four-panel display showing:
- **Trend in average annual flow** (m³/s) over time
- **Trend in annual runoff depth** (mm) 
- **Trend in flow variability index**
- **Trend in baseflow index**

**Use**: Detect long-term hydrological changes, climate impacts, and water security trends

---

### 2. **charts/derived_seasonality.png**
Shows monthly patterns:
- **Hydrograph**: Average monthly flows
- **Monthly runoff coefficients**: Distribution of flow throughout the year
- **Flow distribution boxplots**: Inter-month variability
- **Seasonal flow range**: Max/min/mean by month

**Use**: Understand seasonal water availability, plan water resource management, identify peak flow months

---

### 3. **charts/derived_flow_distribution.png**
Analyzes flow characteristics:
- **Distribution of flow variability index**
- **Distribution of baseflow index**
- **Scatter plot**: Baseflow vs Variability
- **Boxplot**: Annual runoff by basin

**Use**: Classify catchment types, identify flow regime patterns, understand regional differences

---

### 4. **charts/derived_extreme_events.png**
Examines extremes:
- **Annual maximum flows** (flood risk)
- **Annual minimum flows** (drought risk)
- **Peak-to-base ratio** over time
- **Maximum vs mean flow relationship**

**Use**: Assess flood and drought vulnerability, water supply reliability, ecosystem habitat requirements

---

### 5. **charts/derived_station_comparison.png**
Station-specific analysis:
- **Top 10 stations** by average annual flow
- **Hydrological yield vs catchment area** (with variability coloring)
- **Station characterization** (baseflow vs variability quadrant analysis)
- **Annual runoff distribution** for top stations

**Use**: Compare catchment performance, identify exceptional stations, understand scale effects

---

## Dataset Created

### **dsi_final_with_derived_metrics.csv**

**New columns added** (24 additional metrics):
- `flow_variability_index`: Max flow / mean flow
- `baseflow_index`: Min flow / mean flow
- `max_flow`: Maximum monthly flow
- `min_flow`: Minimum monthly flow  
- `mean_flow`: Average monthly flow
- `flow_concentration_index`: Annual runoff / (12 × mean monthly runoff)
- `mean_monthly_mm`: Average of all monthly runoff values
- **12 monthly coefficients**: `oct_coefficient` through `sep_coefficient`

**Total columns**: 111 (up from 87 original)

---

## Key Insights from Your Data

### Flow Variability
- **Average flow variability**: 25x (mean flow to max flow)
- **Range**: Very stable (0.5x) to highly flashy (427x)
- **Interpretation**: Your catchments show diverse behavior from slow-responding to highly reactive

### Baseflow Characteristics
- **Average baseflow**: ~7% of mean flow
- **Low baseflow prevalence**: Suggests many ephemeral or highly seasonal streams
- **Implication**: Water supply may be vulnerable during dry periods

### Hydrological Yield
- **Average yield**: 423 mm/year
- **Variability**: Wide range (1 to 1,566 mm) reflects diverse catchment conditions
- **Regional differences**: Some basins highly productive, others arid

### Seasonal Patterns
- Flow concentration index near 1.0 suggests relatively **uniform annual distribution**
- This indicates either:
  - Well-distributed precipitation throughout the year
  - Significant groundwater/storage buffering effects
  - Mixed seasonal runoff sources

---

## Applications

### Water Resource Management
- **Yield analysis**: Estimate available water per catchment
- **Seasonality**: Plan storage needs and water allocation
- **Drought assessment**: Baseflow index indicates low-flow reliability

### Flood Risk Assessment
- **Flow variability**: High values indicate flash flood potential
- **Extreme events**: Peak flow analysis shows flood frequency
- **Seasonal patterns**: Identify flood-prone months

### Agricultural Planning
- **Seasonal coefficients**: Determine irrigation water availability by month
- **Variability**: Assess water supply reliability for crops
- **Low-flow periods**: Identify when water may be scarce

### Environmental Assessment
- **Baseflow**: Critical for maintaining stream ecosystems
- **Flow regime**: Determine if rivers support aquatic life year-round
- **Hydrological health**: Baseflow + variability characterize river "behavior"

---

## Next Steps

### If you have rainfall data:
```python
# Compute true runoff ratio
df['runoff_ratio'] = df['annual_mm'] / df['rainfall_mm']

# This tells you what fraction of rainfall becomes runoff
# Typical values:
# - Urban/pervious: 0.05-0.30
# - Agricultural: 0.10-0.40  
# - Forest: 0.20-0.50
# - Wetlands: 0.10-0.20
```

### Potential additional analyses:
1. **Flow Duration Curves**: Percentile-based flow analysis
2. **Specific Discharge Maps**: GIS visualization of yield by station
3. **Water Balance**: Compare with meteorological data (rainfall, evapotranspiration)
4. **Trend Analysis**: Statistical detection of significant trends over time
5. **Cluster Analysis**: Group stations by similar flow regime characteristics

---

## References

- **Flow Variability Index**: Helps classify ephemeral vs perennial streams
- **Baseflow Index**: Standardized in BFIHOST (Boorman et al., 1995)
- **Runoff Coefficients**: Used in regionalization studies (Wagener et al., 2007)
- **Flow Concentration**: Related to seasonality measures (Markham, 1970)

