# Jena experiment data preprocessing

This section contains data preprocessing pipelines based on raw data products from the Jena Experiment. This repository reflects the final state prepared for public release. For the most up-to-date version, refer to: https://github.com/Gideon-Stein/jena_experiment_tool_box

The publication branch contains the submitted code associated with the publication: 
https://www.nature.com/articles/s41561-023-01338-5

![Jena experiment](je.jpg)

## Contents

- [temperature_moisture_plot_level/README.md](temperature_moisture_plot_level/README.md): main plot-level temperature/moisture pipeline (scripts, QA notebooks, and logs).
- [covariate_preprocessing/README.md](covariate_preprocessing/README.md): covariate and management preprocessing notebooks and helpers.
- [soil_moisture/README.md](soil_moisture/README.md): soil moisture preprocessing notebooks and checks.
- [station_preprocessing/README.md](station_preprocessing/README.md): weather-station preprocessing scripts and notebooks.
- [old_pipeline/README.md](old_pipeline/README.md): legacy notebooks from earlier pipeline versions.

## Data access

:warning:

These pipelines rely on a large raw data product. Please contact the project owner if you are interested in access.

:warning:

## Environment setup

Use conda:

```bash
conda env create -f environment.yml
```

Or install into an existing environment:

```bash
pip install -r requirements.txt
```
