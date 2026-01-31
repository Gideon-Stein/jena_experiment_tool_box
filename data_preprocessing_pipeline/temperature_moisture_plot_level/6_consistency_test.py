import argparse
import pandas as pd
import numpy as np
from tools import get_all_paths


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--data1_path', 
    default= "/home/datasets4/stein/jena_experiment_data_various_products/transformed_years/classic", type=str )   
    parser.add_argument('--data2_path',
     default= "/home/datasets4/stein/jena_experiment_data_various_products/sum_years/complete_all.csv", type=str )   
    parser.add_argument('--data3_path', 
    default= "/home/datasets4/stein/jena_experiment_data_various_products/filled_years_time_corrected/complete_all_full_new.csv", type=str )  
    parser.add_argument('--resolution', default=30, type=int )   
 
    args = parser.parse_args()

    data2 =  pd.read_csv(args.data2_path)
    data3 =  pd.read_csv(args.data3_path) 
    data3.sort_values(by=["datetime","plotcode"],inplace=True)
    data2.sort_values(by=["datetime","plotcode"],inplace=True)

    # Random sum test. Also checks for consistency through the transform steps
    if args.resolution == 30: 
        tables,tables_list = get_all_paths()
        print(tables[10][500])
        raw  = pd.read_csv(tables[10][500], encoding= 'unicode_escape')
        raw_calc = raw.loc[(pd.to_datetime(raw["t[s]"]) >= "26.04.2013 08:00:00.02") &
         (pd.to_datetime(raw["t[s]"]) <= "26.04.2013 08:30:00.02"),
          "soil_temp_05cm_depth_1A01N[°C]"].mean()

        summed = data2.loc[(data2["datetime"] == "2013-04-26 08:00:00") &
         (data2["plotcode"] == "1A01"),"soil_temp_05cm_depth"] 
        print(raw_calc - summed.values)
        assert (raw_calc - summed.values) < 1.5e-12, "Random mean check failed between raw and summed"
    else:
        assert False, "TEST NOT IMPLEMENTED"


    # Number of small column tests
    assert np.all(data2.columns == data3.columns), "COLUMNS UNEQUAL"
    assert np.all(data2.datetime.sort_values().values == data3.datetime.sort_values().values), "Datetime UNEQUAL"
    assert np.all(data2.plotcode.sort_values().values == data3.plotcode.sort_values().values), "Plotcodes UNEQUAL"
    print("All tests passed")
    print("Done.")

if __name__ == '__main__':
    main()