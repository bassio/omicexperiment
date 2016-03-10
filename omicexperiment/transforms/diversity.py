import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, cdist, squareform
from omicexperiment.transforms.transform import Transform


class BetaDiversity(Transform):
    def __init__(self, distance_metric):
        self.distance_metric = distance_metric
        
    def apply_transform(self, experiment):
        df = experiment.data_df.transpose()
        dm = cdist(df, df, self.distance_metric)
        distance_matrix_df = pd.DataFrame(dm, index=df.index, columns=df.index)
        return experiment.with_data_df(distance_matrix_df)
    
    