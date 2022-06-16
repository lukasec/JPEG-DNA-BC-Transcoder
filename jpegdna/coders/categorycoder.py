"""Coder for categories"""

import numpy as np
from jpegdna.coders import AbstractCoder
from jpegdna.coders.huffmancoder import HuffmanCoder
from jpegdna.coders.goldmancoder import GoldmanCoderDNA, NonDecodableGoldman
from jpegdna.coders.hexcoder import HexCoder
from jpegdna.coders import AutomataGetterException

def find_category_ac(value):
    """Find the category of an ac value

    :param value: Value for which we want the category
    :type value: int
    :return: Category corresponding to the value
    :rtype: int
    """
    if value == 0:
        return 0
    if 1 <= abs(value) <= 5:
        return 1
    if 6 <= abs(value) <= 17:
        return 2
    if 18 <= abs(value) <= 82:
        return 3
    if 83 <= abs(value) <= 375:
        return 4
    if 376 <= abs(value) <= 1263:
        return 5
    if 1264 <= abs(value) <= 5262:
        return 6
    if 5263 <= abs(value) <= 17579:
        return 7
    return -1

# pylint: disable=missing-class-docstring
class NonDecodableCategory(KeyError):
    pass
# pylint: enable=missing-class-docstring


class ACCategoryCoder(AbstractCoder):
    """AC Category value coder

    :param d: Huffman n-ary dictionnary
    :type d: dict
    :param lut: Lut matrix
    :type lut: list
    :var verbose: Verbosity enabler
    :param verbose: bool
    :ivar goldman_coder: Goldman Coder
    :vartype goldman_coder: jpegdna.coders.goldmancoder.GoldmanCoderDNA
    :ivar ad_bits: length of the codeword for the category (initial value: 0)
    :vartype ad_bits: int
    :ivar code_length: length of the codeword for the value (initial value: 0)
    :vartype code_length: int
    """

    def __init__(self, d, lut, verbose=False):
        self.dic = d
        self.goldman_coder = GoldmanCoderDNA()
        self.ad_bits = 0
        self.code_length = 0
        self.lut = lut
        self.verbose = verbose

    def get_state(self, case=None):
        """Return new state after decoding

        :return: The number of bits it took in the stream and
                 the length of the codeword for this category
        :rtype: int, int
        """
        if case is not None and case != 'encode' and case != 'decode':
            raise AutomataGetterException("ACCategoryCoder: Invalid parameter, expected case parameter in {None|'encode'|'decode'}" +
                                          f" but got {case}.")
        return self.ad_bits, self.code_length

    @staticmethod
    def find_category(value):
        """Find the category of an ac value

        :param value: Value for which we want the category
        :type value: int
        :return: Category corresponding to the value
        :rtype: int
        """
        return find_category_ac(value)

    def encode(self, inp):
        """Encode the category of an AC value

        :param inp: Value to be encoded
        :type inp: str
        :return: The encoded message for the category
        :rtype: str
        """

        idx = np.nonzero(np.in1d(self.lut, inp))[0][0]
        huffcoder = HuffmanCoder(self.dic)
        huffcode = huffcoder.encode([str(idx)])
        goldman_inp_stream = "".join(huffcode)
        return self.goldman_coder.encode(goldman_inp_stream)

    def full_decode(self, code, *args):
        try:
            out = self.decode(code)
        except NonDecodableCategory as exc:
            raise exc
        return (out, self.get_state())

    def decode(self, code):
        """Decode the category of an AC value

        Stores the number of bits it took in the stream and
        stores the length of the codeword for this category

        :param code: Sequence to be decoded
        :type code: str
        :return: Decoded sequence
        :rtype: str
        """
        #print(code)
        category = 0
        max_huff = max(map(len, self.dic.values()))
        d_items = list(self.dic.items())
        try:
            if len(code) < max_huff:
                gold_dec = self.goldman_coder.decode(code)
            else:
                gold_dec = self.goldman_coder.decode(code[:max_huff])
        except NonDecodableGoldman:
            raise NonDecodableCategory()
        found = False
        for i in range(len(d_items)):
            diff_len = len(gold_dec) - len(d_items[i][1])
            if diff_len > 0:
                if d_items[i][1] == gold_dec[:-diff_len]:
                    category = int(d_items[i][0])
                    code_length = len(d_items[i][1])
                    found = True
                    break
            elif diff_len == 0:
                if d_items[i][1] == gold_dec:
                    category = int(d_items[i][0])
                    code_length = len(d_items[i][1])
                    found = True
                    break
        if not found:
            raise NonDecodableCategory()
        if category == 0:
            ad_bits = 0
        else:
            ad_bits = category+1
        self.ad_bits = ad_bits
        self.code_length = code_length
        if category < 160:
            return self.lut[category]
        elif category == 160:
            return 'F0'
        elif category == 161:
            return '00'
        else:
            raise ValueError("ACCategoryCoder: Wrong category value")

