"""Random strand generator"""
from random import randint

def generate_random_strand(length, before, after, debug=False):
    """Generate random strands for formatting"""
    alphabet = ["A", "T", "C", "G"]
    if debug:
        strand = "\033[30;47m"
    else:
        strand = ""
    for i in range(length):
        alpha = alphabet.copy()
        alpha.remove(before)
        if i == length-1:
            try:
                alpha.remove(after)
            except:
                pass
        strand += alpha[randint(0, len(alpha)-1)]
        before = strand[-1]
    if debug:
        return strand+"\033[0;30;40m"
    else:
        return strand

def compute_length(string):
    """Compute length of an oligo when including escape sequences"""
    leng = 0
    for car in string:
        if car in ['A', 'T', 'C', 'G']:
            leng += 1
    return leng
