from unittest import TestCase

from omicexperiment.experiment.microbiome import MicrobiomeExperiment

class MicrobiomeExperimentTestCase(TestCase):
    def setUp(self):
        self.mapping = "data/example_map.tsv"
        self.biom = "data/example_fungal.biom"
        self.tax = "data/blast_tax_assignments.txt"
        self.exp = MicrobiomeExperiment(biom, mapping,tax)
        
    def test_init_load_biom_file(self):
        pass
        
    def test_init_load_tsv_file(self):
        pass
        
    def test_init_load_data_df_from_biom_file(self):
        df = self.exp.data_df
        self.assertEqual(df['sample0'].sum(), 86870)
        self.assertEqual(df['sample1'].sum(), 91943)
        self.assertEqual(df['sample2'].sum(), 100428)
        self.assertEqual(df[1234].sum(), 133140)
        self.assertEqual(df[9876].sum(), 225873)
        
    def test_init_load_mapping_df_from_tsv_file(self):
        df = self.exp.mapping_df
        self.assertIn('#SampleID', df.columns)
        self.assertEqual(df.index.name, '#SampleID')
        self.assertEqual(len(df.columns), 9)
        self.assertEqual(len(df.index), 5)
    
    def test_list_samples(self):
        samples = ['1234', '9876', 'sample0', 'sample1', 'sample2']
        for s in samples:
            self.assertIn(s, self.exp.samples)
    
    def test_list_observations(self):
        observations = ['2f328e48f4252bbade0dd7f66b0d5bf1b09617dd', 
                        'ae0ddda08027454fdb5db77c96b94691b8274cdd', 
                        '8f52abc02aed2ce6c63be04570a7e609f9cdac5f', 
                        '3cb3c2347cdbe128b645e432f4dcbca702e0e8e3', 
                        '8e9a3b9a9d91e86f21da1bd57b8ae4486c78bbe0']    
        
        for obs in observations:
            self.assertIn(obs, self.exp.observations)
    
    def 