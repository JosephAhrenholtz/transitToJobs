# Python_module/utils/weight_access.py
import pandas as pd
import geopandas as gpd
from pygris.data import get_lodes
from pygris import tracts
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from filepaths import interim_data, out_data

def load_workers_data():
    ca_lodes_rac = get_lodes(state="CA", year=2021, lodes_type="rac", cache=True)
    workers = (
        ca_lodes_rac
        .groupby('h_geocode', as_index=False)
        .agg({'C000': sum, 'CNS04': sum, 'CNS05': sum, 'CNS18': sum, 'CNS12': sum})
        .rename({'h_geocode': 'fips_block', 'C000': 'total_workers', 'CNS04': 'constr_workers', 'CNS05': 'manuf_workers', 'CNS18': 'serv_workers', 'CNS12': 'tech_workers'}, axis=1)
    )
    workers['fips_bg'] = workers['fips_block'].str[:12]
    workers = workers.groupby('fips_bg').sum().reset_index()
    workers = workers.drop(columns='fips_block').drop_duplicates(subset='fips_bg')
    return workers

def merge_workers_with_accessibility(workers):
    cumul_data = os.path.join(interim_data, 'bg_cumul_access.geojson')
    cumul_access = gpd.read_file(cumul_data).drop(columns='geometry')
    worker_access = workers.merge(cumul_access, on='fips_bg', how='left')
    access_cols = worker_access.filter(regex='_30$', axis=1).columns
    worker_access[access_cols] = worker_access[access_cols].fillna(0).astype(int)
    worker_access['fips'] = worker_access['fips_bg'].str[:11]
    fips = worker_access.pop('fips')
    worker_access.insert(0, 'fips', fips)
    return worker_access

def compute_weighted_averages(worker_access):
    def w_avg_grp(values, weights, item):
        return (values * weights).groupby(item).sum() / weights.groupby(item).sum()

    pairs = [('tot_jobs_30', 'total_workers'), 
             ('constr_jobs_30', 'constr_workers'), 
             ('manuf_jobs_30', 'manuf_workers'), 
             ('serv_jobs_30', 'serv_workers'), 
             ('tech_jobs_30', 'tech_workers')]

    weighted_avgs = pd.DataFrame()
    for job_col, worker_col in pairs:
        weighted_avg = w_avg_grp(values=worker_access[job_col], weights=worker_access[worker_col], item=worker_access.fips)
        weighted_avg = weighted_avg.reset_index()
        weighted_avg.columns = ['fips', f'w_avg_{job_col}']
        weighted_avg = weighted_avg.drop_duplicates('fips')
        if weighted_avgs.empty:
            weighted_avgs = weighted_avg
        else:
            weighted_avgs = pd.merge(weighted_avgs, weighted_avg, on='fips')
    return weighted_avgs

def merge_with_tract_geometries(weighted_avgs):
    crs = 'WGS84'
    bay_cnty_fips = ['001', '075', '041', '013', '095', '055', '085', '097', '081']
    trcts = tracts(state="CA", cb=True, county=bay_cnty_fips, year=2021, cache=True)
    trcts = trcts.rename({'GEOID': 'fips'}, axis=1)
    trcts = trcts.loc[:, ['fips', 'geometry']].to_crs(crs)
    final_access = trcts.merge(weighted_avgs, on='fips', how='left')
    return final_access


def save_final_access(final_access):
    final_access_out = os.path.join(out_data, 'final_access.geojson')
    final_access.to_file(final_access_out, driver='GeoJSON')

