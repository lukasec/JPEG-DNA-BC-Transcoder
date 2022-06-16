"""Tests for the different coders implemented in jpegdna.coders"""

import numpy as np
from jpegdna.coders import GoldmanCoder
from jpegdna.coders import HuffmanCoder
from jpegdna.coders import HexCoder
from jpegdna.coders import ACCategoryCoder, DCCategoryCoder
from jpegdna.coders import DCCoefficientCoder, ACCoefficientCoder
from jpegdna.coders import ValueCoder
from jpegdna.coders.huffmancoder import huffmandict, x_in_y, huffman_nary_tree, huffman_initial_count, indicies_to_code
from jpegdna.coders.categorycoder import count_run_cat
from jpegdna.tools.loader import load_lut_matrix, load_codebook_matrix
from jpegdna.tools.exception_validator import expected_value_error
from jpegdna.tools.exception_validator import expected_non_decodable_category, expected_non_decodable_goldman
from jpegdna.tools.exception_validator import expected_getter_coder_error, expected_setter_coder_error
from jpegdna.tools.exception_validator import expected_setter_encode_coder_error, expected_setter_decode_coder_error

class TestHexCoder():
    """Tests on the hexadecimal coder"""
    def encode_decode_test(self):
        """Functionnal tests for the Hexadecimal coder: encode_decode_test"""
        hexa_coder = HexCoder()
        dec = 25
        hexa = hexa_coder.encode(dec)
        decoded = hexa_coder.decode(hexa)
        assert dec == decoded
    def decode_encode_test(self):
        """Functionnal tests for the Hexadecimal coder: decode_encode_test"""
        hexa_coder = HexCoder()
        hexa = "F3"
        dec = hexa_coder.decode(hexa)
        decoded = hexa_coder.encode(dec)
        assert hexa == decoded
    def encode_failure_test(self):
        """Functionnal tests for the Hexadecimal coder: encode_failure_test"""
        hexa_coder = HexCoder()
        dec = -1
        coded = hexa_coder.encode(dec)
        assert coded == "err"


class TestGoldmanCoder():
    """Tests on the Goldman coder"""
    def encode_test(self):
        """Functionnal tests for the Goldman coder: encode_test"""
        goldman_coder = GoldmanCoder(["A", "T", "C", "G"])
        seq = "012012012"
        encoded = goldman_coder.encode(seq)
        assert len(seq) == len(encoded)
    def decode_test(self):
        """Functionnal tests for the Goldman coder: decode_test"""
        goldman_coder = GoldmanCoder(["A", "T", "C", "G"])
        seq = "012012012"
        encoded = goldman_coder.encode(seq)
        decoded = goldman_coder.decode(encoded)
        assert len(encoded) == len(decoded)
    def encode_decode_test(self):
        """Functionnal tests for the Goldman coder: encode_decode_test"""
        goldman_coder = GoldmanCoder(["A", "T", "C", "G"])
        seq = "012012012"
        encoded = goldman_coder.encode(seq)
        decoded = goldman_coder.decode(encoded)
        assert seq == decoded
    @expected_non_decodable_goldman
    def goldman_coder_failure_test(self):
        """Failure tests for the Goldman coder: NonDecodableGoldman"""
        goldman_coder = GoldmanCoder(["A", "T", "C", "G"])
        encoded = "GGGGGGGGGGGGGGGGGGGGG"
        _ = goldman_coder.decode(encoded)
    @expected_value_error
    def goldman_coder_alphabet_failure_test(self):
        """Failure tests for the Goldman coder: ValueError"""
        _ = GoldmanCoder(["A", "T", "C", "A"])


