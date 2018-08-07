import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, cdist, squareform
from skbio.diversity import alpha_diversity
from skbio.diversity import beta_diversity

from omicexperiment.transforms.transform import Transform
from omicexperiment.transforms.general import RarefactionFunction


class AlphaDiversity(Transform):
    def __init__(self, distance_metric, **kwargs):
        self.distance_metric = distance_metric
        self.kwargs = kwargs

    def __dapply__(self, experiment):
        otu_ids = experiment.data_df.index
        sample_ids = experiment.data_df.columns
        matrix = experiment.data_df.T.as_matrix()
        try:
            alpha = alpha_diversity(self.distance_metric, counts=matrix, ids=sample_ids, **self.kwargs)
        except ValueError as e:
            otu_ids_err_msg = "``otu_ids`` is required for phylogenetic diversity metrics."
            if str(e) == otu_ids_err_msg:
                alpha = alpha_diversity(self.distance_metric, counts=matrix,
                                        ids=sample_ids, otu_ids=otu_ids,
                                        **self.kwargs)
            else:
                raise(e)
                
        return alpha.to_frame(name=self.distance_metric).transpose()

    def __eapply__(self, experiment):
        distance_matrix_df = self.__dapply__(experiment)
        return experiment.with_data_df(distance_matrix_df)


class BetaDiversity(Transform):
    def __init__(self, distance_metric, **kwargs):
        self.distance_metric = distance_metric
        self.kwargs = kwargs

    def __dapply__(self, experiment):
        otu_ids = experiment.data_df.index
        df = experiment.data_df.transpose()
        try:
            dm = beta_diversity(self.distance_metric, counts=df.as_matrix(), otu_ids=otu_ids, **self.kwargs)
        except TypeError as e:
            if 'takes no keyword arguments' in str(e):
                dm = beta_diversity(self.distance_metric, counts=df.as_matrix(), **self.kwargs)
            else:
                raise(e)
            
        distance_matrix_df = pd.DataFrame(dm.data, index=df.index, columns=df.index)
        return distance_matrix_df

    def __eapply__(self, experiment):
        distance_matrix_df = self.__dapply__(experiment)
        new_exp = experiment.with_data_df(distance_matrix_df)
        new_exp.metadata['distance_metric'] = self.distance_metric
        return experiment.with_data_df(distance_matrix_df)


class GroupwiseDistances(Transform):
    def __init__(self, grouping_col, include_between_dists=True, include_within_dists=False, **kwargs):
        self.grouping_col = grouping_col
        self.include_between_dists = include_between_dists
        self.include_within_dists = include_within_dists
        self.kwargs = kwargs

    def __dapply__(self, experiment):
        from collections import OrderedDict
        from itertools import combinations
        
        grouping_col = self.grouping_col
        distance_metric = experiment.metadata['distance_metric']
        
        
        distances_df = pd.DataFrame({distance_metric: squareform(experiment.data_df)},
                        index=pd.MultiIndex.from_tuples(tuple(combinations(experiment.data_df.index, 2)), names=['sample_1', 'sample_2'])).reset_index()

        group_1 = experiment.mapping_df[[grouping_col]].reindex(distances_df['sample_1'])
        group_2 = experiment.mapping_df[[grouping_col]].reindex(distances_df['sample_2'])

        distances_df['group_1'] = group_1.reset_index()[grouping_col]
        distances_df['group_2'] = group_2.reset_index()[grouping_col]
        
        all_within = distances_df[distances_df['group_1'] == distances_df['group_2']]
        all_within_with_label = all_within.copy()
        all_within_with_label['label'] = 'all_within'
        all_within_with_label = all_within_with_label.set_index('label')[[distance_metric]]

        all_between = distances_df[distances_df['group_1'] != distances_df['group_2']]
        all_between_with_label = all_between.copy()
        all_between_with_label['label'] = 'all_between'
        all_between_with_label = all_between_with_label.set_index('label')[[distance_metric]]

        dist_dataframes = OrderedDict()
        dist_dataframes['all_within'] = all_within_with_label
        dist_dataframes['all_between'] = all_between_with_label
        
        if self.include_between_dists:
            for grp1, grp2 in combinations(experiment.mapping_df[grouping_col].unique(), 2):
                lbl = "{}_vs_{}".format(grp1, grp2)
                dist_df = distances_df[(distances_df['group_1'] == grp1) & (distances_df['group_2'] == grp2)]
                dist_df_w_label = dist_df.copy()
                dist_df_w_label['label'] = lbl
                dist_df_w_label = dist_df_w_label.set_index('label')[[distance_metric]]
                dist_dataframes[lbl] = dist_df_w_label
        
        if self.include_within_dists:
            for grp in experiment.mapping_df[grouping_col].unique():
                lbl = "within_{}".format(grp)
                dist_df = distances_df[(distances_df['group_1'] == grp) & (distances_df['group_2'] == grp)]
                dist_df_w_label = dist_df.copy()
                dist_df_w_label['label'] = lbl
                dist_df_w_label = dist_df_w_label.set_index('label')[[distance_metric]]
                dist_dataframes[lbl] = dist_df_w_label
        
        return pd.concat([v for k,v in dist_dataframes.items()])

    def __eapply__(self, experiment):
        groupwise_distances_df = self.__dapply__(experiment)
        return experiment.with_data_df(groupwise_distances_df)


