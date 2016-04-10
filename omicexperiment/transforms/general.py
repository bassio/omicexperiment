from collections import OrderedDict
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, cdist, squareform
from omicexperiment.transforms.transform import Transform
from omicexperiment.taxonomy import tax_as_dataframe
from omicexperiment.util import hybridmethod


class RelativeAbundance(Transform):
    @staticmethod
    def apply_transform(experiment):
        rel_counts = experiment.data_df.apply(lambda c: c / c.sum() * 100, axis=0)
        return experiment.with_data_df(rel_counts)
    

def number_unique_obs(series):
    return (series > 0).sum()


class NumberUniqueObs(Transform):
    name = 'number_unique_obs'
    
    @staticmethod
    def _number_unique_obs(series):
        return (series > 0).sum()
    
    @classmethod
    def apply_transform(cls, experiment):
        transformed_series = (experiment.data_df > 0).sum().transpose()
        transformed_series.name = cls.name
        transposed_transformed_df = pd.DataFrame(transformed_series).transpose()
        return experiment.with_data_df(transposed_transformed_df)
    
    
class Rarefaction(Transform):
    def __init__(self, n, num_reps=1):
        self.n = n
        self.num_reps = num_reps
        
        
    @staticmethod
    def _rarefy_series(series, n, num_reps=1):

        series_name = series.name

        if n == 0:
            sampled_series = pd.Series(0, index=series.index, name=series.name)
            return sampled_series
        
        sampled_series = series.sample(n, replace=True, weights=series)
        sampled_value_counts = sampled_series.index.value_counts()

        if num_reps == 1:
            return sampled_value_counts
        elif num_reps > 1:
            for r in range(num_reps - 1):
                next_sampled_series = series.sample(n, replace=True, weights=series)
                next_sampled_value_counts = next_sampled_series.index.value_counts()

                sampled_value_counts = pd.concat([sampled_value_counts, next_sampled_value_counts], axis=1).fillna(0).sum(axis=1)
                sampled_value_counts.name = series_name

                del next_sampled_series
                del next_sampled_value_counts
            
            sampled_value_counts = sampled_value_counts.sample(n, replace=True, weights=sampled_value_counts).index.value_counts()
            sampled_value_counts.name = series_name
            
            return sampled_value_counts


    @staticmethod
    def _rarefy_dataframe(dataframe, n, num_reps=1):
        rarefied_df = dataframe.apply(Rarefaction._rarefy_series, n=n, num_reps=num_reps)
        rarefied_df.fillna(0, inplace=True, downcast='infer')
        return rarefied_df
    

    def apply_transform(self, experiment):
        n = self.n
        num_reps = self.num_reps
        cutoff_df = experiment.filter(experiment.Sample.count >= n)
        rarefied_df = self._rarefy_dataframe(cutoff_df, n, num_reps)
        return experiment.with_data_df(rarefied_df)

    
class RarefactionFunction(Rarefaction):
    def __init__(self, n, num_reps, func, axis=0, agg_rep=None):
        Rarefaction.__init__(self, n, num_reps)
        self.func = func
        self.axis = axis
        self.agg_rep = agg_rep

    def rarefy_and_apply_func(self, dataframe):
        
        concated_df = None
        
        for rep in range(0, self.num_reps):
            rarefied_df = Rarefaction._rarefy_dataframe(dataframe, self.n, 1)
            func_applied = rarefied_df.apply(self.func, self.axis)
            func_applied.name = self.n
            
            concated_df = pd.concat([concated_df, func_applied], axis=1)#.fillna(0).mean(axis=1)
            
            del rarefied_df
            del func_applied
        
        
        if self.axis == 0:
            transposed = concated_df.transpose()
            transposed.index.name = 'rarefaction'
            
            if self.num_reps > 1:
                #append extra level to index to hold the repetition number
                rep_index = pd.Index(range(len(transposed.index)), name='rep')
                transposed.set_index(rep_index, append=True, inplace=True)
            
            return transposed
        
        else:
            return concated_df
            
        

    def apply_transform(self, experiment):
        cutoff_df = experiment.filter(experiment.Sample.count >= self.n)
        rarefied_df = self.rarefy_and_apply_func(cutoff_df)
        
        if self.agg_rep != None:
            rarefied_df = rarefied_df.groupby(level='rarefaction').apply(self.agg_rep)
            
        return experiment.with_data_df(rarefied_df)
    

class RarefactionCurveFunction(Transform):
    def __init__(self, n, num_reps, step, func, axis=0, agg_rep=None):
        self.n = n
        self.num_reps = num_reps
        self.step = step
        self.func = func
        self.axis = axis
        self.agg_rep = agg_rep
        
    def apply_transform(self, experiment):
        
        cutoff_exp = experiment.efilter(experiment.Sample.count >= self.n)
        
        
        concated_df = None
        
        for level in np.arange(0, self.n, self.step):
            RF = RarefactionFunction(n=level, num_reps=self.num_reps, func=self.func, axis=self.axis, agg_rep=self.agg_rep)
            rarefied_exp = RF.apply_transform(cutoff_exp)
            rarefied_df = rarefied_exp.data_df
            concated_df = pd.concat([concated_df, rarefied_df], levels=['rarefaction', 'rep'])
            del rarefied_exp
            del rarefied_df
                
        return experiment.with_data_df(concated_df)
    
    