class TestHuffmanCoder():
    """Tests on the Huffman tree coder"""
    def dictionnary_builder_test(self):
        """Functionnal tests for the Huffman coder: dictionnay_builder_test"""
        alpha = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        freqs = [1, 2, 25, 15, 3, 9, 18, 135, 225, 27]
        target = {'0': '01', '1': '02110', '2': '02111', '3': '00', '4': '020', '5': '0210', '6': '0212', '7': '022', '8': '1', '9': '2'}
        huffman_coder = HuffmanCoder(alpha, freqs, 3)
        print(huffman_coder.dic)
        assert huffman_coder.dic == target
    @expected_value_error
    def dictionnary_builder_failure_args_test(self):
        """Failure tests for the Huffman coder: ValueError"""
        alpha = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        freqs = [1, 2, 25, 15, 3, 9, 18, 135, 225, 27]
        _ = HuffmanCoder(alpha, freqs)
    @expected_value_error
    def dictionnary_builder_failure_arity_test(self):
        """Failure tests for the Huffman coder: ValueError"""
        alpha = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        freqs = [1, 2, 25, 15, 3, 9, 18, 135, 225, 27]
        _ = HuffmanCoder(alpha, freqs, 1)
    @expected_value_error
    def dictionnary_builder_failure_empty_alphabet_test(self):
        """Failure tests for the Huffman coder: ValueError"""
        alpha = []
        freqs = []
        _ = HuffmanCoder(alpha, freqs, 3)
    def huffman_n_ary_tree_almost_empty_alphabet_test(self):
        """Failure tests for the Huffman Tree builder: Warning"""
        probs = [(1, .99999)]
        _ = huffman_nary_tree(probs, 3)
        assert True
    def huffman_n_ary_tree_almost_normal_alphabet_test(self):
        """Failure tests for the Huffman Tree Builder: Warning"""
        probs = [(1, .49999), (2, 0.5)]
        _ = huffman_nary_tree(probs, 3)
        assert True
    @expected_value_error
    def huffman_initial_count_failure_negative_test(self):
        """Failure tests for helper function Huffman Initial Count: ValueError"""
        huffman_initial_count(0, 3)
        assert True
    @expected_value_error
    def huffman_initial_count_failure_digits_test(self):
        """Failure tests for helper function Huffman Initial Count: ValueError"""
        huffman_initial_count(5, 1)
        assert True
    def huffman_initial_count_margin_test(self):
        """Failure tests for helper function Huffman Initial Count"""
        res = huffman_initial_count(1, 3)
        assert res == 1
    @expected_value_error
    def indices_to_code_failure_negative_test(self):
        """Failure tests for helper function Huffman Initial Count: ValueError"""
        indicies_to_code([-1, 2, 2, 2], 3)
        assert True
    @expected_value_error
    def indices_to_code_failure_digits_test(self):
        """Failure tests for helper function Huffman Initial Count: ValueError"""
        indicies_to_code([25, 2, 2, 2], 1)
        assert True
    def encode_test(self):
        """Functionnal tests for the Huffman coder: encode_test"""
        alpha = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        freqs = [1, 2, 25, 15, 3, 9, 18, 135, 225, 27]
        huffman_coder = HuffmanCoder(alpha, freqs, 3)
        enco = huffman_coder.encode(list("1234567890"))
        print(enco)
        assert enco == '021100211100020021002120221201'
    @expected_value_error
    def encode_failure_test(self):
        """Failure tests for the Hufmman coder: ValueError"""
        alpha = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        freqs = [1, 2, 25, 15, 3, 9, 18, 135, 225, 27]
        huffman_coder = HuffmanCoder(alpha, freqs, 3)
        _ = huffman_coder.encode(list("a234567890"))
    def decode_test(self):
        """Functionnal tests for the Huffman coder: decode_test"""
        alpha = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        probas = [1, 2, 25, 15, 3, 9, 18, 135, 225, 27]
        huffman_coder = HuffmanCoder(alpha, probas, 3)
        enco = '02110'
        decoded = huffman_coder.decode(enco)
        assert decoded == list("1")
    def encode_decode_test(self):
        """Functionnal tests for the Huffman coder: encode_decode_test"""
        alpha = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        freqs = [1, 2, 25, 15, 3, 9, 18, 135, 225, 27]
        huffman_coder = HuffmanCoder(alpha, freqs, 3)
        inp = list("1")
        enco = huffman_coder.encode(inp)
        decoded = huffman_coder.decode(enco)
        assert decoded == inp
    def x_in_y_test(self):
        """Functionnal tests for x_in_y helper"""
        base = "aaa"
        queryt = "a"
        queryf = "b"
        assert x_in_y(queryt, base)
        assert not x_in_y(queryf, base)
    def x_in_y_recov_test(self):
        """Recovery tests for x_in_y helper: TypeError"""
        base = [1, 5, 1]
        queryt = 5
        queryf = 4
        assert x_in_y(queryt, base)
        assert not x_in_y(queryf, base)

