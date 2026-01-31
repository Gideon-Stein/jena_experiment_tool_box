import numpy as np
import pandas as pd



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


def sum_mins(df, resolution, plots = True):
    df["datetime"] = pd.to_datetime(df.loc[:,"datetime"]).dt.floor(
        freq= str(resolution) + "min")
    if plots:
        df = df.groupby(["datetime", "plotcode"]).mean()
    else:
        df = df.groupby(["datetime"]).mean()
    df.reset_index(inplace = True)
    return df

def log(message,name, console=True):
    out = open(name, 'a')
    out.write(message)
    out.write("\n")
    if console: 
        print(message)
    out.close()
    
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






