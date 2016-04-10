import types
import functools
from collections import OrderedDict
from pandas import Series, DataFrame
from omicexperiment import filters
from omicexperiment.plotting.plot_pygal import plot_table, return_plot, return_plot_tree, plot_to_file
from omicexperiment.plotting.groups import group_plot_tree
from omicexperiment.rarefaction import rarefy_dataframe
from omicexperiment.dataframe import load_dataframe
from omicexperiment.transforms.transform import Transform

class Experiment(object):
    def __init__(self, data_df, metadata={}):
        self.data_df = load_dataframe(data_df)
        self.metadata = metadata

class OmicExperiment(Experiment):
    def __init__(self, data_df, mapping_df = None, metadata={}):
        Experiment.__init__(self, data_df, metadata)
        #self.data_df = load_dataframe(data_df)
        
        self.mapping_df = load_dataframe(mapping_df, first_col_in_file_as_index=True)

        
        self.Sample = filters.Sample #add in mapping file variables here for the samples
        self.Observation = filters.Observation #add in observation variables here
    
    
    def apply(self, transforms, axis=0):
        if isinstance(transforms, Transform) \
        or \
        (isinstance(transforms, type) and issubclass(transforms, Transform)):
            transform = transforms #only a single object passed (not a list)
            return transform.apply_transform(self)
        
        elif isinstance(transforms, (types.FunctionType, types.BuiltinFunctionType, functools.partial)):
            func = transforms #only a single object passed (not a list)
            transformed_data_df = DataFrame(self.data_df.apply(func, axis=axis))
            
            #transpose to return the samples as column namess rather than row names
            if axis == 0 : transformed_data_df = transformed_data_df.transpose()
            
            return self.with_data_df(transformed_data_df)
        
        elif isinstance(transforms, list):
            transformed_exp = self
            for transform in transforms:
                transformed_exp = transform.apply_transform(transformed_exp)
            return transformed_exp
        
        else:
            raise NotImplementedError

        
    def filter(self, filter_expr):
        if isinstance(filter_expr, filters.FilterExpression):
            return filter_expr.return_value(self)
        elif isinstance(filter_expr, Series):
            criteria = series = filter_expr
            if series.index.name == self.mapping_df.index.name:
                columns_to_include = series.index[criteria]
                new_counts = self.data_df.reindex(columns=columns_to_include)
                return new_counts
                
    def efilter(self, filter_expr):
        new_counts = self.filter(filter_expr) 
        return self.__class__(new_counts, self.mapping_df)
            
            
    @property
    def samples(self):
        return list(self.data_df.columns)
        
    @property
    def observations(self):
        return list(self.data_df.index)
    
    @property
    def stats_df(self):
        return self.mapping_df.join(self.data_df.transpose(), how='inner')
    
    def get_plot(self):
        plot = return_plot(self.data_df)
        return plot
    
    def get_plot_tree(self):
        plot = return_plot(self.data_df)
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
        
        plot, tree = group_plot_tree(self.data_df, group_col, **kwargs)
        
        if outputfile is not None:
            plot_to_file(plot, tree, outputfile)
        
        return tree
    
    def groupby(self, variable):
        mapping_df = self.mapping_df.copy()
        transposed = self.data_df.transpose()
        joined_df = transposed.join(mapping_df[[variable]])
        means_df = joined_df.groupby(variable).mean()
        retransposed = means_df.transpose()
        return retransposed
    
    def to_relative_abundance(self):
        from omicexperiment.transforms.general import RelativeAbundance
        return RelativeAbundance.apply_transform(self)
        #rel_counts = self.data_df.apply(lambda c: c / c.sum() * 100, axis=0)
        #return self.__class__(rel_counts, self.mapping_df)
    
    def __getitem__(self, value):
        return self.efilter(value)
    
    def with_data_df(self, new_data_df):
        new_exp = self.__class__(new_data_df, self.mapping_df)
        return new_exp
    
    def with_mapping_df(self, new_mapping_df, reindex_data_df=True):
        if reindex_data_df:
            new_data_df = self.data_df.reindex(columns=new_mapping_df.index)
        else:
            new_data_df = self.data_df
            
        new_exp = self.__class__(new_data_df, new_mapping_df)
        return new_exp
    
    def describe(self, as_dict=False):
        desc = \
        (""
        "Num samples: {num_samples}\n"
        "Num observations: {num_observations}\n"
        "Total count: {total_count}\n"
        "Table density (fraction of non-zero values): {table_density}\n"
        "\n"
        "Counts/sample summary:\n"
        "Min: {min_sample}\n"
        "Max: {max_sample}\n"
        "Median: {median_sample}\n"
        "Mean: {mean_sample}\n"
        "Std. dev.: {std_sample}\n"
        "Sample Metadata Categories: None\n"
        "Observation Metadata Categories: None\n"
        "\n"
        "Counts/sample detail:\n"
        "{sample_counts}"
        "")
        
        d = {}
        d['num_samples'] = len(self.data_df.columns)
        d['num_observations'] = len(self.data_df.index)
        d['total_count'] = self.data_df.sum().sum();

        zero_df = (self.data_df==0).apply(lambda x: x.value_counts()).sum(axis=1)
        d['table_density'] = float(zero_df[False]) / zero_df.sum()

        sample_sums_df = self.data_df.sum()
        d['sample_counts'] = sample_sums_df.sort_values().to_string()

        sample_stats_df = sample_sums_df.describe()

        d['min_sample'] = sample_stats_df['min']
        d['max_sample'] = sample_stats_df['max']
        d['mean_sample'] = sample_stats_df['mean']
        d['median_sample'] = sample_stats_df['50%']
        d['std_sample'] = sample_stats_df['std']
        
        if as_dict:
            return d
        else:
            return desc.format(**d)
    
    def compare(self, other_exp):
        self_desc = self.describe(as_dict=True)
        other_desc = other_exp.describe(as_dict=True)
        
        df_dict = OrderedDict()
        df_dict['self'] = self_desc
        df_dict['other'] = other_desc
        
        return DataFrame(df_dict)
    