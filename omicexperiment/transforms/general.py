import numpy as np
import pandas as pd
from omicexperiment.transforms.transform import Transform


class RelativeAbundance(Transform):
    @staticmethod
    def apply_transform(experiment):
        rel_counts = experiment.data_df.apply(lambda c: c / c.sum() * 100, axis=0)
        return experiment.with_data_df(rel_counts)
    
    
class NumberUniqueObs(Transform):
    name = 'number_unique_obs'
    
    @classmethod
    def apply_transform(cls, experiment):
        transformed_series = (experiment.data_df > 0).sum().transpose()
        transformed_series.name = cls.name
        transposed_transformed_df = pd.DataFrame(transformed_series).transpose()
        return experiment.with_data_df(transposed_transformed_df)
    
    
class Rarefaction(Transform):
    def __init__(self, n):
        self.n = n
        
    @staticmethod
    def _rarefy_series(series, n):
        series_sum = series.sum()
        rel_abundance = series.apply(lambda c: c / series_sum)
        sampled = np.random.choice(rel_abundance.index, n, p=rel_abundance)
        sampled_series = pd.Series(sampled, name=series.name)
        return sampled_series.value_counts()


    @staticmethod
    def _rarefy_dataframe(dataframe, n):
        
        rarefied_all = []
        
        for col in dataframe:
            rarefied_series = Rarefaction._rarefy_series(dataframe[col], n)
            rarefied_all.append(rarefied_series)
        
        return pd.concat(rarefied_all,axis=1).fillna(0)
        

    def apply_transform(self, experiment):
        n = self.n
        cuttoff_df = experiment.filter(experiment.Sample.count >= n)
        return experiment.with_data_df( self._rarefy_dataframe(cuttoff_df, n) )

class RarefactionCurve(Transform):
    def __init__(self, n, step, transform_to_apply):
        self.n = n
        self.step = step
        self.transform_to_apply = transform_to_apply
    
    def apply_transform(self, experiment):
        transformed_rarefied_dataframes = []
        
        for cutoff_level in np.arange(0, self.n, self.step):
            rarefied_exp = experiment.apply(Rarefaction(cutoff_level))
            transformed_exp = rarefied_exp.apply(self.transform_to_apply)
            transformed_df = transformed_exp.data_df
            transformed_df.rename(index={self.transform_to_apply.name : cutoff_level}, inplace=True)
            transformed_rarefied_dataframes.append(transformed_df)
        
        rarefaction_curve_df = pd.concat(transformed_rarefied_dataframes, axis=0)
        
        return experiment.with_data_df(rarefaction_curve_df)