def find_category_dc(value):
    """Find the category of a dc value

    :param value: Value for which we want the category
    :type value: int
    :return: Category corresponding to the value
    :rtype: int
    """
    if value == 0:
        return 0
    if 1 <= abs(value) <= 5:
        return 1
    if 6 <= abs(value) <= 17:
        return 2
    if 18 <= abs(value) <= 82:
        return 3
    if 83 <= abs(value) <= 375:
        return 4
    if 376 <= abs(value) <= 1263:
        return 5
    if 1264 <= abs(value) <= 5262:
        return 6
    if 5263 <= abs(value) <= 17579:
        return 7
    if 17580 <= abs(value) <= 72909:
        return 8
    return -1


class DCCategoryCoder(AbstractCoder):
    """DC Category value coder

    :param d: Huffman n-ary dictionnary
    :type d: dict
    :var verbose: Verbosity enabler
    :param verbose: bool
    :ivar goldman_coder: Goldman Coder
    :vartype goldman_coder: jpegdna.coders.goldmancoder.GoldmanCoderDNA
    :ivar ad_bits: length of the codeword for the category (initial value: 0)
    :vartype ad_bits: int
    :ivar code_length: length of the codeword for the value (initial value: 0)
    :vartype code_length: int
    """

    def __init__(self, d, verbose=False):
        self.dic = d
        self.goldman_coder = GoldmanCoderDNA()
        self.ad_bits = 0
        self.code_length = 0
        self.verbose = verbose

    def get_state(self, case=None):
        """Return new state after decoding

        :return: The number of bits it took in the stream and
                 the length of the codeword for this category
        :rtype: int, int
        """
        if case is not None and case != 'encode' and case != 'decode':
            raise AutomataGetterException("DCCategoryCoder: Invalid parameter, expected case parameter in {None|'encode'|'decode'}" +
                                          f" but got {case}.")
        return self.ad_bits, self.code_length

    @staticmethod
    def find_category(value):
        """Find the category of a dc value

        :param value: Value for which we want the category
        :type value: int
        :return: Category corresponding to the value
        :rtype: int
        """
        return find_category_dc(value)

    def encode(self, inp):
        """Encode the category of an DC value

        :param input: Category to be encoded
        :type input: str
        :return: The encoded message for the category
        :rtype: str
        """
        huffcoder = HuffmanCoder(self.dic)
        huffcode = huffcoder.encode(inp)
        goldman_inp_stream = "".join(huffcode)
        return self.goldman_coder.encode(goldman_inp_stream)

    def full_decode(self, code, *args):
        try:
            out = self.decode(code)
        except NonDecodableCategory as exc:
            raise exc
        return (out, self.get_state())

    def decode(self, code):
        """Decode the category of a DC value

        :param code: Sequence to be decoded
        :type code: str
        :return: The decoded category
        :rtype: str
        """
        category = 0
        max_huff = max(map(len, self.dic.values()))
        d_items = list(self.dic.items())
        # print(code)
        try:
            if len(code) < max_huff:
                gold_dec = self.goldman_coder.decode(code)
            else:
                gold_dec = self.goldman_coder.decode(code[:max_huff])
        except NonDecodableGoldman:
            raise NonDecodableCategory()
        found = False
        for i in range(len(d_items)):
            diff_len = len(gold_dec) - len(d_items[i][1])
            if diff_len > 0:
                if d_items[i][1] == gold_dec[:-diff_len]:
                    category = int(d_items[i][0])
                    found = True
                    break
            elif diff_len == 0:
                if d_items[i][1] == gold_dec:
                    category = int(d_items[i][0])
                    found = True
                    break
        if not found:
            raise NonDecodableCategory()
        if category == 0:
            ad_bits = 0
        else:
            ad_bits = category+1
        code_length = len(d_items[category][1])
        self.ad_bits = ad_bits
        self.code_length = code_length
        return str(category)

def count_run_cat(seq_coeff, lut):
    """Counts the number of categories

    :param seq_coeff: Sequence of coefficients
    :type seq_coeff: list(int)
    :param lut: list of hexadecimal codes for categories
    :type lut: list
    """
    num_zeros = 0
    count_run_end = 0
    run_cat_count = np.zeros((160))
    count_run16 = 0
    for i in range(1, 64):
        if (seq_coeff[i:] == [0]*len(seq_coeff[i:])).all():
            count_run_end += 1
            break
        if num_zeros == 16:
            count_run16 += 1
            num_zeros = 0
        else:
            if seq_coeff[i] != 0:
                cat_ac = find_category_ac(seq_coeff[i])
                hexacoder = HexCoder()
                cat_hex = hexacoder.encode(cat_ac)
                zeros_hex = hexacoder.encode(num_zeros)
                runsize = zeros_hex + cat_hex
                idx = np.nonzero(np.in1d(lut, runsize))[0][0]
                run_cat_count[idx] += 1
                num_zeros = 0
            else:
                num_zeros += 1
    return count_run_end, run_cat_count, count_run16
