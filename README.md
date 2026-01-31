# Jena experiment tool box

![Jena experiment](je.jpg)

[Jena experiment](https://the-jena-experiment.de/)

This repository collects multiple subprojects related to the Jena Experiment, including preprocessing pipelines and visualization tools.

## Subprojects

- [data_preprocessing_pipelines](data_preprocessing_pipelines): data preprocessing pipelines for plot-level temperature/moisture, covariates, soil moisture, and station data.
  - [temperature_moisture_plot_level](data_preprocessing_pipelines/temperature_moisture_plot_level): main plot-level temperature/moisture pipeline (scripts, QA notebooks, and logs).
  - [covariate_preprocessing](data_preprocessing_pipelines/covariate_preprocessing): covariate and management preprocessing notebooks and helpers.
  - [soil_moisture](data_preprocessing_pipelines/soil_moisture): soil moisture preprocessing notebooks and checks.
  - [station_preprocessing](data_preprocessing_pipelines/station_preprocessing): weather-station preprocessing scripts and notebooks.

- [jena_experiment_display](jena_experiment_display): visualization and animation tools for plot-level data.

## Installation

Each subproject ships its own environment or requirements file. Follow the instructions in the subproject README you plan to use.

## Maintainer

This repository is maintained by [@GideonStein](https://github.com/Gideon-Stein),
For questions or contributions, feel free to contact me.




