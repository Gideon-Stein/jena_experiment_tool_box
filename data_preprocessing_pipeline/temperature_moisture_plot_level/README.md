# Data preprocessing pipeline: Jena experiment

This repository features the complete preprocessing for the Jena experiment plot level temperature and moisture data + Logs.
The preprocessing pipeline consists of several sequential steps that transform raw Jena experiment data into a clean, filled dataset ready for analysis. The pipeline handles data quality issues, temporal corrections, format transformations, and missing value imputation.



### Input format: 
The scripts expect the data to come in the structure: 
```bash
main_folder/year/data/BD20240010600.csv #and many more of these files
```





# Core Pipeline Scripts (Run them in sequence.)

#### 1. Raw Data Transformation
```bash
python transform_raw.py  --start_year 2003 --end_year 2021 --input_path /path/to/main_folder --output_path /path/to/output_folder
```
**Purpose**: Transforms raw data tables into yearly tables while performing data cleaning.

**Key Features**:
- Spreads incomplete timelines to complete temporal coverage
- Corrects malformed datetime columns using dayfirst=True parsing
- Fixes wrong column names and removes duplicate information using faulty column mapping
- Applies consistency tests for data validation
- Logs all transformations for debugging

**Input**: Raw CSV files organized by year in separate folders
**Output**: Cleaned yearly CSV files with standardized column names and complete timelines (in path/transformed_years/)
**Dependencies**: Requires `stats/faulty_column_mapping.p` and column header file

Note: if many faulty columns are detected, consider updating the column mapping via column_mapping.ipynb

#### 2. Long Format Transformation
```bash
python transform_long.py --year all --data_path /path/to/transformed_years/classic --mode complete --boxplot_range 1.5 --output_path /path/to/output_folder --save_removed --n_sum 30 --mode complete # or block2
```
**Purpose**: Converts wide-format yearly data to long format and applies quality filters.

**Key Features**:
- Reshapes data from wide to long format for easier analysis
- Applies boxplot-based outlier detection (configurable range via --boxplot_range)
- Filters impossible/unrealistic values
- Creates removal tracking files when `--save_removed` is used
- Supports different variable subsets via mode parameter (complete and block2)
- Processes single years or all years at once
- Aggregates to a specific resolution (--n_sum MIN)

**Input**: Wide-format yearly CSV files from transform_raw.py
**Output**: Long-format CSV files with outlier detection applied
**Modes**: "complete" (all variables) or "block2" (subset)


You can stop at this point if a single year file without interpolation is sufficient.


#### 3. Data Combination
```bash
python transform_combine.py --data_path /path/to/previous_output --name complete
```
**Purpose**: Combines all yearly long-format files into a single comprehensive dataset.

**Key Features**:
- Concatenates multiple yearly files into one dataset
- Excludes removed files if necessary.
- Maintains chronological order
- Simple and robust merging process

**Input**: Multiple long-format yearly CSV files
**Output**: Single combined CSV file spanning all years

#### 4. Time Correction (Critical Step)
```bash
python 4_transform_time_correction.py --data_path /path/to/combined --output_path corrected_data.csv
```
**Purpose**: Applies critical temporal corrections for specific time periods with known issues.

**Key Features**:
- Corrects time shift issues in 2005-2011 data
- Handles daylight saving time transitions
- Applies year-specific corrections based on mannual analysis
- Preserves data integrity while fixing temporal alignment

**Note**: This step is essential and should be performed after combining but before filling.

#### 5. Missing Data Imputation
```bash
python transform_fill.py --data_path /path/to/time_corrected --output_path path/to/out/ --minimum_available 2 --vert --hori --comp
```
**Purpose**: Fills missing values using multiple imputation methods.

**Key Features**:
- **Vertical filling** (`--vert`): Uses temporal means across all plots for each timestamp (you can specify the minimum amount of samples that are required to perform this filling at any timestamp via --minimum_available Number)
- **Horizontal filling** (`--hori`): Uses seasonal mean of single plot for each timestamp  
- **Compositional filling** (`--comp`): Ueses seasonal mean over all plot for each timestamp
- Filterare applied in sequence but can be skipped. Only if --comp is applied a fully interpolated dataset is garantueed.
- Quality control with minimum data availability requirements
- Creates tracking files to monitor what was filled
- Preserves original data patterns while imputing missing values
Note, as we partially rely on seasonal means, the interpolated values can change with the addition of new data.

**Input**: Time-corrected combined dataset
**Output**: Complete dataset with missing values filled
**Parameters**: `minimum_available` sets threshold for reliable mean calculations

#### 6. Consistency check: 

**Purpose**: Crosschecks the different data products for consistency. please provide the correct pathings according to the file. 




### Additional Notebooks

#### `column_mapping.ipynb`
**Purpose**: Creates and maintains mappings from incorrect to correct column names.
- **For new data**: When processing new data batches and many faulty column names appear
- Identifies faulty column names in raw data files
- Generates pickled mapping files used by `transform_raw.py`
- Provides workflow for handling column name inconsistencies
- Creates `stats/faulty_column_mapping.p` used throughout pipeline

#### `check_quality.ipynb`
**Purpose**: Visual quality assessment of processed data across different pipeline stages.
- Plots time series data for all plots to identify anomalies
- Compares surface temperature and soil temperature patterns
- Validates data consistency between "complete" and "block2" processing modes
- Generates diagnostic plots for manual inspection

#### `pipline_display.ipynb`
**Purpose**: Comprehensive visualization and analysis of the complete preprocessing pipeline.
- Loads and visualizes data from different processing stages
- Generates diagnostic plots for each transformation step
- Compares data before and after time corrections
- Provides visual validation of filling procedures
- Includes analysis of 2022-2024 data processing results

