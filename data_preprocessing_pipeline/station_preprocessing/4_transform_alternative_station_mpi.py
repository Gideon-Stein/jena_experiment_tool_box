import argparse
import os
import pandas as pd
from tools import threshold_filter, time_sum
from os import listdir
import copy 
import numpy as np
from os.path import isfile, join

#preprocessing raw The notebook has additional infos on the steps
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--data_path', default= 
     "/home/datasets4/stein/jena_experiment_data_raw/weather_station_MPI/original", type=str)
    parser.add_argument('--mode', default= "extreme_analysis", type=str) 
    parser.add_argument('--time_sum', default= 3, type=int) 
    parser.add_argument('--output_path', default= "/home/datasets4/stein/jena_experiment_data_various_products/mpi_weatherstation", type=str)

    args = parser.parse_args()


    supplements = [args.data_path + "/" + f for f in listdir(
        args.data_path) if (isfile(join(args.data_path, f)) & ("csv" in f ))]
    supplements.sort()
    station = [pd.read_csv(x, encoding="unicode_escape") for x in supplements]
    station = pd.concat(station).reset_index(drop=True)
    station.columns = ["Date Time"] + [x[0][:-1] for x in station.columns.str.split('(')][1:]


    station["datetime"] = pd.to_datetime(station["Date Time"].values, format="%d.%m.%Y %H:%M:%S")
    station.drop_duplicates("datetime", inplace=True)
    station.drop(columns = ["Date Time"], inplace = True)


    station.sort_values("datetime", inplace=True)
    station.reset_index(drop=True, inplace=True)

    # spread the table to include all timesteps
    start = pd.Timestamp('01.01.' + "2003" + ' 00:00:00')
    end = pd.Timestamp('31.12.' + "2021" + ' 23:59:00')
    spread = pd.DataFrame(pd.date_range(start, end, freq='10min'), columns=["datetime"])
    station = spread.merge(station, how="left", on= "datetime")


    if args.mode == "extreme_analysis":
        selection = ["datetime","T", "rh", "rain"]
        station = station[selection]

        stats = copy.deepcopy(station)
        stats[[x for x in station.columns if x != "datetime"]] = np.nan
        print("Filtering")
        station, stats = threshold_filter(station,stats, "T", threshold = (-30,50))
        print((~stats.isnull()).sum())
        station, stats = threshold_filter(station,stats, "rh", threshold = (0,100))
        print((~stats.isnull()).sum())
        station, stats = threshold_filter(station,stats, "rain1", threshold = (-2000,1000))
        print((~stats.isnull()).sum())
    else:
        print("SELECTION NOT IMPLEMENTED")

    #sum to 30 minutes and join
    station = time_sum(station, sum_minutes= args.time_sum)
    station.reset_index(drop=True, inplace=True)

    #save
    CHECK_FOLDER = os.path.isdir(args.output_path)
    if not CHECK_FOLDER:
        os.makedirs(args.output_path)
        print("created folder : ", args.output_path)
    station.to_csv(args.output_path + "/" + args.mode +  "_complete.csv",index=False)

if __name__ == '__main__':
    main()