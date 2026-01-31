import argparse
import os
import numpy as np
import copy
from tools import log, fill_with_mean
import pandas as pd 

# Fills a single table in long format using different methods


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--data_path', default=
     "/home/datasets4/stein/jena_experiment_data_various_products/30_min_final/complete_soil_temp_30_min_no_filling_time_correction_new.csv", type=str )   
    parser.add_argument('--output_path', default= "/home/datasets4/stein/jena_experiment_data_various_products/filled_years_time_corrected", type=str )   
    parser.add_argument('--minimum_available', default= 2, type=int )   
    parser.add_argument('--name', default= "complete_all_full_new", type=str )   
    parser.add_argument('--hori', action='store_true' )   
    parser.add_argument('--comp', action='store_true' )   
    parser.add_argument('--vert', action='store_true' )   

    # complete or block2 
    args = parser.parse_args()
    name = "stats/filling.txt"
    data = pd.read_csv(args.data_path,index_col=0)
    data["datetime"] = pd.to_datetime(data["datetime"])
    log("Found this many missing values from: " +  str(len(data)) + " values", name= name)
    log(str(data.isnull().sum()), name= name)
    print("Starting to fill")


    # Create removal file
    fillers = copy.deepcopy(data)
    fillers[[x for x in data.columns if ((x != "datetime") & (x != "plotcode"))]] = np.nan

    # Fill with vertical mean
    if args.vert:
        measurements = [x for x in data.columns if (x != "datetime" and x != "plotcode")]
        
        groups = data[["datetime"] + measurements].groupby("datetime")
        means = groups.mean()
        nPlots = groups.count()
        for x in measurements:
            print(x)
            print(x)
            # filter means that are too sparse
            sparse = nPlots.loc[((nPlots < args.minimum_available) & (nPlots != 0))[x]]
            means.loc[sparse.index.values, x] = np.nan

            log("Calculated the following Vertical means:", name= name)
            log(str(means.isnull().sum()), name= name)

            combine = data.merge(means[[x]], left_on = "datetime", right_index= True)
            indices = combine[((combine[x + "_x"].isnull()) &
                (~(combine[x + "_y"].isnull()))).values].index

            fillers.loc[indices,x] = "Vertical filler"
            data.loc[indices,x] = combine.loc[indices, x + "_y"]

            log("Nans remaining after vertical filling:", name= name)
            log(str(data.isnull().sum()), name= name)

    # Fill with seasonal mean of single plot
    if args.hori:
        print("H")
        for x in [x for x in data.columns if (x != "datetime" and x != "plotcode")]:
            remaining = data[data[x].isnull()].index
            fillers.loc[remaining,x] = "Horizontal filler"
        data = fill_with_mean(data)
        log("Nans remaining after Horizontal filling", name= name)
        log(str(data.isnull().sum()), name= name)
    
    # Fill with seasonal mean over all plots
    if args.comp:
        print("C")
        for x in [x for x in data.columns if (x != "datetime" and x != "plotcode")]:
            remaining = data[data[x].isnull()].index
            fillers.loc[remaining,x] = "Full filler"
        data = fill_with_mean(data)
        log("Nans remaining after Horizontal filling", name= name)
        log(str(data.isnull().sum()), name= name)

    print("Saving...")
    CHECK_FOLDER = os.path.isdir(args.output_path)
    if not CHECK_FOLDER:
        os.makedirs(args.output_path)
        print("created folder : ", args.output_path)
    fillers.to_csv(args.output_path + "/" + args.name +  "_filled" + ".csv",index=False )
    data.to_csv(args.output_path + "/" + args.name + ".csv",index=False )
    print("Done.")

if __name__ == '__main__':
    main()