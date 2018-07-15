import pandas as pd
from omicexperiment.transforms.transform import TransformObjectsProxy, Transform, Filter
from omicexperiment.transforms.observation import ObservationSumCounts

class ObservationMinCount(Filter):
    def __dapply__(self, experiment):
        if self.operator == '__eq__':
            assert isinstance(self.value, int)
            df = experiment.data_df
            return df[df.sum(axis=1) >= self.value]
            
class ObservationMinCountFraction(Filter):
    def __dapply__(self, experiment):
        if self.operator == '__eq__':
            assert isinstance(self.value, float)
            assert self.value <= 1
            df = experiment.data_df
            obs_fractions = df.sum(axis=1) / (df.sum(axis=1).sum())
            return df[obs_fractions >= self.value]

class ObservationMaxCount(Filter):
    def __dapply__(self, experiment):
        if self.operator == '__eq__':
            assert isinstance(self.value, int)
            df = experiment.data_df
            return df[df.sum(axis=1) <= self.value]

class ObservationMinSamples(Filter):
    def __dapply__(self, experiment):
        if self.operator == '__eq__':
            assert isinstance(self.value, int)
            df = experiment.data_df
            absence_presence = (df > 0)
            return df[absence_presence.sum(axis=1) >= self.value]


class Observation(TransformObjectsProxy):
    min_count = ObservationMinCount()
    min_count_fraction = ObservationMinCountFraction()
    max_count = ObservationMaxCount()
    min_samples = ObservationMinSamples()
    
    sum_counts = ObservationSumCounts()

