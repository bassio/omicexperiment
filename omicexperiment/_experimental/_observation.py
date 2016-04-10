import pandas as pd
from omicexperiment.filters.observation import ObservationMinCount, ObservationMinCountFraction, ObservationMinSamples, ObservationMaxCount, ObservationSumCounts

__all__ = ['Observation']

class Observation(object):
    def __init__(self, experiment):
        self.experiment = experiment
    
    class filters(object):
        min_count = ObservationMinCount()
        min_count_fraction = ObservationMinCountFraction()
        min_samples = ObservationMinSamples()
        max_count = ObservationMaxCount()
        
        sum_counts = ObservationSumCounts()
    
    @property
    def list(self):
        return list(self.experiment.data_df.index)
    
    def top_count(self, n):
        top_n_obs = self.experiment.data_df.sum(axis=1).sort_values(ascending=False).head(n).index
        return [o for o in top_n_obs]
    
    def top_rel_abund(self, n):
        rel_abund_df = self.experiment.data_df.apply(lambda c: c / c.sum() * 100, axis=0)
        top_n_obs = rel_abund_df.mean(axis=1).sort_values(ascending=False).head(n).index
        return [o for o in top_n_obs]
    
    def bottom_count(self, n):
        top_n_obs = self.experiment.data_df.sum(axis=1).sort_values(ascending=False).tail(n).index
        return [o for o in top_n_obs]
    
    def bottom_rel_abund(self, n):
        rel_abund_df = self.experiment.data_df.apply(lambda c: c / c.sum() * 100, axis=0)
        top_n_obs = rel_abund_df.mean(axis=1).sort_values(ascending=False).tail(n).index
        return [o for o in top_n_obs]
    