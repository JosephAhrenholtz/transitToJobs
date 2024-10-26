# Python_module/utils/prep_census.py
import pandas as pd
import geopandas as gpd
import fiona
from pygris.data import get_lodes
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from filepaths import interim_data, bgc_file

def wrangle_block_group_data():
    dtypes = {
        'STATEFP': str,
        'COUNTYFP': str,
        'TRACTCE': str,
        'BLKGRPCE': str,
        'POPULATION': int,
        'LATITUDE': float,
        'LONGITUDE': float
    }
    bgc = pd.read_csv(bgc_file, dtype=dtypes)
    bgc['fips_bg'] = bgc['STATEFP'] + bgc['COUNTYFP'] + bgc['TRACTCE'] + bgc['BLKGRPCE']
    bay_cnty_fips = ['001', '075', '041', '013', '095', '055', '085', '097', '081']
    bgc = bgc[bgc['COUNTYFP'].isin(bay_cnty_fips)]
    crs = 'WGS84'
    bgc = gpd.GeoDataFrame(bgc, geometry=gpd.points_from_xy(bgc.LONGITUDE, bgc.LATITUDE)).set_crs(crs)
    bgc = bgc[['fips_bg', 'geometry']]
    return bgc

def load_and_merge_jobs_data(bgc):
    jobs = get_lodes(state="CA", year=2021, lodes_type="wac", cache=True)
    jobs['total_jobs'] = jobs['C000'].astype(int)
    jobs['construct_jobs'] = jobs['CNS04'].astype(int)
    jobs['manuf_jobs'] = jobs['CNS05'].astype(int)
    jobs['serv_jobs'] = jobs['CNS18'].astype(int)
    jobs['tech_jobs'] = jobs['CNS12'].astype(int)
    jobs = jobs.rename(columns={'w_geocode': 'fips_block'})
    jobs['fips_block'] = jobs['fips_block'].astype(str).str.zfill(15)
    jobs['fips_bg'] = jobs['fips_block'].str[:12]
    jobs = jobs.groupby('fips_bg').sum().reset_index()
    jobs = jobs.drop(columns='fips_block').drop_duplicates(subset='fips_bg')
    bgj = bgc.merge(jobs, on='fips_bg', how='left')
    bgj = bgj[['fips_bg', 'total_jobs', 'construct_jobs', 'manuf_jobs', 'serv_jobs', 'tech_jobs', 'geometry']]
    bgj = bgj.fillna(0)
    bgj[['total_jobs', 'construct_jobs', 'manuf_jobs', 'serv_jobs', 'tech_jobs']] = bgj[['total_jobs', 'construct_jobs', 'manuf_jobs', 'serv_jobs', 'tech_jobs']].astype(int)
    bgj = bgj.reset_index(drop=False).rename(columns={'index': 'id'})
    return bgj

def save_bgj(bgj):
    bgj_out = os.path.join(interim_data, 'bg_jobs.geojson')

    bgj.to_file(bgj_out, driver='GeoJSON')


