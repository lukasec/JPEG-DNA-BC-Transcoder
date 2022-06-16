"""General AC and DC coefficients coder"""

import numpy as np
from jpegdna.coders import AbstractCoder
from jpegdna.coders import ACCategoryCoder, DCCategoryCoder, NonDecodableCategory
from jpegdna.coders import HexCoder
from jpegdna.coders import ValueCoder
from jpegdna.coders import AutomataSetterException, AutomataGetterException


class ACCoefficientCoder(AbstractCoder):
    """AC Coefficient General Coder

    :param d: Huffman n-ary dictionnary
    :type d: dict
    :param lut: Lut matrix
    :type lut: list
    :var verbose: Verbosity enabler
    :param verbose: bool
    :ivar category_coder: category coder associated with the value coder
    :vartype category_coder: jpegdna.coders.categorycoder.ACCategoryCoder
    :ivar value_coder: value coder
    :vartype value_coder: jpegdna.coders.valuecoder.ValueCoder
    :ivar gold_code: goldman coded values for every hexa category value
    :vartype gold_code: list
    :ivar count_runcat_len: length of the encoded words for the categories
    :vartype count_runcat_len: int
    """

    def __init__(self, d, lut, codebook, verbose=False):
        self.d = d
        self.lut = lut
        self.category_coder = ACCategoryCoder(d, lut, verbose=verbose)
        self.value_coder = ValueCoder(codebook)
        self.gold_code = None
        self.count_runcat_len = None
        self.num_zeros, self.num_bits, self.end_of_block = None, None, None
        self.hexcoder = HexCoder()
        self.verbose = verbose

    def set_state(self, *args, case=None):
        """Sets the state of the coder

        :param gold_code: goldman code
        :type gold_code: str
        """
        if case is not None and case != 'encode' and case != 'decode':
            raise AutomataSetterException("ACCoefficientCoder: Invalid parameter, expected case parameter in {None|'encode'|'decode'}" +
                                          f" but got {case}")
        if len(args) != 1:
            raise AutomataSetterException(f"ACCoefficientCoder: Invalid umber of arguments, 1 expected (gold_code), {len(args)} given")
        self.gold_code = args[0]

    def get_state(self, case=None):
        """Return new state

        :return: The length of the codeword for this category (case 0: after encoding) or
                 The number of zeros in the stream,  number of bits it took in the stream,
                 if it is the end of the block (case 1: after decoding)
        :rtype: int | int, int, bool
        """
        if case == 'encode':
            return self.count_runcat_len
        if case == 'decode':
            return self.num_zeros, self.num_bits, self.end_of_block
        raise AutomataGetterException("ACCoefficientCoder: Invalid parameter, expected case parameter in {'encode'|'decode'}" +
                                      f" but got {case}")

    def full_encode(self, inp, *args):
        self.set_state(*args)
        code = self.encode(inp)
        return (code, self.get_state(case='encode'))

    def encode(self, inp):
        """Function for coding AC coefficients

        :param inp: Input to be encoded
        :type inp: list(int)
        """
        if self.verbose:
            print(f"----------\nEncoding AC coefficients:\n{inp}")
        count_runcat_len = 0
        ac_code = ""
        num_zeros = 0
        for i in range(1, 64):
            if (inp[i:] == [0]*len(inp[i:])).all():
                ac_code = ac_code + self.gold_code[161]
                count_runcat_len += len(self.gold_code[161])
                if self.verbose:
                    print(f"#EOB: {self.gold_code[161]}")
                break
            if num_zeros == 16:
                ac_code = ac_code + self.gold_code[160]
                count_runcat_len += len(self.gold_code[160])
                num_zeros = 0
                if self.verbose:
                    print(f"#16Z: {self.gold_code[160]}")
            else:
                if inp[i] != 0:
                    cat_ac = self.category_coder.find_category(inp[i])
                    cathex = self.hexcoder.encode(cat_ac)
                    zero_seq = self.hexcoder.encode(num_zeros)
                    runsize = zero_seq + cathex

                    idx = np.nonzero(np.in1d(self.lut, runsize))[0][0]
                    code_cat_ac = self.gold_code[idx]
                    code_value_ac = self.value_coder.full_encode(inp[i], cat_ac)
                    count_runcat_len += len(code_cat_ac)
                    coeff_code_ac = code_cat_ac + code_value_ac
                    ac_code = ac_code + coeff_code_ac
                    if self.verbose:
                        print(f"AC Coefficient {inp[i]}: category {cat_ac}, num_zeros {num_zeros}, runsize {runsize}, "\
                              f"category code: {code_cat_ac}, value code: {code_value_ac}, coeff code: {coeff_code_ac}")
                    num_zeros = 0
                else:
                    num_zeros += 1
                    if self.verbose:
                        print(f"#ZER, num zeros: {num_zeros}")
        self.count_runcat_len = count_runcat_len
        if self.verbose:
            print(f"Coded AC Coefficients: {ac_code}")
            print(f"Count runcat len: {self.count_runcat_len}")
        return ac_code

    def full_decode(self, code, *args):
        out = self.decode(code)
        return (out, self.get_state(case='decode'))

    def decode(self, code):
        """Function for decoding AC coefficients

        :param code: Sequence to be decoded
        :type code: str
        """
        try:
            (runsize, (_, code_length_ac)) = self.category_coder.full_decode(code)
        except NonDecodableCategory as exc:
            raise exc
        if runsize == '00':
            self.end_of_block = True
            ac_value = 0
            self.num_bits = len(self.d["161"])
            self.num_zeros = 0
        elif runsize == 'F0':
            self.end_of_block = False
            ac_value = 0
            self.num_bits = len(self.d["160"])
            self.num_zeros = 16
        else:
            self.end_of_block = False
            category = self.hexcoder.decode(runsize[1])
            if category > 7:
                raise NonDecodableCategory
            self.num_zeros = self.hexcoder.decode(runsize[0])
            if category == 0:
                ad_bits = 0
            else:
                ad_bits = category + 1
            ac_value = self.value_coder.full_decode(code, ad_bits, code_length_ac)
            self.num_bits = code_length_ac + ad_bits
        if self.verbose:
            print(f"Decoding AC coefficient from codeword {code[:self.num_bits]}: runsize = {runsize}, value = {ac_value}")
        return ac_value


