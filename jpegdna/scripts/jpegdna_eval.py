"""Jpeg DNA evaluation script"""

from pathlib import Path
from dataclasses import make_dataclass
import math
import pickle
from skimage import io
import pandas as pd
from pandas import ExcelWriter
import jpegdna
from jpegdna.codecs import JPEGDNAGray

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
            if FORMATTING:
                code_length = 0
                for el in code:
                    code_length += len(el)
                compression_rate = 8 * args[0].shape[0] * args[0].shape[1] / code_length
            else:
                compression_rate = 8 * args[0].shape[0] * args[0].shape[1] / len(code)
            diff = (args[0].astype(int)-decoded.astype(int))
            # plt.imshow(decoded, cmap='gray')
            # plt.show()
            mean_squarred_error = 0
            for i in range(len(diff)):
                for j in range(len(diff[0])):
                    mean_squarred_error += diff[i, j]**2
            mean_squarred_error /= len(diff)
            mean_squarred_error /= len(diff[0])
            psnr = 10 * math.log10((255*255)/mean_squarred_error)
            print(f"Mean squared error: {mean_squarred_error}")
            print(f"PSNR: {psnr}")
            print(f"Compression rate: {compression_rate} bits/nt")
            # io.imsave(str(compression_rate) + ".png", decoded)
            return compression_rate, psnr
    return inner

def encode_decode(img, alpha):
    """Function for encoding and decoding"""
    # Coding
    codec = JPEGDNAGray(alpha, formatting=FORMATTING, verbose=False, verbosity=3)
    if CHOICE == "from_img":
        if FORMATTING:
            oligos = codec.full_encode(img, "from_img")
        else:
            (code, res) = codec.full_encode(img, "from_img")
    elif CHOICE == "from_file":
        with open(Path(jpegdna.__path__[0] + "/data/freqs.pkl"), "rb") as file:
            freqs = pickle.load(file)
        (code, res) = codec.full_encode(img, "from_file", freqs['freq_dc'], freqs['freq_ac'])
    elif CHOICE == "default":
        if FORMATTING:
            oligos = codec.full_encode(img, "default")
        else:
            (code, res) = codec.full_encode(img, "default")
    # Decoding
    codec2 = JPEGDNAGray(alpha, formatting=FORMATTING, verbose=False, verbosity=3)
    if CHOICE == "from_img":
        if FORMATTING:
            decoded = codec2.full_decode(oligos, "from_img")
        else:
            decoded = codec2.full_decode(code, "from_img", res[1], res[2], res[3], res[4])
    elif CHOICE == "from_file":
        with open(Path(jpegdna.__path__[0] + "/data/freqs.pkl"), "rb") as file:
            freqs = pickle.load(file)
        decoded = codec2.full_decode(code, "from_file", res[1], res[2], freqs['freq_dc'], freqs['freq_ac'])
    elif CHOICE == "default":
        if FORMATTING:
            decoded = codec2.full_decode(oligos, "default")
        else:
            decoded = codec2.full_decode(code, "default", res[1], res[2])
    if FORMATTING:
        return oligos, decoded
    return code, decoded

@stats
def experiment(img, alpha):
    """Full experiment with stats and exception handling"""
    return encode_decode(img, alpha)

# pylint: disable=missing-function-docstring
def main():
    value = make_dataclass("value", [("Compressionrate", float), ("PSNR", float)])
    general_results = []
    img_names = ["kodim_gray_1.png", "kodim_gray_2.png", "kodim_gray_3.png", "kodim_gray_4.png", "kodim_gray_5.png"]
    for i in range(len(img_names)):
        img_name = img_names[i]
        img = io.imread(Path(jpegdna.__path__[0] + "/../img/" + img_name))
        values = []
        for alpha in [1e-5, 0.025, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2]:
            print("==================================")
            print(f"Alpha: {alpha}")
            res = experiment(img, alpha)
            if res is not None:
                compression_rate, psnr = res
                values.append(value(compression_rate, psnr))
        general_results.append(values)
    with ExcelWriter("res/results.xlsx") as writer: # pylint: disable=abstract-class-instantiated
        for i in range(len(general_results)):
            dtf = pd.DataFrame(general_results[i])
            dtf.to_excel(writer, sheet_name=img_names[i], index=None, header=True)
# pylint: enable=missing-function-docstring


if __name__ == '__main__':
    main()
