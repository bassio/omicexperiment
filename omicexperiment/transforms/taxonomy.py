from omicexperiment.transforms.transform import Transform, GroupByTransform
from omicexperiment.taxonomy import tax_as_dataframe


class TaxonomyGroupBy(GroupByTransform):
    TAX_RANKS = ['kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species']

    def __init__(self, rank, collapse=True):
        self.rank = rank
        self.collapse = collapse

    @staticmethod
    def tax_rank_levels(highest_res_rank):
        TAX_RANKS = TaxonomyGroupBy.TAX_RANKS
        if highest_res_rank == 'class_':
            highest_res_rank = 'class'
        return TAX_RANKS[:TAX_RANKS.index(highest_res_rank)+1]

    def __dapply__(self, experiment):
        rank = self.rank
        taxlevels_to_rank = TaxonomyGroupBy.tax_rank_levels(rank)

        df = experiment._counts_with_tax()

        #groupby_df
        groupby_df = df.groupby(taxlevels_to_rank).sum().reset_index()

        #drop extra levels (now columns)
        groupby_df.drop([rnk for rnk in taxlevels_to_rank if rnk != rank], axis=1, inplace=True)
        try:
            groupby_df.drop(['otu'], axis=1, inplace=True)
        except ValueError: #not found
            pass

        #further collapse similarly named ranks (e.g. "k__unidentified (Unassigned)")
        if self.collapse:
            groupby_df = groupby_df.groupby(rank).sum()
        else:
            groupby_df.set_index(rank, drop=True, inplace=True)

        return groupby_df

    def __eapply__(self, experiment):
        groupby_df = self.__dapply__(experiment)
        return experiment.with_data_df(groupby_df)


class AssignTaxonomy(Transform):
    def __init__(self, taxonomy_df):
        self.taxonomy_df = taxonomy_df

    @classmethod
    def from_qiime_tax_assignment_file(cls, tax_assignment_file):
        taxonomy_df = tax_as_dataframe(tax_assignment_file)
        return cls(taxonomy_df)

    def __eapply__(self, experiment):
        return experiment.with_taxonomy_df(self.taxonomy_df)


class RemoveUnassigned(Transform):
    @classmethod
    def __dapply__(cls, experiment):
        unassigned_filter = experiment.data_df.index.str.lower().str.contains('unassigned')
        to_remove = experiment.data_df[unassigned_filter].index
        return experiment.data_df.drop(to_remove)

    @classmethod
    def __eapply__(cls, experiment):
        with_unassigned_removed_df = cls.__dapply__(experiment)
        return experiment.with_data_df(with_unassigned_removed_df)
