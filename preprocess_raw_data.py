"""
Rating Curve Lesson — Step 1: Preprocess locally provided township data

This script:
  1) Loads your township river heights CSV.
  2) Explores columns and data types.
  3) Cleans/standardizes columns for later analysis.
  4) Computes simple yearly averages and saves a plot.
  5) Writes a cleaned CSV for downstream steps.

Run from a Windows PowerShell in the folder that contains the this script:
  python preprocess_raw_data.py
"""


# ---- Load packages ----

import os
import pandas as pd
import matplotlib.pyplot as plt


# ---- Load data ----

print("Loading data...")
rh = pd.read_csv('./input/RiverHeights_asof_Apr9_2026.csv') # Exported the River Heights from .xls to .csv for easier handeling in Python.
    # Note: Always make sure data are UTF-8 encoded when loading to avoid encoding issues, especially with special characters.


# ---- Explore the data ----

# Check the dimensions of the data (number of rows and columns)
print("\nShape:", rh.shape)  # (1498 records, 13 columns)

# Display the column names to understand what data is available and to identify relevant columns for analysis
print("\nColumn names:")
print(rh.columns) # There is an extra column 'Unnamed: 12' that appears to be empty and can likely be dropped from the analysis.

# Display the first few rows of the data to understand its structure
 # This shows the first 5 records of the dataset, which can help identify any potential issues with the data 
 # (e.g., missing values, formatting issues) and gives an initial sense of the data's structure and content.
print("\nFirst few rows of the data:")
print(rh.head()) # Only shows the first fiew and last columns. Students may struggle here

# Check the data types of each column to ensure they are appropriate for analysis
 # This is important because if the data types are incorrect (e.g., numerical data stored as strings), 
 # it can lead to errors in analysis and visualization.
print("\nData types of each column:")
print(rh.dtypes) 
 # Date - string. This will need to be converted to a datetime object for time series analysis. 
 # RvrHt - string. This will need to be converted to a numeric type for analysis. Elevation (ft)
 # Year - float64. This should be an integer since it represents a year. 
 # Water Elevation - float64. Good. (ft)
 # 833.80 - What is this column? It's mostly empty with a few text notes. 
 # 832.88 - What is this column? It's empty. Drop?
 # HST CFS/TOT
 # WTTN CFS
 # HP Pond Stick
 # 840.33 - Elevation Monroe Road to close. (ft)
 # Monroe_Road_Closed - string. Should be Boolean because it is categorical (Yes/No). 
    # Courtney added this to identify the records that were highlighted yellow in the .xls 
 # Notes - string. Good. 
 # Unnamed: 12 - This column appears to be empty and can likely be dropped from the analysis.

# Check for missing values in each column to understand the completeness of the data
 # This is important because missing values can affect the results of the analysis and may require imputation
print("\nMissing values in each column:")
print(rh.isnull().sum())


# ---- Clean the data ----

# Drop unnecessary columns that are empty or not relevant to the analysis
rh_cleaned = rh.drop(columns=['Unnamed: 12', '833.80', '832.88']) 

# Convert the 'Date' column to a datetime object for time series analysis
rh_cleaned['Date'] = pd.to_datetime(rh_cleaned['Date'], errors='coerce') 
    # Any values that cannot be converted will be set to NaT (Not a Time).

# Convert the 'RivHt' column to a numeric type for analysis
rh_cleaned['RvrHt'] = pd.to_numeric(rh_cleaned['RvrHt'], errors='coerce') 
    # Any values that cannot be converted will be set to NaN (Not a Number).

# Convert the 'Year' column to an integer type 
rh_cleaned['Year'] = rh_cleaned['Year'].astype('Int64') 
    # Any missing values will be represented as <NA> (pandas' way of representing missing values in integer columns).

# Convert the 'Monroe_Road_Closed' column to a Boolean type since it represents a categorical variable (Yes/No)
rh_cleaned['Monroe_Road_Closed'] = rh_cleaned['Monroe_Road_Closed'].map({'Y': True, 'N': False}) 
    # 'Yes' is mapped to True and 'No' is mapped to False. Any values that are not 'Yes' or 'No' will be set to NaN.

# Rename a column for clarity
rh_cleaned = rh_cleaned.rename(columns={'840.33': 'Flood_Elevation_ft'})

print("\nCleaned data:")
print(rh_cleaned.head())
print(rh_cleaned.dtypes)


# ---- QA/QC ----

# Get summary statistics for numerical columns to understand the distribution of the data
print("\nSummary statistics for numerical columns:")
summary = rh_cleaned.describe() 
print(summary)


# ---- Calculae averages ----

# Calculate the average river height (RvrHt) for each year to understand how river heights have changed over time
average_heights = rh_cleaned.groupby('Year')['RvrHt'].mean()
print("\nAverage River Heights by Year:")
print(average_heights, "\n")


# ---- Plot ----

# Plot the average river heights over time to visualize trends
plt.figure(figsize=(10, 6))
plt.plot(average_heights.index, average_heights.values, marker='o')
plt.title('Average River Heights Over Time')
plt.xlabel('Year')
plt.ylabel('Average River Height (feet)')
plt.grid()

# If the output folder does not exist, create it. 
if not os.path.exists('./figs'):
    os.makedirs('./figs')  # Creates the folder
plt.savefig('./figs/average_river_heights_over_time.png')


# ---- Save cleaned data ----

# If the output folder does not exist, create it. 
if not os.path.exists('./output'):
    os.makedirs('./output')  # Creates the folder

# Write the cleaned data to a new CSV file for future analysis
rh_cleaned.to_csv('./output/RiverHeights_Cleaned.csv', index = False)

