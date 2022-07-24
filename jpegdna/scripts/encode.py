"""Jpeg DNA encoding script"""

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
            oligos = func(*args)
        except ValueError as err:
            print(err)
        else:
            code_length = 0
            for oligo in oligos:
                code_length += len(oligo)
            if len(args[0].shape) == 2:
                compression_rate = 8 * args[0].shape[0] * args[0].shape[1] / code_length
            elif len(args[0].shape) == 3:
                compression_rate = 24 * args[0].shape[0] * args[0].shape[1] / code_length
            else:
                raise ValueError
            print(f"Compression rate: {compression_rate} bits/nt")
            return oligos
    return inner

@stats
def encode_image(img, alpha, defaultfreq, datafpath, verbosity, verbosity_level, extension):
    """Encode an image"""
    codec = JpegDNA(alpha, verbose=verbosity, verbosity=verbosity_level)
    if defaultfreq:
        oligos = codec.encode(img, "default")
    else:
        oligos = codec.encode(img, "from_img")
    if extension in ["pickle", "pkl"]:
        with open(datafpath, 'wb') as f:
            pickle.dump(oligos, f)
    elif extension in ["fasta", "fas"]:
        fasta_file = open(datafpath, "w+", encoding='utf-8')
        out = '\n'.join(['>Oligo' + str(i) + "\n" + el for i, el in enumerate(oligos)])
        fasta_file.write(out)
        fasta_file.close()
    else:
        raise ValueError("Unknown extension")
    return oligos

def encode(alpha, defaultfreq, img_fpath, datafpath, verbosity, verbosity_level, extension):
    """Full image encoder with stats and exception handling"""
    img = io.imread(img_fpath)
    return encode_image(img, alpha, defaultfreq, datafpath, verbosity, verbosity_level, extension)

# pylint: disable=missing-function-docstring
def main():
    config = configparser.ConfigParser()
    with open(Path(jpegdna.__path__[0] + '/scripts/config.ini'), encoding="UTF-8") as cfg:
        config.read_file(cfg)
    verbosity = bool(config['VERB']['enabled'])
    verbosity_level = int(config['VERB']['level'])
    extension = config['IO_DIR']['ext']

    parser = argparse.ArgumentParser()
    parser.add_argument('IMG_FPATH',
                        type=str,
                        help='Filename of the input image')
    parser.add_argument('DATAFPATH',
                        type=str,
                        help='Output file for the quaternary payload')
    parser.add_argument('ALPHA',
                        type=float,
                        help='Dynamic')
    parser.add_argument('-d', '--default_frequencies',
                        action="store_true", help="Enables the use of precalculated default frequencies")
    args = parser.parse_args()

    img_fpath = args.IMG_FPATH
    datafpath = args.DATAFPATH
    alpha = args.ALPHA
    defaultfreq = args.default_frequencies
    encode(alpha, defaultfreq, img_fpath, datafpath, verbosity, verbosity_level, extension)
# pylint: enable=missing-function-docstring


if __name__ == '__main__':
    main()
