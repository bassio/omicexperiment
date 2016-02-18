from omicexperiment.plotting.plot_pygal import plot_table

class FilterExpression(object):
    def __init__(self, operator=None, value=None):
        self.operator = operator
        self.value = value
        
    def __lt__(self, other):
        return self.__class__('__lt__', other)
        
    def __le__(self, other):
        return self.__class__('__le__', other)
        
    def __eq__(self, other):
        return self.__class__('__eq__', other)
        
    def __ne__(self, other):
        return self.__class__('__ne__', other)
        
        
    def __gt__(self, other):
        return self.__class__('__gt__', other)
        
    def __ge__(self, other):
        return self.__class__('__ge__', other)
        
    def return_value(self, experiment_obj):
        return NotImplementedError
        
class ObservationMinCount(FilterExpression):
    def return_value(self, experiment):
        if self.operator == '__eq__':
            assert isinstance(self.value, int)
            df = experiment.counts_df
            return df[df.sum(axis=1) >= self.value]
            
class ObservationMinCountFraction(FilterExpression):
    def return_value(self, experiment):
        if self.operator == '__eq__':
            assert isinstance(self.value, float)
            assert self.value <= 1
            df = experiment.counts_df
            obs_fractions = df.sum(axis=1) / (df.sum(axis=1).sum())
            return df[obs_fractions >= self.value]

class ObservationMaxCount(FilterExpression):
    def return_value(self, experiment):
        if self.operator == '__eq__':
            assert isinstance(self.value, int)
            df = experiment.counts_df
            return df[df.sum(axis=1) <= self.value]

class ObservationMinSamples(FilterExpression):
    def return_value(self, experiment):
        if self.operator == '__eq__':
            assert isinstance(self.value, int)
            df = experiment.counts_df
            absence_presence = (df > 0)
            return df[absence_presence.sum(axis=1) >= self.value]

class SampleMinCount(FilterExpression):
    def return_value(self, experiment):
        if self.operator == '__eq__':
            assert isinstance(self.value, int)
            df = experiment.counts_df
            criteria = (df.sum() >= self.value)
            return df[criteria.index[criteria]]

class SampleMaxCount(FilterExpression):
    def return_value(self, experiment):
        if self.operator == '__eq__':
            assert isinstance(self.value, int)
            df = experiment.counts_df
            criteria = (df.sum() <= self.value)
            return df[criteria.index[criteria]]

class AttributeFilter(FilterExpression):
    def __init__(self, operator=None, value=None, attribute=None):
        FilterExpression.__init__(self, operator, value)
        self.attribute = attribute
        
    def __lt__(self, other):
        return self.__class__('__lt__', other, self.attribute)
        
    def __le__(self, other):
        return self.__class__('__le__', other, self.attribute)
        
    def __eq__(self, other):
        return self.__class__('__eq__', other, self.attribute)
        
    def __ne__(self, other):
        return self.__class__('__ne__', other, self.attribute)
        
    def __gt__(self, other):
        return self.__class__('__gt__', other, self.attribute)
        
    def __ge__(self, other):
        return self.__class__('__ge__', other, self.attribute)

    def return_value(self, experiment):
        if self.operator == '__eq__':
            mapping = experiment.mapping_df
            criteria = (mapping[self.attribute] == self.value)
            df = experiment.counts_df
            return df[criteria.index[criteria]]
        
    def __getattr__(self, name):
        return AttributeFilter(operator = self.operator, value=self.value, attribute=name)
                                

class Sample(object):
    #not_in = 
    #in_
    min_count = SampleMinCount()
    max_count = SampleMaxCount()
    att = AttributeFilter()
    c = AttributeFilter()
    
    
class Observation(object):
    min_count = ObservationMinCount()
    min_count_fraction = ObservationMinCountFraction()
    min_samples = ObservationMinSamples()
    max_count = ObservationMaxCount()

    
class OmicExperiment(object):
    def __init__(self, counts_df, mapping_df = None, taxonomy_assignment_file=None):
        self.counts_df = counts_df
        self.mapping_df = mapping_df
        self.taxonomy_assignment_file = taxonomy_assignment_file
        
        self.Sample = Sample() #add in mapping file variables here for the samples
        self.Observation = Observation() #add in observation variables here
    
    
    def filter(self, filter_expr):
        return filter_expr.return_value(self)
    
    def efilter(self, filter_expr):
        new_counts = filter_expr.return_value(self)
        return self.__class__(new_counts, self.mapping_df, self.taxonomy_assignment_file)
    
    @property
    def samples(self):
        return list(self.counts_df.columns)
        
    @property
    def observations(self):
        return list(self.counts_df.index)
    
    def plot(self, outputfile):
        return plot_table(self.counts_df, outputfile)
        