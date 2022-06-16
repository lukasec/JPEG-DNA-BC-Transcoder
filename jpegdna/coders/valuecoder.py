"""Value coder"""

import numpy as np
from jpegdna.coders import AbstractCoder
from jpegdna.coders import AutomataGetterException, AutomataSetterException, AutomataSetterExceptionEncode, AutomataSetterExceptionDecode

def get_codebook(ad_bits, codebook):
    """Returns the exhaustive codebooks for a given codeword length

    :param ad_bits: codewor length
    :type ad_bits: int
    :return: Codebook
    :rtype: list(str)
    """
    return codebook[ad_bits-2]

def compute_min_value(ad_bits):
    """Compute the min value for the codebook with codewords of length ad_bits

    :param ad_bits: codeword length
    :type ad_bits: int
    :return: min value
    :rtype: int
    """
    tab = [0, None, 1, 6, 18, 83, 376, 1264, 5263, 17580, 72910]
    return tab[ad_bits]

def compute_max_value(ad_bits):
    """Compute the max value for the codebook with codewords of length ad_bits

    :param ad_bits: codeword length
    :type ad_bits: int
    :return: max value
    :rtype: int
    """
    tab = [0, None, 5, 17, 82, 375, 1263, 5262, 17579, 72909, 305276]
    return tab[ad_bits]

class ValueCoder(AbstractCoder):
    """Value Coder

    :var verbose: Verbosity enabler
    :param verbose: bool
    :ivar category: category in which belongs the value
    :vartype category: int
    :ivar ad_bits: length of the word coding the value
    :vartype ad_bits: int
    """

    def __init__(self, codebook, verbose=False):
        self.category = 0
        self.ad_bits = 0
        self.code_length = 0
        self.verbose = verbose
        self.codebook = codebook

    def set_state(self, *args, case=None):
        """Sets the state for the decoding"""
        if len(args) == 1 and case == 'encode':
            self.category = args[0]
        elif case == 'encode':
            raise AutomataSetterExceptionEncode(f"ValueCoder: Invalid number of parameters, 1 expected, {len(args)} given.")
        elif len(args) == 2 and case == 'decode':
            self.ad_bits = args[0]
            self.code_length = args[1]
        elif case == 'decode':
            raise AutomataSetterExceptionDecode(f"ValueCoder: Invalid number of parameters, 2 expected, {len(args)} given.")
        else:
            raise AutomataSetterException("ValueCoder: Invalid parameters, expected case parameter in {'encode'|'decode'}" +
                                          f" but got {case}")

    def get_state(self, case=None):
        """Return new state after encoding

        :return: The number of bits it took in the stream and
                 the length of the codeword for this category
        :rtype: int, int
        """
        if case is not None and case != 'encode' and case != 'decode':
            raise AutomataGetterException("ValueCoder: Invalid parameter, expected case parameter in {None|'encode'|'decode'}" +
                                          f" but got {case}")
        return self.ad_bits, self.code_length

    def full_encode(self, inp, *args):
        self.set_state(*args, case='encode')
        return self.encode(inp)

    def encode(self, inp):
        """Encode a value according to a category

        :param inp: value to be encoded
        :type inp: int
        """
        if self.category == -1:
            raise ValueError("ValueCoder: Invalid value, out of range, category = -1")
        if self.category == 0:
            self.ad_bits = 0
            return ""
        else:
            self.ad_bits = self.category+1
        codebook = get_codebook(self.ad_bits, self.codebook)
        #TODO Prepare code for new codebooks
        min_val = compute_min_value(self.ad_bits)
        if inp > 0:
            # print((inp, min_val, self.ad_bits, len(codebook), (inp-min_val)))
            # print(inp-min_val)
            encoded = codebook[(inp-min_val)]
        else:
            # print((inp, min_val, self.ad_bits, len(codebook), (-abs(inp)-min_val)))
            # print(-(abs(inp)-min_val) - 1)
            encoded = codebook[-(abs(inp)-min_val) - 1]

        return encoded

    def full_decode(self, code, *args):
        self.set_state(*args, case='decode')
        return self.decode(code)

    def decode(self, code):
        """Decode a value

        :param code: Sequence to be decoded
        :type code: str
        """
        if self.ad_bits == 0:
            return 0
        codebook = get_codebook(self.ad_bits, self.codebook)
        code_value = code[self.code_length:self.code_length+self.ad_bits]
        idx = np.nonzero(np.in1d(codebook, code_value))
        try:
            idx = idx[0][0]
        except:
            return 0 # Cdeword not directly decodable because not in the codebook
        min_val, max_val = compute_min_value(self.ad_bits), compute_max_value(self.ad_bits)
        vecpos = list(range(min_val, max_val+1))
        vecneg = list(range(-max_val, -min_val+1))
        vec = vecpos + vecneg
        # print(vecpos)
        # print(vecneg)
        # print(len(vec))
        # print(vec)
        return vec[idx]
