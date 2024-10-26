import os

# Dynamically construct the root
proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Directories
raw_data = os.path.join(proj_dir, 'data', 'raw')
interim_data = os.path.join(proj_dir, 'data', 'interim')
out_data = os.path.join(proj_dir, 'data', 'processed')

# Raw files
bgc_file = os.path.join(raw_data, 'CenPop2020_Mean_BG06.txt') # Source: https://www.census.gov/geographies/reference-files/time-series/geo/centers-population.html
pbf_file = os.path.join(raw_data, 'san-francisco-bay_california.osm.pbf') # Source: https://www.interline.io/osm/extracts/ login for api key: https://app.interline.io/users/sign_in
gtfs_file = os.path.join(raw_data, 'GTFSTransitData_RG.zip') # Source: https://511.org/open-data/transit