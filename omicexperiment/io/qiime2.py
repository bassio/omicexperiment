 
import tempfile
import requests
import re
import ipykernel
import json
import yaml
from zipfile import ZipFile
from pathlib import Path

from pandas import read_csv
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
    
    def to_dataframe(self):
        biom_table = self.load_data()
        return biom_table.to_dataframe().to_dense().astype(int)
    



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
        tax_df.set_index('otu', inplace=True)
        return tax_df
    


