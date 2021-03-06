import types
import functools
from collections import OrderedDict
import numpy as np
from pandas import Series, DataFrame
from omicexperiment.transforms import proxy
from omicexperiment.plotting.plot_pygal import plot_table, return_plot, return_plot_tree, plot_to_file
from omicexperiment.plotting.groups import group_plot_tree
from omicexperiment.rarefaction import rarefy_dataframe
from omicexperiment.dataframe import load_dataframe
from omicexperiment.transforms.transform import Transform, Filter


class Experiment(object):
    def __init__(self, data_df, metadata={}):
        self.data_df = load_dataframe(data_df)
        self.metadata = metadata


class OmicExperiment(Experiment):
    Sample = proxy.Sample()
    Observation = proxy.Observation()
    
    def __init__(self, data_df, mapping_df = None, metadata={}):
        Experiment.__init__(self, data_df, metadata)
        #self.data_df = load_dataframe(data_df)

        self.mapping_df = load_dataframe(mapping_df, first_col_in_file_as_index=True)


    def apply(self, transforms, axis=0):
        if isinstance(transforms, Transform) \
        or \
        (isinstance(transforms, type) and issubclass(transforms, Transform)):
            transform = transforms #only a single object passed (not a list)
            return transform.__eapply__(self)

        elif isinstance(transforms, (types.FunctionType, types.BuiltinFunctionType, functools.partial)):
            func = transforms #only a single object passed (not a list)
            transformed_data_df = DataFrame(self.data_df.apply(func, axis=axis))

            #transpose to return the samples as column namess rather than row names
            if axis == 0 : transformed_data_df = transformed_data_df.transpose()

            return self.with_data_df(transformed_data_df)

        elif isinstance(transforms, list):
            transformed_exp = self
            for transform in transforms:
                transformed_exp = transform.__eapply__(transformed_exp)
            return transformed_exp

        else:
            raise NotImplementedError


    def dapply(self, transforms, axis=0):
        if isinstance(transforms, Transform) \
        or \
        (isinstance(transforms, type) and issubclass(transforms, Transform)):
            transform = transforms #only a single object passed (not a list)
            return transform.__dapply__(self)
        else:
            raise NotImplementedError


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

    def plot(self, backend='pygal', outputfile=None):
        if backend == 'pygal':
            plot = self.get_plot()
            tree = self.get_plot_tree()

            if outputfile is not None:
                plot_to_file(plot, tree, outputfile)

            return tree
        elif backend == 'matplotlib':
            from omicexperiment.plotting.plot_matplotlib import taxa_bar_plot
            return taxa_bar_plot(self.data_df)
        
    def plot_groups(self, mapping_group_col, outputfile=None, **kwargs):
        if isinstance(mapping_group_col, str):
            group_col = self.mapping_df[mapping_group_col]

        plot, tree = group_plot_tree(self.data_df, group_col, **kwargs)

        if outputfile is not None:
            plot_to_file(plot, tree, outputfile)

        return tree

    def plot_interactive(self):
        from omicexperiment.plotting.plot_bokeh import plot_interactive
        fig = plot_interactive(self.data_df)
        from bokeh.io import show, output_notebook
        output_notebook()
        show(fig)
        return fig

    def plot_matplobli(self):
        from omicexperiment.plotting.plot_bokeh import plot_interactive
        fig = plot_interactive(self.data_df)
        from bokeh.io import show, output_notebook
        output_notebook()
        show(fig)
        return fig
                
    def groupby(self, variable, aggfunc=np.mean):
        from omicexperiment.transforms.sample import SampleGroupBy
        return self.apply(SampleGroupBy(variable, aggfunc))

    def to_relative_abundance(self):
        from omicexperiment.transforms.general import RelativeAbundance
        return self.apply(RelativeAbundance)

    def __getitem__(self, value):
        return self.apply(value)

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


    def description(self, as_dict=False):
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
    
    def describe(self):
        print(self.description())
        
    def compare(self, other_exp):
        self_desc = self.describe(as_dict=True)
        other_desc = other_exp.describe(as_dict=True)

        df_dict = OrderedDict()
        df_dict['self'] = self_desc
        df_dict['other'] = other_desc

        return DataFrame(df_dict)
