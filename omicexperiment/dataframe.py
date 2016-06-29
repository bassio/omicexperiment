import numpy as np
import pandas as pd
import hashlib
from pathlib import Path
from biom import parse_table
from biom import Table as BiomTable
from omicexperiment.taxonomy import tax_as_dataframe

def load_biom(biom_filepath):
    with open(biom_filepath) as f:
        t = parse_table(f)
    return t


def is_biomtable_object(obj):
    return isinstance(obj, BiomTable) 


def biomtable_to_dataframe(biom_table_object):
  _bt = biom_table_object
  data = _bt.matrix_data.todense()
  out = pd.SparseDataFrame(data, index=_bt.ids('observation'),
                           columns=_bt.ids('sample'))
  return out.to_dense()


def biomtable_to_sparsedataframe(biom_table_object):
  _bt = biom_table_object
  m = _bt.matrix_data
  data = [pd.SparseSeries(m[i].toarray().ravel()) for i in np.arange(m.shape[0])]
  out = pd.SparseDataFrame(data, index=_bt.ids('observation'),
                           columns=_bt.ids('sample'))
  return out


def load_biom_as_dataframe(biom_filepath):
    t = load_biom(biom_filepath)
    return biomtable_to_dataframe(t)


def load_fasta(fasta_filepath, calculate_sha1=False):
    import hashlib
    from omicexperiment.util import parse_fasta
    
    descs = []
    seqs = []
    for desc, seq in parse_fasta(fasta_filepath):
        descs.append(desc)
        seqs.append(seq)
        
    fasta_df = pd.DataFrame({'description': descs, 'sequence': seqs})

    del descs
    del seqs

    #fasta_df.drop('description', axis=1, inplace=True)
    if calculate_sha1:
        fasta_df['sha1'] = fasta_df['sequence'].apply(lambda x: hashlib.sha1(x.encode('utf-8')).hexdigest())

    return fasta_df

def load_fasta_counts(fasta_filepath, sample_name=None):
    fasta_df = load_fasta(fasta_filepath, calculate_sha1=True)
    if sample_name is None:
        counts = fasta_df['sha1'].value_counts().to_frame(name='count')
    else:
        counts = fasta_df['sha1'].value_counts().to_frame(name=sample_name)
        
    fasta_df.drop('description', axis=1, inplace=True)
    
    fasta_df.set_index('sha1', inplace=True)
    
    joined_df = counts.join(fasta_df)
    joined_df.index.name = 'sha1'
    
    return joined_df.drop_duplicates()


def counts_table_from_fasta_files(fasta_filepaths, sample_names=None):
    
    if sample_names is None:
        sample_names = [None for i in range(len(fasta_filepaths))]
                        
    concated_df = None
    seq_sha1_df = None
    
    for fasta, sample_name in zip(fasta_filepaths, sample_names):
        fasta_df = load_fasta_counts(fasta, fasta)
        seq_sha1_df = pd.concat([seq_sha1_df, fasta_df['sequence']])
        fasta_df.drop('sequence', axis=1, inplace=True)
        concated_df = pd.concat([concated_df, fasta_df])
        del fasta_df
        
    concated_df = concated_df.fillna(0).groupby(level=0).sum()
    concated_df.set_index(seq_sha1_df.drop_duplicates(), append=True, inplace=True)
    
    return concated_df

    
def load_fasta_descriptions(fasta_filepath):
    import hashlib
    from skbio.parse.sequences import parse_fasta
    
    descs = []
    for desc, seq in parse_fasta(fasta_filepath):
        descs.append(desc)
        
    fasta_df = pd.DataFrame({'description': descs})

    del descs

    return fasta_df


def fasta_df_to_counts_table(fasta_df, desc_to_sampleid_func, index='sha1'):
    fasta_df['sample'] = fasta_df['description'].apply(desc_to_sampleid_func)
    
    if index == 'sha1' \
    and 'sha1' not in fasta_df.columns:
        fasta_df['sha1'] = fasta_df['sequence'].apply(lambda x: hashlib.sha1(x).hexdigest())
    
    pivoted = fasta_df.pivot_table(index=index, columns='sample', aggfunc='count', fill_value=0)
    
    fasta_df.drop(['sample', 'sha1'], axis=1, inplace=True)
    
    pivoted.columns = pivoted.columns.droplevel()
    
    #sha1_seqs = pivoted.index.to_series().apply(lambda x: hashlib.sha1(x).hexdigest())
    #sha1_seqs.name = 'sha1'
    #pivoted.set_index(sha1_seqs, append=True, inplace=True)
    
    return pivoted


