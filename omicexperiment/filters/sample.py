import pandas as pd
from omicexperiment.filters.filters import FilterExpression, AttributeFilter, GroupByFilter, FlexibleOperatorMixin, AttributeFlexibleOperatorMixin


class SampleMinCount(FilterExpression):
    def return_value(self, experiment):
        if self.operator == '__eq__':
            assert isinstance(self.value, int)
            df = experiment.data_df
            criteria = (df.sum() >= self.value)
            return df[criteria.index[criteria]]


class SampleMaxCount(FilterExpression):
    def return_value(self, experiment):
        if self.operator == '__eq__':
            assert isinstance(self.value, int)
            df = experiment.data_df
            criteria = (df.sum() <= self.value)
            return df[criteria.index[criteria]]


class SampleCount(FilterExpression, FlexibleOperatorMixin):
    def return_value(self, experiment):
        _op = self._op_function(experiment.data_df.sum())
        criteria = _op(self.value)
        criteria = _op(self.value)
        return experiment.data_df.reindex(columns=criteria.index[criteria])
       
class SampleAttributeFilter(AttributeFilter, AttributeFlexibleOperatorMixin):
    def return_value(self, experiment):
        _op = self._op_function(experiment.mapping_df)
        criteria = _op(self.value)
        return experiment.data_df.reindex(columns=criteria.index[criteria])
        

class SampleGroupBy(GroupByFilter):
    def return_value(self, experiment):
        if self.operator == 'groupby':
            if self.value is not None:
                mapping_df = experiment.mapping_df.copy()
                transposed = experiment.to_relative_abundance().data_df.transpose()
                joined_df = transposed.join(mapping_df[[self.value]])
                means_df = joined_df.groupby(self.value).mean()
                retransposed = means_df.transpose()
            else:
                retransposed = experiment.data_df.copy()
            
            return retransposed
            

class SampleGroupBySum(GroupByFilter):
    def return_value(self, experiment):
        if self.operator == 'groupby':
            if self.value is not None:
                mapping_df = experiment.mapping_df.copy()
                transposed = experiment.data_df.transpose()
                joined_df = transposed.join(mapping_df[[self.value]])
                means_df = joined_df.groupby(self.value).sum()
                retransposed = means_df.transpose()
                return retransposed
            else:
                return experiment.data_df.copy()


class SampleSumCounts(FilterExpression):
    def return_value(self, experiment):
        return experiment.data_df.sum()
    

class Sample(object):
    #not_in = 
    #in_
    count = SampleCount()
    #min_count = SampleMinCount() #?TO DEPRECATE
    #max_count = SampleMaxCount() #?TO DEPRECATE
    
    att = SampleAttributeFilter()
    c = SampleAttributeFilter()
    
    groupby = SampleGroupBy()
    groupby_sum = SampleGroupBySum()
    
    sum_counts = SampleSumCounts()
    