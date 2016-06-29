from omicexperiment.transforms.transform import Transform

class TaxonomyGroupBy(Transform):
    TAX_RANKS = ['kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species']
    
    def __init__(self, rank, collapse=True):
        self.rank = rank
        self.collapse = collapse
    
    @staticmethod
    def tax_rank_levels(highest_res_rank):
        TAX_RANKS = TaxonomyGroupBy.TAX_RANKS
        if highest_res_rank == 'class':
            highest_res_rank = 'class_'
        return TAX_RANKS[:TAX_RANKS.index(highest_res_rank)+1]

    def apply_transform(self, experiment):
        
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
            
        return experiment.with_data_df(groupby_df)
    
    