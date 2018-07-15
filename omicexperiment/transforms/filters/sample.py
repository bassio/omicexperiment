import pandas as pd
from omicexperiment.transforms.transform import Filter, AttributeFilter, GroupByTransform, FlexibleOperatorMixin, AttributeFlexibleOperatorMixin, TransformObjectsProxy
from omicexperiment.transforms.sample import SampleGroupBy, SampleSumCounts


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


class SampleCount(FlexibleOperatorMixin, Filter):
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
        

class Sample(TransformObjectsProxy):
    #not_in = 
    #in_
    count = SampleCount()
    
    att = SampleAttributeFilter()
    c = SampleAttributeFilter()
    
    groupby = SampleGroupBy()
    
    sum_counts = SampleSumCounts()
    
