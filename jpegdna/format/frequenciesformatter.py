"""Formatting method for frequencies"""

from pathlib import Path
import numpy as np

import jpegdna
from jpegdna.format import AbstractFormatter
from jpegdna.tools.strand_tools import generate_random_strand, compute_length
from jpegdna.tools.loader import load_codebook_matrix


class GrayFrequenciesFormatter(AbstractFormatter):
    """Formatter for the gray DC and AC frequencies

    :ivar max_cat: max value for the categories
    :type max_cat: int
    :ivar max_runcat: max value for the run/categories
    :type max_runcat: int
    :ivar dc_freq_len: codeword length for encoding the dc frequencies
    :type dc_freq_len: int
    :ivar ac_freq_len: codeword length for encoding the ac frequencies
    :type ac_freq_len: int
    :ivar oligo_length: Size of the oligos used for formatting
    :type oligo_length: int
    """

    DEFAULT_FREQUENCIES_OFFSET_CODE_LENGTH = 7
    def __init__(self, max_cat, max_runcat, dc_freq_len, ac_freq_len, header, dc_header, ac_header, oligo_length=200, debug=False):
        self.oligo_length = oligo_length
        if debug:
            self.freqs_info_header = "\033[33m" + header + "\033[0m"
            self.dc_freq_header = "\033[32m" + dc_header + "\033[36m"
            self.ac_freq_header = "\033[32m" + ac_header + "\033[36m"
        else:
            self.freqs_info_header = header
            self.dc_freq_header = dc_header
            self.ac_freq_header = ac_header
        self.header_len = len(header)
        self.freq_type_header_len = len(dc_header)
        self.max_cat = max_cat
        self.max_runcat = max_runcat
        self.dc_freq_len = dc_freq_len
        self.ac_freq_len = ac_freq_len
        self.codebook = load_codebook_matrix(Path(jpegdna.__path__[0] + "/data/codebook.pkl"))
        self.debug = debug

    def format(self, inp):
        """Encodes and formats both DC and AC frequencies

        :param inp: frequencies for DC categories and AC run/categories
        :type inp: tuple(list(int))
        :returns: formatted frequency oligos
        :rtype: list(str)
        """
        if self.dc_freq_len != 0 and self.ac_freq_len != 0:
            return (self.format_frequencies(self.encode_frequencies(inp[0], "DC"), "DC") +
                    self.format_frequencies(self.encode_frequencies(inp[1], "AC"), "AC"))
        else:
            return []

    def deformat(self, oligos):
        """Deformats and decodes both DC and AC frequency oligos

        :param oligos: formatted frequency oligos for AC and DC
        :type oligos: list(str)
        :returns: decoded frequency tables
        :rtype: tuple(list(int))
        """
        dc_strand, ac_strand = self.deformat_frequencies(oligos)
        return (self.decode_frequencies(dc_strand, "DC"),
                self.decode_frequencies(ac_strand, "AC"))

    def encode_frequencies(self, freqs, freq_type):
        """Encode the frequencies using fixed-length codebooks

        :param freqs: frequency values to encode
        :type freqs: list(int)
        :param freq_type: DC/AC frequency indicator
        :type freq_type: str
        :returns: strand encoding the frequencies
        :rtype: str
        """
        strand = ""
        if freq_type == "AC":
            cw_length = self.ac_freq_len
        elif freq_type == "DC":
            cw_length = self.dc_freq_len
        else:
            raise ValueError
        for el in freqs:
            strand += self.codebook[cw_length-2][el]
        return strand

    def decode_frequencies(self, strand, freq_type):
        """Decode the frequencies using fixed-length codebooks

        :param strand: encoded frequency values
        :type strand: str
        :param freq_type: DC/AC frequency indicator
        :type freq_type: str
        :returns: list of frequency values
        :rtype: list(int)
        """
        freqs = []
        if freq_type == "AC":
            codeword_length = self.ac_freq_len
            n_freqs = self.max_runcat
        elif freq_type == "DC":
            codeword_length = self.dc_freq_len
            n_freqs = self.max_cat
        else:
            raise ValueError
        for i in range(n_freqs):
            codeword = strand[i*codeword_length:(i+1)*codeword_length]
            value = self.codebook[codeword_length-2].index(codeword)
            freqs.append(value)
        return freqs

    def format_frequencies(self, inp, freq_type):
        """Format the strand encoding either the DC or the AC frequencies

        :param inp: strand to format
        :type inp: str
        :param freq_type: DC/AC frequency indicator
        :type freq_type: str
        :returns: formatted AC or DC frequency oligos
        :rtype: list(str)
        """
        data_payload_length = self.oligo_length - self.DEFAULT_FREQUENCIES_OFFSET_CODE_LENGTH
        if freq_type == "AC":
            if self.debug:
                oligos = [self.freqs_info_header +
                          self.ac_freq_header +
                          self.codebook[self.DEFAULT_FREQUENCIES_OFFSET_CODE_LENGTH - 2][i//data_payload_length] +
                          "\033[0m" +
                          inp[i:i+data_payload_length]
                          for i in range(0, len(inp), data_payload_length)]
            else:
                oligos = [self.freqs_info_header +
                          self.ac_freq_header +
                          self.codebook[self.DEFAULT_FREQUENCIES_OFFSET_CODE_LENGTH - 2][i//data_payload_length] +
                          inp[i:i+data_payload_length]
                          for i in range(0, len(inp), data_payload_length)]
        elif freq_type == "DC":
            if self.debug:
                oligos = [self.freqs_info_header +
                          self.dc_freq_header +
                          self.codebook[self.DEFAULT_FREQUENCIES_OFFSET_CODE_LENGTH - 2][i//data_payload_length] +
                          "\033[0m" +
                          inp[i:i+data_payload_length]
                          for i in range(0, len(inp), data_payload_length)]
            else:
                oligos = [self.freqs_info_header +
                          self.dc_freq_header +
                          self.codebook[self.DEFAULT_FREQUENCIES_OFFSET_CODE_LENGTH - 2][i//data_payload_length] +
                          inp[i:i+data_payload_length]
                          for i in range(0, len(inp), data_payload_length)]
        else:
            raise ValueError
        ind = -1
        while oligos[-1][ind] not in ["A", "T", "C", "G"]:
            ind -= 1
        before = oligos[-1][ind]
        if self.debug:
            oligos[-1] = (oligos[-1] +
                          "\033[30;47m" +
                          generate_random_strand(data_payload_length-compute_length(oligos[-1]) + self.header_len + self.freq_type_header_len + self.DEFAULT_FREQUENCIES_OFFSET_CODE_LENGTH,
                                                 before,
                                                 "A") +
                          "\033[0;37;40m")
        else:
            oligos[-1] = (oligos[-1] +
                          generate_random_strand(data_payload_length-len(oligos[-1]) + self.header_len + self.freq_type_header_len + self.DEFAULT_FREQUENCIES_OFFSET_CODE_LENGTH,
                                                 before,
                                                 "A"))
        return oligos

    def deformat_frequencies(self, oligos):
        """Deformat the oligos describing either the DC or the AC frequencies

        :param oligos: oligos to deformat
        :type inp: list(str)
        :param freq_type: DC/AC frequency indicator
        :type freq_type: str
        :returns: strand encoding the frequencies
        :rtype: str
        """
        max_ac, max_dc = 0, 0
        begin = self.freq_type_header_len
        end = self.DEFAULT_FREQUENCIES_OFFSET_CODE_LENGTH + self.freq_type_header_len
        for oligo in oligos:
            if self.debug:
                if "\033[32m" + oligo[:begin] + "\033[36m" == self.dc_freq_header:
                    if self.codebook[self.DEFAULT_FREQUENCIES_OFFSET_CODE_LENGTH - 2].index(oligo[begin:end]) > max_dc:
                        max_dc = self.codebook[self.DEFAULT_FREQUENCIES_OFFSET_CODE_LENGTH - 2].index(oligo[begin:end])
                elif "\033[32m" + oligo[:begin] + "\033[36m" == self.ac_freq_header:
                    if self.codebook[self.DEFAULT_FREQUENCIES_OFFSET_CODE_LENGTH - 2].index(oligo[begin:end]) > max_ac:
                        max_ac = self.codebook[self.DEFAULT_FREQUENCIES_OFFSET_CODE_LENGTH - 2].index(oligo[begin:end])
                else:
                    raise ValueError
            else:
                if oligo[:begin] == self.dc_freq_header:
                    if self.codebook[self.DEFAULT_FREQUENCIES_OFFSET_CODE_LENGTH - 2].index(oligo[begin:end]) > max_dc:
                        max_dc = self.codebook[self.DEFAULT_FREQUENCIES_OFFSET_CODE_LENGTH - 2].index(oligo[begin:end])
                elif oligo[:begin] == self.ac_freq_header:
                    if self.codebook[self.DEFAULT_FREQUENCIES_OFFSET_CODE_LENGTH - 2].index(oligo[begin:end]) > max_ac:
                        max_ac = self.codebook[self.DEFAULT_FREQUENCIES_OFFSET_CODE_LENGTH - 2].index(oligo[begin:end])
                else:
                    raise ValueError
        strands_freqs_ac = [None]*(max_ac+1)
        strands_freqs_dc = [None]*(max_dc+1)
        for oligo in oligos:
            if self.debug:
                if "\033[32m" + oligo[:begin] + "\033[36m" == self.dc_freq_header:
                    strands_freqs_dc[self.codebook[self.DEFAULT_FREQUENCIES_OFFSET_CODE_LENGTH - 2].index(oligo[begin:end])] = oligo[end:]
                elif "\033[32m" + oligo[:begin] + "\033[36m" == self.ac_freq_header:
                    strands_freqs_ac[self.codebook[self.DEFAULT_FREQUENCIES_OFFSET_CODE_LENGTH - 2].index(oligo[begin:end])] = oligo[end:]
                else:
                    raise ValueError
            else:
                if oligo[:begin] == self.dc_freq_header:
                    strands_freqs_dc[self.codebook[self.DEFAULT_FREQUENCIES_OFFSET_CODE_LENGTH - 2].index(oligo[begin:end])] = oligo[end:]
                elif oligo[:begin] == self.ac_freq_header:
                    strands_freqs_ac[self.codebook[self.DEFAULT_FREQUENCIES_OFFSET_CODE_LENGTH - 2].index(oligo[begin:end])] = oligo[end:]
                else:
                    raise ValueError
        return "".join(strands_freqs_dc), "".join(strands_freqs_ac)


class RGBFrequenciesFormatter(GrayFrequenciesFormatter):
    """Formatter for the RGB DC and AC frequencies

    :ivar max_cat: max value for the categories
    :type max_cat: int
    :ivar max_runcat: max value for the run/categories
    :type max_runcat: int
    :ivar dc_freq_len: codeword length for encoding the dc frequencies
    :type dc_freq_len: int
    :ivar ac_freq_len: codeword length for encoding the ac frequencies
    :type ac_freq_len: int
    :ivar oligo_length: Size of the oligos used for formatting
    :type oligo_length: int
    """

    def format(self, inp):
        """Encodes and formats both DC and AC frequencies

        :param inp: frequencies for DC categories and AC run/categories
        :type inp: tuple(tuple(list(int)))
        :returns: formatted frequency oligos
        :rtype: list(str)
        """
        if self.dc_freq_len != 0 and self.ac_freq_len != 0:
            return (self.format_frequencies(self.encode_frequencies(np.concatenate((inp[0][0], inp[0][1], inp[0][2]), axis=0), "DC"), "DC") +
                    self.format_frequencies(self.encode_frequencies(np.concatenate((inp[1][0], inp[1][1], inp[1][2]), axis=0), "AC"), "AC"))
        else:
            return []

    def deformat(self, oligos):
        """Deformats and decodes both DC and AC frequency oligos

        :param oligos: formatted frequency oligos for AC and DC
        :type oligos: list(str)
        :returns: decoded frequency tables
        :rtype: tuple(tuple(list(int)))
        """
        if self.dc_freq_len == 0 and self.ac_freq_len == 0:
            return (None, None, None)
        dc_strand, ac_strand = self.deformat_frequencies(oligos)
        res = (self.decode_frequencies(dc_strand, "DC"),
               self.decode_frequencies(ac_strand, "AC"))
        return ((res[0][:len(res[0])//3], res[0][len(res[0])//3:2*(len(res[0])//3)], res[0][2*(len(res[0])//3):]),
                (res[1][:len(res[1])//3], res[1][len(res[1])//3:2*(len(res[1])//3)], res[1][2*(len(res[1])//3):]))