class DCCoefficientCoder(AbstractCoder):
    """DC Coefficient General Coder

    :param d: Huffman n-ary dictionnary
    :type d: dict
    :var verbose: Verbosity enabler
    :param verbose: bool
    :ivar category_coder: category coder associated with the value coder
    :vartype category_coder: jpegdna.coders.categorycoder.DCCategoryCoder
    :ivar value_coder: value coder
    :vartype value_coder: jpegdna.coders.valuecoder.ValueCoder
    :ivar gold_code: goldman coded values for every hexa category value in the lut matrix
    :vartype gold_code: list
    :ivar count_cat_len: length of the encoded word for the category
    :vartype count_cat_len: int
    """

    def __init__(self, d, codebook, verbose=False):
        self.d = d
        self.category_coder = DCCategoryCoder(d, verbose=verbose)
        self.value_coder = ValueCoder(codebook)
        self.count_cat_len = None
        self.num_bits = None
        self.gold_code = None
        self.verbose = verbose

    def set_state(self, *args, case=None):
        """Set new state

        :param gold_code: Goldman code
        :type gold_code: str
        """
        if case is not None and case != 'encode' and case != 'decode':
            raise AutomataSetterException("DCCoefficientCoder: Invalid parameter, expected case parameter in {None|'encode'|'decode'}" +
                                          f" but got {case}")
        if len(args) != 1:
            raise AutomataSetterException(f"DCCoefficientCoder: Invalid umber of arguments, 1 expected (gold_code), {len(args)} given")
        self.gold_code = args[0]

    def get_state(self, case=None):
        """Return new state

        :return: The length of the codeword for this category (case 0: after encoding) or
                 The number of bits it took in the stream (case 1: after decoding)
        :rtype: int
        """
        if case == 'encode':
            return self.count_cat_len
        if case == 'decode':
            return self.num_bits
        raise AutomataGetterException("DCCoefficientCoder: Invalid parameter, expected case parameter in {'encode'|'decode'}" +
                                      f" but got {case}")

    def full_encode(self, inp, *args):
        self.set_state(*args)
        code = self.encode(inp)
        return (code, self.get_state(case='encode'))

    def encode(self, inp):
        """Function for coding a DC coefficient

        :param inp: Value to encode
        :type inp: int
        """
        if self.verbose:
            print("----------\nEncoding DC differential coefficient:")
        cat_diff = self.category_coder.find_category(inp)
        code_cat_diff = self.gold_code[cat_diff]
        self.count_cat_len = len(code_cat_diff)
        code_diff = self.value_coder.full_encode(inp, cat_diff)
        if inp != 0:
            dc_code = code_cat_diff + code_diff
            if self.verbose:
                print(f"DC Coefficient {inp}: category: {cat_diff},"\
                      f" category code: {code_cat_diff},"\
                      f" value code: {code_diff}, coeff code: {dc_code}")
        else:
            dc_code = code_cat_diff
            if self.verbose:
                print(f"DC Coefficient {inp}: category: {cat_diff},"\
                      f" category code: {code_cat_diff},"\
                      f" value code: {None}, coeff code: {dc_code}")

        return dc_code

    def full_decode(self, code, *args):
        out = self.decode(code)
        return (out, self.get_state(case='decode'))

    def decode(self, code):
        """Function for decoding a DC coefficient

        :param code: Sequence to be decoded
        :type code: str
        """
        try:
            (cat, (ad_bits, code_length)) = self.category_coder.full_decode(code)
            if int(cat) > 8:
                raise NonDecodableCategory
        except NonDecodableCategory as exc:
            raise exc
        dc_value = self.value_coder.full_decode(code, ad_bits, code_length)
        self.num_bits = code_length + ad_bits
        if self.verbose:
            print(f"----------\nDecoding DC differential coefficient from codeword {code[:self.num_bits]}: category = {cat}, diff value = {dc_value}")
        return dc_value
