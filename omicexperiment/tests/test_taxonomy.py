from unittest import TestCase

from omicexperiment.taxonomy import GreenGenesProcessedTaxonomy

class GreenGenesProcessedTaxonomyTestCase(TestCase):
    def setUp(self):
        pass       
   
    def test_highest_res_rank_tax_string_full(self):
        test_str = "k__Fungi;p__Ascomycota;c__Eurotiomycetes;o__Eurotiales;f__Trichocomaceae;g__Aspergillus;s__Aspergillus bombycis"
        tax = GreenGenesProcessedTaxonomy(test_str)
        self.assertEqual(tax.highest_res_rank, 'species')
    
    def test_highest_res_rank_tax_string_short(self):
        test_str = "k__Fungi;p__Ascomycota;c__Dothideomycetes;o__Pleosporales;f__Pleosporaceae"
        tax = GreenGenesProcessedTaxonomy(test_str)
        self.assertEqual(tax.highest_res_rank, 'family')
        test_str = "k__Fungi;p__Ascomycota;c__Eurotiomycetes;o__Eurotiales;f__Trichocomaceae;g__Aspergillus"
        tax = GreenGenesProcessedTaxonomy(test_str)
        self.assertEqual(tax.highest_res_rank, 'genus')
    
    def test_highest_res_rank_tax_string_contains_unidentified(self):
        test_str = "k__Fungi;p__Ascomycota;c__Dothideomycetes;o__unidentified;f__Pleosporaceae"
        tax = GreenGenesProcessedTaxonomy(test_str)
        self.assertEqual(tax.highest_res_rank, 'class')
        test_str = "k__Fungi;p__Ascomycota;c__unidentified;o__unidentified"
        tax = GreenGenesProcessedTaxonomy(test_str)
        self.assertEqual(tax.highest_res_rank, 'phylum')
    
    def test_highest_res_rank_tax_string_contains_emptystr(self):
        test_str = "k__Fungi;p__Ascomycota;c__;o__;f__"
        tax = GreenGenesProcessedTaxonomy(test_str)
        self.assertEqual(tax.highest_res_rank, 'phylum')
        test_str = "k__Fungi;p__Ascomycota;c__;o__unidentified"
        tax = GreenGenesProcessedTaxonomy(test_str)
        self.assertEqual(tax.highest_res_rank, 'phylum')
       
    def test_highest_res_rank_tax_string_unassigned(self):

        unassigned_test_strings = []
        
        unassigned_test_strings.append("No blast hit")
        unassigned_test_strings.append("unassigned")
        unassigned_test_strings.append("Unassigned")
        unassigned_test_strings.append("k__")
        unassigned_test_strings.append("k__unidentified")
        unassigned_test_strings.append("k__Unidentified")
        unassigned_test_strings.append("k__unidentified;")
        
        for test_str in unassigned_test_strings:
            tax = GreenGenesProcessedTaxonomy(test_str)
            self.assertEqual(tax.highest_res_rank_index, -1)
            self.assertEqual(tax.highest_res_rank, 'unassigned')


if __name__ == "__main__":
    from unittest import main
    main()
    