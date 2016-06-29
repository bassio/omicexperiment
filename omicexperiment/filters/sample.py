import pandas as pd
from omicexperiment.transforms.transform import Filter, AttributeFilter, GroupByTransform, FlexibleOperatorMixin, AttributeFlexibleOperatorMixin
from omicexperiment.transforms.sample import SampleGroupBy


class SampleMinCount(Filter):
    def __dapply__(self, experiment):
        if self.operator == '__eq__':
            assert isinstance(self.value, int)
            df = experiment.data_df
            criteria = (df.sum() >= self.value)
            return df[criteria.index[criteria]]


class SampleMaxCount(Filter):
    def __dapply__(self, experiment):
        if self.operator == '__eq__':
            assert isinstance(self.value, int)
            df = experiment.data_df
            criteria = (df.sum() <= self.value)
            return df[criteria.index[criteria]]


class SampleCount(Filter, FlexibleOperatorMixin):
    def __dapply__(self, experiment):
        _op = self._op_function(experiment.data_df.sum())
        criteria = _op(self.value)
        criteria = _op(self.value)
        return experiment.data_df.reindex(columns=criteria.index[criteria])
       
class SampleAttributeFilter(AttributeFilter, AttributeFlexibleOperatorMixin):
    def __dapply__(self, experiment):
        _op = self._op_function(experiment.mapping_df)
        criteria = _op(self.value)
        return experiment.data_df.reindex(columns=criteria.index[criteria])
        

class SampleSumCounts(Filter):
    def __dapply__(self, experiment):
        return experiment.data_df.sum()
    

class Sample(object):
    #not_in = 
    #in_
    count = SampleCount()
    #min_count = SampleMinCount() #?TO DEPRECATE
    #max_count = SampleMaxCount() #?TO DEPRECATE
    
    att = SampleAttributeFilter()
    c = SampleAttributeFilter()
    
    groupby = SampleGroupBy
    
    sum_counts = SampleSumCounts()
    