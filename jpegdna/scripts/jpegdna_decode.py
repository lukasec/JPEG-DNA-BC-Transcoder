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
def decode_image(code, formatting, defaultfreq, freqfpath, infofpath, gammasfpath, verbosity, verbosity_level):
    """Decode an image"""
    if not formatting:
        with open(infofpath, 'rb') as f:
            dic1 = pickle.load(f)
        with open(gammasfpath, 'rb') as f:
            dic2 = pickle.load(f)
    if not defaultfreq and not formatting:
        with open(freqfpath, 'rb') as f:
            dic3 = pickle.load(f)

    codec = JPEGDNAGray(1, formatting=formatting, verbose=verbosity, verbosity=verbosity_level)
    if formatting:
        if defaultfreq:
            decoded = codec.full_decode(code, "default")
        else:
            decoded = codec.full_decode(code, "from_img")
    elif defaultfreq:
        decoded = codec.full_decode(code, "default", dic1["m"], dic1["n"], dic2['gammas'])
    else:
        decoded = codec.full_decode(code, "from_img", dic1["m"], dic1["n"], dic3["freq_dc"], dic3["freq_ac"], dic2['gammas'])
    return decoded

def decode(formatting, default_freq, datafpath, imgoutpath, freqfpath, infofpath, gammasfpath, verbosity, verbosity_level, extension):
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
            raise ValueError("Wrong extension")
        decoded = decode_image(oligos, formatting, default_freq, freqfpath, infofpath, gammasfpath, verbosity, verbosity_level)
    else:
        with open(datafpath, 'r', encoding="UTF-8") as f:
            code = f.read()
        decoded = decode_image(code, formatting, default_freq, freqfpath, infofpath, gammasfpath, verbosity, verbosity_level)
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
    decode(formatting, defaultfreq, datafpath, imgoutpath, freqfpath, infofpath, gammasfpath, verbosity, verbosity_level, extension)
# pylint: enable=missing-function-docstring


if __name__ == '__main__':
    main()