def load_uc_file(uc_filepath):
    columns = ['Type', 'Cluster', 'Size', 'Id', 'Strand', 'Qlo', 'Tlo', 'Alignment', 'Query', 'Target']
    df = pd.read_csv(uc_filepath, names=columns, header=None, sep="\t")
    df.rename(columns={'Query': 'read', 'Cluster': 'cluster'}, inplace=True)
    
    #check for size annotations and take them away
    sizes_in_labels = df['read'].apply(lambda x: ';size=' in x).any()

    if sizes_in_labels:
        df['read'] = df['read'].apply(lambda x: x.split(';size=')[0])
        
    
    df = df[df['Type'] != 'C']
    seeds = df[df['Type'] == 'S']
    df_joined = pd.merge(df, seeds, on='cluster', suffixes=('', '_seed'), left_index=True)
    df_joined.rename(columns={'read_seed': 'seed'}, inplace=True)
    
    df_joined.set_index('read', drop=False, inplace=True)
    
    return df_joined[['read','cluster', 'seed']]



def load_swarm_otus_file(swarm_otus_filepath):
    columns = ['amplicon_a', 'amplicon_b', 'differences', 'cluster', 'steps']
    swarms_df = pd.read_csv(swarm_otus_filepath, \
                            names=columns, \
                            sep="\t")
    duplicate_amplicons = swarms_df.drop_duplicates('amplicon_a')
    duplicate_amplicons['amplicon_b'] = duplicate_amplicons['amplicon_a']
    concat_df = pd.concat([swarms_df, duplicate_amplicons]).drop_duplicates('amplicon_b')
    concat_df.rename(columns={'amplicon_b': 'read'}, inplace=True)
    concat_df.set_index('read', drop=False, inplace=True)
    return concat_df[['read', 'cluster']].sort_values('cluster')


def load_qiime_otu_assignment_file(otu_assignment_filepath):
    with open(otu_assignment_filepath) as f:
        lines = f.readlines()
    
    read_to_otu_dict = OrderedDict()
    read_to_otu_tuples = []
    
    read_list = []
    otu_list = []

    for l in lines:
        splt = l.split()
        otu_name = splt[0].strip()
        reads = splt[1:]
        for r in reads:
            read = r.strip()
            read_list.append(read)
            otu_list.append(otu_name)
    
    read_to_otu_dict = OrderedDict(read=read_list, otu=otu_list)
    
    del read_list
    del otu_list
    
    df = pd.DataFrame(read_to_otu_dict, index=read_list)
    df.set_index('read', drop=False, inplace=True)

    return df


def load_taxonomy_dataframe(tax_file_or_tax_df):
    if isinstance(tax_file_or_tax_df, pd.DataFrame):
        return tax_file_or_tax_df
    elif isinstance(tax_file_or_tax_df, str):
        #assume file path
        tax_fp = Path(tax_file_or_tax_df)
        assert( tax_fp.exists() )
        return tax_as_dataframe(str(tax_fp))

def load_dataframe(input_file_or_obj, first_col_in_file_as_index=True):
    if isinstance(input_file_or_obj, str):
        #assume file path
        fp = Path(input_file_or_obj)
        assert(fp.exists())
        if fp.suffix == '.biom':
            df = load_biom_as_dataframe(str(fp))
            return df
        elif fp.suffix == '.csv':
            df = pd.read_csv(str(fp))
            if first_col_in_file_as_index:
                df.set_index(df.columns[0], drop=False, inplace=True)
            return df
        elif fp.suffix == '.tsv':
            df = pd.read_csv(str(fp), sep='\t')
            if first_col_in_file_as_index:
                df.set_index(df.columns[0], drop=False, inplace=True)
            return df
        
    elif isinstance(input_file_or_obj, pd.DataFrame):
        return input_file_or_obj

    elif isinstance(input_file_or_obj, BiomTable):
        return biomtable_to_dataframe(input_file_or_obj)
    
