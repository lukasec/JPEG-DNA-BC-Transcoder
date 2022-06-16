"""Huffman n-ary tree coder"""

import math
import bisect
# from collections import defaultdict
from jpegdna.coders import AbstractCoder

def x_in_y(query, base):
    """Checks if query is a subsequence of base"""
    try:
        l = len(query)
    except TypeError:
        l = 1
        query = type(base)((query,))
    for i in range(len(base)):
        if base[i:i+l] == query:
            return True
    return False


class TreeNode(object):

    """Node with an arbitrary number of children.

    As such, it's missing a lot of features, but that's okay. Don't use it for
    a "real" tree."""

    def __init__(self, key, data, children=None):
        """Create the node with the given key, data, and children.

        :key: Any object that can be compared.
        :data: Any object.
        :children: Possibly empty list of TreeNodes.

        """
        self.key = key
        self.data = data
        if children is not None:
            self.children = children
        else:
            self.children = []

    def print(self):
        """Print the tree rooted at the node in tabular form.
        :returns: None

        """
        def _print(node, level):
            print("\t"*level + str((node.key, node.data)))
            for child in node.children:
                _print(child, level + 1)
        _print(self, 0)

    def __eq__(self, other):
        """Test equality with another node."""
        return self.key == other.key

    def __ne__(self, other):
        """Test inequality with another node."""
        return self.key != other.key

    def __lt__(self, other):
        """Test the less than inequality with another node."""
        return self.key < other.key

    def __le__(self, other):
        """Test the less than or equal to inequality with another node."""
        return self.key <= other.key

    def __gt__(self, other):
        """Test the greater than inequality with another node."""
        return self.key > other.key

    def __ge__(self, other):
        """Test the greater than or equal to inequality with another node."""
        return self.key >= other.key

def huffman_initial_count(message_count, digits):
    """
    Return the number of messages that must be grouped in the first layer for
    Huffman Code generation.

    :message_count: Positive integral message count.
    :digits: Integer >= 2 representing how many digits are to be used in codes.
    :returns: The number of messages that _must_ be grouped in the first level
              to form a `digit`-ary Huffman tree.

    """

    if message_count <= 0:
        raise ValueError("Huffman coder : cannot create Huffman tree with <= 0 messages!")
    if digits <= 1:
        raise ValueError("Huffman coder : must have at least two digits for Huffman tree!")

    if message_count == 1:
        return 1

    return 2 + (message_count - 2) % (digits - 1)

def combine_and_replace(nodes, n):
    """
    Combine n nodes from the front of the low-to-high list into one whose key is
    the sum of the merged nodes. The new node's data is set to None, then
    inserted into its proper place in the list.

    Note: The sum of keys made here is the smallest such combination.

    In the contradictory style of Huffman, if any set of nodes were chosen
    except for the first n, then changing a node not in the first n to one that
    is from the first n would reduce the sum of their keys. Thus the smallest
    sum is made from the first n nodes.

    :nodes: A list of TreeNodes.
    :n: Integer < len(nodes).
    :returns: Low-to-high list that combines the last n nodes into one.

    """
    group = nodes[:n]
    combined = TreeNode(sum(node.key for node in group), None, group)
    nodes = nodes[n:]
    bisect.insort(nodes, combined)

    return nodes

def indicies_to_code(path, digits):
    """Convert the path into a string.

    We join the indices directly, from most to least significant, keeping
    leading zeroes.
    Examples:
    [1, 2, 3] -> "123"
    [7, 2, 10] -> "72a"
    [0, 2, 1] ->  "021"
    """
    combination = ""
    for index in path:
        if index < 0:
            raise ValueError("Huffman coder : Negative path index")
        if index >= digits:
            raise ValueError("Huffman coder : Index superior to arity")

        combination += base_n(index, digits)

    return combination

def base_n(num, b, numerals="0123456789abcdefghijklmnopqrstuvwxyz"):
    """base_n"""
    return ((num == 0) and numerals[0]) or (base_n(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])

