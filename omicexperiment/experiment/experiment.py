from omicexperiment import filters
from omicexperiment.plotting.plot_pygal import plot_table, return_plot, return_plot_tree, plot_to_file
from omicexperiment.plotting.groups import group_plot_tree
from omicexperiment.rarefaction import rarefy_dataframe
from omicexperiment.dataframe import load_dataframe


class OmicExperiment(object):
    def __init__(self, counts_df, mapping_df = None):
        self.counts_df = load_dataframe(counts_df)
        self.mapping_df = load_dataframe(mapping_df)
        self.mapping_df.set_index(self.mapping_df.columns[0], drop=False, inplace=True)
        
        self.Sample = filters.Sample #add in mapping file variables here for the samples
        self.Observation = filters.Observation #add in observation variables here
    
    def filter(self, filter_expr):
        return filter_expr.return_value(self)
    
    def efilter(self, filter_expr):
        new_counts = filter_expr.return_value(self)
        return self.__class__(new_counts, self.mapping_df)
    
    @property
    def samples(self):
        return list(self.counts_df.columns)
        
    @property
    def observations(self):
        return list(self.counts_df.index)
    
    def get_plot(self):
        plot = return_plot(self.counts_df)
        return plot
    
    def get_plot_tree(self):
        plot = return_plot(self.counts_df)
        return return_plot_tree(plot)
        
    def plot(self, outputfile=None):
        plot = self.get_plot()
        tree = self.get_plot_tree()
        
        if outputfile is not None:
            plot_to_file(plot, tree, outputfile)
        
        return tree
    
    def plot_groups(self, mapping_group_col, outputfile=None, **kwargs):
        if isinstance(mapping_group_col, str):
            group_col = self.mapping_df[mapping_group_col]
        
        plot, tree = group_plot_tree(self.counts_df, group_col, **kwargs)
        
        if outputfile is not None:
            plot_to_file(plot, tree, outputfile)
        
        return tree
    
    def groupby(self, variable):
        mapping_df = self.mapping_df.copy()
        transposed = self.counts_df.transpose()
        joined_df = transposed.join(mapping_df[[variable]])
        means_df = joined_df.groupby(variable).mean()
        retransposed = means_df.transpose()
        return retransposed
    
    def to_relative_abundance(self):
        rel_counts = self.counts_df.apply(lambda c: c / c.sum() * 100, axis=0)
        return self.__class__(rel_counts, self.mapping_df)
    
    def __getitem__(self, value):
        return self.efilter(value)
    
    def with_counts_df(self, new_counts_df):
        new_exp = self.__class__(new_counts_df, self.mapping_df)
        return new_exp
    
    def with_mapping_df(self, new_mapping_df, reindex_counts_df=True):
        if reindex_counts_df:
            new_counts_df = self.counts_df.reindex(columns=new_mapping_df.index)
        else:
            new_counts_df = self.counts_df
            
        new_exp = self.__class__(new_counts_df, new_mapping_df)
        return new_exp
    
        