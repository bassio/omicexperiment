import numpy as np
from omicexperiment.transforms.transform import Transform
from pandas import DataFrame, concat


def number_unique_obs(series):
    return (series > 0).sum()


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
    
    '''
    def __dapply__(self, experiment):
        cluster_index = self.clusters_df.reindex(experiment.data_df.index)['cluster']

        #append clusters of reads as an extra level to the index
        new_data_df = experiment.data_df.set_index(cluster_index, append=True)
        new_data_df = new_data_df.groupby(level='cluster').apply(self.aggfunc)

        return new_data_df
    '''
    
    def __dapply__(self, experiment):
        #append clusters of reads as an extra level to the index
        new_data_df = experiment.data_df.rename(index=self.clusters_df_dict())
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


    def __dapply__(self, experiment):
        binned_df = ClusterObservations.__dapply__(self, experiment)

        observations_to_keep = experiment.data_df.index.difference(self.clusters_df.index)

        #remove other
        without_binned_obs_df = experiment.data_df.reindex(observations_to_keep)

        #add 'binned' observations back
        return concat([without_binned_obs_df, binned_df])
        groupbywithout_binned_obs_df.loc[self.bin_groupname] = experiment.data_df.loc[self.observations_to_bin].sum()

        return without_binned_obs_df
