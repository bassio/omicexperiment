import numpy as np
from omicexperiment.transforms.transform import Transform


class KeepSamples(Transform):
    def __init__(self, sample_names):
        self.sample_names = list(sample_names)
    
    def __dapply__(self, experiment):
        to_keep = experiment.data_df.columns.intersection(self.sample_names)
        return experiment.data_df.reindex(columns=to_keep)

    def __eapply__(self, experiment):
        kept_samples_df = self.__dapply__(experiment)
        return experiment.with_data_df(kept_samples_df)


class ExcludeSamples(Transform):
    def __init__(self, sample_names, errors='ignore'):
        self.sample_names = list(sample_names)
        self.errors = errors
    
    def __dapply__(self, experiment):
        return experiment.data_df.drop(self.sample_names, axis=1, errors=self.errors)

    def __eapply__(self, experiment):
        after_exc = self.__dapply__(experiment)
        return experiment.with_data_df(after_exc)


class SampleGroupBy(Transform):
    def __init__(self, variable, aggfunc=np.mean):
        self.variable = variable
        self.aggfunc = aggfunc

    def __dapply__(self, experiment):
        mapping_df = experiment.mapping_df.copy()
        transposed = experiment.data_df.transpose()
        joined_df = transposed.join(mapping_df[[self.variable]])
        agg_df = joined_df.groupby(self.variable).apply(self.aggfunc)
        try:
            agg_df.drop(self.variable, axis=1, inplace=True)
        except ValueError:
            pass
        retransposed = agg_df.transpose()
        return retransposed

    def __eapply__(self, experiment):
        retransposed = self.__dapply__(experiment)
        return experiment.with_data_df(retransposed)
