import copy
from re import A
import time
from collections import Counter
from datetime import datetime, timedelta
from os import listdir
from os.path import isdir, isfile, join
import numpy as np
import pandas as pd


# Tools used throughout the transform scripts

def test_columns(data,allColumns): 
    a = list(data.columns)
    a.sort()
    b = copy.deepcopy(allColumns)
    b.sort()
    return a == b 
    
def test_length(data):
    # Amounts of minutes in a year /leap year
    if len(data) == 525600 or len(data) == 527040: 
        return True
    else: 
        return False

def log(message,name, console=True):
    out = open(name, 'a')
    out.write(message)
    out.write("\n")
    if console: 
        print(message)
    out.close()

def test_year(data):
    return np.all(data["t[s]"].dt.year[0] == data["t[s]"].dt.year)

def test_duplicates(data):
    return len(set(data["t[s]"].values)) == len(data)
    
def test_nan(earlier, data, duplicates):
    # cut away time and compare
    a = earlier[1:]
    b = (~data.isnull()).sum()[1:]
    add = duplicates[1:]
    if len(a.compare(b + add)) == 0:
        return  True
    else:
        return False

def control_time_duplicates(data, detailed = False): 
    time_multis = data.loc[data.duplicated(subset="t[s]")]
    column_effects= (~(time_multis.isnull())).sum()
    return column_effects, time_multis

def check_out_of_year_time(data):
    out_of_year = data.loc[(data["t[s]"].dt.year != data["t[s]"].dt.year.mode().values[0])]
    if len(out_of_year) == 0:
        return False
    else:
        return (~(out_of_year.isnull())).sum()

def count_duplicates_and_out_of_year(data):
    time_multis = data.duplicated(subset="t[s]")
    check_out_of_year = (data["t[s]"].dt.year != data["t[s]"].dt.year.mode().values[0])
    count = data.loc[time_multis | check_out_of_year]
    count = (~(count.isnull())).sum()
    return count, time_multis, sum(check_out_of_year)

def load_year(paths, faultyMap,allColumns, debug = False, name="test.txt", time_spread = True): 
    data  = []
    start_time = time.time()
    faulty_counter = 0
    for x in paths: 
        try: 
            # load 
            new  = pd.read_csv(x, encoding= 'unicode_escape')
            # transform time to datetime
            new["t[s]"] = pd.to_datetime(new["t[s]"],dayfirst=True)
            # check if the name and the first date are close together
            nameTime  = transform_name(x.split("/")[-1])
            diff = np.abs((nameTime - new["t[s]"][0]).total_seconds())
            # if not: rebuild time based on file name
            if diff > 86400:
                faulty_counter += 1
                log("Faulty Time column detected." + x  + " Reworking it",name)
                new["t[s]"] = pd.date_range(nameTime,nameTime+timedelta(minutes=len(new)-1), freq='min')
            data.append(new)
        except: 
            log("Broken load: " + x,name)
            faulty_counter += 1
            pass
    log("load all tables --- %s seconds ---" % (time.time() - start_time),name)
    log("Broken tables and faulty table times detected: " + str(faulty_counter) + " from " + str(len(paths)),name)


    # join all tables
    data = pd.concat(data)
    data.reset_index(inplace=True, drop = True)
    log("join all tables --- %s seconds ---" % (time.time() - start_time),name)

    # drop Unamed columns
    data = data.drop(columns=([x for x in data.columns if "Unnamed:" in x]))
    log("drop Unamed columns --- %s seconds ---" % (time.time() - start_time),name)

    # round to minutes
    data["t[s]"] = data["t[s]"].dt.floor('min') 
    log("round to minutes --- %s seconds ---" % (time.time() - start_time),name)

    # check if there are wrong columns. If yes rename them according to name Mapping
    faults = [x for x in data.columns if x in faultyMap.keys()]
    log("Wrong columns found: " + str(faults ),name)
    log("Attempt to correct with: " + str([faultyMap[x] for x in faults]),name)
    for x in faults: 
        if faultyMap[x] not in data.keys(): 
            data.rename(columns= {x: faultyMap[x]}, inplace=True)  
        else: 
            doubles = sum(~np.isnan(data[faultyMap[x]]) & ~np.isnan(data[x]))
            before = sum(np.isnan(data[faultyMap[x]]))
            data.loc[np.isnan(data[faultyMap[x]]),faultyMap[x]] = data.loc[np.isnan(data[faultyMap[x]]),x]
            after =  sum(np.isnan(data[faultyMap[x]]))
            data.drop(columns =x, inplace=True)
            log("Columns were merged. (val duplicates, nan before, nan after): (" + str((doubles,before,after)) + ")",name)
    log("map wrong columns --- %s seconds ---" % (time.time() - start_time),name)

    # If some columns are missing after correction completely add them in: 
    missingCols = [x for x in allColumns if x not in data.columns]
    log("Missing columns: " + str(missingCols),name)
    for col in missingCols: 
        data[col] = np.nan
    log("add missing columns --- %s seconds ---" % (time.time() - start_time),name)

    # Sort the columns consistently: 
    if len([x for x in data.columns if x not in allColumns]) == 0: 
        data = data[allColumns]
    else:
        log("Unknown columns detected: " + str([x for x in data.columns if x not in allColumns]),name)
        return None

    #save for final test that checks that the amount of data is the same after merch
    compareLater = (~data.isnull()).sum()
    remove, time_multis, aof = count_duplicates_and_out_of_year(data)
    log("Time uplicated dates: " + str(sum(time_multis)),name)
    log(str(data["t[s]"].value_counts().sort_values(ascending=False)),name)
    log("Out of year dates: " + str(aof),name)

    if time_spread:
        # spread the table to include all timesteps
        year = data.loc[int(len(data)/2), "t[s]"].year
        start = pd.Timestamp('01.01.' + str(year) + ' 00:00:00')
        end = pd.Timestamp('31.12.' + str(year) + ' 23:59:00')
        spread = pd.DataFrame(pd.date_range(start, end, freq='min'), columns=["t[s]"])
        data = spread.merge(data, how="left", on= "t[s]")
        log("spread table to full timeSeries.  --- %s seconds ---" % (time.time() - start_time),name)

        # Remove duplicates
        data.drop_duplicates(subset = "t[s]", inplace =True)
        data.reset_index(inplace=True, drop = True)
        log("remove duplicates --- %s seconds ---" % (time.time() - start_time),name)

    # Test for data consistency:
    if debug: 
        return (compareLater,data, remove, sum(time_multis), aof)
    else:
        if test_nan(compareLater,data, remove):
            log("Consistency test passed",name)
            return data
        else:
            log("Consistency test failed!",name)
            return None

