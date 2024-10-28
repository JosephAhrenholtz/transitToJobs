# transitToJobs

Calculates accessibility to jobs in the San Francisco Bay Area. It utilizes the regional GTFS feed from [511 Open Data](https://511.org/open-data/transit) and LEHD Origin-Destination Employment Statistics (LODES) from the Census.  The purpose is to create a framework for calculating opportunity accessibility measures via transit/walking that can be used in additional projects and analyses. The project is organized into several modules, each responsible for a specific component of the accessibility calculation.

## Table of Contents

- [Directory Structure](#directory-structure)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Modules](#modules)

## Directory Structure
```
/transitToJobs
├── data
│   ├── raw
│   ├── interim
│   └── processed
├── Python_module
│   └── utils
│       ├── prep_census.py
│       ├── travel_times.py
│       ├── cumul_access.py
│       └── weight_access.py
│   ├── filepaths.py
│   └── main.py 
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Conda

### Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/JosephAhrenholtz/transitToJobs.git
    ```
    ```sh
    cd transitToJobs
    ```

2. **Create and activate the Conda environment:**

    ```sh
    conda env create -f environment.yml
    ```
    ```sh
    conda activate transitToJobs_env
    ```
3. Download the data/ directory from [Drive](https://drive.google.com/drive/folders/1vxKAKVUCX81S7EbYdIgxNtEnthTRESAm) and extract into root directory 


## Usage

### Running the Main Script

To run the entire workflow, execute the `main.py` script.  Note that the travel time calculation is intensive and will take approximately 35 minutes to run:

```sh
python main.py
```

You can run individual modules for specific tasks. For example, to run `prep_census.py`:

```sh
python utils/prep_census.py
```

## Modules

- **`prep_census.py`**
  - **Description:** Wrangles block group weighted centroids and merges with job data from LODES work area characteristics file.
  - **Functions:**
    - `wrangle_block_group_data()`
    - `load_and_merge_jobs_data(bgc)`
    - `save_bgj(bgj)`

- **`travel_times.py`**
  - **Description:** Computes travel times between block group centroids using the transit  network during a typical weekday morning commute window (7-9am).  
  - **Functions:**
    - `load_block_group_jobs()`
    - `create_transport_network()`
    - `compute_travel_time_matrix(transport_network, orig, dest)`

- **`cumul_access.py`**
  - **Description:** Calculates cumulative accessibility to jobs within a 30 minute travel time window at the block group level.
  - **Functions:**
    - `load_data()`
    - `calculate_cumulative_measures(ttm, bgj)`
    - `merge_cumulative_accessibility_data(bgj_sum, bgj, bg)`
    - `save_cumulative_access(bgj_access)`

- **`weight_access.py`**
  - **Description:** Loads workers data from LODES residence area characteristics file and merges with job accessibility measures at the block group level.  Then calculates the average accessible jobs from each Census tract, weighted by workers living in the origin of the commute.  The weighted average approach is used to emphasize accessibility for workers from their place of residence.
  - **Functions:**
    - `load_workers_data()`
    - `merge_workers_with_accessibility(workers)`
    - `compute_weighted_averages(worker_access)`
    - `merge_with_tract_geometries(weighted_avgs)`
    - `save_final_access(final_access)`


## Data Dictionary

### Processed Data
- **`fips`**: FIPS code for the Census tract.
- **`w_avg_tot_jobs_30`**: The average number of jobs accessible by public transit and walking within 30 minutes during a typical AM commute, weighted by the number of workers living in the origin tract.
- **`w_avg_constr_jobs_30`**: The average number of construction sector jobs accessible by public transit and walking within 30 minutes during a typical AM commute, weighted by the number of construction sector workers living in the origin tract.
- **`w_avg_manuf_jobs_30`**: The average number of manufacturing sector jobs accessible by public transit and walking within 30 minutes during a typical AM commute, weighted by the number of manufacturing sector workers living in the origin tract.
- **`w_avg_serv_jobs_30`**: The average number of accommodation and food service sector jobs accessible by public transit and walking within 30 minutes during a typical AM commute, weighted by the number of accommodation and food service sector workers living in the origin tract.
- **`w_avg_tech_jobs_30`**: The average number of professional, scientific, and technical service sector jobs accessible by public transit and walking within 30 minutes during a typical AM commute, weighted by the number of professional, scientific, and technical workers living in the origin tract.
