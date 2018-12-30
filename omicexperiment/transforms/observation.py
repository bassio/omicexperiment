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


class AbundancePrevalenceStatistics(Transform):
    def __init__(self, absence_presence_cutoff=1):
        self.absence_presence_cutoff = absence_presence_cutoff
    
    def __dapply__(self, experiment):
        rel_abund_df = experiment.counts_df.sum(axis=1).sort_values(ascending=False).to_frame(name="mean_relative_abundance")
        rel_abund_df = rel_abund_df.apply(lambda c: c / c.sum() * 100, axis=0)
        
        absence_presence_cutoff = self.absence_presence_cutoff
        prev_df = (experiment.counts_df >= absence_presence_cutoff).astype(int).apply(lambda c: c.sum() / c.count() * 100, axis=1).sort_values(ascending=False).to_frame("prevalence")
        
        abund_prev_df = rel_abund_df.join(prev_df)
        
        return abund_prev_df

    def __eapply__(self, experiment):
        new_data_df = self.__dapply__(experiment)
        return experiment.with_data_df(new_data_df)


class AbundancePrevalenceRankStatistics(AbundancePrevalenceStatistics):
    def __init__(self, absence_presence_cutoff=1, ascending=False):
        super().__init__(absence_presence_cutoff)
        self.ascending = ascending
    
    def __dapply__(self, experiment):
        abund_prev_df = super().__dapply__(experiment)
        ranked_abund_df = abund_prev_df['mean_relative_abundance'].sort_values(ascending=self.ascending).rank(ascending=self.ascending).to_frame()
        ranked_prev_df = abund_prev_df['prevalence'].sort_values(ascending=self.ascending).rank(ascending=self.ascending).to_frame()
        joined_ranked_df = ranked_abund_df.join(ranked_prev_df)
        if self.ascending:
            return joined_ranked_df.iloc[::-1] #reverse the dataframe
        else:
            return joined_ranked_df
        

class TopAbundantObservations(Transform):
    def __init__(self, n):
            self.n = n
    
    @staticmethod
    def top_abundant_taxa(experiment, n):
        abund_prev_df = experiment.apply(AbundancePrevalenceStatistics()).data_df
        abund_series = abund_prev_df['mean_relative_abundance']
        
        top_taxa = list(abund_series.head(n).index)
        
        return top_taxa

    def __dapply__(self, experiment):
        top_taxa = TopAbundantObservations.top_abundant_taxa(experiment, self.n)
        other_taxa = list(experiment.data_df.index.difference(top_taxa))
        
        experiment_other = experiment.apply(BinObservations(other_taxa, groupnames='Other'))
        
        return  experiment_other.data_df
    
    def __eapply__(self, experiment):
        new_data_df = self.__dapply__(experiment)
        return experiment.with_data_df(new_data_df)

