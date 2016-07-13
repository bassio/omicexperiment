import hashlib
import pandas as pd


def parse_fasta(fasta_filepath):
    
    def _parse_fasta(fasta):
        with open(fasta) as f:
            seq = ""
            desc = ""

            for l in f:
                l = l.strip()
                if l.startswith(">"):
                    yield desc, seq
                    desc = l[1:]
                    seq = ""
                    continue
                else:
                    seq = seq + l
                    continue

    iter_fasta = iter(_parse_fasta(fasta_filepath))
    next(iter_fasta)
    for desc, seq in iter_fasta:
        yield desc, seq


def parse_fasta_relabel(fasta_filepath, relabel_fn=lambda x:x):
    for desc, seq in parse_fasta(fasta_filepath):
        yield relabel_fn(desc), seq


def parse_fastq(fastq_filepath):
    with open(fastq_filepath) as f:
        seq = ""
        desc = ""
        qual = ""
        
        for l in f:
            if l.startswith("@"):
                desc = l[1:].strip()
                seq = f.readline().strip()
                plus = f.readline()
                qual = f.readline().strip()
                yield desc, seq, qual
            else:
                raise
        
def counts_df_to_repset_fasta(fasta_counts_df, output_fasta, sizes_out=False):
    sums_df = fasta_counts_df.sum(axis=1).sort_values(ascending=False)
    with open(output_fasta, 'w') as f:
        if sizes_out:
            for (sha1, seq), size in sums_df.iteritems():
                f.write(">{0};size={1};\n".format(sha1,int(size)))
                f.write(seq + "\n")
        else:
            for sha1, seq in sums_df.index:
                f.write(">" + sha1 + "\n")
                f.write(seq + "\n")
                

def sha1_to_sequences(sequence_array):
    seq_series = pd.Series(sequence_array)
    seq_df = pd.DataFrame({'sequence':seq_series})
    seq_df['sha1'] = seq_df['sequence'].apply(lambda x: hashlib.sha1(x.encode('utf-8')).hexdigest())
    seq_df.set_index('sha1', inplace=True)
    return seq_df


def dataframe_to_fasta(sequence_df, filename):
    with open(filename, 'w') as f:
        for row in sequence_df[['sequence']].iterrows():
            print('>' + row[0], file=f) #identifier in index
            print(row[1][0], file=f) #sequence itself
    
    
#adapted from sqlalchemy's hybrid extension module:
# Copyright (C) 2005-2016 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
class hybridmethod(object):
    """A decorator which allows definition of a Python object method with both
    instance-level and class-level behavior.
    """
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        if instance is None:
            return self.func.__get__(owner, owner.__class__)
        else:
            return self.func.__get__(instance, owner)

