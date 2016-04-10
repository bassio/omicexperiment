from collections import namedtuple
import pandas as pd

TAX_RANKS = ('kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species')
TAX_PREFIXES = ('k__', 'p__', 'c__', 'o__', 'f__', 'g__', 's__')

TaxonomyTuple = namedtuple('TaxonomyTuple', ['kingdom', 'phylum', 'class_', 'order', 'family', 'genus', 'species'])


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
  mapping_df.set_index('#SampleID', drop=False, inplace=True)
  transposed = dataframe.transpose()
  joined_df = transposed.join(mapping_df)
  return joined_df


def load_taxonomy_assignment_file_as_dataframe(tax_assignments_file):
  tax_file_df = pd.read_csv(tax_assignments_file, sep="\t", header=None, names=['otu','tax','evalue','tax_id'])

  if tax_file_df['otu'][0] == "#OTU ID":
    tax_file_df = pd.read_csv(tax_assignments_file, sep="\t", header=0, names=['otu','tax','evalue','tax_id'])

  return tax_file_df


class GreenGenesProcessedTaxonomy(object):

    def __init__(self, tax_string):
        self.tax_string = tax_string

    @property
    def tax_tuple_unprocessed(self):
        return tuple(taxon.strip() for taxon in self.tax_string.split(";"))

    @property
    def tax_tuple_no_prefix(self):
        return tuple(self.remove_prefix(taxon) for taxon in self.tax_tuple_unprocessed)

    @property
    def highest_res_rank_index(self):
        tuples = self.tax_tuple_no_prefix

        rank_index = -1

        for ind in range(len(tuples)):
            taxon = tuples[ind].strip()
            if self.is_unidentified(taxon):
                break

            rank_index += 1 #increment

        return rank_index

    @property
    def highest_res_rank(self):
        rank_index = self.highest_res_rank_index

        if rank_index == -1:
            highest_res_rank = 'unassigned'
        else:
            highest_res_rank = TAX_RANKS[rank_index]

        return highest_res_rank

    @property
    def rank_resolution(self):
        return self.highest_res_rank

    @property
    def highest_res_rank_assignment(self):
        rank_index = self.highest_res_rank_index

        if rank_index == -1:
            highest_res_rank_assignment = 'Unassigned'
        else:
            highest_res_rank_assignment = self.tax_tuple_unprocessed[rank_index]

        return highest_res_rank_assignment

    def process_tax_tuple(self):
        tax_tuple = self.tax_tuple_unprocessed
        highest_res_rank_index = self.highest_res_rank_index
        highest_res_rank_assignment = self.highest_res_rank_assignment

        tax_list = list(tax_tuple)

        for ind, taxon in enumerate(tax_tuple):
            if ind > highest_res_rank_index:
                if self.is_unidentified(taxon):
                    taxon = "{0}unidentified".format(TAX_PREFIXES[ind])
                tax_list[ind] = "{0} ({1})".format(taxon, highest_res_rank_assignment)
            else:
                tax_list[ind] = tax_list[ind]


        for extra_level in range(len(tax_list), 7):
            prefix = TAX_PREFIXES[extra_level]
            tax_list.append("{0}unidentified ({1})".format(prefix, highest_res_rank_assignment))

        return tax_list

    @property
    def tax_tuple(self):
        return TaxonomyTuple(*self.process_tax_tuple())

    @staticmethod
    def remove_prefix(taxon):
        if taxon[1:3] == '__':
            return taxon[3:]
        else:
            return taxon

    @staticmethod
    def is_unidentified(taxon):
        taxon_no_prefix = GreenGenesProcessedTaxonomy.remove_prefix(taxon)
        return taxon_no_prefix in ('', 'unidentified', 'No blast hit', 'Unassigned')


def tax_as_tuples(tax_assignments_file):
    tax_file_df = load_taxonomy_assignment_file_as_dataframe(tax_assignments_file)

    otu_to_taxonomy_tuples = []

    for row in zip(tax_file_df['otu'], tax_file_df['tax']):
        otu = row[0]

        taxonomy_obj = GreenGenesProcessedTaxonomy(row[1])
        tax = taxonomy_obj.tax_string
        rank_resolution = taxonomy_obj.rank_resolution
        tax_tuple = taxonomy_obj.tax_tuple

        otu_to_taxonomy_tuples.append((tax_tuple.kingdom, tax_tuple.phylum, tax_tuple.class_, tax_tuple.order, tax_tuple.family, tax_tuple.genus, tax_tuple.species, rank_resolution, tax, otu))

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