def test_count_run_cat():
    """Functionnal tests for the function count_run_cat"""
    seq = np.array([0]*54+[1]*4+[0]*6)
    lut = load_lut_matrix("jpegdna/data/lut.mat")
    res = count_run_cat(seq, lut)
    target_run_cat_count = np.zeros((160))
    target_run_cat_count[0] = 3
    target_run_cat_count[20] = 1
    target = (1, target_run_cat_count, 3)
    print(res[1])
    assert res[0] == target[0]
    assert (res[1] == target[1]).all()
    assert res[2] == target[2]


class TestCategoryCoder():
    """Tests on the jpeg Category coder"""
    def encode_ac_test(self):
        """Functionnal tests for the Categorical coder: encode_AC_test"""
        alpha = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        freqs = [1, 2, 25, 15, 3, 9, 18, 135, 225, 27]
        dic = huffmandict(alpha, freqs, 3)
        ac_category_coder = ACCategoryCoder(dic, load_lut_matrix("jpegdna/data/lut.mat"))
        res = ac_category_coder.encode(ac_category_coder.lut[0])
        print(res)
        assert res == "AC"
    def decode_ac_test(self):
        """Functionnal tests for the Categorical coder: decode_AC_test"""
        alpha = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        freqs = [1, 2, 25, 15, 3, 9, 18, 135, 225, 27]
        dic = huffmandict(alpha, freqs, 3)
        ac_category_coder = ACCategoryCoder(dic, load_lut_matrix("jpegdna/data/lut.mat"))
        res = (ac_category_coder.full_decode("ATCGATCGATCG"))
        print(res[0])
        print(res[1])
        assert res[0] == ac_category_coder.lut[3]
        assert res[1] == (4, 2)
    def encode_decode_ac_test(self):
        """Functionnal tests for the Categorical coder: encode_decode_AC_test"""
        alpha = range(162)
        freqs = [1]*162
        dic = huffmandict(alpha, freqs, 3)
        lut = load_lut_matrix("jpegdna/data/lut.mat")
        ac_category_coder = ACCategoryCoder(dic, lut)
        for i in range(160):
            inp = [ac_category_coder.lut[i]]
            code = ac_category_coder.encode(inp)
            res = (ac_category_coder.full_decode(code))
            assert res[0] == inp[0]
    def encode_dc_test(self):
        """Functionnal tests for the Categorical coder: encode_DC_test"""
        alpha = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        freqs = [1, 2, 25, 15, 3, 9, 18, 135, 225, 27]
        dic = huffmandict(alpha, freqs, 3)
        dc_category_coder = DCCategoryCoder(dic)
        res = dc_category_coder.encode(list("656"))
        assert res == "AGTGAGTATGTG"
    def decode_dc_test(self):
        """Functionnal tests for the Categorical coder: decode_DC_test"""
        alpha = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        freqs = [1, 2, 25, 15, 3, 9, 18, 135, 225, 27]
        dic = huffmandict(alpha, freqs, 3)
        dc_category_coder = DCCategoryCoder(dic)
        res = (dc_category_coder.full_decode(list("ATCGATCGATCG")))
        assert res == ("3", (4, 2))
    def encode_decode_dc_test(self):
        """Functionnal tests for the Categorical coder: encode_decode_DC_test"""
        alpha = range(11)
        probas = [1/11]*11
        dic = huffmandict(alpha, probas, 3)
        dc_category_coder = DCCategoryCoder(dic)
        for i in range(11):
            inp = [str(alpha[i])]
            code = dc_category_coder.encode(inp)
            res = dc_category_coder.full_decode(code)
            assert res[0] == inp[0]
    @expected_non_decodable_category
    def dc_category_coder_failure_test(self):
        """Failure tests for DCCategoryCoder: NonDecodableCategory"""
        alpha = range(11)
        probas = [1/11]*11
        dic = huffmandict(alpha, probas, 3)
        dc_category_coder = DCCategoryCoder(dic)
        _ = (dc_category_coder.full_decode(list("AAAAAAAA")))
    @expected_non_decodable_category
    def ac_category_coder_failure_test(self):
        """Failure tests for DCCategoryCoder: NonDecodableCategory"""
        alpha = range(162)
        probas = [1/162]*162
        dic = huffmandict(alpha, probas, 3)
        lut = load_lut_matrix("jpegdna/data/lut.mat")
        ac_category_coder = ACCategoryCoder(dic, lut)
        _ = (ac_category_coder.full_decode(list("AAAAAAAA")))
    @expected_getter_coder_error
    def dc_category_coder_getter_failure_test(self):
        """Failure tests for ACCategoryCoder: AutomataGetterException"""
        alpha = range(11)
        probas = [1/11]*11
        dic = huffmandict(alpha, probas, 3)
        dc_category_coder = DCCategoryCoder(dic)
        dc_category_coder.get_state(case="coucou")
    @expected_getter_coder_error
    def ac_category_coder_getter_failure_test(self):
        """Failure tests for DCCategoryCoder: AutomataGetterException"""
        alpha = range(162)
        probas = [1/162]*162
        dic = huffmandict(alpha, probas, 3)
        lut = load_lut_matrix("jpegdna/data/lut.mat")
        ac_category_coder = ACCategoryCoder(dic, lut)
        ac_category_coder.get_state(case="coucou")


