import pandas as pd

TAX_RANKS = ['kingdom', 'phylum', 'class_', 'order', 'family', 'genus', 'species']

def tax_rank(rank):
  if rank == 'class':
    rank = 'class_'
  return TAX_RANKS[:TAX_RANKS.index(rank)+1]

def relative_abundance_by_sample(dataframe):
  return dataframe.apply(lambda c: c / c.sum() * 100, axis=0)

def relative_abundance(dataframe, sort_values=True):
  rel_abundances_taxa = relative_abundance_by_sample(dataframe).mean(axis=1)
  if sort_values:
    return rel_abundances_taxa.sort_values(ascending=False)
  else:
    return rel_abundances_taxa

def add_mapping_dataframe(counts_dataframe, mapping_dataframe):
  mapping_df = mapping_dataframe.copy()
  mapping_df.index = mapping_df['#SampleID']
  transposed = dataframe.transpose()
  joined_df = transposed.join(mapping_df)
  return joined_df

def load_taxonomy_assignment_file_as_dataframe(tax_assignments_file):
  tax_file_df = pd.read_csv(tax_assignments_file, sep="\t", header=None, names=['otu','tax','evalue','tax_id'])
    
  if tax_file_df['otu'][0] == "#OTU ID":
    tax_file_df = pd.read_csv(tax_assignments_file, sep="\t", header=0, names=['otu','tax','evalue','tax_id'])
  
  return tax_file_df
  
def tax_as_tuples(tax_assignments_file):
  tax_file_df = load_taxonomy_assignment_file_as_dataframe(tax_assignments_file)
    
  otu_to_taxonomy_tuples = []

  for row in zip(tax_file_df['otu'], tax_file_df['tax'].apply(lambda c: [c.strip() for c in c.split(";")])):
    otu = row[0]
    tax_splt = row[1]
    tax = ";".join(tax_splt)
    tax_dict = {}
    
    kingdom = ""
    phylum = ""
    class_ = ""
    order = ""
    family = ""
    genus = ""
    species = ""
    
    for rank_index in range(len(tax_splt)):
      rank = TAX_RANKS[rank_index]
      tax_dict[rank] = tax_splt[rank_index].strip()
    else:
      if len(tax_splt) > 2:
        highest_res_rank = TAX_RANKS[rank_index]
        highest_res_assignment = tax_dict[highest_res_rank]
        empty_ranks = TAX_RANKS[rank_index+1:]
        for empty_rank in empty_ranks:
            tax_dict[empty_rank] = empty_rank[0:1] + "__unidentified ({high_res})".format(high_res = highest_res_assignment)
      else:
        highest_res_rank = TAX_RANKS[len(tax_splt)]
        empty_ranks = TAX_RANKS[rank_index:]
        for empty_rank in empty_ranks:
            tax_dict[empty_rank] = "Unassigned"
        
  
    otu_to_taxonomy_tuples.append((tax_dict['kingdom'], tax_dict['phylum'], tax_dict['class_'], tax_dict['order'], tax_dict['family'], tax_dict['genus'], tax_dict['species'], tax, otu))

  return otu_to_taxonomy_tuples
  
def tax_as_index(tax_assignments_file):
  otu_to_taxonomy_tuples = tax_as_tuples(tax_assignments_file)
  mi = pd.MultiIndex.from_tuples(otu_to_taxonomy_tuples, names=['kingdom', 'phylum', 'class_', 'order', 'family', 'genus', 'species', 'tax', 'otu'])
  return mi

def tax_as_dataframe(tax_assignments_file):
  otu_to_taxonomy_tuples = tax_as_tuples(tax_assignments_file)
  df = pd.DataFrame.from_records(otu_to_taxonomy_tuples, columns=['kingdom', 'phylum', 'class_', 'order', 'family', 'genus', 'species', 'tax', 'otu'])
  df.index = df['otu']
  return df


def biom_dataframe_with_tax(otu_table, tax_assignments_file, groupby=None, rank=None, collapse_after_rank=True):
  
  tax_multiindex = tax_as_index(tax_assignments_file)
  
  mi = tax_multiindex
  
  print(len(df.index), len(mi))
  
  assert len(df.index) == len(mi)
  
  df.index = mi
  
  if rank is not None:
    df2 = df.groupby(level=tax_rank(rank)).sum().reset_index()
    df2.drop([rnk for rnk in tax_rank(rank) if rnk != rank], axis=1, inplace=True)
    #further collapse similarly named ranks (e.g. "g__unidentified")
    if collapse_after_rank:
      df2 = df2.groupby(rank).sum()
    else:
      df2.index = df2[rank]
      df2.drop([rank], axis=1, inplace=True)
    
    #remove "" i.e. No blast hit.
    df2.index = pd.Index([i if (i != '') else 'No blast hit' for i in df2.index], name=rank)
    return df2
    
  if groupby is not None:
    return df.groupby(level=groupby)
  else:
    return df
  #df2 = df.groupby(level='otu').sum()  


    
def load_taxonomy(experiment, taxonomy_assignment_file):
    experiment.counts_df
    
    
