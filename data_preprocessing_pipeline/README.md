# Jena experiment data preprocessing
This section contains a number of data preprocessing pipelines that are based on various raw data products from the jena experiment. Note, this is the final state before releaseing it on github for public usage.
Please refer to this version for the most up to date version: https://github.com/Gideon-Stein/jena_experiment_tool_box

Further, the publication branch holds the submitted code that was submitted for our publication: 
https://www.nature.com/articles/s41561-023-01338-5


![Jena experiment](je.jpg)


## This project contains:

- [temperature_moisture_plot_level/README.md](temperature_moisture_plot_level/README.md): main plot-level temperature/moisture pipeline (scripts, QA notebooks, and logs).
- [covariate_preprocessing/README.md](covariate_preprocessing/README.md): covariate and management preprocessing notebooks and helpers.
- [soil_moisture/README.md](soil_moisture/README.md): soil moisture preprocessing notebooks and checks.
- [station_preprocessing/README.md](station_preprocessing/README.md): weather-station preprocessing scripts and notebooks.
- [old_pipeline/README.md](old_pipeline/README.md): legacy notebooks from earlier pipeline versions.


:warning:

Note, we rely on a large raw data product. 
Please contact us if you are interested in the raw data.
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
