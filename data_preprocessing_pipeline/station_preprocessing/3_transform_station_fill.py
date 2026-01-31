import argparse
import os
import pandas as pd
import copy
import numpy as np
from tools import log, fill_with_mean 

# Fills a single table in long format using different methods
#TODO  Not sure if this is all needed for seasonal mean fill. 


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--data_path', default=
     "/home/datasets4/stein/jena_experiment_data_various_products/station_processed/extreme_analysis_station.csv", type=str )   
    parser.add_argument('--output_path', default=
     "/home/datasets4/stein/jena_experiment_data_various_products/station_processed", type=str )   

    # complete or block2 
    name = "station_filling.txt"
    args = parser.parse_args()
    data = pd.read_csv(args.data_path)
    data["datetime"] = pd.to_datetime(data["datetime"])

    log(str(data.isnull().sum()), name=name )
    print("Starting to fill")


    # Create removal file
    fillers = copy.deepcopy(data)
    fillers[[x for x in data.columns if (x != "datetime")]] = np.nan

    print("H")
    for x in [x for x in data.columns if (x != "datetime")]:
        remaining = data[data[x].isnull()].index
        fillers.loc[remaining,x] = "Full filler"
    data = fill_with_mean(data, plots = False)
    log("Nans remaining after Horizontal filling", name= name)
    log(str(data.isnull().sum()), name= name)
    

    print("Saving...")
    CHECK_FOLDER = os.path.isdir(args.output_path)
    if not CHECK_FOLDER:
        os.makedirs(args.output_path)
        print("created folder : ", args.output_path)
    data.to_csv(args.output_path +  "/" + "filled_station.csv",index=False)
    fillers.to_csv(args.output_path + "/" +  "stats_filled_station.csv",index=False)


    print("Done.")

if __name__ == '__main__':
    main()