def huffman_nary_tree(probabilities, digits, verbose=False):
    """Return a Huffman tree using the given number of digits.

    :probabilities: List of tuples (symbol, probability) where probability is
                    any floating point and symbol is any object.
    :digits: Integral number of digits to use in the Huffman encoding. Must be
             at least two.
    :returns: TreeNode that is the root of the Huffman tree.

    """
    if digits <= 1:
        raise ValueError("Huffman coder : Arity must be superior to 2")

    if len(probabilities) == 0:
        raise ValueError("Huffman coder : Empty probability set")

    if len(probabilities) == 1:
        symbol, freq = probabilities[0]
        if freq != 1 and verbose:
            print(f"The probabilities sum to {freq} (!= 1)...")
        if math.isclose(freq, 1.0) and verbose:
            print("(but they are close)")

        return TreeNode(freq, symbol)

    # TreeNode does rich comparison on key value (probability), so we can
    # pass this right to sorted().
    probabilities = [TreeNode(freq, symbol) for (symbol, freq) in probabilities]
    probabilities = sorted(probabilities)

    # Grab the required first set of messages.
    initial_count = huffman_initial_count(len(probabilities), digits)
    probabilities = combine_and_replace(probabilities, initial_count)

    # If everything is coded correctly, this loop is guaranteed to terminate
    # due to the initial number of messages merged.
    while len(probabilities) != 1:
        # Have to grab `digits` nodes from now on to meet an optimum code requirement.
        probabilities = combine_and_replace(probabilities, digits)

    if probabilities[0].key != 1 and verbose:
        print(f"The probabilities sum to {probabilities[0].key} (!= 1)...")
        if math.isclose(probabilities[0].key, 1.0) and verbose:
            print("(but they are close)")

    return probabilities.pop()

def huffmandict(alphabet, freqs, n, verbose=False):
    """Function that creates the dictionnary for the huffman coder

    :param alphabet: List of elements that can be encoded
    :type alphabet: list
    :param freqs: List of appearence frequencies for each element in the alphabet
    :type freqs: list
    :param n: base of the n-ary tree
    :type n: int
    :var verbose: Verbosity enabler
    :param verbose: bool
    :var debug: Verbosity for debug enabler
    :param debug: bool

    :return: Codewords for each element of the alphabet
    :rtype: dict
    """
    probas = [el/sum(freqs) for el in freqs]
    couples_sym_prob = list(zip(alphabet, probas))
    def visit(node, path, decoding_dict):
        if len(node.children) == 0:
            code = indicies_to_code(path, n)
            decoding_dict[code] = node.data
        else:
            for k, child in enumerate(node.children):
                path.append(k)
                visit(child, path, decoding_dict)
                path.pop()

    root = huffman_nary_tree(couples_sym_prob, n, verbose=verbose)
    decoding_dict = dict()
    visit(root, [], decoding_dict)
    dic_items = decoding_dict.items()
    dic = dict(sorted([(str(el[1]), el[0]) for el in dic_items], key=lambda x: int(x[0])))
    if verbose:
        print(f"Huffman dictionnary:\n{dic}\nCodeword lengths:\n{dict([(el[0], len(el[1])) for el in dic.items()])}\n========================")
    return dic

class HuffmanCoder(AbstractCoder):
    """Huffman n-ary tree coder

    case 1:

    :param alphabet: List of elements that can be encoded
    :type alphabet: list
    :param feqs: List of appearence frequencies for each element in the alphabet
    :type freqs: list
    :param n: base of the n-ary tree
    :type n: int
    :var verbose: Verbosity enabler
    :param verbose: bool
    :var debug: Verbosity for debug enabler
    :param debug: bool

    case 2:

    :param dic: Huffman dictionnary
    :type dic: dict
    """

    def __init__(self, *args, verbose=False):
        if len(args) == 3:
            self.dic = huffmandict(*args, verbose=verbose)
        elif len(args) == 1:
            self.dic = args[0]
        else:
            raise ValueError("Huffman coder : Wrong number of arguments for Huffman instantiation, "\
                             "either use the Huffman dictionnary or the parameters for the huffmandict function as entry")
        self.verbose = verbose

    def find_codeword_key(self, word):
        """Find the symbol associated with a codeword in the huffman dictionnary

        :param word: codeword for which we want the symbol
        :type word: str
        :return: Symbol in the alphabet corresonding to the codeword
        :rtype: str
        """
        for sym, codeword in self.dic.items():
            if word == codeword:
                return sym
        return None

    def encode(self, inp):
        """Encode a signal using a Huffman n-ary dictionnary

        :param inp: Signal to be encoded
        :type inp: list
        :return: Encoded signal
        :rtype: str
        """
        enco = ""
        while inp != []:
            try:
                tmp_code = self.dic[inp[0]]
            except:
                tmp_code = []
                raise ValueError("Huffman coder : Invalid input, use the inputs defined in the huffman dictionnary")
            enco += tmp_code
            inp = inp[1:]
        return enco

    def decode(self, code):
        """Decode a signal using the Huffman n-ary dictionnary

        :param code: Signal to be decoded
        :type code: str
        :return: Decoded signal
        :rtype: list
        """
        decoded = []
        max_len_codeword = 0
        for el in self.dic.values():
            if len(el) > max_len_codeword:
                max_len_codeword = len(el)
        while code != "":
            for i in range(1, min(len(code)+1, max_len_codeword)):
                res = self.find_codeword_key(code[0:i+1])
                if res is not None:
                    decoded.append(res)
                    code = code[i+1:]
        return decoded
