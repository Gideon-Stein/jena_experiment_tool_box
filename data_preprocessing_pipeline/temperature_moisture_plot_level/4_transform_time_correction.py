import argparse
import pandas as pd

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', default= "/home/datasets4/stein/jena_experiment_data_various_products/30_min_final/complete_soil_temp_30_min.csv", type=str )   
    parser.add_argument('--output_path', default= "/home/datasets4/stein/jena_experiment_data_various_products/30_min_final/complete_soil_temp_30_min_no_filling_time_correction.csv", type=str )   



    args = parser.parse_args()

    # 2022
    data = pd.read_csv(args.data_path)
    data.datetime = pd.to_datetime(data.datetime)

    out = data.copy()

    c1 = (out.datetime.dt.year == 2005) & (out.datetime.dt.day_of_year >= 142)
    c2 = (out.datetime.dt.year == 2011) & (out.datetime.dt.day_of_year < 9)
    c3 = (out.datetime.dt.year.isin([2006,2007,2008,2009,2010]))
    c4 = (out.datetime.dt.year == 2005) & (out.datetime.dt.day_of_year == 142) & (out.datetime.dt.hour == 0)
    c5 = (out.datetime.dt.year == 2011) & (out.datetime.dt.day_of_year == 8) & (out.datetime.dt.hour == 23)

    keep = out[c5].copy()
    remove = out[c4].index

    out.loc[(c1 & ~c4) | c2 | c3, "datetime"] = out[(c1 & ~c4)| c2 | c3].datetime.values + pd.Timedelta("-1H")
    out.drop(index=remove, inplace = True)

    out = pd.concat((out,keep))
    out.sort_values(["plotcode", "datetime"],inplace=True)
    out.reset_index(drop=True, inplace=True)

    print(len(out.datetime.unique()) * len(out.plotcode.unique()))
    print(len(data))
    print(len(out.datetime.unique()) * len(out.plotcode.unique()) == len(data))
    print(len(out.datetime.unique()) * len(out.plotcode.unique()))
    print(len(out[out.duplicated(subset=["datetime", "plotcode"])]))

    #cT = (data.plotcode == "2A03N")
    #cT2 = (data.datetime.dt.year == 2014)
    #print(data.loc[cT & cT2,"soil_temp_15cm"] == (
    #    out.loc[cT & cT2, "soil_temp_15cm"]).values)

    #cT = (data.plotcode == "2A03N")
    #cT2 = (data.datetime.dt.year == 2007)
    #print((data.loc[cT & cT2,"soil_temp_15cm"] == np.roll(
    #    (out.loc[cT & cT2, "soil_temp_15cm"]).values,2)).sum())


    out.to_csv(args.output_path)

    print("Done")
if __name__ == '__main__':
    main()