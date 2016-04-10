import numpy as np
import pandas as pd

def rarefy(series, n):
    series_sum = series.sum()
    rel_abundance = series.apply(lambda c: c / series_sum)
    sampled = np.random.choice(rel_abundance.index, n, p=rel_abundance)
    sampled_series = pd.Series(sampled, name=series.name)
    return sampled_series.value_counts()


def rarefy_dataframe(dataframe, n):
    
    rarefied_all = []
    
    for col in dataframe:
        rarefied_series = rarefy(dataframe[col], n)
        rarefied_all.append(rarefied_series)
    
    return pd.concat(rarefied_all,axis=1).fillna(0)
    
