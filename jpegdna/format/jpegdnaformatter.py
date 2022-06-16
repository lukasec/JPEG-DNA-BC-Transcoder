"""Gray-level strand formatter"""

import warnings
import math
from jpegdna.format import AbstractFormatter, GeneralInfoFormatter, GrayFrequenciesFormatter, RGBFrequenciesFormatter, DataFormatter
from jpegdna.tools.strand_tools import compute_length


class JpegDNAFormatter(AbstractFormatter):
    """Jpeg DNA gray level formatter class

    :param aplha: Alpha value (quantization step multiplier)
    :type alpha: float
    :param freq_origin: Choose between default and adapted frequencies
    :type freq_origin: str
    :param primer: Primer name used
    :type primer: str
    """

    DEFAULT_DC_FRQ_LEN = 7
    DEFAULT_AC_FREQ_LEN = 10
    DEFAULT_MAX_CAT = 11
    DEFAULT_MAX_RUNCAT = 162
    DEFAULT_BLOCKDIMS = (8, 8)
    DEFAULT_CENTERING_OFFSET = 75
    DEFAULT_OFFSET_SIZE = 8
    DEFAULT_GENERAL_INFO_HEADER = "AATAATA"
    DEFAULT_FREQS_INFO_HEADER = "ATCCGTC"
    DEFAULT_DATA_INFO_HEADER = "TTGAGGA"
    DEFAULT_DC_FREQ_HEADER = "ATTC"
    DEFAULT_AC_FREQ_HEADER = "AGAG"
    PRIMERS = {
        None : ("", ""),
        "illumina" : ("GTTCAGAGTTCTACAGTCCGACGATC", "TGGAATTCTCGGGTGCCAAGG")
    }
    PRIMER_LENGTHS = {
        None : (0, 0),
        "illumina" : (26, 21)
    }
    def __init__(self, alpha, image_type, sampler="4:2:2", freq_origin=None, primer=None, oligo_length=200, debug=False):
        self.debug = debug
        self.primer = None
        self.primer_type = primer
        self.set_primer()
        self.alpha = alpha
        self.freq_dc, self.freq_ac, self.m, self.n = None, None, None, None
        self.oligo_length = oligo_length

        if debug:
            self.general_info_header = "\033[33m" + self.DEFAULT_GENERAL_INFO_HEADER + "\033[0m"
            self.freqs_info_header = "\033[33m" + self.DEFAULT_FREQS_INFO_HEADER + "\033[0m"
            self.data_info_header = "\033[33m" + self.DEFAULT_DATA_INFO_HEADER + "\033[0m"
            self.dc_freq_header = "\033[32m" + self.DEFAULT_DC_FREQ_HEADER + "\033[36m"
            self.ac_freq_header = "\033[32m" + self.DEFAULT_AC_FREQ_HEADER + "\033[36m"
        else:
            self.general_info_header = self.DEFAULT_GENERAL_INFO_HEADER
            self.freqs_info_header = self.DEFAULT_FREQS_INFO_HEADER
            self.data_info_header = self.DEFAULT_DATA_INFO_HEADER
            self.dc_freq_header = self.DEFAULT_DC_FREQ_HEADER
            self.ac_freq_header = self.DEFAULT_AC_FREQ_HEADER

        self.general_info_header_len = len(self.DEFAULT_GENERAL_INFO_HEADER)
        self.freqs_info_header_len = len(self.DEFAULT_FREQS_INFO_HEADER)
        self.data_info_header_len = len(self.DEFAULT_DATA_INFO_HEADER)
        self.freq_type_header_len = len(self.DEFAULT_AC_FREQ_HEADER)

        self.image_id = "AATTC"
        self.image_id_len = len(self.image_id)
        self.parity_len = 4
        self.sense_len = 2
        self.blockdims = self.DEFAULT_BLOCKDIMS
        self.freq_origin = freq_origin
        self.offset_size = self.DEFAULT_OFFSET_SIZE
        if self.freq_origin == "from_img":
            self.dc_freq_len = self.DEFAULT_DC_FRQ_LEN
            self.ac_freq_len = self.DEFAULT_AC_FREQ_LEN
            self.max_cat = self.DEFAULT_MAX_CAT
            self.max_runcat = self.DEFAULT_MAX_RUNCAT
        elif self.freq_origin == "default" or self.freq_origin == "from_file" or self.freq_origin is None:
            self.dc_freq_len = 0
            self.ac_freq_len = 0
            self.max_cat = 0
            self.max_runcat = 0
        else:
            raise ValueError("Wrong freq_origin parameter")
        self.centering_offset = self.DEFAULT_CENTERING_OFFSET
        self.image_type = image_type
        self.sampler = sampler
        self.general_info_formatter = GeneralInfoFormatter(self.alpha,
                                                           self.freq_origin,
                                                           self.m,
                                                           self.n,
                                                           self.blockdims,
                                                           self.max_cat,
                                                           self.max_runcat,
                                                           self.offset_size,
                                                           self.dc_freq_len,
                                                           self.ac_freq_len,
                                                           self.image_type,
                                                           self.sampler,
                                                           self.DEFAULT_GENERAL_INFO_HEADER,
                                                           oligo_length=(self.oligo_length -
                                                                         self.primer_length -
                                                                         self.general_info_header_len -
                                                                         self.image_id_len -
                                                                         self.parity_len -
                                                                         self.sense_len),
                                                           debug=debug)
        if self.image_type == "gray":
            self.frequency_formatter = GrayFrequenciesFormatter(self.max_cat,
                                                                self.max_runcat,
                                                                self.dc_freq_len,
                                                                self.ac_freq_len,
                                                                self.DEFAULT_FREQS_INFO_HEADER,
                                                                self.DEFAULT_DC_FREQ_HEADER,
                                                                self.DEFAULT_AC_FREQ_HEADER,
                                                                oligo_length=(self.oligo_length -
                                                                              self.primer_length -
                                                                              self.freqs_info_header_len -
                                                                              self.image_id_len -
                                                                              self.parity_len -
                                                                              self.sense_len -
                                                                              self.freq_type_header_len),
                                                                debug=debug)
        elif self.image_type == "RGB":
            self.DEFAULT_MAX_CAT = 11 * 3 # pylint: disable = invalid-name
            self.DEFAULT_MAX_RUNCAT = 162 * 3 # pylint: disable = invalid-name
            self.frequency_formatter = RGBFrequenciesFormatter(self.max_cat,
                                                               self.max_runcat,
                                                               self.dc_freq_len,
                                                               self.ac_freq_len,
                                                               self.DEFAULT_FREQS_INFO_HEADER,
                                                               self.DEFAULT_DC_FREQ_HEADER,
                                                               self.DEFAULT_AC_FREQ_HEADER,
                                                               oligo_length=(self.oligo_length -
                                                                             self.primer_length -
                                                                             self.freqs_info_header_len -
                                                                             self.image_id_len -
                                                                             self.parity_len -
                                                                             self.sense_len -
                                                                             self.freq_type_header_len),
                                                               debug=debug)
        else:
            self.frequency_formatter = None
        self.data_formatter = DataFormatter(self.DEFAULT_DATA_INFO_HEADER,
                                            self.DEFAULT_OFFSET_SIZE,
                                            oligo_length=(self.oligo_length -
                                                          self.primer_length -
                                                          self.data_info_header_len -
                                                          self.image_id_len -
                                                          self.parity_len -
                                                          self.sense_len),
                                            debug=debug)

    def set_primer(self):
        """Sets the primer from the primer type"""
        try:
            self.primer_length = sum(self.PRIMER_LENGTHS[self.primer_type])
            if self.debug:
                self.primer = ("\033[31m" + self.PRIMERS[self.primer_type][0] + "\033[0m",
                               "\033[31m" + self.PRIMERS[self.primer_type][1] + "\033[0m")
            else:
                self.primer = self.PRIMERS[self.primer_type]
        except:
            raise ValueError("Non-existing primer")

    def set_alpha(self, alpha):
        """Set alpha value"""
        self.alpha = alpha
        self.general_info_formatter.alpha = alpha

    def set_freq_origin(self, choice):
        """Set frequency origin"""
        if choice in ["from_img", "from_file", "default"]:
            self.freq_origin = choice
        else:
            raise ValueError("Wrong freq origin")
        if self.freq_origin == "default" or self.freq_origin == "from_file":
            self.dc_freq_len = 0
            self.ac_freq_len = 0
            self.general_info_formatter.dc_freq_len = 0
            self.general_info_formatter.ac_freq_len = 0
            self.frequency_formatter.dc_freq_len = 0
            self.frequency_formatter.ac_freq_len = 0
        self.max_cat = self.DEFAULT_MAX_CAT
        self.max_runcat = self.DEFAULT_MAX_RUNCAT
        self.general_info_formatter.max_cat = self.DEFAULT_MAX_CAT
        self.general_info_formatter.max_runcat = self.DEFAULT_MAX_RUNCAT
        self.frequency_formatter.max_cat = self.DEFAULT_MAX_CAT
        self.frequency_formatter.max_runcat = self.DEFAULT_MAX_RUNCAT

    def set_state(self, *args, case=None):
        if case == "format":
            if len(args) < 4:
                raise ValueError("Wrong argument number")
            self.set_freq_origin(args[0])
            self.m = args[1]
            self.n = args[2]
            self.general_info_formatter.m = args[1]
            self.general_info_formatter.n = args[2]
            if self.freq_origin == "from_img":
                if len(args) != 6:
                    raise ValueError("Wrong argument number")
                if isinstance(args[3], tuple) and isinstance(args[4], tuple):
                    self.freq_dc = (args[3][0].astype(int),
                                    args[3][1].astype(int),
                                    args[3][2].astype(int))
                    self.freq_ac = (args[4][0].astype(int),
                                    args[4][1].astype(int),
                                    args[4][2].astype(int))
                    max_freq_dc = max((max(self.freq_dc[0]),
                                       max(self.freq_dc[1]),
                                       max(self.freq_dc[2])))
                    max_freq_ac = max((max(self.freq_ac[0]),
                                       max(self.freq_ac[1]),
                                       max(self.freq_ac[2])))
                else:
                    self.freq_dc = args[3].astype(int)
                    self.freq_ac = args[4].astype(int)
                    max_freq_dc, max_freq_ac = max(self.freq_dc), max(self.freq_ac)
                if max_freq_dc <= 7997:
                    self.dc_freq_len = self.DEFAULT_DC_FRQ_LEN
                else:
                    found = False
                    for ii in range(5, len(self.general_info_formatter.codebook)):
                        if len(self.general_info_formatter.codebook[ii]) > max_freq_dc:
                            self.dc_freq_len = ii + 2
                            warnings.warn(f"Default length for the DC frequencies is too small, length set up to {self.dc_freq_len}", ResourceWarning)
                            found = True
                            break
                    if not found:
                        raise IndexError("Codebook too small for the DC frequencies")
                if max_freq_ac <= 464743:
                    self.ac_freq_len = self.DEFAULT_AC_FREQ_LEN
                else:
                    found = False
                    for ii in range(8, len(self.general_info_formatter.codebook)):
                        if len(self.general_info_formatter.codebook[ii]) > max_freq_ac:
                            self.ac_freq_len = ii + 2
                            warnings.warn(f"Default length for the AC frequencies is too small, length set up to {self.ac_freq_len}", ResourceWarning)
                            found = True
                            break
                    if not found:
                        raise IndexError("Codebook too small for the AC frequencies")
                self.general_info_formatter.dc_freq_len = self.dc_freq_len
                self.general_info_formatter.ac_freq_len = self.ac_freq_len
                self.frequency_formatter.dc_freq_len = self.dc_freq_len
                self.frequency_formatter.ac_freq_len = self.ac_freq_len
            n_data_oligos = math.ceil(args[-1] /(self.oligo_length -
                                                 self.primer_length -
                                                 self.general_info_header_len -
                                                 self.image_id_len -
                                                 self.parity_len -
                                                 self.sense_len -
                                                 self.DEFAULT_OFFSET_SIZE))
            if n_data_oligos <= 24633:
                self.offset_size = self.DEFAULT_OFFSET_SIZE
            else:
                found = False
                for ii in range(6, len(self.general_info_formatter.codebook)):
                    n_data_oligos = math.ceil(args[-1] /(self.oligo_length -
                                                        self.primer_length -
                                                        self.general_info_header_len -
                                                        self.image_id_len -
                                                        self.parity_len -
                                                        self.sense_len -
                                                        (ii+2)))
                    if len(self.general_info_formatter.codebook[ii]) > n_data_oligos:
                        self.offset_size = ii + 2
                        warnings.warn(f"Default length for the data offsets is too small, length set up to {self.offset_size}", ResourceWarning)
                        found = True
                        break
                if not found:
                    raise IndexError("Codebook too small for the data strand offsets")
            self.general_info_formatter.offset_size = self.offset_size
            self.data_formatter.offset_size = self.offset_size
        else:
            raise ValueError

    def get_state(self, case=None):
        if case == "deformat":
            return self.alpha, self.m, self.n, self.freq_dc, self.freq_ac
        else:
            raise ValueError

    def full_format(self, inp, *args):
        args += tuple([len(inp)])
        self.set_state(*args, case="format")
        oligos = self.format(inp)
        if self.debug:
            for oligo in oligos:
                print(oligo)
        return oligos

    def full_deformat(self, oligos, *args):
        data_strand = self.deformat(oligos)
        return data_strand, self.get_state(case="deformat")

    def format(self, inp):
        oligos = ([self.general_info_formatter.format(None)] +
                  self.frequency_formatter.format((self.freq_dc, self.freq_ac)) +
                  self.data_formatter.format(inp))
        if self.debug:
            for oligo in oligos:
                print(oligo)
        return self.add_primers_and_sense(self.add_ids(oligos, self.centering_offset))

    def deformat(self, oligos):
        oligos_cleanup = [None] * len(oligos)
        for i, oligo in enumerate(oligos):
            oligos_cleanup[i] = ""
            for char in oligo:
                if char in ["A", "T", "C", "G"]:
                    oligos_cleanup[i] += char
        if self.debug:
            for oligo in oligos_cleanup:
                print(oligo)
        payload_strands = self.get_payload(oligos_cleanup)
        general_info_strand, freq_strands, data_strands = None, [], []
        for strand in payload_strands:
            header = strand[:7]
            substrand = strand[7:]
            if self.debug:
                print("\033[33m" + header + "\033[0m" + substrand)
                if "\033[33m" + header + "\033[0m" == self.general_info_header:
                    general_info_strand = substrand
                elif "\033[33m" + header + "\033[0m" == self.freqs_info_header:
                    freq_strands.append(substrand)
                elif "\033[33m" + header + "\033[0m" == self.data_info_header:
                    data_strands.append(substrand)
                else:
                    raise ValueError("Wrong header")
            else:
                if header == self.general_info_header:
                    general_info_strand = substrand
                elif header == self.freqs_info_header:
                    freq_strands.append(substrand)
                elif header == self.data_info_header:
                    data_strands.append(substrand)
                else:
                    raise ValueError("Wrong header")

        # General info
        self.general_info_formatter.deformat(general_info_strand)
        self.image_type = self.general_info_formatter.IMAGE_TYPES[self.general_info_formatter.image_type]
        self.sampler = self.general_info_formatter.sampler
        if self.image_type == "gray":
            self.frequency_formatter = GrayFrequenciesFormatter(self.max_cat,
                                                                self.max_runcat,
                                                                self.dc_freq_len,
                                                                self.ac_freq_len,
                                                                self.DEFAULT_FREQS_INFO_HEADER,
                                                                self.DEFAULT_DC_FREQ_HEADER,
                                                                self.DEFAULT_AC_FREQ_HEADER,
                                                                oligo_length=(self.oligo_length -
                                                                              self.primer_length -
                                                                              self.freqs_info_header_len -
                                                                              self.image_id_len -
                                                                              self.parity_len -
                                                                              self.sense_len -
                                                                              self.freq_type_header_len),
                                                                debug=self.debug)
        elif self.image_type == "RGB":
            self.DEFAULT_MAX_CAT = 11 * 3 # pylint: disable = invalid-name
            self.DEFAULT_MAX_RUNCAT = 162 * 3 # pylint: disable = invalid-name
            self.frequency_formatter = RGBFrequenciesFormatter(self.max_cat,
                                                               self.max_runcat,
                                                               self.dc_freq_len,
                                                               self.ac_freq_len,
                                                               self.DEFAULT_FREQS_INFO_HEADER,
                                                               self.DEFAULT_DC_FREQ_HEADER,
                                                               self.DEFAULT_AC_FREQ_HEADER,
                                                               oligo_length=(self.oligo_length -
                                                                             self.primer_length -
                                                                             self.freqs_info_header_len -
                                                                             self.image_id_len -
                                                                             self.parity_len -
                                                                             self.sense_len -
                                                                             self.freq_type_header_len),
                                                               debug=self.debug)
        self.freq_origin = self.general_info_formatter.freq_origin
        self.alpha = self.general_info_formatter.alpha
        self.blockdims = self.general_info_formatter.blockdims
        self.m, self.n = self.general_info_formatter.m, self.general_info_formatter.n
        self.offset_size = self.general_info_formatter.offset_size
        self.data_formatter.offset_size = self.offset_size

        # Frequencies
        if self.freq_origin == "from_img":
            self.max_cat = self.general_info_formatter.max_cat
            self.max_runcat = self.general_info_formatter.max_runcat
            self.dc_freq_len = self.general_info_formatter.dc_freq_len
            self.ac_freq_len = self.general_info_formatter.ac_freq_len
            self.frequency_formatter.dc_freq_len = self.general_info_formatter.dc_freq_len
            self.frequency_formatter.ac_freq_len = self.general_info_formatter.ac_freq_len
            self.frequency_formatter.max_cat = self.general_info_formatter.max_cat
            self.frequency_formatter.max_runcat = self.general_info_formatter.max_runcat
            (self.freq_dc, self.freq_ac) = self.frequency_formatter.deformat(freq_strands)
            if self.debug:
                print(f"DC frequencies : {self.freq_dc}")
                print(f"AC frequencies : {self.freq_ac}")
        #if RGB
        elif self.DEFAULT_MAX_CAT == 33 and self.DEFAULT_MAX_RUNCAT == 162*3:
            self.freq_ac = (None, None, None)
            self.freq_dc = (None, None, None)

        # Data strand
        data_strand = self.data_formatter.deformat(data_strands)
        if self.debug:
            print(f"Data strand: {data_strand}")
        return data_strand

    def add_ids(self, oligos, n):
        """Adding primers to formatted oligos

        :param oligos: list of formatted oligos without offset
        :type oligos: list
        :return: list of oligos with offset added at the beginning of each oligo
        :rtpye: list
        """

        res = []
        for el in oligos:
            el1, el2 = self.cut_payload(el, n)
            if self.debug:
                res.append(el1 + "\033[34m" + self.image_id + "\033[35m" + self.add_parity_strand(el, self.image_id, self.add_sense_nt('end')) + el2)
            else:
                res.append(el1 + self.image_id + self.add_parity_strand(el, self.image_id, self.add_sense_nt('end')) + el2)
        return res

    def add_primers_and_sense(self, oligos):
        """Adding primers to formatted oligos

        :param oligos: list of formatted oligos without primers
        :type oligos: list
        :return: list of oligos with primers added at the beginning and at the end of each oligo
        :rtpye: list
        """

        res = []
        for el in oligos:
            if self.debug:
                res.append(self.primer[0] + "\033[0;32m" + self.add_sense_nt("begin") + "\033[0m" + el + "\033[0;32m" + self.add_sense_nt("end") + "\033[0m" + self.primer[1])
            else:
                res.append(self.primer[0] + self.add_sense_nt("begin") + el + self.add_sense_nt("end") + self.primer[1])
        return res

    def get_payload(self, oligos):
        """Taking primers and sense nts off formatted oligos

        :param oligos: list of formatted oligos without primers
        :type oligos: list
        :return: list of oligos with primers added at the beginning and at the end of each oligo
        :rtpye: list
        """

        res = []
        payload_strands = []
        if self.debug:
            for oligo in oligos:
                payload_strands.append(oligo[compute_length(self.primer[0])+1+(self.oligo_length - self.centering_offset - self.primer_length - 2):-(compute_length(self.primer[1])+1)] +
                                       oligo[compute_length(self.primer[0])+1:compute_length(self.primer[0])+1+(self.oligo_length - self.centering_offset - self.primer_length - 11)])
                res.append("\033[31m" + oligo[:compute_length(self.primer[0])] +
                           "\033[32m" + oligo[compute_length(self.primer[0])] +
                           "\033[0m" + oligo[compute_length(self.primer[0])+1:
                                             compute_length(self.primer[0])+1+(self.oligo_length - self.centering_offset - self.primer_length - 11)] +
                           "\033[34m" + oligo[compute_length(self.primer[0])+1+(self.oligo_length - self.centering_offset - self.primer_length - 11):
                                              compute_length(self.primer[0])+1+(self.oligo_length - self.centering_offset - self.primer_length - 6)] +
                           "\033[35m" + oligo[compute_length(self.primer[0])+1+(self.oligo_length - self.centering_offset - self.primer_length - 6):
                                              compute_length(self.primer[0])+1+(self.oligo_length - self.centering_offset - self.primer_length - 2)] +
                           "\033[0m" + oligo[compute_length(self.primer[0])+1+(self.oligo_length - self.centering_offset - self.primer_length - 2):
                                             -(compute_length(self.primer[1])+1)] +
                           "\033[32m" + oligo[-(compute_length(self.primer[1])+1)] +
                           "\033[31m" + oligo[-(compute_length(self.primer[1])):] + "\033[0m")
        else:
            for oligo in oligos:
                payload_strands.append(oligo[len(self.primer[0])+1+(self.oligo_length - self.centering_offset - self.primer_length - 2):-(len(self.primer[1])+1)] +
                                       oligo[len(self.primer[0])+1:len(self.primer[0])+1+(self.oligo_length - self.centering_offset - self.primer_length - 11)])
        if self.debug:
            for oligo in res:
                print(oligo)
        return payload_strands

    def add_sense_nt(self, pos):
        """Compute the sens nucleotide either the beginning one or the ending one

        :param pos: either "begin" or "end", position of the sense nt to compute
        :type pos: str
        :returns: sense nucleotide
        :rtype: str
        """

        if pos == "begin":
            if self.primer_type is not None and self.primer[0][-1] == "A":
                return "T"
            return "A"
        elif pos == "end":
            if self.primer_type is not None and self.primer[1][0] == "C":
                return "G"
            return "C"
        else:
            raise ValueError

    def add_parity_strand(self, data, image_id, sense_nt):
        """Computes the parity strand for the current oligo

        :param data: strand on which to compute parities for each base
        :type data: str
        :param image_id: id of the image
        :type image_id: str
        :param sense_nt: sense nucelotide
        :type sens_nt: str
        """

        parity = [data.count("A")%2,
                  data.count("T")%2,
                  data.count("C")%2,
                  data.count("G")%2]
        strand = [None]*4
        # First element
        if parity[0] == 0:
            first_candidate = "A"
            second_candidate = "T"
        else:
            first_candidate = "C"
            second_candidate = "G"
        if image_id[-1] != first_candidate:
            strand[0] = first_candidate
        else:
            strand[0] = second_candidate
        # Last element
        if parity[-1] == 0:
            first_candidate = "A"
            second_candidate = "T"
        else:
            first_candidate = "C"
            second_candidate = "G"
        if sense_nt != first_candidate:
            strand[-1] = first_candidate
        else:
            strand[-1] = second_candidate
        #Middle elements : case with different parities (simple)
        if parity[1] != parity[2]:
            # Second element
            if parity[1] == 0:
                first_candidate = "A"
                second_candidate = "T"
            else:
                first_candidate = "C"
                second_candidate = "G"
            if strand[0] != first_candidate:
                strand[1] = first_candidate
            else:
                strand[1] = second_candidate
            # Third element
            if parity[2] == 0:
                first_candidate = "A"
                second_candidate = "T"
            else:
                first_candidate = "C"
                second_candidate = "G"
            if strand[3] != first_candidate:
                strand[2] = first_candidate
            else:
                strand[2] = second_candidate
        # Middle elements: case with same parities (hard)
        else:
            if parity[0] == parity[-1] or parity[0] == parity[1]:
                if parity[1] == 0:
                    first_candidate = "A"
                    second_candidate = "T"
                else:
                    first_candidate = "C"
                    second_candidate = "G"
                if strand[0] != first_candidate:
                    strand[1] = first_candidate
                else:
                    strand[1] = second_candidate
                if strand[1] != first_candidate:
                    strand[2] = first_candidate
                else:
                    strand[2] = second_candidate
            else:
                if parity[2] == 0:
                    first_candidate = "A"
                    second_candidate = "T"
                else:
                    first_candidate = "C"
                    second_candidate = "G"
                if strand[3] != first_candidate:
                    strand[2] = first_candidate
                else:
                    strand[2] = second_candidate
                if strand[2] != first_candidate:
                    strand[1] = first_candidate
                else:
                    strand[1] = second_candidate

        return "".join(strand)

    def cut_payload(self, el, n):
        """Cuts the payoad in two halves after the n-th nucleotide

        :param el: Stand to be cut
        :type el: string
        :returns: Two cuts
        :rtype: Tuple(string)
        """

        count = 0
        pos = 0
        for char in el:
            pos += 1
            if char in ["A", "T", "C", "G"]:
                count += 1
            if count == n:
                break
        return el[pos:], el[:pos]
