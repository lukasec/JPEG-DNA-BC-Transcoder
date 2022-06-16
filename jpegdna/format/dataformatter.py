"""Formatting method for data oligo"""
from pathlib import Path

import jpegdna
from jpegdna.format import AbstractFormatter
from jpegdna.tools.strand_tools import generate_random_strand, compute_length
from jpegdna.tools.loader import load_codebook_matrix


class DataFormatter(AbstractFormatter):
    """Formatter for the strand coming out of the compression algorithm

    :ivar oligo_length: Size of the oligos used for formatting
    :type oligo_length: int
    """

    def __init__(self, header, offset_size, oligo_length=200, debug=False):
        self.oligo_length = oligo_length
        self.offset_size = offset_size
        if debug:
            self.data_info_header = "\033[33m" + header + "\033[0m"
        else:
            self.data_info_header = header
        self.header_len = len(header)
        self.codebook = load_codebook_matrix(Path(jpegdna.__path__[0] + "/data/codebook.pkl"))
        self.debug = debug

    def format(self, inp):
        """Method formatting the data strand into oligos

        :param inp: strand resulting from the compression algorithm
        :type inp: str
        :returns: list of formatted oligos of size self.oligo_length
        :rtype: list(str)
        """
        data_payload_length = self.oligo_length - self.offset_size
        if self.debug:
            oligos = [self.data_info_header +
                      "\033[36m" +
                      self.codebook[self.offset_size - 2][i//data_payload_length] +
                      "\033[0m" +
                      inp[i:i+data_payload_length] for i in range(0, len(inp), data_payload_length)]
        else:
            oligos = [self.data_info_header +
                      self.codebook[self.offset_size - 2][i//data_payload_length] +
                      inp[i:i+data_payload_length] for i in range(0, len(inp), data_payload_length)]
        ind = -1
        while oligos[-1][ind] not in ["A", "T", "C", "G"]:
            ind -= 1
        before = oligos[-1][ind]
        if self.debug:
            oligos[-1] = (oligos[-1] +
                          "\033[30;47m" +
                          generate_random_strand(data_payload_length-compute_length(oligos[-1]) + self.header_len + self.offset_size,
                                                 before,
                                                 "A") +
                          "\033[0;37;40m")
        else:
            oligos[-1] = (oligos[-1] +
                          generate_random_strand(data_payload_length-len(oligos[-1]) + self.header_len + self.offset_size,
                                                 before,
                                                 "A"))
        return oligos

    def deformat(self, oligos):
        """Methods deformatting the oligos and rebuilding the data strand

        :param oligos: data oligos
        :type oligos: list(str)
        :returns: data strand resulting from compression
        :rtype: str
        """
        max_offset = 0
        for oligo in oligos:
            if self.codebook[self.offset_size - 2].index(oligo[:self.offset_size]) > max_offset:
                max_offset = self.codebook[self.offset_size - 2].index(oligo[:self.offset_size])
        data_strands = [None] * (max_offset + 1)
        for oligo in oligos:
            data_strands[self.codebook[self.offset_size - 2].index(oligo[:self.offset_size])] = oligo[self.offset_size:]
        return "".join(data_strands)
