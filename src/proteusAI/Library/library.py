# This source code is part of the proteusAI package and is distributed
# under the MIT License.

__name__ = "proteusAI"
__author__ = "Jonathan Funk"

import os
import sys
current_path = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.join(current_path, '..')
sys.path.append(root_path)
from proteusAI.Protein.protein import Protein
from proteusAI.Library.esm_tools import *
import pandas as pd
from typing import Union, Optional



class Library:
    """
    The Library object holds information about proteins, labels and representations.
    It is also used to create mathematical representations of proteins.

    The library object serves as input to Model objects, to train machine learning models.

    Attributes:
        project (str): Path to the project. Will create one if the path does not exist.
        data (str): Path to data file ().
        proteins (list): List of proteins.
    """
    representation_types = ['esm1v', 'esm2', 'vae']

    def __init__(self, project: str, overwrite: bool = False, names: Union[list, tuple] = [], seqs: Union[list, tuple] = [], proteins: Union[list, tuple] = [], y: Union[list, tuple] = [], y_type: str = None):
        """
        Initialize a new library.

        Args:
            name (str): Path to library.
            overwrite (bool): Allow to overwrite files if True.
            names (list): List of protein names.
            seqs (list): List of sequences as strings.
            proteins (Protein, optional): List of proteusAI protein objects.
            y (list): List of y values.
            y_type: Type of y values class ('class') or numeric ('num') 
        """
        self.project = project
        self.overwrite = overwrite
        self.proteins = proteins
        self.names = names
        self.seqs = seqs
        self.reps = []
        
        # handle case if library does not exist
        if not os.path.exists(self.project):
            self.initialize_library()

        # if the library already exists
        else:
            # load existing information
            print(f"Library {project} already exists. Loading existing library...")
            self.load_library()

    def initialize_library(self):
        """
        initializing a new library.
        """
        print(f"Initializing library '{self.project}'...")
        
        # create project library
        os.makedirs(self.project)
        print(f"library created at {self.project}")

        # check if sequence have been provided
        if len(self.seqs) > 0:
            # create dummy names if no names are provided
            if len(self.seqs) != len(self.names):
                print(f"Number of sequences ({len(self.seqs)}), does not match the number of names ({len(self.names)})")
                print("Dummy names will be created")
                self.names = [f"protein_{i}" for i in range(len(self.seqs))]

            # create protein objects
            for name, seq in zip(self.names, self.seqs):
                protein = Protein(name, seq)
                self.proteins.append(protein)

        print('Done!')

    def load_library(self):
        """
        Load an existing library.
        """
        print(f"Loading library '{self.project}'...")

        # Check for data
        data_path = os.path.join(self.project, 'data')
        if os.path.exists(data_path):
            data_files = os.listdir(data_path)
            if len(data_files) > 0:
                for dat in data_files:
                    print(f"- Found '{dat}' in 'data/'.")

        # Check for models
        models_path = os.path.join(self.project, 'models')
        if os.path.exists(models_path):
            cls_path = os.path.join(models_path, 'cls')
            if os.path.exists(cls_path):
                classifier_models = os.listdir(cls_path)
                print(f"- Found {len(classifier_models)} classifier models in 'models/cls'.")

            reg_path = os.path.join(models_path, 'reg')
            if os.path.exists(reg_path):
                regressor_models = os.listdir(reg_path)
                print(f"- Found {len(regressor_models)} regressor models in 'models/reg'.")

        # Check for representations
        rep_path = os.path.join(self.project, 'rep')
        if os.path.exists(rep_path):
            for rep_type in self.representation_types:
                rep_type_path = os.path.join(rep_path, rep_type)
                if os.path.exists(rep_type_path):
                    self.reps.append(rep_type)
                    print(f"- Found representations of type '{rep_type}' in 'rep/{rep_type}'.")

        print("Loading done!")


    def read_data(self, data: str, seqs: str, y: str, y_type: str='num', names: str = None, sheet: Optional[str] = None):
        """
        Reads data from a CSV or Excel file and populates the Library object.

        Args:
            data (str): Path to the data file (CSV or Excel).
            seqs (str): Column name for sequences in the data file.
            y (str): Column name for y values in the data file.
            y_type (str): Type of y values ('class' or 'num').
            names (str, optional): Column name for sequence names in the data file.
            sheet (str, optional): Name of the Excel sheet to read.
        """
        # Determine file type based on extension
        file_ext = os.path.splitext(data)[1].lower()

        if file_ext in ['.xlsx', '.xls']:
            if sheet is None:
                df = pd.read_excel(data)
            else:
                df = pd.read_excel(data, sheet_name=sheet)
        elif file_ext == '.csv':
            df = pd.read_csv(data)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

        # Validate the columns exist
        if seqs not in df.columns or y not in df.columns:
            raise ValueError("The provided column names do not match the columns in the data file.")

        self.seqs = df[seqs].tolist()
        self.y = df[y].tolist()

        # If names are not provided, generate dummy names
        if names not in df.columns:
            self.names = [f"protein_{i}" for i in range(len(self.seqs))]
        else:
            self.names = df[names].tolist()

        # Create protein objects from names and sequences
        self.proteins = [Protein(name, seq) for name, seq in zip(self.names, self.seqs)]

        # check for available representations, store in protein object if representation is found
        print(self.reps)
        if len(self.reps) > 0:
            for rep in self.reps:
                rep_path = os.path.join(self.project, f"rep/{rep}")
                proteins = []
                rep_names = [f for f in os.listdir(rep_path) if f.endswith('.pt')]
                for protein in self.proteins:
                    f_name = protein.name + '.pt'
                    if f_name in rep_names:
                        protein._rep.append(rep)
                    proteins.append(protein)

                self.proteins = proteins
    
    def compute(self, method: str, model = None, batch_size: int = 1):
        """
        Compute representations for proteins.

        Args:
            method (str): Method for computing representation
            batch_size (int, optional): Batch size for representation computation.
        """
        
        assert method in self.representation_types, f"'{method}' is not a supported method"
        assert isinstance(batch_size, (int, type(None)))

        if method in ["esm2", "esm1v"]:
            self.esm_builder(model=method, batch_size=batch_size)
    
    def esm_builder(self, model: str="esm2", batch_size: int=1):
        """
        Computes esm representations.

        Args:
            model (str): Supports esm2 and esm1v.
            batch_size (int): Batch size for computation.
        """

        dest = os.path.join(self.project, f"rep/{model}")
        if not os.path.exists(dest):
            os.makedirs(dest)

        # Filtering out proteins that have already computed representations
        proteins_to_compute = [protein for protein in self.proteins if not os.path.exists(os.path.join(dest, protein.name + '.pt'))]

        # get names for and sequences for computation
        names = [protein.name for protein in proteins_to_compute]
        seqs = [protein.seq for protein in proteins_to_compute]
        
        # compute representations
        batch_compute(seqs, names, dest=dest, model=model, batch_size=batch_size)

        
        for protein in proteins_to_compute:
            if model not in protein.refs:
                protein.refs.append(model)