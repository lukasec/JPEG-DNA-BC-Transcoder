"""Encoding and decoding main functions for JPEG-DNA in RGB"""

from pathlib import Path
import pickle
import jpegdna
from jpegdna.codecs.jpeg_dna_gray import JPEGDNAGray
from jpegdna.transforms import RGBYCbCr, ChannelSampler
from jpegdna.format import JpegDNAFormatter

# Imports for Transcoder
import pyximport
pyximport.install()
from decoder import PyCoefficientDecoder 
import numpy as np

CHANNEL_VERBOSITY_THRESHOLD = 0
COLOR_CONVERSION_VERBOSITY_THRESHOLD = 1
CHANNEL_SAMPLER_VERBOSITY_THRESHOLD = 1

GRAY_CODEC_VERBOSITY_THRESHOLD = 3


class JPEGDNARGB(JPEGDNAGray):
    """JPEG-DNA codec for RGB images

    :param aplha: Alpha value (quantization step multiplier)
    :type alpha: float
    :param formatting: Formatting enabler
    :type formatting: bool
    :param channel_sampler: Sampler name used to subsample chrominance channels
    :type channel_sampler: str
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
    """

    # Path of JPEG image, and type of subsampling passed as additional arguments
    def __init__(self, alpha, img_fpath, channel_sampler, encoding, formatting=False, primer=None, verbose=False, verbosity=0):
        self.path = img_fpath # Remember path of image for reading DCT coefficients and quantization tables of JPEG image
        self.sampler_name = channel_sampler # Now passed as an argument
        self.encoding = encoding # Boolean value used in set_alpha method
        self.primer = primer
        super().__init__(alpha, img_fpath, encoding,
                         formatting=formatting,
                         primer=self.primer,
                         verbose=(verbose and verbosity >= GRAY_CODEC_VERBOSITY_THRESHOLD),
                         verbosity=verbosity-3)
        self.verbose_rgb = verbose
        if formatting:
            self.formatter = JpegDNAFormatter(None,
                                              "RGB",
                                              sampler=channel_sampler,
                                              primer=self.primer,
                                              oligo_length=200,
                                              debug=False)
        self.color_converter = RGBYCbCr()
        self.channel_sampler = ChannelSampler(sampler=channel_sampler)
        self.sampler_name = channel_sampler

    def set_alpha(self, alpha, encoding):
        """ Modified: this method now essentially is part of
            the encoding process which extracts the 
            quantization tables of the JPEG image
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
                self.formatter = JpegDNAFormatter(self.alpha, "RGB", None, primer=self.primer, oligo_length=200, debug=False)

    def set_gammas(self, gammas):
        """Setter for the quantization table
            This method essentially is part
            of the decoding process

        :param gammas: quantization table
        :type gammas: np.array
        """
        self.gammas = gammas
        if self.formatting:
            self.formatter = JpegDNAFormatter(self.gammas, "RGB", sampler=self.sampler_name,
                                              primer=self.primer, oligo_length=200, debug=False)

    # pylint: disable=invalid-name
    def compute_min_dynamic(self, img, channel_type=None):
        alphamin_Y = super().compute_min_dynamic(img[0], channel_type="luma")
        alphamin_Cb = super().compute_min_dynamic(img[1], channel_type="chroma")
        alphamin_Cr = super().compute_min_dynamic(img[2], channel_type="chroma")
        return max(alphamin_Y, alphamin_Cb, alphamin_Cr)
    # pylint: enable=invalid-name

    def set_frequencies_default_rgb(self, channel):
        """Sets the frequencies to the package's default frequency tables
        """

        with open(Path(jpegdna.__path__[0] + "/data/freqs_rgb_" + self.channel_sampler.sampler + ".pkl"), "rb") as file:
            freqs = pickle.load(file)
        self.freq_dc = freqs[channel]['freq_dc']
        self.freq_ac = freqs[channel]['freq_ac']

    def get_default_frequencies_rgb(self, channel):
        """Gets the frequencies to the package's default frequency tables
        """

        with open(Path(jpegdna.__path__[0] + "/data/freqs_rgb_" + self.channel_sampler.sampler + ".pkl"), "rb") as file:
            freqs = pickle.load(file)
        return freqs[channel]['freq_dc'], freqs[channel]['freq_ac']

    # pylint: disable=invalid-name
    def full_encode(self, inp, *args):
        if self.verbose_rgb:
            print(f"========================\nTranscoding input image\n========================")
        if len(args) == 0:
            raise ValueError
        YCbCr = self.channel_sampler.forward(self.color_converter.forward(inp))
        #Computing min dynamic
        min_alpha = self.compute_min_dynamic(YCbCr)
        if self.alpha < min_alpha:
            raise ValueError(f"Invalid alpha value, minimal possible value for this image: {min_alpha}")
        #Computing frequencies
        Y, Cb, Cr = YCbCr # Ignore, kept to avoid errors with the original code
        gamma_tables = [None, None, None]

        # Transcoder: Init. coefficient decoder
        dec = PyCoefficientDecoder(self.path)

        # Encoding Y
        self.set_channel_type("luma")
        gamma_tables[0] = self.get_gammas()
        if args[0] == "from_img":
            # Read DCT coefficients of L channel and also its height and width in blocks
            self.set_frequencies_from_img(Y, np.array(dec.get_dct_coefficients(0)), dec.get_height_in_blocks(0), dec.get_width_in_blocks(0))
        # Not relevant to Transcoder
        elif args[0] == "default":
            if len(args) != 1:
                raise ValueError
            self.set_frequencies_default_rgb("Y")
        elif args[0] == "from_file":
            if len(args) <= 3:
                raise ValueError
            self.set_frequencies_from_array(args[1][0], args[1][1])
        else:
            raise ValueError
        str_Y = super().encode(Y)
        res_Y = super().get_state()

        # Encoding Cb
        self.set_channel_type("chroma")
        gamma_tables[1] = self.get_gammas()
        if args[0] == "from_img":
            # Read DCT coefficients of Cb channel and also its height and width in blocks
            self.set_frequencies_from_img(Cb, np.array(dec.get_dct_coefficients(1)), dec.get_height_in_blocks(1), dec.get_width_in_blocks(1))
        # Not relevant to Transcoder
        elif args[0] == "default":
            if len(args) != 1:
                raise ValueError
            self.set_frequencies_default_rgb("Cb")
        elif args[0] == "from_file":
            if len(args) <= 3:
                raise ValueError
            self.set_frequencies_from_array(args[2][0], args[2][1])
        else:
            raise ValueError
        str_Cb = super().encode(Cb)
        res_Cb = super().get_state()

        # Encoding Cr
        self.set_channel_type("chroma")
        gamma_tables[2] = self.get_gammas()
        if args[0] == "from_img":
            # Read DCT coefficients of Cr channel and also its height and width in blocks
            self.set_frequencies_from_img(Cr, np.array(dec.get_dct_coefficients(2)), dec.get_height_in_blocks(2), dec.get_width_in_blocks(2))
        # Not relevant to Transcoder
        elif args[0] == "default":
            if len(args) != 1:
                raise ValueError
            self.set_frequencies_default_rgb("Cr")
        elif args[0] == "from_file":
            if len(args) <= 3:
                raise ValueError
            self.set_frequencies_from_array(args[3][0], args[3][1])
        else:
            raise ValueError
        str_Cr = super().encode(Cr)
        res_Cr = super().get_state()
        if self.formatting:
            self.set_gammas(gamma_tables)
            return self.formatter.full_format(str_Y + str_Cb + str_Cr, args[0],
                                              res_Y[1], res_Y[2],
                                              (res_Y[3], res_Cb[3], res_Cr[3]),
                                              (res_Y[4], res_Cb[4], res_Cr[4]))
        else:
            return (str_Y + str_Cb + str_Cr, (res_Y, res_Cb, res_Cr), gamma_tables)

    def full_decode(self, code, *args):
        if self.formatting:
            code, (gamma_tables, m, n, freq_dc_out, freq_ac_out) = self.formatter.full_deformat(code)
            freq_origin = self.formatter.freq_origin
        else:
            gamma_tables = args[-1]

        self.set_gammas(gamma_tables[0])
        formatting = self.formatting
        self.formatting = False

        if formatting:
            if freq_origin == "from_img" or freq_origin == "from_array":
                Y = super().full_decode(code, freq_origin, m[0], n[0], freq_dc_out[0], freq_ac_out[0], gamma_tables[0])
            elif freq_origin == "default":
                freq_dc, freq_ac = self.get_default_frequencies_rgb('Y')
                Y = super().full_decode(code, "from_file", m[0], n[0], freq_dc, freq_ac, gamma_tables[0])
            else:
                raise ValueError("Wrong parameters")
        else:
            if args[0] == "from_img" or args[0] == "from_array":
                Y = super().full_decode(code, args[0], args[1][0][0], args[1][0][1], args[1][0][2], args[1][0][3], gamma_tables[0])
            elif args[0] == "default":
                freq_dc, freq_ac = self.get_default_frequencies_rgb('Y')
                Y = super().full_decode(code, "from_file", args[1][0][0], args[1][0][1], freq_dc, freq_ac, gamma_tables[0])
            else:
                raise ValueError("Wrong parameters")
        code = self.remain

        self.set_gammas(gamma_tables[1])
        if formatting:
            if freq_origin == "from_img" or freq_origin == "from_array":
                Cb = super().full_decode(code, freq_origin, m[1], n[1], freq_dc_out[1], freq_ac_out[1], gamma_tables[1])
            elif freq_origin == "default":
                freq_dc, freq_ac = self.get_default_frequencies_rgb('Cb')
                Cb = super().full_decode(code, "from_file", m[1], n[1], freq_dc, freq_ac, gamma_tables[1])
            else:
                raise ValueError("Wrong parameters")
        else:
            if args[0] == "from_img" or args[0] == "from_array":
                Cb = super().full_decode(code, args[0], args[1][1][0], args[1][1][1], args[1][1][2], args[1][1][3], gamma_tables[1])
            elif args[0] == "default":
                freq_dc, freq_ac = self.get_default_frequencies_rgb('Cb')
                Cb = super().full_decode(code, "from_file", args[1][1][0], args[1][1][1], freq_dc, freq_ac, gamma_tables[1])
            else:
                raise ValueError("Wrong parameters")
        code = self.remain

        self.set_gammas(gamma_tables[2])
        if formatting:
            if freq_origin == "from_img" or freq_origin == "from_array":
                Cr = super().full_decode(code, freq_origin, m[2], n[2], freq_dc_out[2], freq_ac_out[2], gamma_tables[2])
            elif freq_origin == "default":
                freq_dc, freq_ac = self.get_default_frequencies_rgb('Cr')
                Cr = super().full_decode(code, "from_file", m[2], n[2], freq_dc, freq_ac, gamma_tables[2])
            else:
                raise ValueError("Wrong parameters")
        else:
            if args[0] == "from_img" or args[0] == "from_array":
                Cr = super().full_decode(code, args[0], args[1][2][0], args[1][2][1], args[1][2][2], args[1][2][3], gamma_tables[2])
            elif args[0] == "default":
                freq_dc, freq_ac = self.get_default_frequencies_rgb('Cr')
                Cr = super().full_decode(code, "from_file", args[1][2][0], args[1][2][1], freq_dc, freq_ac, gamma_tables[2])
            else:
                raise ValueError("Wrong parameters")
        self.formatting = formatting

        jpeg_decoded =  self.color_converter.inverse(self.channel_sampler.inverse((Y, Cb, Cr)))
        if self.verbose_rgb:
            print(f"========================\nDecoding DNA\n========================")
        return jpeg_decoded
    # pylint: enable=invalid-name
