from omicexperiment.transforms.observation import ClusterObservations
from omicexperiment.dataframe import load_uc_file, load_swarm_otus_file, load_qiime_otu_map_file
import pandas as pd

class ClusterOTUs(ClusterObservations):
    def __init__(self, clusters_df):
        ClusterObservations.__init__(self, clusters_df)

    @classmethod
    def from_uc_file(cls, uc_filepath):
        clusters_df = load_uc_file(uc_filepath)
        clusters_df['cluster'] = clusters_df['seed']
        clusters_df = clusters_df[['observation', 'cluster']]
        return cls(clusters_df)

    @classmethod
    def from_swarm_otus_file(cls, swarm_otus_filepath):
        clusters_df = load_swarm_otus_file(swarm_otus_filepath)
        return cls(clusters_df)

    @classmethod
    def from_qiime_otu_map_file(cls, otu_map_file):
        clusters_df = load_qiime_otu_map_file(otu_map_file)
        return cls(clusters_df)
