# ./README.md

# Rating Curve Lesson (Python)

**Objective:**  
Understand and build a simple **rating curve** that relates **stage (gage height)** to **discharge (streamflow)** at a USGS site, and then apply that relation to township elevation data to estimate discharge.

> A **rating curve** is an empirical relationship between stage and discharge at a streamgage. Because stage is measured continuously, a rating lets us estimate continuous discharge using occasional direct measurements and a calibrated relation.

---

## What you will produce

By the end, you will have:

- Cleaned township data: `./output/RiverHeights_Cleaned.csv`
- USGS daily data: `./input/USGS-05424157_Streamflow_Data.csv`, cleaned copy `./output/USGS_Cleaned.csv`
- Site metadata: `./input/USGS-05424157_Location_Metadata.csv`, plus `./output/gage_elevation_ft.json`
- Rating parameters: `./output/rating_params_05424157.json`
- Rating table: `./output/rating_table_05424157.csv`
- Plots:
  - `./figs/average_river_heights_over_time.png`
  - `./figs/daily_discharge_over_time.png`
  - `./figs/daily_gage_height_over_time.png`
  - `./figs/rating_curve_05424157.png`
  - `./figs/estimated_daily_discharge_over_time.png`
  - `./figs/combined_estimated_and_usgs_discharge.png`
- Estimated discharge CSV: `./output/Township_Estimated_Discharge_05424157.csv`

---

## Prerequisites (Windows, no conda)

1. **Open a Windows PowerShell** in the working folder that contains your data and scripts.
2. **Verify Python is installed**  
   ```powershell
   python --version
3. **Install Required Packages**
   ```powershell
   pip install pandas numpy matplotlib dataretrieval scipy


# Scripts

Scripts can be viewed and edited with a text editor (e.g. notepad, notepad++, SublimeText) or an Integrated Development Environment (IDE) (e.g. VS Code, Spyder, Positorn). 

- preprocess_raw_data.py - Preprocess locally provided township data

- get_usgs_data.py - Download USGS daily data via dataretrieval

- process_usgs_data.py - Process USGS daily data and compute a road-closure threshold

- make_rating_curve.py - Build and apply a stage-discharge rating curve

# References

Hodson, T.O., Hariharan, J.A., Black, S., and Horsburgh, J.S., 2023, dataretrieval (Python): a Python package for discovering and retrieving water data available from U.S. federal hydrologic web services: U.S. Geological Survey software release, https://doi.org/10.5066/P94I5TX3. 