def transform_name(name):
    t = name[2:-4]
    date = pd.Timestamp(int(t[:4]), 1, 1,int(t[7:9]), int(t[9:11])) + timedelta(int(t[4:7]) - 1)
    return date

def get_all_paths(path2 ="/home/datasets4/stein/jena_experiment/raw", return_years = False): # asumes year/range/files
    years = sorted(listdir(path2))
    split = []
    for x in years: 
        split.append(sorted([f for f in listdir(path2 + "/" + x) if isdir(join(path2 + "/" + x, f))]))
    tables = []
    for x in range(len(years)):
        current_year = []
        for y in split[x]: 
            current_year.append(sorted([path2 + "/" + years[x] + "/" + y + "/" + f for f in listdir(path2 + "/" + years[x] + "/" + y) if isfile(join(path2 + "/" + years[x] + "/" + y, f))]))
        tables.append([item for sublist in current_year for item in sublist])
    tables_list = [item for sublist in tables for item in sublist]
    if not return_years:
        return tables,tables_list
    else:
        return tables,tables_list, [int(x) for x in years]


def threshold_filter(ts,removals, which="soil_temp", threshold = (-30,45)) :
    cols = [x for x in ts.columns if which in x]
    for x in cols: 
        condition = ((( ts[x]<= threshold[1] ) & (ts[x] >= threshold[0])) | np.isnan(ts[x]))
        removals.loc[~condition, x] = ts.loc[~condition,x]
        removals.loc[~condition, x + "_removed"] = "Threshold filter"
        ts.loc[~condition,x] = np.nan
    return ts, removals

def time_sum(ts, sum_minutes= 30):
    out = pd.DataFrame(columns=ts.columns)
    new = ts.values.reshape((-1,sum_minutes,len(ts.columns)))
    time = new[:,0,0]
    data = np.nanmean(new[:,:,1:].astype("float64"),axis=1)
    out = pd.DataFrame(time, columns=["t[s]"])
    out = pd.concat([out,pd.DataFrame(data)], axis = 1)
    out.columns = ts.columns
    return out

# depcrcated
def sum_30_min(df):
    split = df["datetime"].dt.minute >= 30
    df.loc[split, "datetime"] = df.loc[split, "datetime"].dt.floor(freq= "H") + pd.DateOffset(minutes=30)
    df.loc[~split, "datetime"] = df.loc[~split, "datetime"].dt.floor(freq= "H")
    df = df.groupby(["datetime", "plotcode"]).mean()
    df.reset_index(inplace = True)
    return df

