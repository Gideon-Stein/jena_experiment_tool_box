# Data preprocessing pipeline: Jena experiment

This repository contains the full preprocessing workflow for Jena Experiment plot-level temperature and moisture data, including logs. The pipeline consists of sequential steps that transform raw data into a clean, filled dataset ready for analysis, handling data quality issues, temporal corrections, format transformations, and missing-value imputation.

## Input format

The scripts expect data in the following structure:

```bash
main_folder/year/data/BD20240010600.csv
```

## Core pipeline scripts (run in sequence)

#### 1. Raw data transformation

```bash
python 1_transform_raw.py --start_year 2003 --end_year 2021 --input_path /path/to/main_folder --output_path /path/to/output_folder
```

**Purpose**: Transforms raw data tables into yearly tables while performing data cleaning.

**Key features**:
- Expands incomplete timelines to full temporal coverage
- Corrects malformed datetime columns using `dayfirst=True` parsing
- Fixes incorrect column names and removes duplicate information using faulty column mapping
- Applies consistency tests for validation
- Logs all transformations for debugging

**Input**: Raw CSV files organized by year in separate folders.

**Output**: Cleaned yearly CSV files with standardized column names and complete timelines (in path/transformed_years/).

**Dependencies**: Requires `stats/faulty_column_mapping.p` and the column header file.

Note: If many faulty columns are detected, update the column mapping via column_mapping.ipynb.

#### 2. Long-format transformation

```bash
python 2_transform_long.py --year all --data_path /path/to/transformed_years/classic --mode complete --boxplot_range 1.5 --output_path /path/to/output_folder --save_removed --n_sum 30
```

**Purpose**: Converts wide-format yearly data to long format and applies quality filters.

**Key features**:
- Reshapes data from wide to long format for easier analysis
- Applies boxplot-based outlier detection (configure with `--boxplot_range`)
- Filters impossible or unrealistic values
- Creates removal tracking files when `--save_removed` is used
- Supports different variable subsets via `--mode` (complete or block2)
- Processes single years or all years at once
- Aggregates to a specific resolution (`--n_sum` minutes)

**Input**: Wide-format yearly CSV files from 1_transform_raw.py.

**Output**: Long-format CSV files with outlier detection applied.

**Modes**: complete (all variables) or block2 (subset).

You can stop here if a single-year file without interpolation is sufficient.

#### 3. Data combination

```bash
python 3_transform_combine.py --data_path /path/to/previous_output --name complete
```

**Purpose**: Combines yearly long-format files into a single comprehensive dataset.

**Key features**:
- Concatenates multiple yearly files into one dataset
- Excludes removed files if necessary
- Maintains chronological order

**Input**: Multiple long-format yearly CSV files.

**Output**: Single combined CSV file spanning all years.

#### 4. Time correction (critical step)

```bash
python 4_transform_time_correction.py --data_path /path/to/combined --output_path corrected_data.csv
```

**Purpose**: Applies temporal corrections for specific periods with known issues.

**Key features**:
- Corrects time-shift issues in 2005–2011 data
- Handles daylight saving time transitions
- Applies year-specific corrections based on manual analysis
- Preserves data integrity while fixing temporal alignment

**Note**: This step is essential and should be performed after combining but before filling.

#### 5. Missing data imputation

```bash
python 5_transform_fill.py --data_path /path/to/time_corrected --output_path /path/to/out --minimum_available 2 --vert --hori --comp
```

**Purpose**: Fills missing values using multiple imputation methods.

**Key features**:
- **Vertical filling** (`--vert`): Uses temporal means across all plots for each timestamp (configure minimum samples with `--minimum_available`)
- **Horizontal filling** (`--hori`): Uses seasonal means of a single plot for each timestamp
- **Compositional filling** (`--comp`): Uses seasonal means across all plots for each timestamp
- Filters are applied in sequence but can be skipped; applying `--comp` guarantees a fully interpolated dataset
- Quality control with minimum data availability requirements
- Creates tracking files to monitor what was filled
- Preserves original data patterns while imputing missing values

Note: As the pipeline relies on seasonal means, interpolated values can change with the addition of new data.

**Input**: Time-corrected combined dataset.

**Output**: Complete dataset with missing values filled.

**Parameters**: `minimum_available` sets the threshold for reliable mean calculations.

#### 6. Consistency check

**Purpose**: Cross-checks the different data products for consistency. Provide correct paths according to the file.

## Additional notebooks

#### column_mapping.ipynb
**Purpose**: Creates and maintains mappings from incorrect to correct column names.
- For new data: use when many faulty column names appear in raw data batches
- Identifies faulty column names in raw data files
- Generates pickled mapping files used by 1_transform_raw.py
- Provides workflow for handling column name inconsistencies
- Creates `stats/faulty_column_mapping.p` used throughout the pipeline

#### check_quality.ipynb
**Purpose**: Visual quality assessment of processed data across different pipeline stages.
- Plots time series data for all plots to identify anomalies
- Compares surface temperature and soil temperature patterns
- Validates data consistency between complete and block2 processing modes
- Generates diagnostic plots for manual inspection

#### pipline_display.ipynb
**Purpose**: Visualization and analysis of the complete preprocessing pipeline.
- Loads and visualizes data from different processing stages
- Generates diagnostic plots for each transformation step
- Compares data before and after time corrections
- Provides visual validation of filling procedures
- Includes analysis of 2022–2024 data processing results

