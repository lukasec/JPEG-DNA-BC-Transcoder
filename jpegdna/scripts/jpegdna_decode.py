"""Jpeg DNA decoding script"""

from pathlib import Path
import pickle
import argparse
import configparser
from skimage import io
import jpegdna
from jpegdna.codecs import JPEGDNAGray

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
def decode_image(code, alpha, formatting, defaultfreq, freqfpath, infofpath, verbosity, verbosity_level):
    """Decode an image"""
    if not formatting:
        with open(infofpath, 'rb') as f:
            dic1 = pickle.load(f)
    if not defaultfreq and not formatting:
        with open(freqfpath, 'rb') as f:
            dic2 = pickle.load(f)

    codec = JPEGDNAGray(alpha, formatting=formatting, verbose=verbosity, verbosity=verbosity_level)
    if formatting:
        if defaultfreq:
            decoded = codec.full_decode(code, "default")
        else:
            decoded = codec.full_decode(code, "from_img")
    elif defaultfreq:
        decoded = codec.full_decode(code, "default", dic1["m"], dic1["n"])
    else:
        decoded = codec.full_decode(code, "from_img", dic1["m"], dic1["n"], dic2["freq_dc"], dic2["freq_ac"])
    return decoded

def decode(alpha, formatting, default_freq, datafpath, imgoutpath, freqfpath, infofpath, verbosity, verbosity_level):
    """Full image decoder with stats and exception handling"""
    if formatting:
        with open(datafpath, 'rb') as f:
            oligos = pickle.load(f)
        decoded = decode_image(oligos, alpha, formatting, default_freq, freqfpath, infofpath, verbosity, verbosity_level)
    else:
        with open(datafpath, 'r', encoding="UTF-8") as f:
            code = f.read()
        decoded = decode_image(code, alpha, formatting, default_freq, freqfpath, infofpath, verbosity, verbosity_level)
    io.imsave(imgoutpath, decoded)
    return decoded

# pylint: disable=missing-function-docstring
def main():
    config = configparser.ConfigParser()
    with open(Path(jpegdna.__path__[0] + '/scripts/config.ini'), encoding="UTF-8") as cfg:
        config.read_file(cfg)
    verbosity = bool(config['VERB']['enabled'])
    verbosity_level = int(config['VERB']['level'])

    parser = argparse.ArgumentParser()
    parser.add_argument('DATAFPATH',
                        type=str,
                        help='Input file for the quaternary payload')
    parser.add_argument('IMGOUTPATH',
                        type=str,
                        help='Output path for the reconstructed image')
    parser.add_argument('-d', '--default_frequencies',
                        action="store_true", help="Enables the use of precalculated default frequencies")
    formatting_subparsers = parser.add_subparsers(dest='formatting_command')
    spf = formatting_subparsers.add_parser("no_format")
    spf.add_argument('ALPHA',
                     type=float,
                     help='Dynamic')
    args = parser.parse_args()

    datafpath = args.DATAFPATH
    imgoutpath = args.IMGOUTPATH
    formatting = (args.formatting_command != "no_format")
    defaultfreq = args.default_frequencies
    if defaultfreq or formatting:
        freqfpath = None
    else:
        freqfpath = config['IO_DIR']["dir"] + config['IO_DECODE']["freqs_in_path"]
    if formatting:
        infofpath = None
        alpha = 1
    else:
        infofpath = config['IO_DIR']["dir"] + config['IO_DECODE']["info_in_path"]
        alpha = args.ALPHA
    decode(alpha, formatting, defaultfreq, datafpath, imgoutpath, freqfpath, infofpath, verbosity, verbosity_level)
# pylint: enable=missing-function-docstring


if __name__ == '__main__':
    main()
