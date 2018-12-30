 
import tempfile
import requests
import re
import ipykernel
import json
import yaml
from zipfile import ZipFile
from pathlib import Path
from io import StringIO
from collections import OrderedDict

from pandas import read_csv, DataFrame, Series
from biom.parse import load_table


class Qiime2ArtifactFile(object):    
    
    def __init__(self, pth):
        self.path = Path(pth).absolute()
        assert(self.path.exists())
        self._zipfile = None
        

    @property
    def __zipfile__(self):
        return ZipFile(str(self.path))
    
    @property
    def metadata_file(self):
        with ZipFile(str(self.path)) as myzip:
            for f in myzip.namelist():
                if f.endswith("metadata.yaml"):
                    return f
    @property
    def metadata(self):
        with self.__zipfile__ as myzip:
            with myzip.open(self.metadata_file) as metadata_yaml:
                return yaml.load(metadata_yaml)
            
    @property
    def __id__(self):
        return str(Path(self.metadata_file).parent.name)




class BiomTable(Qiime2ArtifactFile):
    __data_format__ = 'BIOMV210DirFmt'
    __semantic_type__ = 'FeatureTable[Frequency]'
    __singlefiledir_filename__ = 'feature-table.biom'
    
    @property
    def __data_path__(self):
        return str(Path(self.__id__) / 'data' / self.__singlefiledir_filename__)
    
    def load_data(self):
        with self.__zipfile__ as myzip:
            with tempfile.TemporaryDirectory() as tmpdir:
                extracted_file_pth_str = myzip.extract(self.__data_path__, tmpdir)
                return load_table(extracted_file_pth_str)
    
    def to_dataframe(self, astype='int64'):
        biom_table = self.load_data()
        if astype is None:
            return biom_table.to_dataframe().to_dense()
        else:
            return biom_table.to_dataframe().to_dense().astype(astype)
    



class TaxonomyAssignment(Qiime2ArtifactFile):
    __data_format__ = 'TSVTaxonomyDirectoryFormat'
    __semantic_type__ = 'FeatureData[Taxonomy]'
    __singlefiledir_filename__ = 'taxonomy.tsv'
    
    @property
    def __data_path__(self):
        return str(Path(self.__id__) / 'data' / self.__singlefiledir_filename__)
    
    def load_data(self):
        with self.__zipfile__ as myzip:
            with tempfile.TemporaryDirectory() as tmpdir:
                extracted_file_pth_str = myzip.extract(self.__data_path__, tmpdir)
                return read_csv(extracted_file_pth_str, sep="\t")
    
    def to_dataframe(self):
        tax_df = self.load_data()
        tax_df.rename(columns={'Feature ID': 'otu', 'Taxon': 'tax'}, inplace=True)
        tax_df.set_index('otu', drop=False, inplace=True)
        return tax_df
    


class NewickTree(Qiime2ArtifactFile):
    __data_format__ = 'NewickDirectoryFormat'
    __semantic_type__ = 'Phylogeny[Rooted]'
    __singlefiledir_filename__ = 'tree.nwk'
    
    @property
    def __data_path__(self):
        return str(Path(self.__id__) / 'data' / self.__singlefiledir_filename__)
    
    def load_data(self):
        with self.__zipfile__ as myzip:
            with tempfile.TemporaryDirectory() as tmpdir:
                extracted_file_pth_str = myzip.extract(self.__data_path__, tmpdir)
                with open(extracted_file_pth_str) as f:
                    return f.read()
    
    def to_treenode(self):
        from skbio.tree import TreeNode
        data_str = self.load_data()
        treenode = TreeNode.read(StringIO(data_str))
        return treenode
    
    def to_dataframe(self):
        tree = self.to_treenode()
        all_nodes = [l for l in tree.root().preorder()]

        all_nodes = {node: len(node.ancestors()) for node in all_nodes}
        nodes_ancestors = [[node] + node.ancestors() for node in all_nodes]

        lst_of_dcts = [OrderedDict({i:n.name for (i,n) in enumerate(reversed(lstn))}) for lstn in nodes_ancestors]
        
        dct_of_dcts = OrderedDict()
        for i, dct in enumerate(lst_of_dcts):
            last_node_ie_tip = next(reversed(dct.values()))
            dct_of_dcts[i] = last_node_ie_tip
                          

        df_nodes = DataFrame(lst_of_dcts, index=dct_of_dcts.values())
        df_nodes.index.name = 'node'

        col_levels = [c for c in df_nodes.columns]
        df_nodes = df_nodes.drop_duplicates().reset_index().set_index(col_levels)
        
        return df_nodes
    


class DistanceMatrix(Qiime2ArtifactFile):
    __data_format__ = 'DistanceMatrixDirectoryFormat'
    __semantic_type__ = 'DistanceMatrix'
    __singlefiledir_filename__ = 'distance-matrix.tsv'
    
    @property
    def __data_path__(self):
        return str(Path(self.__id__) / 'data' / self.__singlefiledir_filename__)
    
    def load_data(self):
        with self.__zipfile__ as myzip:
            with tempfile.TemporaryDirectory() as tmpdir:
                extracted_file_pth_str = myzip.extract(self.__data_path__, tmpdir)
                return read_csv(extracted_file_pth_str, sep="\t", index_col=0)
    
    def to_dataframe(self):
        dm_df = self.load_data()
        return dm_df
    
