import pandas as pd
from omicexperiment.filters.filters import FilterExpression

class ObservationMinCount(FilterExpression):
    def return_value(self, experiment):
        if self.operator == '__eq__':
            assert isinstance(self.value, int)
            df = experiment.data_df
            return df[df.sum(axis=1) >= self.value]
            
class ObservationMinCountFraction(FilterExpression):
    def return_value(self, experiment):
        if self.operator == '__eq__':
            assert isinstance(self.value, float)
            assert self.value <= 1
            df = experiment.data_df
            obs_fractions = df.sum(axis=1) / (df.sum(axis=1).sum())
            return df[obs_fractions >= self.value]

class ObservationMaxCount(FilterExpression):
    def return_value(self, experiment):
        if self.operator == '__eq__':
            assert isinstance(self.value, int)
            df = experiment.data_df
            return df[df.sum(axis=1) <= self.value]

class ObservationMinSamples(FilterExpression):
    def return_value(self, experiment):
        if self.operator == '__eq__':
            assert isinstance(self.value, int)
            df = experiment.data_df
            absence_presence = (df > 0)
            return df[absence_presence.sum(axis=1) >= self.value]

            
class ObservationSumCounts(FilterExpression):
    def return_value(self, experiment):
        return experiment.data_df.sum(axis=1)


class Observation(object):
    min_count = ObservationMinCount()
    min_count_fraction = ObservationMinCountFraction()
    min_samples = ObservationMinSamples()
    max_count = ObservationMaxCount()
    
    sum_counts = ObservationSumCounts()

