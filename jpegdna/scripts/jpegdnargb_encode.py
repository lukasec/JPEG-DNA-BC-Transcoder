"""Jpeg DNA RGB encoding script"""

import os
from pathlib import Path
import pickle
import argparse
import configparser
from skimage import io
import jpegdna
from jpegdna.codecs import JPEGDNARGB
import pyximport
pyximport.install()
from decoder import PyCoefficientDecoder 
import numpy as np

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
                compression_rate = 24 * args[0].shape[0] * args[0].shape[1] / code_length
                print(f"Compression rate: {compression_rate} bits/nt")
            else:
                compression_rate = 24 * args[0].shape[0] * args[0].shape[1] / len(code)
                print(f"Compression rate: {compression_rate} bits/nt")

                img_info_y = {"m": res[0][1], "n": res[0][2]}
                freq_info_y = {"freq_dc": res[0][3], "freq_ac": res[0][4]}
                img_info_cb = {"m": res[1][1], "n": res[1][2]}
                freq_info_cb = {"freq_dc": res[1][3], "freq_ac": res[1][4]}
                img_info_cr = {"m": res[2][1], "n": res[2][2]}
                freq_info_cr = {"freq_dc": res[2][3], "freq_ac": res[2][4]}

                img_info = {"Y": img_info_y, "Cb": img_info_cb, "Cr": img_info_cr}
                freq_info = {"Y": freq_info_y, "Cb": freq_info_cb, "Cr": freq_info_cr}
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
def encode_image(img, alpha, formatting, defaultfreq, datafpath, freqoutfpath, infofpath, verbosity, verbosity_level, img_fpath, qtpath, channel_sampler):
    """Function for encoding"""

    codec = JPEGDNARGB(alpha, img_fpath, True, qtpath, channel_sampler, formatting=formatting, verbose=verbosity, verbosity=verbosity_level)
    if formatting:
        if defaultfreq:
            # Pass the img_fpath as an argument as well
            oligos = codec.full_encode(img,"default")
        else:
            oligos = codec.full_encode(img, "from_img")
        return oligos
    elif defaultfreq:
        (code, res) = codec.full_encode(img, "default")
    else:
        (code, res) = codec.full_encode(img, "from_img")
    return code, res
# pylint: enable=unused-argument

def encode(alpha, formatting, defaultfreq, qtpath, channel_sampler, img_fpath, datafpath, freqoutfpath, infofpath, verbosity, verbosity_level):
    """Full image encoder with stats and exception handling"""

    img = io.imread(img_fpath)
    # Pass also the img_fpath as an argument
    return encode_image(img, alpha, formatting, defaultfreq, datafpath, freqoutfpath, infofpath, verbosity, verbosity_level, img_fpath, qtpath, channel_sampler)

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
    parser.add_argument('QT_path',
                        type=str,
                        help='Output file for the quantization tables')
    #parser.add_argument('SubSamp',
                        #type=str,
                        #help='Subsampling mode')
    #alpha_removed
    #parser.add_argument('ALPHA',
                        #type=float,
                        #help='Dynamic')
    parser.add_argument('-d', '--default_frequencies',
                        action="store_true", help="Enables the use of precalculated default frequencies")
    parser.add_argument('-f', '--enable_formatting',
                        action="store_true", help="Enables formatting into an oligo pull")
    args = parser.parse_args()

    img_fpath = args.IMG_FPATH
    datafpath = args.DATAFPATH
    qtpath = args.QT_path

    d = PyCoefficientDecoder(img_fpath) 
    sampling_factors = (d.h_samp_factor(0), d.v_samp_factor(0), d.h_samp_factor(1), d.v_samp_factor(1), d.h_samp_factor(2), d.v_samp_factor(2))
    if  sampling_factors == (1,1,1,1,1,1):
        channel_sampler = '4:4:4'
    if  sampling_factors == (1,2,1,1,1,1):
        channel_sampler = '4:4:0'
    if  sampling_factors == (2,1,1,1,1,1):
        channel_sampler = '4:2:2'
    if  sampling_factors == (2,2,1,1,1,1):
        channel_sampler = '4:2:0'
    if  sampling_factors == (4,1,1,1,1,1):
        channel_sampler = '4:1:1'
    if  sampling_factors == (4,2,1,1,1,1):
        channel_sampler = '4:1:1'
    #alpha = args.ALPHA
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
    encode(1, formatting, defaultfreq, qtpath, channel_sampler, img_fpath, datafpath, freqoutfpath, infofpath, verbosity, verbosity_level)
    print(f'Please remember for decoding: Subsampling mode is {channel_sampler}')
# pylint: enable=missing-function-docstring


if __name__ == '__main__':
    main()