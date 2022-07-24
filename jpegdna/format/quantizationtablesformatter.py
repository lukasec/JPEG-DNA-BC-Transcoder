"""Formatting method for general info oligo"""

from pathlib import Path
import numpy as np

import jpegdna
from jpegdna.format import AbstractFormatter
from jpegdna.tools.strand_tools import generate_random_strand, compute_length
from jpegdna.tools.loader import load_codebook_matrix

class QuantizationTablesInfoFormatter(AbstractFormatter):
    """Formatter for the general information related to the compression

    :ivar blockdims: dimensions of the block used for DCT
    :type blockdims: tuple
    :ivar image_type: type of image
    :type image_type: str
    :ivar header: header for the quantization tables oligos
    :type header: str
    :ivar oligo_length: Size of the oligos used for formatting
    :type oligo_length: int
    """
    DEFAULT_QUANTIZATION_TABLES_OFFSET_CODE_LENGTH = 7
    DEFAULT_QUANTIZATION_TABLES_CODE_LENGTH = 10
    def __init__(self, blockdims, image_type, header, oligo_length=200, debug=False):
        self.blockdims = blockdims
        self.image_type = image_type
        self.header = header
        if debug:
            self.header = "\033[33m" + header + "\033[0m"
        else:
            self.header = header
        self.header_len = len(header)
        self.oligo_length = oligo_length
        self.cw_length = self.DEFAULT_QUANTIZATION_TABLES_CODE_LENGTH
        self.debug = debug
        self.codebook = load_codebook_matrix(Path(jpegdna.__path__[0] + "/data/codebook.pkl"))

    def format(self, inp):
        """Encodes and formats the quantization tables

        :param inp: quantization tables
        :type inp: np.array|tuple(np.array)
        :returns: formatted quantization tables oligos
        :rtype: list(str)
        """
        return (self.format_tables(self.encode_tables(inp)))

    def deformat(self, oligos):
        """Deformats and decodes quantization tables

        :param oligos: formatted quantization tables
        :type oligos: list(str)
        :returns: decoded quantization tables
        :rtype: np.array|tuple(np.array)
        """
        strand = self.deformat_tables(oligos)
        return (self.decode_tables(strand))

    def format_tables(self, inp):
        """Format the strand encoding the quantization tables

        :param inp: strand to format
        :type inp: str
        :returns: formatted quantization tables oligos
        :rtype: list(str)
        """
        data_payload_length = self.oligo_length - self.DEFAULT_QUANTIZATION_TABLES_OFFSET_CODE_LENGTH
        if self.debug:
            oligos = [self.header +
                      self.codebook[self.DEFAULT_QUANTIZATION_TABLES_OFFSET_CODE_LENGTH - 2][i//data_payload_length] +
                      inp[i:i+data_payload_length]
                      for i in range(0, len(inp), data_payload_length)]
        else:
            oligos = [self.header +
                      self.codebook[self.DEFAULT_QUANTIZATION_TABLES_OFFSET_CODE_LENGTH - 2][i//data_payload_length] +
                      inp[i:i+data_payload_length]
                      for i in range(0, len(inp), data_payload_length)]
        ind = -1
        while oligos[-1][ind] not in ["A", "T", "C", "G"]:
            ind -= 1
        before = oligos[-1][ind]
        if self.debug:
            oligos[-1] = (oligos[-1] +
                          "\033[30;47m" +
                          generate_random_strand(data_payload_length-compute_length(oligos[-1]) + self.header_len + self.DEFAULT_QUANTIZATION_TABLES_OFFSET_CODE_LENGTH,
                                                 before,
                                                 "A") +
                          "\033[0;37;40m")
        else:
            oligos[-1] = (oligos[-1] +
                          generate_random_strand(data_payload_length-len(oligos[-1]) + self.header_len + self.DEFAULT_QUANTIZATION_TABLES_OFFSET_CODE_LENGTH,
                                                 before,
                                                 "A"))
        return oligos

    def deformat_tables(self, oligos):
        """Deformat the oligos describing the quantization tables

        :param oligos: oligos to deformat
        :type inp: list(str)
        :returns: strand encoding the quantization tables
        :rtype: str
        """
        maxi = 0
        end = self.DEFAULT_QUANTIZATION_TABLES_OFFSET_CODE_LENGTH
        for oligo in oligos:
            if self.debug:
                if self.codebook[self.DEFAULT_QUANTIZATION_TABLES_OFFSET_CODE_LENGTH - 2].index(oligo[:end]) > maxi:
                    maxi = self.codebook[self.DEFAULT_QUANTIZATION_TABLES_OFFSET_CODE_LENGTH - 2].index(oligo[:end])
            else:
                if self.codebook[self.DEFAULT_QUANTIZATION_TABLES_OFFSET_CODE_LENGTH - 2].index(oligo[:end]) > maxi:
                    maxi = self.codebook[self.DEFAULT_QUANTIZATION_TABLES_OFFSET_CODE_LENGTH - 2].index(oligo[:end])
        strands_quantization = [None]*(maxi+1)
        for oligo in oligos:
            if self.debug:
                strands_quantization[self.codebook[self.DEFAULT_QUANTIZATION_TABLES_OFFSET_CODE_LENGTH - 2].index(oligo[:end])] = oligo[end:]
            else:
                strands_quantization[self.codebook[self.DEFAULT_QUANTIZATION_TABLES_OFFSET_CODE_LENGTH - 2].index(oligo[:end])] = oligo[end:]
        return "".join(strands_quantization)

    def encode_tables(self, inp):
        """Encode the quantization tables using fixed-length codebooks

        :param inp: quantization tables to encode
        :type inp: np.array|tuple(np.array)
        :returns: strand encoding the quantization tables
        :rtype: str
        """
        strand = ""
        if self.image_type == "gray":
            for i in range(self.blockdims[0]):
                for j in range(self.blockdims[1]):
                    strand += self.codebook[self.cw_length-2][round(100*inp[i,j])]
        elif self.image_type == "RGB":
            for k in range(3):
                for i in range(self.blockdims[0]):
                    for j in range(self.blockdims[1]):
                        strand += self.codebook[self.cw_length-2][round(100*inp[k][i,j])]
        else:
            raise ValueError
        return strand

    def decode_tables(self, strand):
        """Decode the quantization tables using fixed-length codebooks

        :param strand: encoded quantization tables
        :type strand: str
        :returns: quantization tables
        :rtype: np.array|tuple(np.array)
        """
        if self.image_type == "gray":
            tables = np.zeros(self.blockdims)
            for i in range(self.blockdims[0]):
                for j in range(self.blockdims[1]):
                    codeword = strand[:self.cw_length]
                    strand = strand[self.cw_length:]
                    tables[i, j] = self.codebook[self.cw_length-2].index(codeword)/100
        elif self.image_type == "RGB":
            tables = (np.zeros(self.blockdims),
                      np.zeros(self.blockdims),
                      np.zeros(self.blockdims))
            for k in range(3):
                for i in range(self.blockdims[0]):
                    for j in range(self.blockdims[1]):
                        codeword = strand[:self.cw_length]
                        strand = strand[self.cw_length:]
                        tables[k][i, j] = self.codebook[self.cw_length-2].index(codeword)/100
        return tables
