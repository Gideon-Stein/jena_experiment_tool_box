import pandas as pd
from functools import reduce
import numpy as np

def load_management(p,p2,window_filter=7):

    d = pd.read_csv(p)
    d2 = pd.read_csv(p2)
    d = pd.concat([d2,d],axis=0)
    d["start date"]  = pd.to_datetime(d["start date"])
    d["end date"]  = pd.to_datetime(d["end date"])
    # keep relevant categories
    d = d[d["category"].isin(['weeding', 'mowing', 'biomass harvest'])]
    d = d[d["experiment"].isin(['main experiment'])]
    # remove end dates that are further than 14 days later: 
    cond = (d.loc[:,"end date"] - d.loc[:,"start date"]).dt.days > window_filter
    d.loc[cond, "end date"] = (d.loc[cond,"start date"] + pd.Timedelta(days=window_filter)).values
    return d

def rejoin_intervals(d, window_filter = 7):
    #reunite periods that are very close together (1 week for now)
    overlap = d[(d["start"] - d["end"].shift(1)).dt.days < window_filter].index
    for x in overlap: 
        d.loc[x-1,"end"] = d.loc[x,"end"]
    d.drop(index = overlap, inplace=True)
    d.reset_index(inplace=True, drop = True)
    return d


def format_management(d, cat= "biomass harvest", verbose=0):
    stack = []
    for x in np.arange(2002,2021):
        subset = d[d["start date"].dt.year == x]
        subset = subset[subset["category"] == cat]
        subset = subset[subset["experiment"] == "main experiment"]
        if cat != "weeding":
            subset = subset[subset["exception"].isnull()]
        if len(subset) == 0: 
            if verbose == 1:
                print("Nothing in " + str(x))
        elif len(subset) <= 4: 
            start = subset["start date"].values.min()
            end = subset["end date"].values.max()
            if verbose == 1:
                print((end - start) / 86400000000000)
            stack.append([start, end])

        else: 
            months = subset["start date"].dt.month.unique()
            for m in months: 
                m_subset = subset[subset["start date"].dt.month == m]
                start = m_subset["start date"].values.min()
                end = m_subset["end date"].values.max()
                if verbose == 1:
                    print((end - start) / 86400000000000)
                stack.append([start, end])
    harvest = pd.DataFrame(stack, columns = ["start", "end"])
    harvest.sort_values("start", inplace=True)
    return harvest

def format_biomass(biomass):
    # For now lets not rely on the individual biomass of plants.
    #reformat the table into, select target, weeds, and dead seperately and jointly
    stack = []
    for x in ["Target", "Weeds", "Dead"]:
        for y in ["May", "Aug", "annual"]:
            if y == "annual":
                cond = (biomass.loc[:,"subsample"] == y)
            else: 
                cond = (biomass.loc[:,"subsample"] == "mean")
            a = biomass.loc[cond &
                            (biomass.loc[:,"species_other"] == x) &
                            (biomass.loc[:,"season"] == y),biomass.columns]
            a.loc[:,x + "_" + y] = a.loc[:,["biomass"]].values
            a.drop(columns= ["species_other", "biomass", "subsample", "season"], inplace = True)
            stack.append(a)
    df_merged = reduce(lambda  left,right: pd.merge(left,right,on=["plotcode", "year"],
                                            how='outer'), stack)
    # If some values is missing we need to skip them because the sum is not accurate
    for y in ["May", "Aug", "annual"]:
        df_merged["Total_" + y] = df_merged[[
            x for x in df_merged.columns if y in x]].sum(axis=1, skipna=False)
    return df_merged.sort_values(["year", "plotcode"]).reset_index(drop=True)


def format_height(height):
    # Similar idea like biomass processing
    stack = []
    for y in ["May", "August", "September"]:
        a = height.loc[(height.loc[:,"subsample"] == "mean") &
                        (height.loc[:,"season"] == y),height.columns]
        
        a.loc[:,"target_leaf_" + y] = a.loc[:,["height_target_leaf"]].values
        a.loc[:,"target_flower_" + y] = a.loc[:,["height_target_flower"]].values

        a.drop(columns= ["height_target_leaf","height_target_flower", "subsample", "season"], inplace = True)
        stack.append(a)
    df_merged = reduce(lambda  left,right: pd.merge(left,right,on=["plotcode", "year"],
                                            how='outer'), stack)
    return df_merged.sort_values(["year", "plotcode"]).reset_index(drop=True)

