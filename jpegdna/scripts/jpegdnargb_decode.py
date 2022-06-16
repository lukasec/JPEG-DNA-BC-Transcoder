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
def decode_image(code, alpha, formatting, defaultfreq, freqfpath, infofpath, verbosity, verbosity_level, QTorJPG_path, channel_sampler):
    """Decode an image"""
    if not formatting:
        with open(infofpath, 'rb') as f:
            info = pickle.load(f)
    if not defaultfreq and not formatting:
        with open(freqfpath, 'rb') as f:
            freqs = pickle.load(f)

    codec = JPEGDNARGB(alpha, QTorJPG_path, False, "", channel_sampler, formatting=formatting, verbose=verbosity, verbosity=verbosity_level)
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
                                                       info["Cr"]["n"])))
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
                                                        freqs["Cr"]["freq_ac"])))
    return decoded

def decode(alpha, formatting, default_freq, datafpath, imgoutpath, freqfpath, infofpath, verbosity, verbosity_level, QT_path, channel_sampler):
    """Full image decoder with stats and exception handling"""
    if formatting:
        with open(datafpath, 'rb') as f:
            oligos = pickle.load(f)
        decoded = decode_image(oligos, alpha, formatting, default_freq, freqfpath, infofpath, verbosity, verbosity_level, QT_path, channel_sampler)
    else:
        with open(datafpath, 'r', encoding="UTF-8") as f:
            code = f.read()
        decoded = decode_image(code, alpha, formatting, default_freq, freqfpath, infofpath, verbosity, verbosity_level, QT_path, channel_sampler)
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
    parser.add_argument('SubSamp',
                        type=str,
                        help='Subsampling mode')
    parser.add_argument('QTFPATH',
                        type=str,
                        help='Pass quantization tables')
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
    # alpha_removed
    #spf.add_argument('ALPHA',
                     #type=float,
                     #help='Dynamic')
    args = parser.parse_args()

    channel_sampler = args.SubSamp
    QT_path = args.QTFPATH # New path
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
        #alpha = 1
    else:
        infofpath = config['IO_DIR']["dir"] + config['IO_DECODE']["info_in_path"]
        #alpha = args.ALPHA
    # Also pass jpg_path as argument
    decode(1, formatting, defaultfreq, datafpath, imgoutpath, freqfpath, infofpath, verbosity, verbosity_level, QT_path, channel_sampler) 
# pylint: enable=missing-function-docstring


if __name__ == '__main__':
    main()
