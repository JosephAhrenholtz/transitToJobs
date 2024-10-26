# Python_module/main.py
import sys
import os


# Add the utils directory to sys.path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils'))
#print(f"Adding to sys.path: {utils_path}")
sys.path.append(utils_path)


from utils.prep_census import wrangle_block_group_data, load_and_merge_jobs_data, save_bgj
from utils.travel_times import load_block_group_jobs, create_transport_network, compute_travel_time_matrix
from utils.cumul_access import load_data, calculate_cumulative_measures, merge_cumulative_accessibility_data, save_cumulative_access
from utils.weight_access import load_workers_data, merge_workers_with_accessibility, compute_weighted_averages, merge_with_tract_geometries, save_final_access

def main():
    # Step 1: Prepare Census Data
    bgc = wrangle_block_group_data()
    bgj = load_and_merge_jobs_data(bgc)
    save_bgj(bgj)

    # Step 2: Compute Travel Times
    bgj = load_block_group_jobs()
    transport_network = create_transport_network()
    compute_travel_time_matrix(transport_network, bgj, bgj)

    # Step 3: Calculate Cumulative Access
    ttm, bgj, bg = load_data()
    bgj_sum = calculate_cumulative_measures(ttm, bgj)
    bgj_access = merge_cumulative_accessibility_data(bgj_sum, bgj, bg)
    save_cumulative_access(bgj_access)

    # Step 4: Compute Weighted Access
    workers = load_workers_data()
    worker_access = merge_workers_with_accessibility(workers)
    weighted_avgs = compute_weighted_averages(worker_access)
    final_access = merge_with_tract_geometries(weighted_avgs)
    save_final_access(final_access)

if __name__ == "__main__":
    main()