"""Helper functions for .mat data"""
import pickle
from scipy.io import loadmat

def load_lut_matrix(string):
    """Loads matrix values saved in .mat file"""
    return loadmat(string)["lut"]

def load_codebook_matrix(string):
    """Loads matrix values saved in .pkl file"""
    with open(string, "rb") as f:
        arr = pickle.load(f)
    return arr
