import pandas as pd

TAX_RANKS = ['kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species']


def tax_rank(rank):
  if rank == 'class':
    rank = 'class_'
  return TAX_RANKS[:TAX_RANKS.index(rank)+1]


def is_kingdom_unassigned(kingdom_assignment):
  if kingdom_assignment == 'Unassigned':
    return True
  elif 'No blast hit' in kingdom_assignment:
    return True
  elif 'k__' not in kingdom_assignment:
    return True

  return False

  
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
            taxon = tax_splt[rank_index].strip()
            if taxon[3:] == "": #i.e. g__ only or s__ only
                rank_index -= 1 #the highest rank known is actually the rank up in the tree
                break
            else:
                tax_dict[rank] = taxon
        
        highest_res_rank = TAX_RANKS[rank_index]
        
        if highest_res_rank == 'kingdom' \
        and is_kingdom_unassigned(tax_dict[highest_res_rank]):
            highest_res_rank = 'unassigned'
            highest_res_assignment = 'Unassigned'
            
        else:
            highest_res_assignment = tax_dict[highest_res_rank]
            
        empty_ranks = TAX_RANKS[rank_index+1:]
        
        for empty_rank in empty_ranks:
            tax_dict[empty_rank] = empty_rank[0:1] + "__unidentified ({})".format(highest_res_assignment)
            
    
        otu_to_taxonomy_tuples.append((tax_dict['kingdom'], tax_dict['phylum'], tax_dict['class'], tax_dict['order'], tax_dict['family'], tax_dict['genus'], tax_dict['species'], highest_res_rank, tax, otu))

    return otu_to_taxonomy_tuples

  
def tax_as_index(tax_assignments_file):
    otu_to_taxonomy_tuples = tax_as_tuples(tax_assignments_file)
    mi = pd.MultiIndex.from_tuples(otu_to_taxonomy_tuples, names=['kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species', 'rank_resolution', 'tax', 'otu'])
    return mi


def tax_as_dataframe(tax_assignments_file):
    otu_to_taxonomy_tuples = tax_as_tuples(tax_assignments_file)
    df = pd.DataFrame.from_records(otu_to_taxonomy_tuples, columns=['kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species', 'rank_resolution', 'tax', 'otu'])
    df.set_index('otu', drop=False, inplace=True)
    df['rank_resolution'] = df['rank_resolution'].astype("category", categories=['kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species'], ordered=True)
    return df

    
    
