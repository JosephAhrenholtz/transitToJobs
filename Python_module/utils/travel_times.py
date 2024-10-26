# Python_module/utils/travel_times.py
import geopandas as gpd
import datetime
from r5py import TransportNetwork, TravelTimeMatrixComputer
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from filepaths import interim_data, pbf_file, gtfs_file

def load_block_group_jobs():
    bgj = gpd.read_file(os.path.join(interim_data, 'bg_jobs.geojson'))
    return bgj

def create_transport_network():
    transport_network = TransportNetwork(pbf_file, [gtfs_file])
    return transport_network

def compute_travel_time_matrix(transport_network, orig, dest):
    travel_time_computer = TravelTimeMatrixComputer(
        transport_network,
        origins=orig,
        destinations=dest,
        departure=datetime.datetime(2023, 3, 15, 7, 0),
        departure_time_window=datetime.timedelta(hours=2),
        transport_modes=["TRANSIT", "WALK"]
    )
    travel_time_matrix = travel_time_computer.compute_travel_times()
    matrix_out = os.path.join(interim_data, 'travel_time_matrix.csv')
    travel_time_matrix.to_csv(matrix_out, index=False)