import argparse
import os
import pandas as pd
import numpy as np
from os import listdir

#preprocessing raw The notebook has additional infos on the steps

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', default= "/home/datasets4/stein/jena_experiment_data_raw/jena_experiment/OK_Download/", type=str )   
    parser.add_argument('--output_path', default="/home/datasets4/stein/jena_experiment_data_various_products/station_processed", type=str )   

    args = parser.parse_args()

    files = sorted(listdir(args.data_path))
    a = pd.read_excel(args.data_path+ files[0])
    for x in files[1:-1]: 
        a = pd.concat([a,pd.read_excel(args.data_path + x)])

    # b has all columns doubled with some weird 30minute resolution data.
    b = pd.read_excel(args.data_path + files[-1])
    for x in list(b.columns): 
        if ".1" in x:
            b.drop([x], axis=1, inplace=True)
    a = pd.concat([a,b])
    a.reset_index(inplace=True)
    
    duplicates = ["Tpot1 (K)", "Tdew1 (degC)" ,"VPmax1 (mbar)", "VPact1 (mbar)", "VPdef1 (mbar)", "H2OC1 (mmol/mol)", "rho1 (g/m**3)"]
    real = ["Tpot (K)", "Tdew (degC)" ,"VPmax (mbar)", "VPact (mbar)", "VPdef (mbar)", "H2OC (mmol/mol)", "rho (g/m**3)"]

    for x in range(len(real)):
        print(sum((~np.isnan(a[duplicates[x]])) & (~np.isnan(a[real[x]]))))

    # No double entries. Lets join them
    for x in range(len(real)):
        a.loc[~np.isnan(a[duplicates[x]]),[real[x]]] = a.loc[~np.isnan(a[duplicates[x]]),[duplicates[x]]].values
        a.drop([duplicates[x]], axis=1, inplace=True)
    print(sum(np.isnan(a[real[x]])))
    
    # Drop trash
    a.drop(["index"], axis=1, inplace=True)
    a.drop(["Unnamed: 53"], axis=1, inplace=True)
    
    # Drop seconds from time
    a.loc[:,"Date Time"] = a.loc[:,"Date Time"].astype('datetime64[m]')

    # Drop some NaNs
    a.drop(997644,inplace = True)
    a.reset_index(inplace=True, drop=True)

    #save
    CHECK_FOLDER = os.path.isdir(args.output_path)
    if not CHECK_FOLDER:
        os.makedirs(args.output_path)
        print("created folder : ", args.output_path)
    a.to_csv(args.output_path + "/" + "raw_station.csv",index=False)

if __name__ == '__main__':
    main()