from collections import OrderedDict
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, cdist, squareform
from omicexperiment.transforms.transform import Transform
from omicexperiment.taxonomy import tax_as_dataframe
from omicexperiment.util import hybridmethod


class RelativeAbundance(Transform):
    @classmethod
    def __dapply__(cls, experiment):
        rel_counts = experiment.data_df.apply(lambda c: c / c.sum() * 100, axis=0)
        return rel_counts

    @classmethod
    def __eapply__(cls, experiment):
        rel_counts = cls.__dapply__(experiment)
        return experiment.with_data_df(rel_counts)


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
        sampled_value_counts.name = series_name

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


    def __dapply__(self, experiment):
        n = self.n
        num_reps = self.num_reps
        cutoff_df = experiment.dapply(experiment.Sample.count >= n)
        rarefied_df = self._rarefy_dataframe(cutoff_df, n, num_reps)
        return rarefied_df


    def __eapply__(self, experiment):
        rarefied_df = self.__dapply__(experiment)
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


    def __dapply__(self, experiment):
        cutoff_df = experiment.dapply(experiment.Sample.count >= self.n)
        rarefied_df = self.rarefy_and_apply_func(cutoff_df)

        if self.agg_rep != None:
            rarefied_df = rarefied_df.groupby(level='rarefaction').apply(self.agg_rep)

        return rarefied_df

    def __eapply__(self, experiment):
        rarefied_df = self.__dapply__(experiment)
        return experiment.with_data_df(rarefied_df)


class RarefactionCurveFunction(Transform):
    def __init__(self, n, num_reps, step, func, axis=0, agg_rep=None):
        self.n = n
        self.num_reps = num_reps
        self.step = step
        self.func = func
        self.axis = axis
        self.agg_rep = agg_rep


    def __dapply__(self, experiment):
        cutoff_exp = experiment.apply(experiment.Sample.count >= self.n)


        concated_df = None

        for level in np.arange(0, self.n, self.step):
            RF = RarefactionFunction(n=level, num_reps=self.num_reps, func=self.func, axis=self.axis, agg_rep=self.agg_rep)
            rarefied_exp = cutoff_exp.apply(RF)
            rarefied_df = rarefied_exp.data_df
            concated_df = pd.concat([concated_df, rarefied_df], levels=['rarefaction', 'rep'])
            del rarefied_exp
            del rarefied_df

        return concated_df


    def __eapply__(self, experiment):
        concated_df = self.__dapply__(experiment)
        return experiment.with_data_df(concated_df)



class RarefactionCurve(Transform):
    def __init__(self, n, num_reps, step, transform_to_apply):
        self.n = n
        self.num_reps = num_reps
        self.step = step
        self.transform_to_apply = transform_to_apply


    def __dapply__(self, experiment):
        transformed_rarefied_dataframes = []

        for cutoff_level in np.arange(0, self.n, self.step):
            rarefied_exp = experiment.apply(Rarefaction(cutoff_level))
            transformed_exp = rarefied_exp.apply(self.transform_to_apply)
            transformed_df = transformed_exp.data_df
            transformed_df.rename(index={self.transform_to_apply.name : cutoff_level}, inplace=True)
            transformed_rarefied_dataframes.append(transformed_df)

        rarefaction_curve_df = pd.concat(transformed_rarefied_dataframes, axis=0)

        return rarefaction_curve_df


    def __eapply__(self, experiment):
        rarefaction_curve_df = self.__dapply__(experiment)
        return experiment.with_data_df(rarefaction_curve_df)


class Dereplicate(Transform):
    pass


class DistanceMatrix(Transform):
    def __init__(self, distance_metric):
        self.distance_metric = distance_metric

    def __dapply__(self, experiment):
        df = experiment.data_df.transpose()
        dm = cdist(df, df, self.distance_metric)
        distance_matrix_df = pd.DataFrame(dm, index=df.index, columns=df.index)
        return distance_matrix_df

    def __eapply__(self, experiment):
        distance_matrix_df = self.__dapply__(experiment)
        return experiment.with_data_df(distance_matrix_df)
