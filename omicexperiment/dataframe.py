import numpy as np
import pandas as pd
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

def load_taxonomy_dataframe(tax_file_or_tax_df):
    if isinstance(tax_file_or_tax_df, pd.DataFrame):
        return tax_file_or_tax_df
    elif isinstance(tax_file_or_tax_df, str):
        #assume file path
        tax_fp = Path(tax_file_or_tax_df)
        assert( tax_fp.exists() )
        return tax_as_dataframe(str(tax_fp))

def load_dataframe(input_file_or_obj):
    if isinstance(input_file_or_obj, str):
        #assume file path
        fp = Path(input_file_or_obj)
        assert(fp.exists())
        if fp.suffix == '.biom':
            df = load_biom_as_dataframe(str(fp))
            return df
        elif fp.suffix == '.csv':
            df = pd.read_csv(str(fp))
            return df
        elif fp.suffix == '.tsv':
            df = pd.read_csv(str(fp), sep='\t')
            return df
        
    elif isinstance(input_file_or_obj, pd.DataFrame):
        return input_file_or_obj

    elif isinstance(input_file_or_obj, BiomTable):
        return biomtable_to_dataframe(input_file_or_obj)
    
