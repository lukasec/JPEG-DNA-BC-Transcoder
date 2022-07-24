"""Jpeg DNA decoding script"""

from pathlib import Path
import pickle
import argparse
import configparser
from skimage import io
import jpegdna
from jpegdna.codecs import JPEGDNARGB

def stats(func):
    """Stats printing and exception handling decorator"""

    def inner(*args):
        try:
            decoded = func(*args)
        except ValueError as err:
            print(err)
        else:
            return decoded
    return inner

@stats
def decode_image(code, formatting, defaultfreq, freqfpath, infofpath, gammasfpath, verbosity, verbosity_level, channel_sampler):
    """Decode an image"""
    if not formatting:
        with open(infofpath, 'rb') as f:
            info = pickle.load(f)
        with open(gammasfpath, 'rb') as f:
            gammas = pickle.load(f)
    if not defaultfreq and not formatting:
        with open(freqfpath, 'rb') as f:
            freqs = pickle.load(f)

    codec = JPEGDNARGB(1, "", channel_sampler, False, formatting=formatting, verbose=verbosity, verbosity=verbosity_level)
    if formatting:
        if defaultfreq:
            decoded = codec.full_decode(code, "default")
        else:
            decoded = codec.full_decode(code, "from_img")
    elif defaultfreq:
        decoded = codec.full_decode(code, "default", ((info["Y"]["m"],
                                                       info["Y"]["n"]),
                                                      (info["Cb"]["m"],
                                                       info["Cb"]["n"]),
                                                      (info["Cr"]["m"],
                                                       info["Cr"]["n"])), gammas['gammas'])
    else:
        decoded = codec.full_decode(code, "from_img", ((info["Y"]["m"],
                                                        info["Y"]["n"],
                                                        freqs["Y"]["freq_dc"],
                                                        freqs["Y"]["freq_ac"]),
                                                       (info["Cb"]["m"],
                                                        info["Cb"]["n"],
                                                        freqs["Cb"]["freq_dc"],
                                                        freqs["Cb"]["freq_ac"]),
                                                       (info["Cr"]["m"],
                                                        info["Cr"]["n"],
                                                        freqs["Cr"]["freq_dc"],
                                                        freqs["Cr"]["freq_ac"])), gammas['gammas'])
    return decoded

def decode(formatting, default_freq, datafpath, imgoutpath, freqfpath, infofpath, gammasfpath, verbosity, verbosity_level, channel_sampler, extension):
    """Full image decoder with stats and exception handling"""
    if formatting:
        if extension in ["pickle", "pkl"]:
            with open(datafpath, 'rb') as f:
                oligos = pickle.load(f)
        elif extension in ["fasta", "fas"]:
            ids, oligos = [], []
            with open(datafpath, "r", encoding="utf-8") as f:
                for line in f:
                    if line[0] == ">":
                        ids.append(line[1:])
                    else:
                        oligos.append(line)
        else:
            raise ValueError("Wring Extension")
        decoded = decode_image(oligos, formatting, default_freq, freqfpath, infofpath, gammasfpath, verbosity, verbosity_level, channel_sampler)
    else:
        with open(datafpath, 'r', encoding="UTF-8") as f:
            code = f.read()
        decoded = decode_image(code, formatting, default_freq, freqfpath, infofpath, gammasfpath, verbosity, verbosity_level, channel_sampler)
    io.imsave(imgoutpath, decoded)
    return decoded

# pylint: disable=missing-function-docstring
def main():
    config = configparser.ConfigParser()
    with open(Path(jpegdna.__path__[0] + '/scripts/config.ini'), encoding="UTF-8") as cfg:
        config.read_file(cfg)
    verbosity = bool(config['VERB']['enabled'])
    verbosity_level = int(config['VERB']['level'])
    extension = config['IO_DIR']['ext']

    parser = argparse.ArgumentParser()
    parser.add_argument('SubSamp',
                        type=str,
                        help='Type of Chroma Subsampling')
    parser.add_argument('DATAFPATH',
                        type=str,
                        help='Input file for the quaternary payload')
    parser.add_argument('IMGOUTPATH',
                        type=str,
                        help='Output path for the reconstructed image')
    parser.add_argument('-d', '--default_frequencies',
                        action="store_true", help="Enables the use of precalculated default frequencies")
    parser.add_argument('-f', '--enable_formatting',
                        action="store_true", help="Enables formatting into an oligo pull")
    args = parser.parse_args()

    channel_sampler = args.SubSamp # Remember type of subsampling of the original JPEG image
    datafpath = args.DATAFPATH
    imgoutpath = args.IMGOUTPATH
    formatting = args.enable_formatting
    defaultfreq = args.default_frequencies
    if defaultfreq or formatting:
        freqfpath = None
    else:
        freqfpath = config['IO_DIR']["dir"] + config['IO_DECODE']["freqs_in_path"]
    if formatting:
        infofpath = None
        gammasfpath = None
    else:
        infofpath = config['IO_DIR']["dir"] + config['IO_DECODE']["info_in_path"]
        gammasfpath = config['IO_DIR']["dir"] + config['IO_DECODE']["gammas_in_path"]
    decode(formatting, defaultfreq, datafpath, imgoutpath, freqfpath, infofpath, gammasfpath, verbosity, verbosity_level, channel_sampler, extension)
# pylint: enable=missing-function-docstring


if __name__ == '__main__':
    main()
