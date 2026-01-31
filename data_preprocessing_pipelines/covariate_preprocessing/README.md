# Covariate preprocessing

This folder contains notebooks and helpers used to prepare covariate and management datasets that complement the main plot-level pipeline.

## Contents

- covariate_preprocessing.ipynb: integrates covariates such as biomass, cover/height, LAI, root biomass, and related measurements.
- management_preprocessing.ipynb: prepares management and treatment metadata.
- snow_cover.ipynb: processes snow cover and related meteorological variables.
- covariate_tools.py: shared helper functions for the covariate notebooks.

## Notes

Most covariate sources are currently available through 2020; newer years may require updates in the notebooks or source files.


#### `covariate_preprocessing.ipynb`
**Purpose**: Processes environmental covariates and supplementary data to bring them into a machine learning friendly format.
- Integrates biomass, cover, height, LAI, and root biomass data (2003-2020)
- Processes soil respiration and microbial biomass measurements
- Handles SPEI (Standardized Precipitation-Evapotranspiration Index) data
- Validates realized diversity measurements
- **Note**: Most data extends only to 2020, requires updates for recent years

#### `management_preprocessing.ipynb`
**Purpose**: Processes experimental management and treatment data.

#### `snow_cover.ipynb`
**Purpose**: Processes snow cover data from the DWD for the area of Jena.