class TestValueCoder():
    """Tests on the Value coder"""
    def encode_value_test(self):
        """Functionnal tests for the DCT value coder: encode_value_test"""
        codebook = load_codebook_matrix("jpegdna/data/codebook.pkl")
        value_coder = ValueCoder(codebook)
        code = value_coder.full_encode(1, 5)
        print(code)
        assert code == "CGATCA"
    @expected_value_error
    def encode_value_failure_test(self):
        """Failure tests for the DCT value coder: ValueError"""
        codebook = load_codebook_matrix("jpegdna/data/codebook.pkl")
        value_coder = ValueCoder(codebook)
        _ = value_coder.full_encode(5, -1)
    def getter_value_coder_test(self):
        """Functionnal tests for the DCT value coder: getter_value_coder_test"""
        codebook = load_codebook_matrix("jpegdna/data/codebook.pkl")
        value_coder = ValueCoder(codebook)
        assert value_coder.get_state() == (0, 0)
    @expected_getter_coder_error
    def getter_value_coder_failure_test(self):
        """Failure tests for the DCT value coder: AutomataGetterException"""
        codebook = load_codebook_matrix("jpegdna/data/codebook.pkl")
        value_coder = ValueCoder(codebook)
        _ = value_coder.get_state(case='titatitutu')
    @expected_setter_coder_error
    def setter_value_coder_failure_test(self):
        """Failure tests for the DCT value coder: AutomataSetterException"""
        codebook = load_codebook_matrix("jpegdna/data/codebook.pkl")
        value_coder = ValueCoder(codebook)
        value_coder.set_state(case='titatitutu')
    @expected_setter_encode_coder_error
    def setter_value_coder_encode_failure_test(self):
        """Failure tests for the DCT value coder: AutomataSetterExceptionEncode"""
        codebook = load_codebook_matrix("jpegdna/data/codebook.pkl")
        value_coder = ValueCoder(codebook)
        value_coder.set_state(case='encode')
    @expected_setter_decode_coder_error
    def setter_value_coder_decode_failure_test(self):
        """Failure tests for the DCT value coder: AutomataSetterExceptionDecode"""
        codebook = load_codebook_matrix("jpegdna/data/codebook.pkl")
        value_coder = ValueCoder(codebook)
        value_coder.set_state(case='decode')
    def decode_value_test(self):
        """Functionnal tests for the DCT value coder: decode_value_test"""
        codebook = load_codebook_matrix("jpegdna/data/codebook.pkl")
        value_coder = ValueCoder(codebook)
        val = value_coder.full_decode("ATCTTG", 2, 4)
        print(val)
        assert val == -5
        val = value_coder.full_decode("AAAAAA", 2, 4)
        print(val)
        assert val == 0
    @expected_setter_coder_error
    def coefficient_coder_ac_setter_failure_case_test(self):
        """Failure tests for the setter AC value coder: AutomataSetterException"""
        codebook = load_codebook_matrix("jpegdna/data/codebook.pkl")
        lut = load_lut_matrix("jpegdna/data/lut.mat")
        prob_ac = [1/162]*162
        gold_coder = GoldmanCoder(["A", "T", "C", "G"])
        dict_ac = huffmandict(range(162), prob_ac, 3)
        huffman_ac_coder = HuffmanCoder(dict_ac)
        huffcode_ac, gold_code_ac = [], []
        for i in range(162):
            huffcode_ac.append(huffman_ac_coder.encode([str(i)]))
            gold_code_ac.append(gold_coder.encode(huffcode_ac[i]))
        ac_coeff_coder = ACCoefficientCoder(dict_ac, lut, codebook)
        ac_coeff_coder.set_state(1, case="titatitutu")
    @expected_setter_coder_error
    def coefficient_coder_ac_setter_failure_args_test(self):
        """Failure tests for the setter AC value coder: AutomataSetterException"""
        codebook = load_codebook_matrix("jpegdna/data/codebook.pkl")
        lut = load_lut_matrix("jpegdna/data/lut.mat")
        prob_ac = [1/162]*162
        gold_coder = GoldmanCoder(["A", "T", "C", "G"])
        dict_ac = huffmandict(range(162), prob_ac, 3)
        huffman_ac_coder = HuffmanCoder(dict_ac)
        huffcode_ac, gold_code_ac = [], []
        for i in range(162):
            huffcode_ac.append(huffman_ac_coder.encode([str(i)]))
            gold_code_ac.append(gold_coder.encode(huffcode_ac[i]))
        ac_coeff_coder = ACCoefficientCoder(dict_ac, lut, codebook)
        ac_coeff_coder.set_state(1, 2, 3, 4, case="encode")
    @expected_getter_coder_error
    def coefficient_coder_ac_getter_failure_test(self):
        """Failure tests for the getter AC value coder: AutomataGetterException"""
        codebook = load_codebook_matrix("jpegdna/data/codebook.pkl")
        lut = load_lut_matrix("jpegdna/data/lut.mat")
        prob_ac = [1/162]*162
        gold_coder = GoldmanCoder(["A", "T", "C", "G"])
        dict_ac = huffmandict(range(162), prob_ac, 3)
        huffman_ac_coder = HuffmanCoder(dict_ac)
        huffcode_ac, gold_code_ac = [], []
        for i in range(162):
            huffcode_ac.append(huffman_ac_coder.encode([str(i)]))
            gold_code_ac.append(gold_coder.encode(huffcode_ac[i]))
        ac_coeff_coder = ACCoefficientCoder(dict_ac, lut, codebook)
        ac_coeff_coder.get_state(case="titatitutu")
    def encode_ac_test(self):
        """Functionnal tests for the DCT value coder: encode_AC_test"""
        codebook = load_codebook_matrix("jpegdna/data/codebook.pkl")
        inp = np.array([51]*5)
        target = "TCTGAAGAGTCTGAAGAGTCTGAAGAGTCTGAAGAGTCTA"
        lut = load_lut_matrix("jpegdna/data/lut.mat")
        prob_ac = [1/162]*162
        gold_coder = GoldmanCoder(["A", "T", "C", "G"])
        dict_ac = huffmandict(range(162), prob_ac, 3)
        huffman_ac_coder = HuffmanCoder(dict_ac)
        huffcode_ac, gold_code_ac = [], []
        for i in range(162):
            huffcode_ac.append(huffman_ac_coder.encode([str(i)]))
            gold_code_ac.append(gold_coder.encode(huffcode_ac[i]))
        ac_coeff_coder = ACCoefficientCoder(dict_ac, lut, codebook)
        print(f"Gold_code: {gold_code_ac}")
        (code_ac, res) = ac_coeff_coder.full_encode(inp, gold_code_ac)
        print(f"Code: {code_ac}")
        print(f"Count run cat len: {res}")
        assert code_ac == target
    def decode_ac_test(self):
        """Functionnal tests for the DCT value coder: decode_AC_test"""
        codebook = load_codebook_matrix("jpegdna/data/codebook.pkl")
        inp = "TCTGAAGAGTCTGAAGAGTCTGAAGAGTCTGAAGAGTCTA"
        lut = load_lut_matrix("jpegdna/data/lut.mat")
        prob_ac = [1/162]*162
        gold_coder = GoldmanCoder(["A", "T", "C", "G"])
        dict_ac = huffmandict(range(162), prob_ac, 3)
        huffman_ac_coder = HuffmanCoder(dict_ac)
        huffcode_ac, gold_code_ac = [], []
        for i in range(162):
            huffcode_ac.append(huffman_ac_coder.encode([str(i)]))
            gold_code_ac.append(gold_coder.encode(huffcode_ac[i]))
        print(f"Gold_code: {gold_code_ac}")
        ac_coeff_coder = ACCoefficientCoder(dict_ac, lut, codebook)
        (coeff, (num_zeros, num_bits, end_of_block)) = ac_coeff_coder.full_decode(inp)
        print(f"Coefficient: {coeff}")
        print(f"Num_bits: {num_bits}")
        assert num_zeros == 0
        assert not end_of_block
        assert num_bits == 9
        assert coeff == 51
    def encode_decode_ac_test(self):
        """Functionnal tests for the DCT value coder: encode_decode_AC_test"""
        codebook = load_codebook_matrix("jpegdna/data/codebook.pkl")
        inp = np.array([50]*64)
        lut = load_lut_matrix("jpegdna/data/lut.mat")
        prob_ac = [1/162]*162
        gold_coder = GoldmanCoder(["A", "T", "C", "G"])
        dict_ac = huffmandict(range(162), prob_ac, 3)
        huffman_ac_coder = HuffmanCoder(dict_ac)
        huffcode_ac, gold_code_ac = [], []
        for i in range(162):
            huffcode_ac.append(huffman_ac_coder.encode([str(i)]))
            gold_code_ac.append(gold_coder.encode(huffcode_ac[i]))
        ac_coeff_coder = ACCoefficientCoder(dict_ac, lut, codebook)
        (code_ac, _) = ac_coeff_coder.full_encode(inp, gold_code_ac)
        print(f"Gold_code: {gold_code_ac}")
        print(f"Code: {code_ac}")
        (coeff, (num_zeros, num_bits, end_of_block)) = ac_coeff_coder.full_decode(code_ac)
        print(f"Coefficient: {coeff}")
        print(f"Num_zeros: {num_zeros}")
        print(f"Num_bits: {num_bits}")
        print(f"End_of_block: {end_of_block}")
        assert num_zeros == 0
        assert not end_of_block
        assert num_bits == 9
        assert coeff == 50
    def encode_dc_test(self):
        """Functionnal tests for the DCT value coder: encode_DC_test"""
        codebook = load_codebook_matrix("jpegdna/data/codebook.pkl")
        inp = 51
        prob_dc = [1/11]*11
        gold_coder = GoldmanCoder(["A", "T", "C", "G"])
        dict_dc = huffmandict(range(11), prob_dc, 3)
        huffman_dc_coder = HuffmanCoder(dict_dc)
        huffcode_dc, gold_code_dc = [], []
        for i in range(11):
            huffcode_dc.append(huffman_dc_coder.encode([str(i)]))
            gold_code_dc.append(gold_coder.encode(huffcode_dc[i]))
        print(f"Gold_code: {gold_code_dc}")

        dc_coeff_coder = DCCoefficientCoder(dict_dc, codebook)
        (code_dc, res) = dc_coeff_coder.full_encode(inp, gold_code_dc)
        print(f"Code: {code_dc}")
        print(f"Count run cat len: {res}")
        assert code_dc == "ATAGAG"
    def decode_dc_test(self):
        """Functionnal tests for the DCT value coder: decode_DC_test"""
        codebook = load_codebook_matrix("jpegdna/data/codebook.pkl")
        prob_dc = [1/11]*11
        gold_coder = GoldmanCoder(["A", "T", "C", "G"])
        dict_dc = huffmandict(range(11), prob_dc, 3)
        huffman_dc_coder = HuffmanCoder(dict_dc)
        huffcode_dc, gold_code_dc = [], []
        for i in range(11):
            huffcode_dc.append(huffman_dc_coder.encode([str(i)]))
            gold_code_dc.append(gold_coder.encode(huffcode_dc[i]))
        print(f"Gold_code: {gold_code_dc}")

        dc_coeff_coder = DCCoefficientCoder(dict_dc, codebook)
        (coeff, (num_bits)) = dc_coeff_coder.full_decode("ATAGAG")
        print(f"Coefficient: {coeff}")
        print(f"Num_bits: {num_bits}")
        assert coeff == 51
        assert num_bits == 6
    def encode_decode_dc_test(self):
        """Functionnal tests for the DCT value coder: encode_decode_DC_test"""
        codebook = load_codebook_matrix("jpegdna/data/codebook.pkl")
        inp = 50
        prob_dc = [1/11]*11
        gold_coder = GoldmanCoder(["A", "T", "C", "G"])
        dict_dc = huffmandict(range(11), prob_dc, 3)
        huffman_dc_coder = HuffmanCoder(dict_dc)
        huffcode_dc, gold_code_dc = [], []
        for i in range(11):
            huffcode_dc.append(huffman_dc_coder.encode([str(i)]))
            gold_code_dc.append(gold_coder.encode(huffcode_dc[i]))

        dc_coeff_coder = DCCoefficientCoder(dict_dc, codebook)
        (code_dc, _) = dc_coeff_coder.full_encode(inp, gold_code_dc)
        print(f"Gold_code: {gold_code_dc}")
        print(f"Code: {code_dc}")
        (coeff, (num_bits)) = dc_coeff_coder.full_decode(code_dc)
        print(f"Coefficient: {coeff}")
        print(f"Num_bits: {num_bits}")
        assert coeff == 50
        assert num_bits == 6
    @expected_setter_coder_error
    def coefficient_coder_dc_setter_failure_case_test(self):
        """Failure tests for the setter DC value coder: AutomataSetterException"""
        codebook = load_codebook_matrix("jpegdna/data/codebook.pkl")
        prob_dc = [1/11]*11
        gold_coder = GoldmanCoder(["A", "T", "C", "G"])
        dict_dc = huffmandict(range(11), prob_dc, 3)
        huffman_dc_coder = HuffmanCoder(dict_dc)
        huffcode_dc, gold_code_dc = [], []
        for i in range(11):
            huffcode_dc.append(huffman_dc_coder.encode([str(i)]))
            gold_code_dc.append(gold_coder.encode(huffcode_dc[i]))
        dc_coeff_coder = DCCoefficientCoder(dict_dc, codebook)
        dc_coeff_coder.set_state(1, case="titatitutu")
    @expected_setter_coder_error
    def coefficient_coder_dc_setter_failure_args_test(self):
        """Failure tests for the setter DC value coder: AutomataSetterException"""
        codebook = load_codebook_matrix("jpegdna/data/codebook.pkl")
        prob_dc = [1/11]*11
        gold_coder = GoldmanCoder(["A", "T", "C", "G"])
        dict_dc = huffmandict(range(11), prob_dc, 3)
        huffman_dc_coder = HuffmanCoder(dict_dc)
        huffcode_dc, gold_code_dc = [], []
        for i in range(11):
            huffcode_dc.append(huffman_dc_coder.encode([str(i)]))
            gold_code_dc.append(gold_coder.encode(huffcode_dc[i]))
        dc_coeff_coder = DCCoefficientCoder(dict_dc, codebook)
        dc_coeff_coder.set_state(1, 2, 3, 4, case="encode")
    @expected_getter_coder_error
    def coefficient_coder_dc_getter_failure_test(self):
        """Failure tests for the getter DC value coder: AutomataGetterException"""
        codebook = load_codebook_matrix("jpegdna/data/codebook.pkl")
        prob_dc = [1/11]*11
        gold_coder = GoldmanCoder(["A", "T", "C", "G"])
        dict_dc = huffmandict(range(11), prob_dc, 3)
        huffman_dc_coder = HuffmanCoder(dict_dc)
        huffcode_dc, gold_code_dc = [], []
        for i in range(11):
            huffcode_dc.append(huffman_dc_coder.encode([str(i)]))
            gold_code_dc.append(gold_coder.encode(huffcode_dc[i]))
        dc_coeff_coder = DCCoefficientCoder(dict_dc, codebook)
        dc_coeff_coder.get_state(case="titatitutu")
    def value_coder_thorough_test(self):
        """Functionnal tests for the value coder: ValueCoder Thorough test"""
        codebook = load_codebook_matrix("jpegdna/data/codebook.pkl")
        prob_dc = [1/11]*11
        gold_coder = GoldmanCoder(["A", "T", "C", "G"])
        dict_dc = huffmandict(range(11), prob_dc, 3)
        huffman_dc_coder = HuffmanCoder(dict_dc)
        for k in range(-2000, 2000):
            print(f"Value tested: {k}")
            inp = k
            huffcode_dc, gold_code_dc = [], []
            for i in range(11):
                huffcode_dc.append(huffman_dc_coder.encode([str(i)]))
                gold_code_dc.append(gold_coder.encode(huffcode_dc[i]))

            dc_coeff_coder = DCCoefficientCoder(dict_dc, codebook)
            (code_dc, _) = dc_coeff_coder.full_encode(inp, gold_code_dc)
            print(f"Gold_code: {gold_code_dc}")
            print(f"Code: {code_dc}")
            (coeff, (num_bits)) = dc_coeff_coder.full_decode(code_dc)
            print(f"Coefficient: {coeff}")
            print(f"Num_bits: {num_bits}")
            assert coeff == inp
