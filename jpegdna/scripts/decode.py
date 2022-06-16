"""Jpeg DNA decoding script"""

from pathlib import Path
import pickle
import argparse
import configparser
from skimage import io
import jpegdna
from jpegdna.codecs import JpegDNA

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
def decode_image(oligos, verbosity, verbosity_level):
    """Decode an image"""
    codec = JpegDNA(1, verbose=verbosity, verbosity=verbosity_level)
    decoded = codec.decode(oligos)
    return decoded

def decode(datafpath, imgoutpath, verbosity, verbosity_level):
    """Full image decoder with stats and exception handling"""
    with open(datafpath, 'rb') as f:
        oligos = pickle.load(f)
    decoded = decode_image(oligos, verbosity, verbosity_level)
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
    args = parser.parse_args()

    datafpath = args.DATAFPATH
    imgoutpath = args.IMGOUTPATH

    decode(datafpath, imgoutpath, verbosity, verbosity_level)
# pylint: enable=missing-function-docstring


if __name__ == '__main__':
    main()
