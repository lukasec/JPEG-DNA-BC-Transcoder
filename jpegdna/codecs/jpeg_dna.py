"""Encoding and decoding main functions for JPEG-DNA"""
from jpegdna.codecs.jpeg_dna_gray import JPEGDNAGray
from jpegdna.codecs.jpeg_dna_rgb import JPEGDNARGB
from jpegdna.format import JpegDNAFormatter


class JpegDNA():
    """General codec for JpegDNA"""
    def __init__(self, alpha, primer=None, sampler="4:2:0", verbosity=False, verbose=0):
        self.alpha = alpha
        self.sampler = sampler
        self.primer = primer
        self.verbosity = verbosity
        self.verbose = verbose
        self.codec = None

    def encode(self, inp, *args):
        """Encoding function that will adapt infuncion of the input shape
        :param inp: Input image to encode
        :type inp: np.array
        :return: Encoded oligos
        :rtype: list[str]
        """
        if len(inp.shape) == 3:
            image_type = "RGB"
        elif len(inp.shape) == 2:
            image_type = "gray"
        else:
            raise ValueError
        if image_type == "RGB":
            self.codec = JPEGDNARGB(self.alpha, formatting=True, primer=self.primer, channel_sampler=self.sampler, verbosity=self.verbosity, verbose=self.verbose)
        elif image_type == "gray":
            self.codec = JPEGDNAGray(self.alpha, formatting=True, primer=self.primer, verbosity=self.verbosity, verbose=self.verbose)
        return self.codec.full_encode(inp, *args)

    def decode(self, code):
        """Decoding function that will adapt in function of the format info
        :param code: Input oligos to deformat and decode
        :type code: list[str]
        :return: Decoded image
        :rtype: np.array
        """
        formatter = JpegDNAFormatter(None, None)
        code, (alpha, m, n, freq_dc_out, freq_ac_out) = formatter.full_deformat(code)
        freq_origin = formatter.freq_origin
        image_type = formatter.image_type
        if image_type == "RGB":
            sampler = formatter.sampler
            self.codec = JPEGDNARGB(alpha, formatting=False, primer=self.primer, channel_sampler=sampler, verbosity=self.verbosity, verbose=self.verbose)
        elif image_type == "gray":
            self.codec = JPEGDNAGray(alpha, formatting=False, primer=self.primer, verbosity=self.verbosity, verbose=self.verbose)
        else:
            raise ValueError
        if freq_origin == "default":
            if image_type == "gray":
                return self.codec.full_decode(code, freq_origin, m, n)
            elif image_type == "RGB":
                return self.codec.full_decode(code, freq_origin, ((m[0], n[0]), (m[1], n[1]), (m[2], n[2])))
        else:
            if image_type == "gray":
                return self.codec.full_decode(code, freq_origin, m, n, freq_dc_out, freq_ac_out)
            elif image_type == "RGB":
                return self.codec.full_decode(code, freq_origin,
                                         ((m[0], n[0], freq_dc_out[0], freq_ac_out[0]),
                                          (m[1], n[1], freq_dc_out[1], freq_ac_out[1]),
                                          (m[2], n[2], freq_dc_out[2], freq_ac_out[2])))