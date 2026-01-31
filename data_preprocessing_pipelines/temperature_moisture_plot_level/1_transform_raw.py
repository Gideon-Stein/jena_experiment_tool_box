import argparse
import pickle
import os
import pandas as pd
from tools import get_all_paths,load_year, log, test_columns, test_length,test_year,test_duplicates


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', default= "classic", type=str )    # keep. option to plugin additional selection if necessary-
    parser.add_argument('--start_year', default= 2003, type=int )   
    parser.add_argument('--end_year', default= 2021, type=int )   
    parser.add_argument('--output_path', default= "/home/datasets4/stein/jena_experiment_data_various_products/", type=str )    
    parser.add_argument('--input_path', default= "/home/datasets4/stein/jena_experiment_data_various_products/jena_experiment/raw", type=str )   
    parser.add_argument('--columns_path', default= "stats/header_file.csv", type=str )   

 
    args = parser.parse_args()

    print("Loading general files")
    # All paths, [0] split into years, [1] joint
    tables,tables_list, years = get_all_paths(args.input_path, return_years=True)
    print(tables)
    allColumns = list(pd.read_csv(args.columns_path,
     encoding= 'unicode_escape').columns)[:-1]

    #skip ealier years if needed
    try:
        start = years.index(args.start_year)
    except: 
        start = 0
    try:
        end = years.index(args.end_year)
    except: 
        end = len(years)
    print(years)
    tables = tables[start:end+1]
    years = years[start:end+1]
    print("Number of remaining years: " + str(len(tables)) )

    # Get years and faulty columns
    faultyMap  = pickle.load(open("stats/faulty_column_mapping.p", "rb"))

    # This is the procedure:
    for count, table in enumerate(tables):
        print("Begin with " + str(years[count]))
        try:
            name = "transform_logs/" + str(years[count])
            # Load year table
            data = load_year(table, faultyMap,allColumns,name= name)
            # Testing
            log("Running some additional tests", name= name)
            if isinstance(data, pd.DataFrame):
                if not test_columns(data,allColumns):
                    log("Column test failed.", name= name)
                    assert False, "Column test failed."
                if not test_length(data):
                    log("Length test failed.", name= name)
                    assert False, "Length test failed."
                if not test_year(data):
                    log("Year test failed.", name= name)
                    assert False, "Year test failed."
                if not test_duplicates(data):
                    log("Duplicate test failed.", name= name)
                    assert False, "Duplicate test failed."
                log("All tests passed.", name= name)
            else: 
                log("Loading returned no Data. Error or consistency failed", name= name)
                return None

            if args.mode == "additional":
                log("NOT IMPLEMENTED YET", name= name)
                return None
            elif args.mode == "classic":
                # Only Take what is needed for the dataset and what was filtered
                data = data[["t[s]"] + [x for x in allColumns if (("soil_temp" in x) or
                 ("air" in x) or ("surface" in x))]]
            else:
                print("Unknown saving type.")
                return None

            #save
            CHECK_FOLDER = os.path.isdir(args.output_path + "/transformed_years/" + args.mode)
            if not CHECK_FOLDER:
                os.makedirs(args.output_path + "/transformed_years/" + args.mode)
                print("created folder : ", args.output_path + "/transformed_years/" + args.mode)
            data.to_csv(args.output_path + "/transformed_years/" + args.mode + "/" + args.mode + "_"  + str(years[count]) + ".csv",index=False )

        except Exception as e:
            print(str(years[count]) + " failed. Reason:")
            print(e)   
if __name__ == '__main__':
    main()

