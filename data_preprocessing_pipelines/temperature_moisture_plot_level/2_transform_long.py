import argparse
import os
import pandas as pd
import numpy as np
import copy
from tools import log, select_variable_subset, cast_to_long_format, threshold_filter, boxplot_filter,sum_mins
from os import listdir
from os.path import isfile, join



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--year', default= "all", type=str )    #(all orspecify single year
    parser.add_argument('--data_path', default= "/home/datasets4/stein/jena_experiment_data_various_products/transformed_years/classic", type=str )   
    parser.add_argument('--mode', default= "complete", type=str )   # complete or block2 
    parser.add_argument('--output_path', default= "/home/datasets4/stein/jena_experiment_data_various_products/", type=str )   
    parser.add_argument('--boxplot_range', default=1.5, type=float )    
    parser.add_argument('--offset', default=0, type=int )    # skips n years if needed
    parser.add_argument('--n_sum', default=0, type=int )    
    parser.add_argument('--save_removed', action='store_true')    



    args = parser.parse_args()

    # Get all available years
    files = [args.data_path + "/" + f for f in
        listdir(args.data_path) if isfile(join(args.data_path, f))]
    files.sort()
    files = files[args.offset:]
    if args.year != "all":
        files = [x for x in files if args.year in x]

    print(files)
    for count, file in enumerate(files): 
        name = "transform_logs/" + str(args.year)
        log("Loading " + file, name= name)
        data = pd.read_csv(file)
        log("Sum time " + file, name= name)
        log("Cast to long format ", name= name) 
        data = select_variable_subset(data, mode=args.mode)        
        data = cast_to_long_format(data)
        log("Filter ", name= name)

        # Create removal file
        removals = copy.deepcopy(data)
        for x in [x for x in data.columns if ((x != "datetime") & (x != "plotcode"))]:
            removals[x] = np.nan
            removals[x + "_removed"] = np.nan

        if args.mode == "complete":
            # Filter impossible values
            log("Values in table: " +  str(len(data)), name= name)
            # Filter values: For Soil Temp: -30/45
            data, removals  = threshold_filter(data,removals, which="soil_temp", threshold = (-30,45))
            log("After removals: ", name= name)
            log(str((~removals.isnull()).sum()), name= name)

            # custom fixes. Boxplot is not always perfect.
            data, removals = boxplot_filter(data,removals, acceptRange=args.boxplot_range, nPlots=90)
            log("After boxplot: " , name= name)
            log(str((~removals.isnull()).sum()), name= name)

            # custom fixes. Boxplot is not always perfect. 
            for var in data.columns:
                custom1 = (data['datetime'] < "2003-04-15 23:59") & (~(data[var].isnull()))
                if var == "plotcode" or var =="datetime":
                    pass
                else:
                    removals.loc[custom1, var] = data.loc[custom1, var]
                    removals.loc[custom1, var + "_removed"] = "Custom filter 1"
                    data.loc[custom1,var] = np.nan
            log("After custom1: ", name= name)
            log(str((~removals.isnull()).sum()), name= name)

            for var in data.columns:
                if var == "plotcode" or var =="datetime":
                    pass
                else:
                    custom2 = data[var] < -20
                    removals.loc[custom2, var] = data.loc[custom2, var]
                    removals.loc[custom2, var + "_removed"] = "Custom filter 2"
                    data.loc[custom2,var] = np.nan
            log("After custom2: ", name= name)
            log(str((~removals.isnull()).sum()), name= name)

        elif args.mode == "block2":
            log("Values in table: " +  str(len(data)), name= name)
            # Filter values: For Soil Temp: -30/45
            data, removals  = threshold_filter(data,removals, which="soil_temp", threshold = (-30,45))
            log(str((~removals.isnull()).sum()), name= name)
            data,  removals   = threshold_filter(data,removals, which="air_temp", threshold = (-30,45))
            log(str((~removals.isnull()).sum()), name= name)
            # Filter values: For Soil Temp: -45/55
            data,  removals   = threshold_filter(data,removals, which="surface", threshold = (-30,50))
            log(str((~removals.isnull()).sum()), name= name)
            # For Air Temp: -0/100
            data,  removals   = threshold_filter(data,removals, which="humidiy", threshold = (0,100))
            log(str((~removals.isnull()).sum()), name= name)
            log("After removals: ", name= name)
            log(str((~removals.isnull()).sum()), name= name)

            # boxplot filter
            data, removals = boxplot_filter(data,removals, acceptRange=args.boxplot_range, nPlots=22)
            log("After boxplot: ", name= name)
            log(str((~removals.isnull()).sum()), name= name)

            # custom fixes. Boxplot is not always perfect. 
            for var in data.columns: 
                if var == "plotcode" or var =="datetime":
                    pass
            else:
                custom1 = (data['datetime'] > pd.Timestamp("2014-07-30 23:59")) &  (data['datetime']
                < (pd.Timestamp("2014-07-31 23:59"))) & (~(data[var].isnull()))
                if ("05cm" not in var) and ("air_rel" not in var):  
                    removals.loc[custom1, var] = data.loc[custom1, var]
                    removals.loc[custom1, var + "_removed"] = "Custom filter 1"
                    data.loc[custom1,var] = np.nan
            log("After custom1: ", name= name)
            log(str((~removals.isnull()).sum()), name= name)

            #2
            custom2 = (data['soil_temp_60cm_depth']<= 0.1)
            removals.loc[custom2, 'soil_temp_60cm_depth'] = data.loc[custom2, 'soil_temp_60cm_depth']
            removals.loc[custom2, 'soil_temp_60cm_depth_removed'] = "Custom filter 2"
            data.loc[custom2, 'soil_temp_60cm_depth'] = np.nan
            log("After custom2: ", name= name)
            log(str((~removals.isnull()).sum()), name= name)

            #3 
            custom3 = (data['datetime'] > pd.Timestamp("2002-12-31 23:59")) & (
                data['datetime'] < (pd.Timestamp("2003-08-01 00:00"))) & (data["surface_temp_south_west"] < -10)
            removals.loc[custom3, 'surface_temp_south_west'] = data.loc[custom3, 'surface_temp_south_west']
            removals.loc[custom3, 'surface_temp_south_west_removed'] = "Custom filter 3"
            data.loc[custom3, 'surface_temp_south_west'] = np.nan
            log("After custom3: ", name= name)
            log(str((~removals.isnull()).sum()), name= name)

        else: 
            print("Unknown MODE")
            return None

        log(str((~removals.isnull()).sum()), name= name)
        # Testing
        day = data["datetime"].dt.dayofyear.values
        assert (int(day[0]) == 1) & ((int(day[-1]) == 365) | (int(day[-1]) == 366)), "Time error!"
        if args.mode == "complete":
            assert len(set(data.plotcode)) == 90, "not the correct number of plotcodes"
        if args.mode == "block2":
            assert len(set(data.plotcode)) == 22, "not the correct number of plotcodes"
        day = data["datetime"].dt.dayofyear.values
        assert (int(day[0]) == 1) & ((int(day[-1]) == 365) | (int(day[-1]) == 366)), "Time error!"

        if args.n_sum == 0: 
            log("No summing...", name = name)
        else:
            log("summing time..", name= name)
            data = sum_mins(data, resolution= args.n_sum)

        #save
        CHECK_FOLDER = os.path.isdir(args.output_path + "/sum_years")
        if not CHECK_FOLDER:
            os.makedirs(args.output_path + "/sum_years")
            print("created folder : ", args.output_path + "/sum_years")
        if args.year == "all":
            data.to_csv(args.output_path + "/sum_years/"  + args.mode + "_"  +
            str(2003 + count+ args.offset) +  ".csv",index=False)
            if args.save_removed:
                removals.to_csv(args.output_path + "/sum_years/"  + args.mode + "_"  +
                str(2003 + count+ args.offset) +  "_removed.csv",index=False)
        else:
            data.to_csv(args.output_path + "/sum_years/"  + args.mode + "_"  +
            args.year +  ".csv",index=False)
            if args.save_removed:
                removals.to_csv(args.output_path + "/sum_years/"  + args.mode + "_"  +
                args.year +  "_removed.csv",index=False)

    print("Done")
if __name__ == '__main__':
    main()