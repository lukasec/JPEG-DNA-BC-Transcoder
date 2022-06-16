"""Jpeg DNA encoding script"""

import os
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
            if args[2]:
                oligos = func(*args)
            else:
                code, res = func(*args)
        except ValueError as err:
            print(err)
        else:
            if args[2]:
                code_length = 0
                for oligo in oligos:
                    code_length += len(oligo)
                compression_rate = 8 * args[0].shape[0] * args[0].shape[1] / code_length
                print(f"Compression rate: {compression_rate} bits/nt")
            else:
                compression_rate = 8 * args[0].shape[0] * args[0].shape[1] / len(code)
                print(f"Compression rate: {compression_rate} bits/nt")
                img_info = {"total_runlength_nts": res[0], "m": res[1], "n": res[2]}
                freq_info = {"freq_dc": res[3], "freq_ac": res[4]}
            if args[2]:
                with open(args[4], 'wb') as f:
                    pickle.dump(oligos, f)
            else:
                with open(args[4], 'w', encoding="UTF-8") as f:
                    f.write(code)
                with open(args[6], "wb") as f:
                    pickle.dump(img_info, f)
                if not args[3]:
                    with open(args[5], "wb") as f:
                        pickle.dump(freq_info, f)
    return inner

# pylint: disable=unused-argument
@stats
def encode_image(img, alpha, formatting, defaultfreq, datafpath, freqoutfpath, infofpath, verbosity, verbosity_level):
    """Encode an image"""
    codec = JPEGDNAGray(alpha, formatting=formatting, verbose=verbosity, verbosity=verbosity_level)
    if formatting:
        if defaultfreq:
            oligos = codec.full_encode(img, "default")
        else:
            oligos = codec.full_encode(img, "from_img")
        return oligos
    elif defaultfreq:
        (code, res) = codec.full_encode(img, "default")
    else:
        (code, res) = codec.full_encode(img, "from_img")
    return code, res
# pylint: enable=unused-argument

def encode(alpha, formatting, defaultfreq, img_fpath, datafpath, freqoutfpath, infofpath, verbosity, verbosity_level):
    """Full image encoder with stats and exception handling"""
    img = io.imread(img_fpath)
    return encode_image(img, alpha, formatting, defaultfreq, datafpath, freqoutfpath, infofpath, verbosity, verbosity_level)

# pylint: disable=missing-function-docstring
def main():
    config = configparser.ConfigParser()
    with open(Path(jpegdna.__path__[0] + '/scripts/config.ini'), encoding="UTF-8") as cfg:
        config.read_file(cfg)
    verbosity = bool(config['VERB']['enabled'])
    verbosity_level = int(config['VERB']['level'])

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
    parser.add_argument('-f', '--enable_formatting',
                        action="store_true", help="Enables formatting into an oligo pull")
    args = parser.parse_args()

    img_fpath = args.IMG_FPATH
    datafpath = args.DATAFPATH
    alpha = args.ALPHA
    formatting = args.enable_formatting
    defaultfreq = args.default_frequencies
    if not formatting:
        io_dir = config['IO_DIR']["dir"]
        if not os.path.exists(io_dir):
            os.mkdir(io_dir)
        infofpath = io_dir + config['IO_ENCODE']["info_out_path"]
    else:
        infofpath = None
    if defaultfreq or formatting:
        freqoutfpath = None
    else:
        freqoutfpath = io_dir + config['IO_ENCODE']["freqs_out_path"]
    encode(alpha, formatting, defaultfreq, img_fpath, datafpath, freqoutfpath, infofpath, verbosity, verbosity_level)
# pylint: enable=missing-function-docstring


if __name__ == '__main__':
    main()