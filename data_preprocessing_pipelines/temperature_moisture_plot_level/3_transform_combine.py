import argparse
from os import listdir
import pandas as pd
from os.path import isfile, join

# combines single years in long format

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', default= "/home/datasets4/stein/jena_experiment_data_various_products/sum_years", type=str )   
    parser.add_argument('--name', default= "complete", type=str )   

    args = parser.parse_args()

    # Get all available years
    files = [args.data_path + "/" + args.name + "/" + f for f in
        listdir(args.data_path+ "/" + args.name) if isfile(join(args.data_path + "/" + args.name, f))]
    files = [x for x in files if "removed" not in x]
    files.sort()


    print(files)

    #sum
    data = pd.concat([pd.read_csv(x) for x in files])




    
    data.to_csv(args.data_path + "/" +  args.name +   "_all.csv",index=False)
    print("Done")
if __name__ == '__main__':
    main()