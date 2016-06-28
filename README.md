# The *omicexperiment* python package

The omicexperiment package is an open-source, BSD-licensed, Python 3 package for analysis of dataframes of 'omic experiments', built upon the solid foundations of the Python scientific stack.

The omicexperiment package has the goal of providing a pleasant API for *rapid* analysis of 'omic experiments' in interactive environments.

The R bioinformatics community has already provided similar implementations for similar functionality.
Examples include DESeqDataSet (from the package DeSeq2), MRExperiment (from the package metagenomeSeq), phyloseq-class (from the package phyloseq).
To my knowledge, there exists no similar powerful functionality available to users of python.

The philosophy of this package is to build upon solid foundations of the python scientific stack and try not to re-invent the wheel. Packages such as numpy and pandas are powerful optimized libraries in dealing with matrix and tabular data, respectively. This package's backend thus consists almost entirely of pandas DataFrames and pandas APIs. 

## Example code

    from omicexperiment.experiment.microbiome import MicrobiomeExperiment
    from omicexperiment.filters import Sample, Taxonomy
    
    mapping = "example_map.tsv"
    biom = "example_fungal.biom"
    tax = "blast_tax_assignments.txt"
    
    #our Experiment object
    exp = MicrobiomeExperiment(biom, mapping,tax)

    #include only samples with more than 90000 counts
    exp.filter(Sample.count > 90000)
    
    ##collapse the OTUs in the _data_ DataFrame to genus level assignment
    exp.filter(Taxonomy.groupby('genus')) #any taxonomic rank can be passed
    

## Installation

Just clone the git repository.
Hopefully very shortly, the package will be uploaded to PyPi and will be pip-installable.

Due to bugs in handling numpy installation in setuptools, it is better to install numpy first using 'pip install numpy'.

## Dependencies

Current omicexperiment dependencies:

- numpy
- scipy
- pandas
- scikit-bio
- biom-format
- lxml
- pygal

## License

This package is released as open-source, under a BSD License. Please see COPYING.txt.

## Documentation

Please see the doc folder in the package (https://github.com/bassio/omicexperiment/tree/master/doc), it contains Jupyter notebooks that runs you through most of the current package functionality. 

## Acknowledgements

Thank you to all the great python bioinformatics and data science community for releasing their code as open source.

## Contributing and use in your research

Please be advised that at this stage, this package is still alpha software. Testing is still not implemented so be careful. But if you are interested in contributing to this project, please contact. Contributors are welcome to improve the software.
Nowadays, I expect the package to continue growing slowly as I add functionality and improvements as long as I need it in my own research. I will be initially focusing on developing the MicrobiomeExperiment part. 