class RarefactionCurve(Transform):
    #consider deprecation or replacement
    def __init__(self, n, num_reps, step, transform_to_apply):
        self.n = n
        self.num_reps = num_reps
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
    
    
class Cluster(Transform):
    def __init__(self, clusters_df, tax_assignment_file=None):
        self.clusters_df = clusters_df
        self.tax_assignment_file = tax_assignment_file
    
    @classmethod
    def from_uc_file(cls, uc_filepath, tax_assignment_file=None, seed_as_cluster_label=True):
        from omicexperiment.dataframe import load_uc_file
        clusters_df = load_uc_file(uc_filepath)
        if seed_as_cluster_label:
            clusters_df['cluster'] = clusters_df['seed']
        return cls(clusters_df, tax_assignment_file)
    
    @classmethod
    def from_swarm_otus_file(cls, swarm_otus_filepath):
        from omicexperiment.dataframe import load_swarm_otus_file
        clusters_df = load_swarm_otus_file(swarm_otus_filepath)
        return cls(clusters_df)
        
    def apply_transform(self, experiment):
        read_cluster_df = self.clusters_df
        
        cluster_index = read_cluster_df.reindex(experiment.data_df.index)['cluster']
        
        #append clusters of reads as an extra level to the index
        new_data_df = experiment.data_df.set_index(cluster_index, append=True)
        new_data_df = new_data_df.groupby(level='cluster').sum()

        if not (self.tax_assignment_file is None):
            taxdf_from_new_assignment_file = tax_as_dataframe(self.tax_assignment_file)
            new_unique_clusters = read_cluster_df['cluster'].drop_duplicates()
            new_taxonomy_df = taxdf_from_new_assignment_file.reindex(new_unique_clusters)
            
            return experiment.__class__(new_data_df, experiment.mapping_df, new_taxonomy_df, experiment.metadata)
        else:
            return experiment.__class__(new_data_df, experiment.mapping_df, experiment.taxonomy_df, experiment.metadata)
        

class DistanceMatrix(Transform):
    def __init__(self, distance_metric):
        self.distance_metric = distance_metric
        
    def apply_transform(self, experiment):
        df = experiment.data_df.transpose()
        dm = cdist(df, df, self.distance_metric)
        distance_matrix_df = pd.DataFrame(dm, index=df.index, columns=df.index)
        return experiment.with_data_df(distance_matrix_df)
    

class ClusterIntoOTUs(Transform):
    def __init__(self, otu_assignment_file, tax_assignment_file):
        self.otu_assignment_file = otu_assignment_file
        self.tax_assignment_file = tax_assignment_file
    
    def __process_assignment_file(self):
        with open(self.otu_assignment_file) as f:
            lines = f.readlines()
        
        read_to_otu_dict = OrderedDict()
        read_to_otu_tuples = []
        
        read_list = []
        otu_list = []

        for l in lines:
            splt = l.split()
            otu_name = splt[0].strip()
            reads = splt[1:]
            for r in reads:
                read = r.strip()
                read_list.append(read)
                otu_list.append(otu_name)
        
        read_to_otu_dict = OrderedDict(read=read_list, otu=otu_list)
        
        del read_list
        del otu_list
        
        df = pd.DataFrame(read_to_otu_dict, index=read_list)
        df.index.name = 'read'
    
        return df
    
    
    def apply_transform(self, experiment):
        read_otu_df = self.__process_assignment_file()
        new_data_df = experiment.data_df.join(read_otu_df).groupby("otu").sum().reset_index().set_index("otu")
        
        if self.tax_assignment_file is not None:
            taxdf_from_new_assignment_file = tax_as_dataframe(self.tax_assignment_file)
            new_taxonomy_df = pd.merge(taxdf_from_new_assignment_file, read_otu_df, left_on='otu', right_on='otu')
            new_taxonomy_df.rename(columns={'read':'otu_old'}, inplace=True)
            new_taxonomy_df.set_index('otu', drop=False, inplace=True)
            
            return experiment.__class__(new_data_df, experiment.mapping_df, new_taxonomy_df, experiment.metadata)
        else:
            return experiment.__class__(new_data_df, experiment.mapping_df, experiment.taxonomy_df, experiment.metadata)
        


class Dereplicate(Transform):
    pass


class BinObservations(Transform):
    def __init__(self, observations_to_bin, bin_groupname='Other'):
        self.observations_to_bin = observations_to_bin
        self.bin_groupname = bin_groupname
    
    def apply_transform(self, experiment):
        new_df = experiment.data_df.copy()

        #add sum of the other
        new_df.loc[self.bin_groupname] = new_df.loc[self.observations_to_bin].sum()

        #remove other
        without_binned_obs_df = new_df.loc[~new_df.index.isin(self.observations_to_bin)]
        
        return without_binned_obs_df
        