def format_lai(lai):
    # Similar idea like biomass processing
    # ignore the few September samples
    stack = []
    for y in ["May", "August"]:
        a = lai.loc[(lai.loc[:,"season"] == y),lai.columns]
        
        a.loc[:,"LAI_" + y] = a.loc[:,["LAI"]].values
        a.loc[:,"LAI_" + y] = a.loc[:,["LAI"]].values
        a.drop(columns= ["LAI", "repNr", "season"], inplace = True)
        stack.append(a)
    df_merged = reduce(lambda  left,right: pd.merge(left,right,on=["plotcode", "year"],
                                            how='outer'), stack)
    return df_merged.sort_values(["year", "plotcode"]).reset_index(drop=True)


def format_microb(microb):
    # Similar idea like biomass processing
    # there are some duplicate lines with wildy different values....
    # Guess we just drop one.

    microb[microb == -9999] = np.nan
    microb.rename(columns= {"plot": "plotcode"}, inplace = True)
    #reordering
    microb = microb[["plotcode", "year"] + [
        "basal_respiration","soil_microbial_biomass_C",
            	"respiratory_quotient",	"soil_water_content"]]

    return microb.sort_values(["year", "plotcode"]).drop_duplicates(["plotcode", "year"]).reset_index(drop=True)

def format_roots(roots):
    # couple of insights: 
    # - September only measured in 2004. removed.
    # - I added up the seperated measurements from post 2006 to make a consistent ts (0-30 cm)
    # - 30-40 is dropped because not present in many years.
    # - The split between fine and coarse is dropped since half empty.
    # - I am also adding the depth steps as additional variables. 

    #remove sep and too deep values
    roots = roots.loc[roots.loc[:,"month"] != 9]
    roots = roots.loc[(roots.loc[:,"depth.min"] != 0.3) &
                       (roots.loc[:,"depth.max"] != 0.4)]
    roots.drop(columns = ["Unnamed: 0", "month", "coarse_root.bm","fine_root.bm"], inplace = True)

    stack = []
    for x in [[0,0.05,5],[0.05,0.10,10],[0.10,0.20,10],[0.20,0.30,10]]:
        a = roots.loc[(roots.loc[:,"depth.min"] == x[0]) & (roots.loc[:,"depth.max"] == x[1]), :].copy()
        a["root.bm"]=  a["root.bm"] / x[2]
        a.rename(columns = {"root.bm": "root_bm_"+ str(x[0]) + "_" + str(x[1])}, inplace = True)
        a.drop(columns = ["depth.min","depth.max"], inplace = True) 
        stack.append(a)

    roots = roots.groupby(["year", "plot"]).sum().reset_index()
    roots.rename(columns = {"root.bm": "root_bm_0_0.30"}, inplace = True)
    roots.drop(columns = ["depth.min","depth.max"], inplace = True) 

    stack.append(roots)

    final_df = reduce(lambda  left,right: pd.merge(left,right,on=["year", "plot"]
    ,how='outer'), stack)

    final_df.rename(columns={"plot": "plotcode"}, inplace=True)
    
    return final_df

def format_cover(cover):
    # couple of insights: 
    # - Number state in how much & of the total area the specices is present.
    # - Lets keep individual plants out. 
    # - But we can calculate the realized diversity from this! 
    # - Sr weed is the reao8ed species including weed? 
    #  /plot so I keep it out for now


    stack = []
    # Amount of present/frequent species each year.
    for threshold in [["realized_species_", 0], ["abundant_species_",9]]:
        present = cover.loc[(cover["cover"] > threshold[1]) & (cover["group"] == "Target")]
        present = present.groupby(["year", "season", "plotcode"]).count()["cover"].reset_index()
        for x in present["season"].unique():
            a = present.loc[(present.loc[:,"season"] == x),present.columns]
            a.loc[:,threshold[0] + x] = a.loc[:,["cover"]].values
            a.drop(columns= ["cover", "season"], inplace = True)
            stack.append(a)


    rel_cover = cover.loc[(cover.loc[:,"group"] == "Plot.level"), cover.columns]
    rel_cover.drop(columns = ["group", "SRweed"], inplace = True)
    for y in rel_cover["species_other"].unique():
        for x in rel_cover["season"].unique():

            a = rel_cover.loc[(rel_cover.loc[:,"species_other"] == y) &
                            (rel_cover.loc[:,"season"] == x),rel_cover.columns]
            a.loc[:,"cover_" + x + "_" + y] = a.loc[:,["cover"]].values
            a.drop(columns= ["cover", "species_other", "season"], inplace = True)
            stack.append(a)
    df_merged = reduce(lambda  left,right: pd.merge(left,right,on=["plotcode", "year"],
                                            how='outer'), stack)

    return df_merged.sort_values(["year", "plotcode"]).reset_index(drop=True)