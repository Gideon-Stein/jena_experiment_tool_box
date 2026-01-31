import argparse
import os
import copy
from tools import threshold_filter, sum_mins
import numpy as np 
import pandas as pd

#preprocessing raw The notebook has additional infos on the steps
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--data_path', default= 
     "/home/datasets4/stein/jena_experiment_data_various_products/station_processed/raw_station.csv", type=str)
    parser.add_argument('--data_path2', default=
     "/home/datasets4/stein/jena_experiment_data_raw/JenaExp_2021_30min.csv", type=str)
    parser.add_argument('--mode', default= "extreme_analysis", type=str) 
    parser.add_argument('--sum_minutes', default= 30, type=int) 
    parser.add_argument('--output_path', default= "/home/datasets4/stein/jena_experiment_data_various_products/station_processed", type=str)

    args = parser.parse_args()

    station = pd.read_csv(args.data_path)
    station2 = pd.read_csv(args.data_path2)

    print(args.mode)

    # Rename columns without units
    station.columns = ["datetime"] + [x[0][:-1] for x in station.columns.str.split('(')][1:]
    station["datetime"] = pd.to_datetime(station["datetime"])

    # spread the table to include all timesteps
    start = pd.Timestamp('01.01.' + "2003" + ' 00:00:00')
    end = pd.Timestamp('31.12.' + "2020" + ' 23:59:00')
    spread = pd.DataFrame(pd.date_range(start, end, freq='10min'), columns=["datetime"])
    station = spread.merge(station, how="left", on= "datetime")
    # consistency fix
    station2.rename(columns={"dateTime": "datetime", "T_air": "T", "p_air": "p", "albedo": "Albedo"}, inplace=True)


    if args.mode == "extreme_analysis":
        selection = ["datetime","T", "rh", "SM008", "SM016", "rain1"]
        selection2= ["dateTime","T_air", "rh", "SM008", "SM016", "rain1"]   
        station = station[selection]
        station2 = station2[selection2]
        station2.rename(columns={"dateTime": "datetime", "T_air": "T"}, inplace=True)

        stats = copy.deepcopy(station)
        stats[[x for x in station.columns if x != "datetime"]] = np.nan
        print("Filtering")
        station, stats = threshold_filter(station,stats, "T", threshold = (-30,50))
        print((~stats.isnull()).sum())
        station, stats = threshold_filter(station,stats, "rh", threshold = (0,100))
        print((~stats.isnull()).sum())
        station, stats = threshold_filter(station,stats,"SM0", threshold = (-1,100))
        print((~stats.isnull()).sum())
        station, stats = threshold_filter(station,stats, "rain1", threshold = (-2000,1000))
        print((~stats.isnull()).sum())


    elif args.mode == "simple_weather":
        weather = ['datetime',"p", "T", "rh", "sh", "wv", "wd", "rain1", 'SDUR', "rho", "Albedo",'VPmax', 'VPact', 'VPdef', 'H2OC']
        station = station.loc[:,weather]
        station2= station2.loc[:,weather]

        #just nan filter
        station[station == -9999] = np.nan
        station2[station2 == -9999] = np.nan

    elif args.mode == "simple_specific":
        specifics = ['datetime','SDIR', 'LWDR', 'LWUR', 'TRAD', 'PAR', 'Rn','Tpyr', 'TDR', 'TUR','SWDR','SWUR','Tpot', 'Tdew']
        station = station.loc[:,specifics ]
        station2= station2.loc[:,specifics ]
        #just nan filter
        station[station == -9999] = np.nan
        station2[station2 == -9999] = np.nan

    elif args.mode == "simple_soil":
        soil = ['datetime','SHF1', 'SHF2','SHF3', 'SHF4', 'SHF5', 'SHFM',
                'ST002', 'ST004', 'ST008', 'ST016','ST032', 'ST064', 'ST128',
                'SM008', 'SM016', 'SM032', 'SM064', 'SM128']
        
        station = station.loc[:,soil]
        station2= station2.loc[:,soil]
        #just nan filter
        station[station == -9999] = np.nan
        station2[station2 == -9999] = np.nan

    else:
        print("SELECTION NOT IMPLEMENTED") 


    #sum to 30 minutes and join
    if args.sum_minutes == 10:
        pass
        print("No summing")
    else:
        station = sum_mins(station, resolution=args.sum_minutes, plots=False)
    station2["datetime"] = pd.to_datetime(station2["datetime"]) - pd.Timedelta(minutes=30)
    station = pd.concat([station, station2])
    station.reset_index(drop=True, inplace=True)

    print(len(station))
    print(len(station2))
    #save
    CHECK_FOLDER = os.path.isdir(args.output_path)
    if not CHECK_FOLDER:
        os.makedirs(args.output_path)
        print("created folder : ", args.output_path)
    station.to_csv(args.output_path + "/" + args.mode + "_" + str(args.sum_minutes) + "_station.csv",index=False)

if __name__ == '__main__':
    main()