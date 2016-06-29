import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, cdist, squareform
from skbio.diversity import alpha 

from omicexperiment.transforms.transform import Transform
from omicexperiment.transforms.general import RarefactionFunction

'''
class AlphaDiversity(Transform):
    def __init__(self, metric):
        if isinstance(metric, str):
            self.metric = getattr(alpha, metric)
        else:
            self.metric = metric
        
    def apply_transform(self, experiment):
        rf = RarefactionFunction(n=250, num_reps=10, func=self.metric, axis=0, agg_rep=np.mean)
        new_exp = rf.apply_transform(exp)

        shannon = new_exp.data_df.transpose()[250]
        shannon.name = 'shannon'
        shannon_df = new_exp.mapping_df.join(shannon, how='inner')
'''

class BetaDiversity(Transform):
    def __init__(self, distance_metric):
        self.distance_metric = distance_metric
        
    def apply_transform(self, experiment):
        df = experiment.data_df.transpose()
        dm = cdist(df, df, self.distance_metric)
        distance_matrix_df = pd.DataFrame(dm, index=df.index, columns=df.index)
        return experiment.with_data_df(distance_matrix_df)
    

def filter_distance_matrix(experiment, grouping_col, group_1, group_2):
    grouping_series = experiment.mapping_df[grouping_col]
    
    group_1_samples = experiment.mapping_df[grouping_series==group_1].index
    group_2_samples = experiment.mapping_df[grouping_series==group_2].index
    
    dm = experiment.data_df.reindex(index=group_1_samples, columns=group_2_samples)
    
    return dm


def distances(experiment, grouping_col, group_1, group_2):
    dm = filter_distance_matrix(experiment, grouping_col, group_1, group_2)
    try:
        return squareform(dm)
    except ValueError: #assymetric DM
        if group_1 != group_2:
            return dm.as_matrix().flatten()
        else:
            raise