"""Encoding and decoding main functions for JPEG-DNA"""

from pathlib import Path
import pickle
from tkinter import N
import numpy as np
import jpegdna
from jpegdna.transforms import DCT
from jpegdna.transforms import ZigZag
from jpegdna.coders import AbstractCoder
from jpegdna.coders import ACCoefficientCoder, DCCoefficientCoder
from jpegdna.coders import GoldmanCoderDNA
from jpegdna.coders import HuffmanCoder
from jpegdna.format import JpegDNAFormatter
from jpegdna.coders.categorycoder import NonDecodableCategory, find_category_dc, count_run_cat
from jpegdna.tools.loader import load_lut_matrix, load_codebook_matrix

# Imports for Transcoder
import pyximport
pyximport.install()
from decoder import PyCoefficientDecoder 


BLOCK_VERBOSITY_THRESHOLD = 1
BLOCK_CENTERING_VERBOSITY_THRESHOLD = 2
HUFFMAN_VERBOSITY_THRESHOLD = 2
GOLDMAN_VERBOSITY_THRESHOLD = 2
ZIG_ZAG_VERBOSITY_THRESHOLD = 2
QUANTIZATION_VERBOSITY_THRESHOLD = 2
DCT_VERBOSITY_THRESHOLD = 2
VALUE_CODER_VERBOSITY_THRESHOLD = 3
VALUE_CODER_DEBUG_THRESHOLD = 5
EOB_SHIFT_IDX = 15


