from omicexperiment.experiment.experiment import OmicExperiment
from omicexperiment.dataframe import load_taxonomy_dataframe
from omicexperiment.taxonomy import tax_as_index, tax_as_dataframe
from omicexperiment.filters import Taxonomy
from omicexperiment.rarefaction import rarefy_dataframe


class MicrobiomeExperiment(OmicExperiment):
    def __init__(self, data_df, mapping_df = None, taxonomy_assignment_file=None):
        OmicExperiment.__init__(self, data_df, mapping_df)
        self.__init_taxonomy(taxonomy_assignment_file)
        
    def __init_taxonomy(self, taxonomy_assignment_file):
        self.taxonomy_assignment_file = taxonomy_assignment_file
        self._tax_df = load_taxonomy_dataframe(taxonomy_assignment_file)
        
        self.Taxonomy = Taxonomy
    
    @property
    def tax_index(self):
        try:
            return self._tax_index
        except AttributeError:
            self._tax_index = tax_as_index(self.taxonomy_assignment_file)
            return self._tax_index
        
    @property
    def taxonomy_df(self):
        try:
            return self._tax_df
        except AttributeError:
            self._tax_df = tax_as_dataframe(self.taxonomy_assignment_file)
            return self._tax_df
    
    def _counts_with_tax(self):
        joined_df = self.taxonomy_df.join(self.data_df, how='right')
        return joined_df
    
    
    def efilter(self, filter_expr):
        new_exp = OmicExperiment.efilter(self, filter_expr)
        new_exp.__init_taxonomy(self.taxonomy_assignment_file)
        return new_exp
    
    def to_relative_abundance(self):
        rel_counts = self.data_df.apply(lambda c: c / c.sum() * 100, axis=0)
        return self.__class__(rel_counts, self.mapping_df, self.taxonomy_assignment_file)
    
    
    def __getitem__(self, value):
        return self.efilter(value)
    
    
    def rarefy(self, n):
        from omicexperiment.transforms.general import Rarefaction
        return self.apply(Rarefaction(n))
        #cuttoff_df = self.filter(self.Sample.min_count == n)
        #return self.__class__( rarefy_dataframe(cuttoff_df, n), self.mapping_df, self.taxonomy_assignment_file)
        

class QiimeMicrobiomeExperiment(MicrobiomeExperiment):
    pass
