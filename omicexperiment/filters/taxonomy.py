import pandas as pd
from omicexperiment.filters.filters import FilterExpression, AttributeFilter, GroupByFilter, AttributeFlexibleOperatorMixin


class TaxonomyAttributeFilter(AttributeFilter, AttributeFlexibleOperatorMixin):
    def return_value(self, experiment):
        _op = self._op_function(experiment._counts_with_tax())
        criteria = _op(self.value)
        return experiment.data_df[criteria]
        

class TaxonomyGroupBy(GroupByFilter):
    TAX_RANKS = ['kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species']
    
    collapse_after_groupby_rank = True
    
    @staticmethod
    def tax_rank(rank):
        TAX_RANKS = TaxonomyGroupBy.TAX_RANKS
        if rank == 'class':
            rank = 'class_'
        return TAX_RANKS[:TAX_RANKS.index(rank)+1]

    def return_value(self, experiment):
        if self.operator == 'groupby':
            df = experiment.data_df
            rank = self.value
            tax_rank = TaxonomyGroupBy.tax_rank
            if rank is not None:
                taxlevels_to_rank = tax_rank(rank)
                df = experiment._counts_with_tax()
                #df2 = df.groupby(level=taxlevels_to_rank).sum().reset_index()
                df2 = df.groupby(taxlevels_to_rank).sum().reset_index()
                
                #drop extra levels (now columns)
                df2.drop([rnk for rnk in taxlevels_to_rank if rnk != rank], axis=1, inplace=True)
                try:
                    df2.drop(['otu'], axis=1, inplace=True)
                except ValueError: #not found
                    pass
                
                #further collapse similarly named ranks (e.g. "g__unidentified")
                if self.collapse_after_groupby_rank:
                    df2 = df2.groupby(rank).sum()
                else:
                    df2.index = df2[rank]
                    df2.drop([rank], axis=1, inplace=True)
    
                #remove "" i.e. No blast hit / Unassigned.
                df2.index = pd.Index([i if (i != '') else 'Unassigned' for i in df2.index], name=rank)
                return df2
            else:
                return df
            
    
class TaxonomyGroupByNoCollapse(GroupByFilter):
    collapse_after_groupby_rank = False


class Taxonomy(object):
    groupby = TaxonomyGroupBy()
    kingdom = TaxonomyAttributeFilter(attribute='kingdom')
    phylum = TaxonomyAttributeFilter(attribute='phylum')
    class_ = TaxonomyAttributeFilter(attribute='class')
    order = TaxonomyAttributeFilter(attribute='order')
    family = TaxonomyAttributeFilter(attribute='family')
    genus = TaxonomyAttributeFilter(attribute='genus')
    species = TaxonomyAttributeFilter(attribute='species')
    otu = TaxonomyAttributeFilter(attribute='otu')
    rank_resolution = TaxonomyAttributeFilter(attribute='rank_resolution')
    
