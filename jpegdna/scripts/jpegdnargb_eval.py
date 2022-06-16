"""Jpeg DNA RGB evaluation script"""

from pathlib import Path
from dataclasses import make_dataclass
import math
import pickle
from skimage import io
import pandas as pd
from pandas import ExcelWriter
import jpegdna
from jpegdna.codecs import JPEGDNARGB
from jpegdna.transforms import RGBYCbCr

# Choose between "from_img" and "default" for the frequencies
CHOICE = "from_img"
# Enables formatting (if True, bit-rate will be estimated with format taken into account)
FORMATTING = True

def stats(func):
    """Stats printing and exception handling decorator"""

    def inner(*args):
        try:
            code, decoded = func(*args)
        except ValueError as err:
            print(err)
        else:
            general_mean_squarred_error = 0
            if FORMATTING:
                code_length = 0
                for el in code:
                    code_length += len(el)
                compression_rate = 24 * args[0].shape[0] * args[0].shape[1] / code_length
            else:
                compression_rate = 24 * args[0].shape[0] * args[0].shape[1] / len(code)
            channel_names = ["Y", "Cb", "Cr"]
            psnr_s = [0] * 3
            color_conv = RGBYCbCr()
            img_ycbcr = color_conv.forward(args[0])
            decoded_ycbcr = color_conv.forward(decoded)
            for k in range(3):
                diff = (img_ycbcr[:, :, k].astype(int)-decoded_ycbcr[:, :, k].astype(int))
                mean_squarred_error = 0
                for i in range(len(diff)):
                    for j in range(len(diff[0])):
                        mean_squarred_error += diff[i, j]**2
                mean_squarred_error /= len(diff)
                mean_squarred_error /= len(diff[0])
                general_mean_squarred_error += mean_squarred_error
                psnr = 10 * math.log10((255*255)/mean_squarred_error)
                print(f"Mean squared error {channel_names[k]}: {mean_squarred_error}")
                print(f"PSNR {channel_names[k]}: {psnr}")
                psnr_s[k] = psnr
            general_mean_squarred_error /= 3
            psnr = 10 * math.log10((255*255)/general_mean_squarred_error)
            print(f"Mean squared error: {general_mean_squarred_error}")
            print(f"General PSNR: {psnr}")
            print(f"Compression rate: {compression_rate} bits/nt")
            return compression_rate, psnr, psnr_s
    return inner

def encode_decode(img, alpha):
    """Function for encoding and decoding"""
    # Coding
    codec = JPEGDNARGB(alpha, formatting=FORMATTING, verbose=False, verbosity=3)
    if CHOICE == "from_img":
        if FORMATTING:
            oligos = codec.full_encode(img, "from_img")
        else:
            (code, res) = codec.full_encode(img, "from_img")
    elif CHOICE == "from_file":
        with open(Path(jpegdna.__path__[0] + "/data/freqs_rgb_4_2_2.pkl"), "rb") as file:
            freqs = pickle.load(file)
        (code, res) = codec.full_encode(img, "from_file", freqs['freq_dc'], freqs['freq_ac'])
    elif CHOICE == "default":
        if FORMATTING:
            oligos = codec.full_encode(img, "default")
        else:
            (code, res) = codec.full_encode(img, "default")
    # Decoding
    codec2 = JPEGDNARGB(alpha, formatting=FORMATTING, verbose=False, verbosity=3)
    if CHOICE == "from_img":
        if FORMATTING:
            decoded = codec2.full_decode(oligos, "from_img")
        else:
            params = ((res[0][1], res[0][2], res[0][3], res[0][4]),
                      (res[1][1], res[1][2], res[1][3], res[1][4]),
                      (res[1][1], res[2][2], res[2][3], res[2][4]))
            decoded = codec2.full_decode(code, "from_img", params)
    elif CHOICE == "from_file":
        with open(Path(jpegdna.__path__[0] + "/data/freqs_rgb_4_2_2.pkl"), "rb") as file:
            freqs = pickle.load(file)
        params = ((res[0][1], res[0][2], freqs['Y']['freq_dc'], freqs['Y']['freq_ac']),
                  (res[1][1], res[1][2], freqs['Cb']['freq_dc'], freqs['Cb']['freq_ac']),
                  (res[2][1], res[2][2], freqs['Cr']['freq_dc'], freqs['Cr']['freq_ac']))
        decoded = codec2.full_decode(code, "from_file", params)
    elif CHOICE == "default":
        if FORMATTING:
            decoded = codec2.full_decode(oligos, "default")
        else:
            params = ((res[0][1], res[0][2]),
                      (res[1][1], res[1][2]),
                      (res[2][1], res[2][2]))
            decoded = codec2.full_decode(code, "default", params)
    if FORMATTING:
        return oligos, decoded
    return code, decoded

@stats
def experiment(img, alpha):
    """Full experiment with stats and exception handling"""
    return encode_decode(img, alpha)

# pylint: disable=missing-function-docstring
def main():
    value = make_dataclass("value", [("Compressionrate", float),
                                     ("PSNR", float),
                                     ("PSNR_Y", float),
                                     ("PSNR_Cb", float),
                                     ("PSNR_Cr", float)])
    general_results = []
    img_names = []
    for i in range(1, 25):
        img_names.append(f"kodim{i:02d}.png")
    for i in range(len(img_names)):
        img_name = img_names[i]
        img = io.imread(Path(jpegdna.__path__[0] +  "/../img/" + img_name))
        values = []
        for alpha in [1e-5, 0.025, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2]:
            print("==================================")
            print(f"Alpha: {alpha}")
            res = experiment(img, alpha)
            if res is not None:
                if len(res) == 3:
                    compression_rate, psnr, psnr_s = res # pylint: disable=unbalanced-tuple-unpacking
                    values.append(value(compression_rate, psnr, psnr_s[0], psnr_s[1], psnr_s[2]))
                else:
                    continue
        general_results.append(values)
    with ExcelWriter("res/results_rgb.xlsx") as writer: # pylint: disable=abstract-class-instantiated
        for i in range(len(general_results)):
            dtf = pd.DataFrame(general_results[i])
            dtf.to_excel(writer, sheet_name=img_names[i], index=None, header=True)
# pylint: enable=missing-function-docstring


if __name__ == '__main__':
    main()
