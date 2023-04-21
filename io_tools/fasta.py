import os
from biotite.sequence import ProteinSequence
import numpy as np

def load_all(path: str, file_type: str = '.fasta', biotite: bool = False) -> tuple:
    """
    Loads all fasta files from a directory, returns the names/ids and sequences as lists.

    Parameters:
        path (str): path to directory containing fasta files
        file_type (str): some fastas are stored with different file endings. Default '.fasta'.
        biotite (bool): returns sequences as biotite.sequence.ProteinSequence object

    Returns:
        tuple: two lists containing the names and sequences

    Example:
        names, sequences = load_fastas('/path/to/fastas')
    """
    files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(file_type)]

    names = []
    sequences = []
    for file in files:
        with open(file, 'r') as f:
            current_sequence = ""
            for line in f:
                line = line.strip()
                if line.startswith(">"):
                    if current_sequence:
                        sequences.append(current_sequence)
                    names.append(line[1:])
                    current_sequence = ""
                else:
                    current_sequence += line
            if biotite:
                sequences.append(ProteinSequence(current_sequence))
            else:
                sequences.append(current_sequence)

    return names, sequences


def load(file: str, biotite: bool = False) -> tuple:
    """
    Load all sequences in a fasta file. Returns names and sequences

    Parameters:
        file (str): path to file
        biotite (bool): returns sequences as biotite.sequence.ProteinSequence object

    Returns:
        tuple: two lists containing the names and sequences

    Example:
        names, sequences = load_fastas('example.fasta')
    """

    names = []
    sequences = []
    with open(file, 'r') as f:
        current_sequence = ""
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if current_sequence:
                    sequences.append(current_sequence)
                names.append(line[1:])
                current_sequence = ""
            else:
                current_sequence += line
        if biotite:
            sequences.append(ProteinSequence(current_sequence))
        else:
            sequences.append(current_sequence)

    return names, sequences


def write(names: list, sequences: list, dest: str = None):
    """
    Takes a list of names and sequences and writes a single
    fasta file containing all the names and sequences. The
    files will be saved at the destination

    Parameters:
        names (list): list of sequence names
        sequences (list): list of sequences
        dest (str): path to output file

    Example:
        write_fasta(names, sequences, './out.fasta')
    """
    assert type(names) == list and type(sequences) == list, 'names and sequences must be type list'
    assert len(names) == len(sequences), 'names and sequences must have the same length'

    with open(dest, 'w') as f:
        for i in range(len(names)):
            f.writelines('>' + names[i] + '\n')
            if i == len(names) - 1:
                f.writelines(sequences[i])
            else:
                f.writelines(sequences[i] + '\n')


def one_hot_encoding(sequence: str):
    '''
    Returns one hot encoding for amino acid sequence. Unknown amino acids will be
    encoded with 0.5 at in entire row.

    Parameters:
    -----------
        sequence (str): Amino acid sequence

    Returns:
    --------
        numpy.ndarray: One hot encoded sequence
    '''
    # Define amino acid alphabets and create dictionary
    amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
    aa_dict = {aa: i for i, aa in enumerate(amino_acids)}

    # Initialize empty numpy array for one-hot encoding
    seq_one_hot = np.zeros((len(sequence), len(amino_acids)))

    # Convert each amino acid in sequence to one-hot encoding
    for i, aa in enumerate(sequence):
        if aa in aa_dict:
            seq_one_hot[i, aa_dict[aa]] = 1.0
        else:
            # Handle unknown amino acids with a default value of 0.5
            seq_one_hot[i, :] = 0.5

    return seq_one_hot