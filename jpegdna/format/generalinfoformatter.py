"""Formatting method for general info oligo"""

from pathlib import Path
import numpy as np

import jpegdna
from jpegdna.format import AbstractFormatter
from jpegdna.tools.strand_tools import generate_random_strand, compute_length
from jpegdna.tools.loader import load_codebook_matrix
from jpegdna.transforms import ChannelSampler


class GeneralInfoFormatter(AbstractFormatter):
    """Formatter for the general information related to the compression

    :ivar alpha: alpha value of the compression, if it is known
    :type alpha: float
    :ivar freq_origin: origin of the frequencies ("default" or "from_img")
    :type freq_origin: str
    :ivar m: first dimension of the image
    :type m: int
    :ivar n: second dimension of the image
    :type n: int
    :ivar blockdims: dimensions of the block used for DCT
    :type blockdims: tuple
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

    IMAGE_TYPES = ["gray", "RGB"]
    def __init__(self, alpha, freq_origin, m, n, blockdims, max_cat, max_runcat, offset_size, dc_freq_len, ac_freq_len, image_type, sampler, header, oligo_length=200, debug=False):
        self.alpha = alpha
        self.freq_origin = freq_origin
        self.m, self.n = m, n
        self.oligo_length = oligo_length
        if debug:
            self.general_info_header = "\033[33m" + header + "\033[0m"
        else:
            self.general_info_header = header
        self.header_len = len(header)
        self.barcodes = ['AATTC',
                         'AAGAG',
                         'ATAAC',
                         'ACCTG',
                         'TTATG',
                         'TCTCG',
                         'TGCAG',
                         'CCACA',
                         'CGTTG',
                         'GGATC']
        self.blockdims = blockdims
        self.max_cat = max_cat
        self.max_runcat = max_runcat
        self.offset_size = offset_size
        self.dc_freq_len = dc_freq_len
        self.ac_freq_len = ac_freq_len
        self.codebook = load_codebook_matrix(Path(jpegdna.__path__[0] + "/data/codebook.pkl"))
        self.debug = debug
        if image_type is not None:
            self.image_type = self.IMAGE_TYPES.index(image_type)
        else:
            self.image_type = None
        self.sampler = sampler
        # self.samplers = list(set([el[25:].replace("_", ":") for el in dir(ChannelSampler) if "_ChannelSampler__" in el]))
        self.samplers = ['4:2:0', '4:2:2', '4:1:1', '4:4:0', '4:4:4']
        if self.sampler is not None:
            self.channel_sampler = ChannelSampler(sampler=self.sampler)
        else:
            self.channel_sampler = None

    def colored_image(self):
        """Check if image is colored or gray level

        :rtype: bool
        """
        return self.image_type == 1

    def format(self, inp):
        if inp is not None:
            raise ValueError
        data_payload_length = self.oligo_length
        n_rows, n_cols = self.m, self.n
        alpha = round(self.alpha, 3)
        blockdims = self.blockdims
        max_cat, max_runcat = self.max_cat, self.max_runcat
        offset_size = self.offset_size
        dc_freq_len, ac_freq_len = self.dc_freq_len, self.ac_freq_len
        int_alpha = int(alpha)
        float_alpha = alpha - int_alpha
        image_type = self.image_type
        if self.debug:
            oligo = (self.general_info_header +
                     "\033[31m" + self.barcodes[blockdims[0]] + self.barcodes[blockdims[1]] +
                     "\033[32m" + self.barcodes[n_rows//1000] + self.barcodes[(n_rows%1000)//100] + self.barcodes[(n_rows%100)//10] + self.barcodes[n_rows%10] +
                     "\033[31m" + self.barcodes[n_cols//1000] + self.barcodes[(n_cols%1000)//100] + self.barcodes[(n_cols%100)//10] + self.barcodes[n_cols%10] +
                     "\033[32m" + self.barcodes[max_cat//10] + self.barcodes[max_cat%10] +
                     "\033[31m" + self.barcodes[max_runcat//100] + self.barcodes[(max_runcat%100)//10] + self.barcodes[max_runcat%10] +
                     "\033[32m" + self.barcodes[offset_size//10] + self.barcodes[offset_size%10] +
                     "\033[31m" + self.barcodes[dc_freq_len//10] + self.barcodes[dc_freq_len%10] +
                     "\033[32m" + self.barcodes[ac_freq_len//10] + self.barcodes[ac_freq_len%10] +
                     "\033[31m" + self.barcodes[int_alpha] +
                     "\033[32m" + self.barcodes[int((float_alpha*10)%10)] +
                     "\033[32m" + self.barcodes[int((float_alpha*100)%10)] +
                     "\033[32m" + self.barcodes[int((float_alpha*1000)%10)] +
                     "\033[31m" + self.barcodes[image_type] + "\033[0m")
        else:
            oligo = (self.general_info_header +
                     self.barcodes[blockdims[0]] + self.barcodes[blockdims[1]] +
                     self.barcodes[n_rows//1000] + self.barcodes[(n_rows%1000)//100] + self.barcodes[(n_rows%100)//10] + self.barcodes[n_rows%10] +
                     self.barcodes[n_cols//1000] + self.barcodes[(n_cols%1000)//100] + self.barcodes[(n_cols%100)//10] + self.barcodes[n_cols%10] +
                     self.barcodes[max_cat//10] + self.barcodes[max_cat%10] +
                     self.barcodes[max_runcat//100] + self.barcodes[(max_runcat%100)//10] + self.barcodes[max_runcat%10] +
                     self.barcodes[offset_size//10] + self.barcodes[offset_size%10] +
                     self.barcodes[dc_freq_len//10] + self.barcodes[dc_freq_len%10] +
                     self.barcodes[ac_freq_len//10] + self.barcodes[ac_freq_len%10] +
                     self.barcodes[int_alpha] +
                     self.barcodes[int((float_alpha*10)%10)] +
                     self.barcodes[int((float_alpha*100)%10)] +
                     self.barcodes[int((float_alpha*1000)%10)] +
                     self.barcodes[image_type])
        if self.colored_image():
            oligo += self.barcodes[self.samplers.index(self.sampler)]
        ind = -1
        while oligo[ind] not in ["A", "T", "C", "G"]:
            ind -= 1
        before = oligo[ind]
        if self.debug:
            return oligo + "\033[30;47m" + generate_random_strand(data_payload_length-compute_length(oligo)+self.header_len, before, "A") + "\033[0;37;40m"
        else:
            return oligo + generate_random_strand(data_payload_length-len(oligo)+self.header_len, before, "A")

    def deformat(self, oligos):
        oligo = oligos
        reading_head = 0
        self.blockdims = (self.barcodes.index(oligo[reading_head:reading_head+5]), self.barcodes.index(oligo[reading_head+5:reading_head+10]))
        reading_head += 10
        self.m = (self.barcodes.index(oligo[reading_head:reading_head+5]) * 1000 +
                  self.barcodes.index(oligo[reading_head+5:reading_head+10]) * 100 +
                  self.barcodes.index(oligo[reading_head+10:reading_head+15]) * 10 +
                  self.barcodes.index(oligo[reading_head+15:reading_head+20]))
        reading_head += 20
        self.n = (self.barcodes.index(oligo[reading_head:reading_head+5]) * 1000 +
                  self.barcodes.index(oligo[reading_head+5:reading_head+10]) * 100 +
                  self.barcodes.index(oligo[reading_head+10:reading_head+15]) * 10 +
                  self.barcodes.index(oligo[reading_head+15:reading_head+20]))
        reading_head += 20
        self.max_cat = (self.barcodes.index(oligo[reading_head:reading_head+5]) * 10 +
                        self.barcodes.index(oligo[reading_head+5:reading_head+10]))
        reading_head += 10
        self.max_runcat = (self.barcodes.index(oligo[reading_head:reading_head+5]) * 100 +
                           self.barcodes.index(oligo[reading_head+5:reading_head+10]) * 10 +
                           self.barcodes.index(oligo[reading_head+10:reading_head+15]))
        reading_head += 15
        self.offset_size = (self.barcodes.index(oligo[reading_head:reading_head+5]) * 10 +
                            self.barcodes.index(oligo[reading_head+5:reading_head+10]))
        reading_head += 10
        self.dc_freq_len = (self.barcodes.index(oligo[reading_head:reading_head+5]) * 10 +
                            self.barcodes.index(oligo[reading_head+5:reading_head+10]))
        reading_head += 10
        self.ac_freq_len = (self.barcodes.index(oligo[reading_head:reading_head+5]) * 10 +
                            self.barcodes.index(oligo[reading_head+5:reading_head+10]))
        if self.dc_freq_len == 0 and self.ac_freq_len == 0:
            self.freq_origin = "default"
        else:
            self.freq_origin = "from_img"
        reading_head += 10
        self.alpha = (self.barcodes.index(oligo[reading_head:reading_head+5]) +
                      self.barcodes.index(oligo[reading_head+5:reading_head+10]) / 10 +
                      self.barcodes.index(oligo[reading_head+10:reading_head+15]) / 100 +
                      self.barcodes.index(oligo[reading_head+15:reading_head+20]) / 1000)
        reading_head += 20
        self.image_type = self.barcodes.index(oligo[reading_head:reading_head+5])
        reading_head += 5
        if self.colored_image():
            self.sampler = self.samplers[self.barcodes.index(oligo[reading_head:reading_head+5])]
            res = self.channel_sampler.forward((np.zeros((self.n, self.m, 3))))
            self.m, self.n = [None, None, None], [None, None, None]
            self.n[0], self.m[0] = res[0].shape
            self.n[1], self.m[1] = res[1].shape
            self.n[2], self.m[2] = res[2].shape
            self.m = tuple(self.m)
            self.n = tuple(self.n)
        if self.debug:
            print(f"Block dimensions: {self.blockdims}")
            print(f"Image size: {(self.m, self.n)}")
            print(f"(max_cat, max_runcat): {(self.max_cat, self.max_runcat)}")
            print(f"(dc_freq_len, ac_freq_len): {((self.dc_freq_len, self.ac_freq_len))}")
            print(f"alpha: {self.alpha}")
