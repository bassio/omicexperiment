import numpy as np
from omicexperiment.transforms.transform import Transform
from omicexperiment.transforms.general import Rarefaction
from pandas import DataFrame, concat
from collections import OrderedDict

def number_unique_obs(series):
    return (series > 0).sum()


class ObservationSumCounts(Transform):
    def __dapply__(self, experiment):
        return experiment.data_df.sum(axis=1).to_frame("sum_counts")
    
    def __eapply__(self, experiment):
        sums_df = self.__dapply__(experiment)
        return experiment.with_data_df(sums_df)


class NumberUniqueObservations(Transform):
    name = 'number_unique_obs'

    @staticmethod
    def _number_unique_obs(series):
        return (series > 0).sum()

    @classmethod
    def __dapply__(cls, experiment):
        transformed_series = (experiment.data_df > 0).sum().transpose()
        transformed_series.name = cls.name
        transposed_transformed_df = DataFrame(transformed_series).transpose()
        return transposed_transformed_df

    @classmethod
    def __eapply__(cls, experiment):
        transposed_transformed_df = cls.__dapply__(experiment)
        return experiment.with_data_df(transposed_transformed_df)


class ClusterObservations(Transform):
    def __init__(self, clusters_df, aggfunc=np.sum):
        self.clusters_df = clusters_df
        self.clusters_df.set_index('observation', inplace=True)
        self.aggfunc = aggfunc
    
    def clusters_df_dict(self):
        return self.clusters_df.to_dict()['cluster']
    
    def __dapply__(self, experiment):
        #rename the observations according to their clusters
        new_data_df = experiment.data_df.rename(index=self.clusters_df_dict())
        
        #apply the aggregation
        new_data_df.index.rename('cluster', inplace=True)
        new_data_df_agg = new_data_df.groupby(level='cluster').agg(self.aggfunc)
        
        del new_data_df
        
        return new_data_df_agg

    def __eapply__(self, experiment):
        new_data_df = self.__dapply__(experiment)
        return experiment.with_data_df(new_data_df)


class BinObservations(ClusterObservations):
    def __init__(self, observations_to_bin, groupnames='Other', aggfunc=np.sum):

        if isinstance(groupnames, list) \
        and len(groupnames) != len(observations_to_bin):
            raise Exception("The groupnames argument must be of same length as observations_to_bin.")
        clusters_df = DataFrame({'observation': observations_to_bin, 'cluster': groupnames})
        clusters_df.index.name = 'observation'

        ClusterObservations.__init__(self, clusters_df, aggfunc)



class AbundanceFilteringWangEtAl(ClusterObservations):
    
    @staticmethod
    def _bootstrap_series_concatenate(series, num_reps=1):
        series_sum = series.sum()
        
        rarefy = Rarefaction._rarefy_series
        
        series_list = [rarefy(series, series_sum, num_reps=1) 
                    for i in range(num_reps)]
        
        return concat(series_list, axis=1).fillna(0)

    @staticmethod
    def calculate_af_threshold(counts_series, num_reps=1000):
        series = counts_series.sort_values(ascending=False)

        bootstrap_df = AbundanceFilteringWangEtAl._bootstrap_series_concatenate(series, num_reps)
        bootstrap_df_transposed = bootstrap_df.transpose()

        abund_real = series

        abund_boot = bootstrap_df_transposed.mean().sort_values(ascending=False)
        abund_995 = bootstrap_df_transposed.quantile(0.995)
        abund_005 = bootstrap_df_transposed.quantile(0.005)

        abund_adj = (2 * abund_real) - abund_boot
        abund_adj = abund_adj.sort_values(ascending=False).fillna(0)
        
        ci99_higher = abund_adj + (abund_995 - abund_boot)
        ci99_higher = ci99_higher.sort_values(ascending=False).fillna(0)

        ci99_lower = abund_adj - (abund_boot - abund_005)
        ci99_lower = ci99_lower.sort_values(ascending=False)
        
        unreliable = ci99_lower[ci99_lower <= 0].index
        
        if unreliable.shape[0] > 0:
            threshold = int(series[unreliable].max())
        else:
            threshold = 0
            
        return threshold
    
    @staticmethod
    def abundance_filter_dataframe(counts_df, num_reps=1000):
        
        calculate_threshold = AbundanceFilteringWangEtAl.calculate_af_threshold
        
        new_df_dict = OrderedDict()
    
        for col in counts_df.columns:
            counts_column = counts_df[col]
            threshold = calculate_threshold(counts_column, num_reps)
            sequences_to_keep = counts_df[counts_column > threshold].index
            new_df_dict[col] = counts_column.reindex(sequences_to_keep)
            
        return DataFrame.from_dict(new_df_dict).fillna(0)
    
    @classmethod
    def __dapply__(cls, experiment):
        counts_df = experiment.data
        return AbundanceFilteringWangEtAl.abundance_filter_dataframe(counts_df)
     
    @classmethod
    def __eapply__(cls, experiment):
        filtered_df = cls.__dapply__(experiment)
        return experiment.with_data_df(filtered_df)
