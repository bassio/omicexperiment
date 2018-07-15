import numpy as np
from omicexperiment.transforms.transform import TransformObjectsProxy, Transform


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


_index = object()


class SampleGroupBy(Transform):
    def __init__(self, variable=_index, aggfunc=np.mean):
        self.variable = variable
        self.aggfunc = aggfunc
    
    def __get__(self, instance, owner):
        if isinstance(instance, TransformObjectsProxy):
            self.experiment = instance.experiment
            return self
        else:
            return super().__get__(instance, owner)
        

    def __call__(self, variable, aggfunc=np.mean):
        #self.variable = variable
        #self.aggfunc = aggfunc
        
        if hasattr(self, 'experiment'):
            new_instance = self.__class__(variable, aggfunc)
            new_instance.experiment = self.experiment
            return new_instance.__eapply__(self.experiment)
            #return self.__eapply__(self.experiment)
        else:
            return self
    
    def groupby(self, experiment):
        mapping_df = experiment.mapping_df
        transposed = experiment.data_df.transpose()
        
        if self.variable is _index:
            index_df = mapping_df.index.to_frame()
            joined_df = transposed.join(index_df)
            self.variable = index_df.columns
        else:
            joined_df = transposed.join(mapping_df[[self.variable]])
        
        print(self.variable)
        df_groupby_obj = joined_df.groupby(self.variable)
        print(df_groupby_obj)
        return df_groupby_obj
    
    def __dapply__(self, experiment):
        agg_df = self.groupby(experiment).apply(self.aggfunc)
        try:
            agg_df.drop(self.variable, axis=1, inplace=True)
        except ValueError:
            pass
        retransposed = agg_df.transpose()
        return retransposed

    def __eapply__(self, experiment):
        retransposed = self.__dapply__(experiment)
        return experiment.with_data_df(retransposed)


class SampleSumCounts(Transform):
    def __dapply__(self, experiment):
        return experiment.data_df.sum().to_frame("obs_count").transpose()
    
    def __eapply__(self, experiment):
        sums_df = self.__dapply__(experiment)
        return experiment.with_data_df(sums_df)

