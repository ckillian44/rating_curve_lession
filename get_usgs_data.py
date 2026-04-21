"""
Rating Curve Lesson — Step 2: Download USGS daily data via dataretrieval

This script:
  1) Pulls site metadata for a USGS monitoring location.
  2) Pulls daily discharge (00060) and gage height (00065) from 2022-01-01 to present.
  3) Saves both datasets as CSV for offline processing in later steps.

Notes:
  • We use the public USGS dataretrieval 'waterdata' client. If import fails, prompt upgrade.
  • Parameter code '00060' = Discharge (cfs), '00065' = Gage height (ft).
  • Monitoring location format uses the prefix 'USGS-05424157'.

Run:
  python get_usgs_data.py
"""


# ---- Load packages ----

from dataretrieval import waterdata # https://github.com/DOI-USGS/dataretrieval-python


# ---- Specify USGS site number ----

# https://apps.usgs.gov/nwismapper/
# https://waterdata.usgs.gov/monitoring-location/USGS-05424157/#dataTypeId=continuous-00065-0&period=P7D&showFieldMeasurements=true
# The new dataRetrieval package uses the format 'USGS-05424157' instead of '05424157'. 
site_id = 'USGS-05424157' # Specify the site number here because we will use it more than once. 


# ---- Get site metadata from USGS ----

# Do students have an understanding of what metadata are and why they are important?
# Location metadata
loc_df, loc_metadata = waterdata.get_monitoring_locations(
    monitoring_location_id = site_id     # Specified above
    )


# ---- Save site metadata ----

# Write the data to a CSV file for later use
loc_df.to_csv('./input/USGS-05424157_Location_Metadata.csv', index = False) # index = False to avoid writing the row numbers to the file


# ---- Get available data from USGS ----

# Get daily streamflow data (returns DataFrame and metadata)
data_df, data_metadata = waterdata.get_daily(
    monitoring_location_id = site_id,     # Specified above
    parameter_code = ['00060', '00065'],  # Discharge, Gage height; Parameter code definitions: https://waterdata.usgs.gov/code-dictionary/
    time = '2022-01-01/..'                # .. means to get data up to the most recent available date
)


# ---- Save streamflow data ----

# Write the data to a CSV file for later use
data_df.to_csv('./input/USGS-05424157_Streamflow_Data.csv', index = False) # index = False to avoid writing the row numbers to the file