class JPEGDNAGray(AbstractCoder):
    """JPEG-DNA codec for gray-level images
    :param aplha: Alpha value (quantization step multiplier)
    :type alpha: float
    :param formatting: Formatting enabler
    :type formatting: bool
    :param channel_type: Channel type choice ('luma' or 'chroma')
    :type channel_type: str
    :var verbose: Verbosity enabler
    :param verbose: bool
    :var verbosity: Verbosity level
    :param verbosity: int
    :ivar alpha: alpha value (compression rate?)
    :vartype alpha: float
    :ivar lut: hexa codes for the categories
    :vartype lut: list
    :ivar dct: dct transform
    :vartype dct: jpegdna.transforms.dctransform.DCT
    :ivar zigzag: Zigzag transform
    :vartype zigzag: jpegdna.transforms.zigzag.ZigZag
    :ivar dc_coeff_coder: DC coefficient coder
    :vartype dc_coeff_coder: jpegdna.coders.coefficientcoder.DCCoefficientCoder
    :ivar ac_coeff_coder: AC coefficient coder
    :vartype ac_coeff_coder: jpegdna.coders.coefficientcoder.ACCoefficientCoder
    """

    GAMMAS = np.array([[16, 11, 10, 16, 24, 40, 51, 61],
                       [12, 12, 14, 19, 26, 58, 60, 55],
                       [14, 13, 16, 24, 40, 57, 69, 56],
                       [14, 17, 22, 29, 51, 87, 80, 62],
                       [18, 22, 37, 56, 68, 109, 103, 77],
                       [24, 35, 55, 64, 81, 104, 113, 92],
                       [49, 64, 78, 87, 103, 121, 120, 101],
                       [72, 92, 95, 98, 112, 100, 103, 99]])
    GAMMAS_CHROMA = np.array([[17, 18, 24, 47, 99, 99, 99, 99],
                              [18, 21, 26, 66, 99, 99, 99, 99],
                              [24, 26, 59, 99, 99, 99, 99, 99],
                              [47, 66, 99, 99, 99, 99, 99, 99],
                              [99, 99, 99, 99, 99, 99, 99, 99],
                              [99, 99, 99, 99, 99, 99, 99, 99],
                              [99, 99, 99, 99, 99, 99, 99, 99],
                              [99, 99, 99, 99, 99, 99, 99, 99]])
    EOB_SHIFT = False
    def __init__(self, alpha, img_fpath, encoding, qtpath, formatting=False, primer=None, channel_type="luma", verbose=False, verbosity=0):
        self.path = img_fpath
        self.encoding = encoding
        self.qtpath = qtpath
        self.channel_type = channel_type
        self.formatting = formatting
        self.primer = primer
        self.set_alpha(alpha, encoding)
        self.lut = load_lut_matrix(Path(jpegdna.__path__[0] + "/data/lut.mat"))
        self.codebook = load_codebook_matrix(Path(jpegdna.__path__[0] + "/data/codebook.pkl"))
        self.dct = DCT()
        self.zigzag = ZigZag(verbose=False)
        self.total_runlength_nts, self.freq_dc, self.freq_ac, self.m, self.n = None, None, None, None, None
        self.verbose = verbose
        self.verbosity = verbosity
        self.remain = ""
        if self.formatting:
            self.formatter = JpegDNAFormatter(self.alpha, "gray", None, primer=self.primer, oligo_length=200, debug=False)
        else:
            self.formatter = None
        self.dc_coeff_coder = None
        self.ac_coeff_coder = None
        self.huffman_dc_coder = None
        self.huffman_ac_coder = None

    def set_alpha(self, alpha, encoding):
        """Setter for alpha value
        :param alpha: alpha value
        :type alpha: float
        """

        if encoding:
            dec = PyCoefficientDecoder(self.path)
            self.alpha = alpha
            if self.channel_type == "luma":
                self.gammas = np.array(dec.get_quantization_table(0))
            elif self.channel_type == "chroma":
                self.gammas = np.array(dec.get_quantization_table(1))
            else:
                raise ValueError("Wrong channel type, either pick 'luma' or 'chroma'")
            if self.formatting:
                self.formatter = JpegDNAFormatter(self.alpha, "gray", None, primer=self.primer, oligo_length=200, debug=False)
        else:
            QT = np.load(self.path)
            self.alpha = alpha
            if self.channel_type == "luma":
                self.gammas = QT['x']
            elif self.channel_type == "chroma":
                self.gammas = QT['y']
            else:
                raise ValueError("Wrong channel type, either pick 'luma' or 'chroma'")
            if self.formatting:
                self.formatter = JpegDNAFormatter(self.alpha, "gray", None, primer=self.primer, oligo_length=200, debug=False)



    def get_alpha(self):
        """Getter for alpha value
        :return: alpha value
        :rtype: float
        """
        return self.alpha

    def set_channel_type(self, channel_type):
        """Setter for the channel type
        :param channel_type: Choice between 'luma' and 'chroma'
        :type channel_type: str
        """
        self.channel_type = channel_type
        self.set_alpha(self.alpha, self.encoding)

    def set_state(self, *args, case=None):
        """Sets the state of the codec
        :param freq_dc: List of appearance frequences for each element of the alphabet in the dc values
        :type freq_dc: list(float)
        :param freq_ac: List of appearance frequences for each element of the alphabet in the ac values
        :type freq_ac: list(float)
        :param m: length of an image block
        :type m: int
        :param n: height of an image block
        :type n: int
        """
        if len(args) == 0:
            raise ValueError
        if case == 'encode':
            min_alpha = self.compute_min_dynamic(args[0])
            if self.alpha < min_alpha:
                raise ValueError(f"Invalid alpha value, minimal possible value for this image: {min_alpha}")
            if len(args) < 2:
                raise ValueError
            if args[1] == "from_img":
                self.set_frequencies_from_img(args[0])
            elif args[1] == "from_file":
                if len(args) != 4:
                    raise ValueError
                self.set_frequencies_from_array(args[2], args[3])
            elif args[1] == "default":
                self.set_frequencies_default()
            else:
                raise ValueError("No frequency specified, pick between {'from_img'|'from_file'|'default'}")
        elif case == 'decode':
            if len(args) < 3:
                raise ValueError
            self.m = args[1]
            self.n = args[2]
            if args[0] == "from_img" or args[0] == "from_file":
                if len(args) != 5:
                    raise ValueError
                self.freq_dc = args[3]
                self.freq_ac = args[4]
            elif args[0] == "default":
                self.set_frequencies_default()
            else:
                raise ValueError("No frequency specified, pick between {'from_img'|'from_file'|'default'}")
        else:
            raise ValueError

    def get_state(self, case=None):
        """Get codec state after encoding"""

        if case is not None:
            raise ValueError
        return self.total_runlength_nts, self.m, self.n, self.freq_dc, self.freq_ac

    def compute_min_dynamic(self, img, channel_type="luma"):
        """Compute the minimum possible alpha value for a given image
        :param img: input image
        :type img: np.array
        :return: minimum possible alpha value
        :rtype: float
        """

        n, m = np.shape(img)[0:2]
        nb_row_blocks = int(n/8)
        nb_col_blocks = int(m/8)
        max_dc_coeff = 0
        max_ac_coeff = 0
        for i in range(nb_row_blocks):
            for j in range(nb_col_blocks):
                # block definition
                block = (img[i*8:(i+1)*8, j*8:(j+1)*8]).copy()
                block = block.astype(int) - 128
                # dct transform
                block_dct = self.dct.full_forward(block, "ortho")
                # quantization
                if channel_type == "luma":
                    coeff = np.divide(block_dct, self.GAMMAS).round().astype(int)
                elif channel_type == "chroma":
                    coeff = np.divide(block_dct, self.GAMMAS_CHROMA).round().astype(int)
                else:
                    raise ValueError("Wrong channel type, either pick 'luma' or 'chroma'")
                # zigag transform -> sequence of quantized values
                seq_coeff = self.zigzag.forward(coeff)
                # computing max DC and AC coefficient
                if abs(seq_coeff[0]) > max_dc_coeff:
                    max_dc_coeff = abs(seq_coeff[0])
                for el in seq_coeff[1:]:
                    if abs(el) > max_ac_coeff:
                        max_ac_coeff = abs(el)
        min_alpha = max_dc_coeff / 72909
        if min_alpha > max_ac_coeff / 17579:
            min_alpha = max_ac_coeff / 17579
        return min_alpha

    def set_frequencies_default(self):
        """Sets the frequencies to the package's default frequency tables
        """

        with open(Path(jpegdna.__path__[0] + "/data/freqs.pkl"), "rb") as file:
            freqs = pickle.load(file)
        self.freq_dc = freqs['freq_dc']
        self.freq_ac = freqs['freq_ac']

    def set_frequencies_from_array(self, freq_dc, freq_ac):
        """Sets the frequencies used using a pre-existing frequency tables
        :param freq_dc: DC coefficients frequencies table
        :type freq_dc: array
        :param freq_ac: AC coefficients frequencies table
        :type inp: array
        """

        self.freq_dc = freq_dc
        self.freq_ac = freq_ac

    # Transcoder: instead of computing DCT and quantizing, just read JPEG image's DCT coefficients
    # DCT coefficient are passed as argument, so are the height and width in blocks of our DCT coefficients
    def set_frequencies_from_img(self, inp, DCT_coeffs, height_in_blocks, width_in_blocks):
        """Computes the frenquencies in function of the image DCT quantized coefficients
        :param inp: input image
        :type inp: np.array
        """
        self.zigzag.verbose = False
        self.n, self.m = np.shape(inp)[0:2]
        nb_row_blocks = height_in_blocks # Read from JPEG file instead of computed
        nb_col_blocks = width_in_blocks # # Read from JPEG file instead of computed
        count_cat_dc = np.zeros((11))
        run_cat_count_tot = np.zeros((160))
        count_run_end_tot = 0
        count_run16_tot = 0

        idx = 0     
        for i in range(nb_row_blocks):
            dc_prev_coeff = 0
            for j in range(nb_col_blocks):

                # Read quantized DCT coefficients
                coeff = DCT_coeffs[idx,:].reshape((8,8))
                idx = idx + 1

                # Now continue JPEG DNA encoding 
                # zigag transform -> sequence of quantized values
                seq_coeff = self.zigzag.forward(coeff)
                # differential coding of the dc value
                diff = seq_coeff[0] - dc_prev_coeff
                dc_prev_coeff = seq_coeff[0]
                # counting categories
                cat_dc = find_category_dc(diff)
                count_cat_dc[cat_dc] += 1
                (count_run_end, run_cat_count, count_run16) = count_run_cat(seq_coeff, self.lut)
                count_run16_tot += count_run16
                count_run_end_tot += count_run_end
                run_cat_count_tot += run_cat_count
        self.freq_dc = count_cat_dc
        self.freq_ac = np.append(run_cat_count_tot, np.array([count_run16_tot, count_run_end_tot]))

    def full_encode(self, inp, *args):
        self.set_state(inp, *args, case='encode')
        out = self.encode(inp)
        if self.formatting:
            return self.formatter.full_format(out, args[0], *self.get_state()[1:])
        else:
            return (out, self.get_state())

    def encode(self, inp):
        """JPEG-DNA encoder: encodes the image into a DNA-like bitstream
        :param inp: input image
        :type inp: np.array
        :return: DNA-like bitstream
        :rtype: str
        """

        if self.verbose:
            print(f"========================\nEncoding input image:\n{inp}\n========================")
        self.zigzag.verbose = (self.verbose and self.verbosity >= ZIG_ZAG_VERBOSITY_THRESHOLD)

        total_cat_len_count = 0
        total_run_len_count = 0

        self.total_runlength_nts = 0
        self.n, self.m = np.shape(inp)[0:2]
        if self.n%8 != 0:
            inp = np.pad(inp, ((0, 8-self.n%8), (0, 0)), 'edge')
        if self.m%8 != 0:
            inp = np.pad(inp, ((0, 0), (0, 8-self.m%8)), 'edge')
        nb_row_blocks = int(np.shape(inp)[0]/8)
        nb_col_blocks = int(np.shape(inp)[1]/8)

        gold_coder = GoldmanCoderDNA()
        if self.verbose and self.verbosity >= HUFFMAN_VERBOSITY_THRESHOLD:
            print("Building Huffman Coder for DC values")
            print(f"Frequencies:\n{self.freq_dc}")
        self.huffman_dc_coder = HuffmanCoder(range(11), self.freq_dc, 3,
                                             verbose=(self.verbose and self.verbosity >= HUFFMAN_VERBOSITY_THRESHOLD))
        if self.verbose and self.verbosity >= HUFFMAN_VERBOSITY_THRESHOLD:
            print("Building Huffman Coder for AC values")
            print(f"Frequencies:\n{self.freq_ac}")
        if self.EOB_SHIFT:
            # Cheating with the position of the codeword for #EOB (the codeword should not be too short)
            dummy_freq_ac_idx = np.argpartition(self.freq_ac, -EOB_SHIFT_IDX)[-EOB_SHIFT_IDX:]
            val = min(self.freq_ac[dummy_freq_ac_idx])
            if val != 1:
                self.freq_ac[-1] = abs(val-1)
            else:
                self.freq_ac[-1] = 1
        self.huffman_ac_coder = HuffmanCoder(range(162), self.freq_ac, 3,
                                             verbose=(self.verbose and self.verbosity >= HUFFMAN_VERBOSITY_THRESHOLD))

        huffcode_ac, gold_code_ac = [], []
        for i in range(162):
            huffcode_ac.append(self.huffman_ac_coder.encode([str(i)]))
            gold_code_ac.append(gold_coder.encode(huffcode_ac[i]))
        huffcode_dc, gold_code_dc = [], []
        for i in range(11):
            huffcode_dc.append(self.huffman_dc_coder.encode([str(i)]))
            gold_code_dc.append(gold_coder.encode(huffcode_dc[i]))

        if self.verbose and self.verbosity >= GOLDMAN_VERBOSITY_THRESHOLD:
            print(f"DNA codes for DC categories: {gold_code_dc}")
            print(f"DNA codes for AC categories: {gold_code_ac}")
            print("========================")

        self.dc_coeff_coder = DCCoefficientCoder(self.huffman_dc_coder.dic, self.codebook,
                                                 verbose=(self.verbose and self.verbosity >= VALUE_CODER_VERBOSITY_THRESHOLD))
        self.ac_coeff_coder = ACCoefficientCoder(self.huffman_ac_coder.dic, self.lut, self.codebook,
                                                 verbose=(self.verbose and self.verbosity >= VALUE_CODER_VERBOSITY_THRESHOLD))
        jpeg_coded = ""
        for i in range(nb_row_blocks):
            dc_prev_coeff = 0
            for j in range(nb_col_blocks):
                # block definition
                block = (inp[i*8:(i+1)*8, j*8:(j+1)*8]).copy()
                if self.verbose and self.verbosity >= BLOCK_VERBOSITY_THRESHOLD:
                    print(f"--------------------\nEncoding block ({i},{j}):\n{block}")
                # centering values
                centered_block = block.astype(int) - 128
                if self.verbose and self.verbosity >= BLOCK_CENTERING_VERBOSITY_THRESHOLD:
                    print(f"----------\nCentered block ({i},{j}):\n{centered_block}")
                # dct transform
                block_dct = self.dct.full_forward(centered_block, "ortho")
                if self.verbose and self.verbosity >= DCT_VERBOSITY_THRESHOLD:
                    print(f"----------\nForward dct:\n{block_dct}")
                # quantization
                coeff = np.divide(block_dct, self.gammas)
                if self.verbose and self.verbosity >= QUANTIZATION_VERBOSITY_THRESHOLD:
                    print(f"----------\nDivided block:\n{coeff}")
                coeff = coeff.round().astype(int)
                if self.verbose and self.verbosity >= QUANTIZATION_VERBOSITY_THRESHOLD:
                    print(f"----------\nQuantized block:\n{coeff}")
                # zigag transform -> sequence of quantized values
                seq_coeff = self.zigzag.forward(coeff)
                # differential coding of the dc value
                diff = seq_coeff[0] - dc_prev_coeff
                dc_prev_coeff = seq_coeff[0]
                # coding the dc and ac values
                (code_dc, count_cat_len) = self.dc_coeff_coder.full_encode(diff, gold_code_dc)
                (code_ac, count_runcat_len) = self.ac_coeff_coder.full_encode(seq_coeff, gold_code_ac)
                # category length
                total_cat_len_count += count_cat_len
                total_run_len_count += count_runcat_len
                # block data formatting
                code_block = code_dc + code_ac
                if self.verbose and self.verbosity >= BLOCK_VERBOSITY_THRESHOLD:
                    print(f"----------\nEncoded block ({i},{j}):\n{code_block}")
                # adding to stream
                jpeg_coded += code_block
        self.total_runlength_nts = total_cat_len_count + total_run_len_count
        if self.verbose:
            print(f"========================\nEncoded stream:\n{jpeg_coded}\n========================")
        return jpeg_coded

    def full_decode(self, code, *args):
        if self.formatting:
            code, (alpha, m, n, freq_dc, freq_ac) = self.formatter.full_deformat(code)
            freq_origin = self.formatter.freq_origin
            self.set_alpha(alpha, False)
            self.set_state(freq_origin, m, n, freq_dc, freq_ac, case='decode')
        else:
            self.set_state(*args, case='decode')
        if args[0] in ["default", "from_file"] and self.EOB_SHIFT:
            # Cheating with the position of the codeword for #EOB (the codeword should not be too short)
            dummy_freq_ac_idx = np.argpartition(self.freq_ac, -EOB_SHIFT_IDX)[-EOB_SHIFT_IDX:]
            val = min(np.array(self.freq_ac)[dummy_freq_ac_idx])
            if val != 1:
                self.freq_ac[-1] = abs(val-1)
            else:
                self.freq_ac[-1] = 1
        return self.decode(code)

    def decode(self, code):
        """JPEG-DNA decoder: decodes the input DNA-like bitstream into an block image of size self.n x self.m
        :param code: DNA-like bitstream
        :type code: str
        :return: block image
        :rtype: np.array
        """

        # if self.verbose:
        #     print(f"========================\nDecoding DNA stream:\n{code}\n========================")
        self.zigzag.verbose = (self.verbose and self.verbosity >= ZIG_ZAG_VERBOSITY_THRESHOLD)
        if self.n%8 == 0:
            nb_row_blocks = int(self.n/8)
        else:
            nb_row_blocks = int(self.n/8) + 1
        if self.m%8 == 0:
            nb_col_blocks = int(self.m/8)
        else:
            nb_col_blocks = int(self.m/8) + 1
        jpeg_decoded = np.zeros((nb_row_blocks*8, nb_col_blocks*8))

        gold_coder = GoldmanCoderDNA()
        if self.verbose and self.verbosity >= HUFFMAN_VERBOSITY_THRESHOLD:
            print("Building Huffman Coder for DC values")
        self.huffman_dc_coder = HuffmanCoder(range(11), self.freq_dc, 3,
                                             verbose=(self.verbose and self.verbosity >= HUFFMAN_VERBOSITY_THRESHOLD))
        if self.verbose and self.verbosity >= HUFFMAN_VERBOSITY_THRESHOLD:
            print("Building Huffman Coder for AC values")
        self.huffman_ac_coder = HuffmanCoder(range(162), self.freq_ac, 3,
                                             verbose=(self.verbose and self.verbosity >= HUFFMAN_VERBOSITY_THRESHOLD))

        huffcode_ac, gold_code_ac = [], []
        for i in range(162):
            huffcode_ac.append(self.huffman_ac_coder.encode([str(i)]))
            gold_code_ac.append(gold_coder.encode(huffcode_ac[i]))

        huffcode_dc, gold_code_dc = [], []
        for i in range(11):
            huffcode_dc.append(self.huffman_dc_coder.encode([str(i)]))
            gold_code_dc.append(gold_coder.encode(huffcode_dc[i]))

        if self.verbose and self.verbosity >= GOLDMAN_VERBOSITY_THRESHOLD:
            print(f"DNA codes for DC categories: {gold_code_dc}")
            print(f"DNA codes for AC categories: {gold_code_ac}")
            print("========================")

        self.dc_coeff_coder = DCCoefficientCoder(self.huffman_dc_coder.dic, self.codebook,
                                                 verbose=(self.verbose and self.verbosity >= VALUE_CODER_VERBOSITY_THRESHOLD))
        self.ac_coeff_coder = ACCoefficientCoder(self.huffman_ac_coder.dic, self.lut, self.codebook,
                                                 verbose=(self.verbose and self.verbosity >= VALUE_CODER_VERBOSITY_THRESHOLD))

        for i in range(nb_row_blocks):
            dc_prev_coeff = 0
            for j in range(nb_col_blocks):
                # decoding block from bitstream
                try:
                    if self.verbose and self.verbosity >= BLOCK_VERBOSITY_THRESHOLD:
                        print(f"--------------------\nDecoding block ({i},{j}):")
                    seq_coeff = []
                    if code == "":
                        seq_coeff = [0]*64
                    else:
                        (value, (num_bits)) = self.dc_coeff_coder.full_decode(code)
                        code = code[num_bits:]
                        coefficient = dc_prev_coeff + value
                        seq_coeff = [coefficient]
                        dc_prev_coeff = coefficient
                        while len(seq_coeff) < 64:
                            if code == "":
                                for _ in range(64-len(seq_coeff)):
                                    seq_coeff.append(0)
                            else:
                                (coeff, (num_zeros, num_bits, end_of_block)) = self.ac_coeff_coder.full_decode(code)
                                if end_of_block:
                                    for _ in range(64-len(seq_coeff)):
                                        seq_coeff.append(0)
                                    length = len(gold_code_ac[161])
                                    code = code[length:]
                                else:
                                    for _ in range(num_zeros):
                                        seq_coeff.append(0)
                                    seq_coeff.append(coeff)
                                    code = code[num_bits:]
                except NonDecodableCategory:
                    print("Category undecodable, synchronising to next block")
                    eob_str = gold_code_ac[161]
                    for l in range(len(code)-len(eob_str)):
                        if code[l:l+len(eob_str)] == eob_str:
                            code = code[l+len(eob_str):]
                            break
                    continue
                # inverse zigzag transform
                block = self.zigzag.full_inverse(seq_coeff, 8, 8)
                # inverse quantization
                block = block * self.gammas
                if self.verbose and self.verbosity >= QUANTIZATION_VERBOSITY_THRESHOLD:
                    print(f"----------\nDequantized block:\n{block}")
                # inverse dct transform + rounding
                block = (self.dct.full_inverse(block, "ortho")).round()
                if self.verbose and self.verbosity >= DCT_VERBOSITY_THRESHOLD:
                    print(f"----------\nInverse dct:\n{block}")
                # decentering values
                block += 128
                if self.verbose and self.verbosity >= BLOCK_CENTERING_VERBOSITY_THRESHOLD:
                    print(f"--------------------\nDecentered block ({i},{j}):\n{block}")
                # adding decoded block to image
                jpeg_decoded[i*8:(i+1)*8, j*8:(j+1)*8] = block
                if self.verbose and self.verbosity >= BLOCK_VERBOSITY_THRESHOLD:
                    print(f"--------------------\nDecoded block ({i},{j}):\n{block}")
        jpeg_decoded = np.clip(jpeg_decoded[:self.n, :self.m], 0, 255).astype(np.uint8)
        # For channel synchronisation in RGB
        self.remain = code
        if self.verbose:
            print(f"========================\nReconstructed image:\n{jpeg_decoded}\n========================")
        self.zigzag.verbose = False
        return jpeg_decoded