import os
import pandas as pd
import sys
sys.path.append('../../../src/')
from proteusAI.ml_tools.esm_tools.esm_tools import *

# collect all datasets
mutant_datasets = [f for f in os.listdir('../datasets/')]

# create directories for all datasets
for dataset in mutant_datasets:
    study_name = dataset.split('.')[0]
    os.makedirs(f'representations/{study_name}', exist_ok=True)


# compute embeddings for all datasets
batch_size = 10
for dataset in mutant_datasets:
    
    # get names and sequences from dataframe
    df = pd.read_csv(f'representations/{study_name}.csv')
    sequences = df['mutated_sequence'].to_list()
    names = df['mutant'].to_list()
    
    for i in range(0, len(names), batch_size):
        # batch sequences and names
        batch_names = names[i:i+batch_size]
        batch_seqs = sequences[i:i+batch_size]
        
        # compute representations
        results, batch_lens, batch_labels, alphabet = esm_compute(batch_seqs, model=model)
        sequence_representations = get_seq_rep(results, batch_lens)
        
        # save representations
        for j, n in enumerate(batch_names):  # we need to use enumerate here to get the correct name for each sequence representation
            seq_rep_path = f'representations/{n}.pt'
            if not os.path.exists(seq_rep_path):  # check if file already exists
                torch.save(sequence_representations[j], seq_rep_path)