# depcrcated
def sum_mins(df, resolution, plots = True):
    df["datetime"] = pd.to_datetime(df.loc[:,"datetime"]).dt.floor(
        freq= str(resolution) + "min")
    if plots:
        df = df.groupby(["datetime", "plotcode"]).mean()
    else:
        df = df.groupby(["datetime"]).mean()
    df.reset_index(inplace = True)
    return df

def cast_to_long_format(data):
    variables = list(set(["_".join(x.split("_")[:-1]) for x in data.columns[1:]]))
    out = []
    for variable in variables: 
        subtable = pd.DataFrame(data[[x for x in data.columns if variable in x]].stack(dropna=False))
        subtable.reset_index(inplace = True)
        # cut the unit correctly
        if "air_rel" in variable:
            subtable["level_1"] = [x.split("_")[-1][:-4] for x in subtable["level_1"]]
        else:
            subtable["level_1"] = [x.split("_")[-1][:-5] for x in subtable["level_1"]]

        subtable.rename(columns={"level_1": "plotcode", 0: variable}, inplace=True)
        if len(out) == 0: 
            out = subtable
        else:
            out = out.merge(subtable, how ="outer", on=["plotcode", "level_0"] )
    out = out.merge(data["t[s]"], left_on ="level_0", right_index= True)
    out.rename(columns={"t[s]": "datetime"}, inplace = True)
    out.drop(columns=["level_0"],inplace = True)
    out = out[["datetime", "plotcode"] +  variables]
    out["datetime"] = pd.to_datetime(out["datetime"])
    return out

def select_variable_subset(data, mode="complete"):
    if mode == "complete":
        selection =  []
        a = ["_".join(x.split("_")[:-1]) for x in data.columns]
        for x in set(a):
            if a.count(x) == 90 :
                selection.append(x)
        print(selection)
    elif mode == "block2":
        selection = [x for x in data.columns if "_2A" in x ]
    else:
        return None
    return data.loc[:,["t[s]"] + [x for x in data if any(sel in x for sel in selection)]]

def boxplot_filter(data, removed, acceptRange=1.5, nPlots=90):
    variables = [x for x in data.columns if ((x != "datetime") & (x != "plotcode"))]

    for var in variables: 
        # Calculate limits for removing
        Q1 = data[["datetime",var]].groupby('datetime').quantile(0.25)
        Q3 = data[["datetime",var]].groupby('datetime').quantile(0.75)
        mean = data[["datetime",var]].groupby('datetime').mean()
        iqr = Q3 - Q1
        outlier_step = acceptRange * iqr  
        mini = np.tile(Q1 - outlier_step,nPlots).flatten()
        maxi = np.tile(Q3 + outlier_step,nPlots).flatten()
        mean = np.tile(mean,nPlots).flatten()
        # Get condition for removing
        # Hacky way to take out values were only one plot exists
        sel1 = (mean == data[var])
        sel2 = (mini > data[var])
        sel3 = (maxi < data[var])
        # log everything
        removed.loc[sel1,var] = data.loc[sel1, var]
        removed.loc[sel2,var] = data.loc[sel2, var]
        removed.loc[sel3,var] = data.loc[sel3, var]
        removed.loc[sel1,var + "_removed"] = "Single TS"
        removed.loc[sel2,var + "_removed"] = "Under acceptance range"
        removed.loc[sel3,var + "_removed"] = "Over acceptance range"
        data.loc[sel1, var] = np.nan
        data.loc[sel2, var] = np.nan
        data.loc[sel3, var] = np.nan
    return data, removed

def fill_with_mean(data, plots=True):
    original_time = data["datetime"].values
    #remove the year
    data["datetime"] = data["datetime"].astype("str").str.slice(start=5)
    if plots:
        cols = data.columns[2:]
        means = data.groupby(["datetime", "plotcode"]).mean().reset_index()
        for x in cols: 
            means.rename(columns={x: x + "_mean"}, inplace=True)
        data = data.merge(means, how= "left", on= ["datetime", "plotcode"])
    else:
        cols = data.columns[1:]
        means = data.groupby(["datetime"]).mean().reset_index()
        for x in cols: 
            means.rename(columns={x: x + "_mean"}, inplace=True)
        data = data.merge(means, how= "left", on= ["datetime"])
    for x in cols: 
        print(x)
        missing = data[x].isnull()
        data.loc[missing, x] = data.loc[missing, x + "_mean"]
        data.drop(columns=[x + "_mean"], inplace=True)
    data["datetime"] = original_time
    return data

def test_filling(data1,data2, threshold = 1.4210854715202004e-10):
    diff = np.nanmax(data1.loc[:,data1.columns[2:]]  - data2.loc[:,data2.columns[2:]])
    return diff < threshold