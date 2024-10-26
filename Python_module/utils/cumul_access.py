# Python_module/utils/cumul_access.py
import pandas as pd
import geopandas as gpd
from pygris import block_groups
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from filepaths import interim_data

def load_data():
    ttm_data = os.path.join(interim_data, 'travel_time_matrix.csv')
    ttm = pd.read_csv(ttm_data, dtype={"from_id": str})
    bgj_data = os.path.join(interim_data, 'bg_jobs.geojson')
    bgj = gpd.read_file(bgj_data)

    crs = 'WGS84'
    bay_cnty_fips = ['001', '075', '041', '013', '095', '055', '085', '097', '081']
    bg = block_groups(state="CA", cb=True, county=bay_cnty_fips, year=2021, cache=True)
    bg = bg.rename({'GEOID': 'fips_bg'}, axis=1)
    bg = bg.loc[:, ['fips_bg', 'geometry']].to_crs(crs)
    return ttm, bgj, bg

def calculate_cumulative_measures(ttm, bgj):
    cutoff = 30
    ttm = ttm[ttm["travel_time"] < cutoff]
    bgj = bgj.drop(columns="geometry")
    bgj_sum = pd.merge(ttm[["from_id", "to_id"]], bgj[["id", "total_jobs", "construct_jobs", "manuf_jobs", "serv_jobs", "tech_jobs"]], left_on="to_id", right_on="id")
    bgj_sum = bgj_sum[["from_id", "total_jobs", "construct_jobs", "manuf_jobs", "serv_jobs", "tech_jobs"]].groupby("from_id", as_index=False).sum()
    bgj_sum = bgj_sum.rename(columns={"total_jobs": "tot_jobs_30", "construct_jobs": "constr_jobs_30", "manuf_jobs": "manuf_jobs_30", "serv_jobs": "serv_jobs_30", "tech_jobs": "tech_jobs_30"})
    return bgj_sum

def merge_cumulative_accessibility_data(bgj_sum, bgj, bg):
    bgj_fips = bgj[['id', 'fips_bg']]
    bgj_fips['id'] = bgj_fips['id'].astype(str)
    bgj_access = pd.merge(bgj_sum, bgj_fips, left_on="from_id", right_on="id")
    bgj_access = bgj_access.drop(columns="id")
    bgj_access = bg.merge(bgj_access, on='fips_bg', how='left')
    return bgj_access

def save_cumulative_access(bgj_access):
    cumul_access_out = os.path.join(interim_data, 'bg_cumul_access.geojson')
    bgj_access.to_file(cumul_access_out, driver='GeoJSON')



