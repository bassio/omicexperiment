from omicexperiment.experiment.experiment import OmicExperiment
from omicexperiment.taxonomy import tax_as_index, tax_as_dataframe, process_taxonomy_dataframe
from omicexperiment.transforms import proxy
from omicexperiment.rarefaction import rarefy_dataframe


class MicrobiomeExperiment(OmicExperiment):
    
    Taxonomy = proxy.Taxonomy()
    
    def __init__(self, data_df, mapping_df = None, taxonomy_assignment_file=None, metadata={}):
        OmicExperiment.__init__(self, data_df, mapping_df, metadata)
        self.__init_taxonomy(taxonomy_assignment_file)

    def __init_taxonomy(self, taxonomy_assignment_file):
        self.taxonomy_assignment_file = taxonomy_assignment_file
        self._tax_df = process_taxonomy_dataframe(taxonomy_assignment_file)


    def load_tax_assignment(self, taxonomy_assignment_file):
        self.taxonomy_assignment_file = taxonomy_assignment_file
        self._tax_df = process_taxonomy_dataframe(taxonomy_assignment_file)

        self.Taxonomy = Taxonomy

    @classmethod
    def from_experiment(self, exp):
        return MicrobiomeExperiment(exp.data_df, exp.mapping_df, exp.taxonomy_df, exp.metadata)

    @property
    def tax_index(self):
        try:
            return self._tax_index
        except AttributeError:
            self._tax_index = tax_as_index(self.taxonomy_assignment_file)
            return self._tax_index

    @property
    def data(self):
        return self.data_df

    @property
    def counts_df(self):
        return self.data_df

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
    
    def _metadata_with_data_df(self):
        return self.mapping_df.join(self.counts_df.T)
        

    def __getitem__(self, value):
        return self.apply(value)


    def rarefy(self, n, num_reps=1):
        from omicexperiment.transforms.general import Rarefaction
        return self.apply(Rarefaction(n, num_reps))


    def with_data_df(self, new_data_df):
        new_exp = self.__class__(new_data_df, self.mapping_df, self.taxonomy_df, self.metadata)

        return new_exp

    def with_mapping_df(self, new_mapping_df, reindex_data_df=True):
        if reindex_data_df:
            new_data_df = self.data_df.reindex(columns=new_mapping_df.index)
        else:
            new_data_df = self.data_df

        new_exp = self.__class__(new_data_df, new_mapping_df, self.taxonomy_df, self.metadata)

        return new_exp

    def with_taxonomy_df(self, new_taxonomy_df):
        new_exp = self.__class__(self.data_df, self.mapping_df, new_taxonomy_df, self.metadata)

        return new_exp

    def to_tsv(self, filepath_or_buf, dataframe='data_df'):
        df = getattr(self, dataframe)
        if dataframe == 'data_df':
            df.to_csv(filepath_or_buf, sep="\t", index_label=True, encoding='utf-8')
        else:
            df.to_csv(filepath_or_buf, sep="\t", index_label=True, encoding='utf-8')


class QiimeMicrobiomeExperiment(MicrobiomeExperiment):
    pass
