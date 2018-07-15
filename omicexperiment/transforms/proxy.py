from omicexperiment.transforms.transform import TransformObjectsProxy, Transform

from omicexperiment.transforms.sample import SampleGroupBy, SampleSumCounts
from omicexperiment.transforms.filters.sample import SampleAttributeFilter, SampleCount

from omicexperiment.transforms.observation import ObservationSumCounts
from omicexperiment.transforms.filters.observation import ObservationMinCount, ObservationMinCountFraction, ObservationMaxCount, ObservationMinSamples

from omicexperiment.transforms.taxonomy import TaxonomyGroupBy
from omicexperiment.transforms.filters.taxonomy import TaxonomyAttributeFilter


class Sample(TransformObjectsProxy):
    #not_in = 
    #in_
    count = SampleCount()
    
    att = SampleAttributeFilter()
    c = SampleAttributeFilter()
    
    groupby = SampleGroupBy()
    
    sum_counts = SampleSumCounts()



class Observation(TransformObjectsProxy):
    min_count = ObservationMinCount()
    min_count_fraction = ObservationMinCountFraction()
    max_count = ObservationMaxCount()
    min_samples = ObservationMinSamples()
    
    sum_counts = ObservationSumCounts()



class Taxonomy(TransformObjectsProxy):
    groupby = TaxonomyGroupBy('tax')
    kingdom = TaxonomyAttributeFilter(attribute='kingdom')
    phylum = TaxonomyAttributeFilter(attribute='phylum')
    class_ = TaxonomyAttributeFilter(attribute='class')
    order = TaxonomyAttributeFilter(attribute='order')
    family = TaxonomyAttributeFilter(attribute='family')
    genus = TaxonomyAttributeFilter(attribute='genus')
    species = TaxonomyAttributeFilter(attribute='species')
    otu = TaxonomyAttributeFilter(attribute='otu')
    rank_resolution = TaxonomyAttributeFilter(attribute='rank_resolution')
    
