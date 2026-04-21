"""
Rating Curve Lesson — Step 3: Process USGS daily data and compute a road-closure threshold

This script:
  1) Cleans the USGS daily CSV (drops non-essential columns, fixes time).
  2) Splits discharge (00060) and gage height (00065).
  3) Reads a township-provided absolute flood elevation and USGS gage elevation,
     then computes the gage-height threshold where Monroe Road closes.
  4) Creates two simple plots for teaching: discharge over time, gage height vs threshold.

Run:
  python process_usgs_data.py
"""


# ---- Load packages ----

import pandas as pd
import matplotlib.pyplot as plt


# ---- Load data ----

# Load the data that was previously downloaded from the USGS website and saved as a CSV file. 
# This allows us to work with the data without having to download it again, which can save time and reduce the load on the USGS servers.
print("Loading data...")
df = pd.read_csv('./input/USGS-05424157_Streamflow_Data.csv') 


# ---- Explore the data ----

print(df.shape) # Check the dimensions of the data (number of rows and columns)

# Drop the columns that indicate the parameter code since we already know what parameters we are working with
df = df.drop(columns=['time_series_id', # Useless for students and not needed for analysis
                      'daily_id',       # Useless for students and not needed for analysis
                      'geometry_type',  # Not needed unless a map will be created 
                      'geometry',       # Not needed unless a map will be created, requires geopandas package 
                      'last_modified'   # Useless for students and not needed for analysis
                      ]) 

# print(df.columns) 
print(df.dtypes)

# Check the first few rows of the data to understand its structure and to identify any potential issues with the data 
# (e.g., missing values, formatting issues) and explore data structure and content.
print(df.head()) 

# Check the unique values in the 'parameter_code' column to confirm that we are only working with the parameters we 
# specified (discharge and gage height).
print("\nUnique parameter codes:", df['parameter_code'].unique()) # '00060', '00065'

# Approved, provisional - Provisional data are subject to revision and should be used with caution. 
# Approved data have been reviewed and are considered final.
summary_status = df['approval_status'].value_counts() # Get the count of each unique value in the 
  # 'approval_status' column to understand the distribution of data quality.
print("\nApproval status summary:")
print(summary_status)


# ---- Clean data ----

# Convert the 'time' column to a datetime object for time series analysis
df['time'] = pd.to_datetime(df['time'], errors = 'coerce')

# Write the cleaned data to a new CSV file for future analysis
df.to_csv('./output/USGS_Cleaned.csv', index = False)

discharge_data = df[df['parameter_code'] == 60] # Filter the data to only include discharge data

gage_height_data = df[df['parameter_code'] == 65] # Filter the data


# ---- Calculate road closure river height ----

# Read in the cleaned raw data to get the flood elevation at which Monroe Road is closed. 
raw_cleaned = pd.read_csv('./output/RiverHeights_Cleaned.csv')

# Get a single value 
vals = raw_cleaned['Flood_Elevation_ft'].unique()
len(vals) == 1
road_close_elevation_ft = vals[0]
print("\nRoad closure elevation (ft):", road_close_elevation_ft)

# Read in metadata to get elevation of gage
metadata_df = pd.read_csv('./input/USGS-05424157_Location_Metadata.csv')

# Get the gage elevation in feet from the metadata. This is the elevation of the gage above sea level.
gage_elevation_ft = metadata_df['altitude'] 
print("Gage elevation (ft):", gage_elevation_ft[0])
gage_elevation_ft.to_csv("./output/gage_elevation_ft.txt", index = False)

# Calculate the river height at which Monroe Road is closed
road_close_height_ft = road_close_elevation_ft - gage_elevation_ft[0] # Get the gage height data in
print("Road closure river height (ft):", round(road_close_height_ft, 2))

# # Add a new column to the metadata dataframe for the road closure height. This will be used later to compare against 
# # the gage height data to identify when the river height exceeds the road closure height.
# gage_height_data['Road_Closure_Height_ft'] = road_close_height_ft 
# print(gage_height_data)


# ---- Plot discharge data ----

# Map categories → colors
color_map = {
    'Approved': 'C0',      # default blue (or any color you prefer)
    'Provisional': 'gray'
}

# Apply to dataframe
colors = discharge_data['approval_status'].map(color_map)

fig, ax = plt.subplots(figsize=(10, 6))

for status, color in color_map.items():
    subset = discharge_data[discharge_data['approval_status'] == status]

    ax.plot(
        subset['time'],
        subset['value'],
        color = color,
        linestyle = '-',
        marker = 'o',
        markersize = 3,
        label = status
    )
ax.legend()
ax.set_title('Daily Discharge Over Time')
ax.set_xlabel('Date')
ax.set_ylabel('Discharge (cfs)')
plt.grid()
plt.tight_layout()
plt.savefig('./figs/daily_discharge_over_time.png')


# ---- Plot gage height data ----

plt.figure(figsize = (10, 6))
# Plot actual data
plt.plot(gage_height_data['time'], gage_height_data['value'], marker='o', markersize = 3, linestyle='-', label='Gage Height (ft)')
# Plot a horizontal line at the road-closure height (constant)
plt.axhline(
    y = road_close_height_ft,
    color = 'red',
    linestyle = '--',
    linewidth = 2,
    label = f'Road Closure Threshold ({road_close_height_ft:.2f} ft)'
)
plt.title('Daily Gage Height Over Time') 
plt.xlabel('Date')
plt.ylabel('Gage Height (ft)') 
plt.grid()
plt.legend()
plt.tight_layout()
# plt.show() 
plt.savefig('./figs/daily_gage_height_over_time.png')

