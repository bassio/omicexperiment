from skbio.stats.ordination import pcoa
from omicexperiment.transforms.transform import Transform

from omicexperiment.util import hybridmethod


class PCoA(Transform):
    @hybridmethod
    def apply_transform(self, experiment):
        dm = experiment.data_df
        pcoa_results = pcoa(dm)
        pcoa_df = pcoa_results.samples
        pcoa_df.index = dm.index #sample names
        pcoa_df = pcoa_df.transpose()
        pcoa_exp = experiment.with_data_df(pcoa_df)
        pcoa_exp.metadata['pcoa'] = pcoa_results
        return pcoa_exp