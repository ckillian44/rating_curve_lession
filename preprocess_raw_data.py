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

"""
Discussion: What is a dataframe?

A pandas DataFrame is a table of data in Python, similar to a spreadsheet. It has rows and columns, 
where each column can hold a different type of information (numbers, text, dates). It's designed to make loading, 
cleaning, analyzing, and visualizing data easy and fast.

"""
print("Loading data . . .")
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
"""
Discussion: What are data types and why are they important?

Each column column of a pandas dataframe is assigned a data type. These data types matter because they determine:
    what operations are allowed (e.g., math, comparisons)
    how plots and summaries behave
    whether data are interpreted correctly (e.g., dates vs text)

This project uses several core Python/pandas data types.
Here they are, explained in plain language.

1. Strings (object in pandas): A string is just text — letters, numbers, punctuation, anything inside quotes.
    Examples in this lesson:
        Dates before conversion (e.g., "4/10/2026")
        Notes or comments
        "Y"/"N" values for Monroe_Road_Closed
        USGS approval status: "Approved", "Provisional"
        Parameter code "00060" or "00065"
    Why it matters:
        Text cannot be used directly in math or plotting numeric trends.
        That is why we convert strings like "4/10/2026" into real dates, and codes like "00060" into filters.

2. Integers (int64 or Int64): Whole numbers without decimals.
    Examples in this lesson:
        Year after conversion
        Some ID fields (if present)
    Why it matters:
        Integers sort cleanly (e.g., by year).
        They can be grouped, counted, or compared.

3. Floating-point numbers (float64): Numbers with decimals, e.g., 4.23 or -0.15.
    Examples:
        RvrHt (river height)
        Water_Elevation_ft
        USGS value fields for discharge and gage height
        Flood_Elevation_ft
    Why it matters:
        Most scientific datasets use floats for measurements.
        Floats allow plotting, fitting the rating curve, performing math, etc.

4. Datetimes (datetime64[ns]): A true Python date/time object with calendar awareness.
    Examples:
        Date in the township dataset
    Why it matters:
        You can sort by time correctly (“April” won't come before “January”).
        You can plot time-series.

5. Boolean (bool): A binary value (0/1, True/False) Useful for tagging data, creating filters, or marking conditions.
    Examples:
        Monroe_Road_Closed after converting "Y"/"N" → True / False
    Why it matters:
        Booleans let you easily select things such as:
        Pythondf[df["Monroe_Road_Closed"] == True]Show more lines

6. Pandas Categorical (category) (optional but common): A text column stored efficiently with fixed allowed values.
    Not used explicitly, but a good concept for students.
    Examples that could be categorical:
        Approval status (Approved / Provisional)
        Yes/No columns
        Location or site codes
    Why it matters:
        Saves memory
        Useful for machine learning or statistics
        Speeds up comparisons

"""
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

