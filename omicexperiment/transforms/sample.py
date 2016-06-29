import numpy as np
from omicexperiment.transforms.transform import Transform

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
