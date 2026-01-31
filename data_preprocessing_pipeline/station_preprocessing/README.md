# Weather station preprocessing

Scripts and notebooks for processing raw weather station data and producing cleaned, analysis-ready station time series.

## Scripts

### 1_transform_station_raw.py

**Purpose**: Combines raw Excel station downloads into a single CSV and fixes duplicated columns and malformed records.

**What it does**:
- concatenates all Excel files in `--data_path`
- merges duplicated columns (e.g., `Tpot1` -> `Tpot`)
- drops known junk columns and a known bad row
- truncates timestamps to minute resolution

**Usage**:

```bash
python 1_transform_station_raw.py \
	--data_path /path/to/OK_Download \
	--output_path /path/to/station_processed
```

**Output**: `raw_station.csv` in `--output_path`.

---

### 2_transform_station_filter.py

**Purpose**: Builds a cleaned station time series from a CSV and an auxiliary dataset, applies mode-specific filters, and resamples to a target minute resolution.

**Modes**:
- `extreme_analysis`: filters `T`, `rh`, `SM0*`, `rain1` by thresholds
- `simple_weather`: selects standard weather variables and drops `-9999`
- `simple_specific`: selects radiation/energy variables and drops `-9999`
- `simple_soil`: selects soil temperature/moisture variables and drops `-9999`

**Usage**:

```bash
python 2_transform_station_filter.py \
	--data_path /path/to/raw_station.csv \
	--data_path2 /path/to/JenaExp_2021_30min.csv \
	--mode extreme_analysis \
	--sum_minutes 30 \
	--output_path /path/to/station_processed
```

**Output**: `<mode>_<sum_minutes>_station.csv` in `--output_path`.

---


### 3_transform_station_fill.py

**Purpose**: Fills missing station values using a mean-based fill and produces fill-tracking files.

**What it does**:
- logs missing values to `station_filling.txt`
- labels all missing entries as “Full filler”
- fills using `fill_with_mean(plots=False)`

**Usage**:

```bash
python 3_transform_station_fill.py \
	--data_path /path/to/extreme_analysis_station.csv \
	--output_path /path/to/station_processed
```

**Output**:
- `filled_station.csv`
- `stats_filled_station.csv`

---


### 4_transform_alternative_station_mpi

**Purpose**: Filters and aggregates an alternative station source  (MPI weatherstation) to a clean 10-minute series and then resamples to a chosen resolution.

**Notes**:
- Reads all CSVs in `--data_path`
- Builds a full 10-minute timeline for 2003–2021
- Applies threshold filtering in `extreme_analysis` mode

**Usage**:

```bash
python 4_transform_alternative_station_mpi.py \
	--data_path /path/to/weather_station_MPI/original \
	--mode extreme_analysis \
	--time_sum 3 \
	--output_path /path/to/weather_station_MPI
```

**Output**: `<mode>_complete.csv` in `--output_path`.

---

### tools.py

**Purpose**: Shared utilities for filtering, resampling, logging, and consistency checks used by the scripts above.
Key helpers include `threshold_filter()`, `time_sum()`, `sum_mins()`, and `fill_with_mean()`.


## Other files
- station_filling.txt: fill log written by `transform_station_fill.py`.

## Notes

Default paths in scripts point to local datasets; pass `--data_path`/`--output_path` for your environment.


