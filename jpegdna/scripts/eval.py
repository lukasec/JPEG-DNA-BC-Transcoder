"""Jpeg DNA evaluation script"""

from pathlib import Path
import math
from skimage import io
import jpegdna
from jpegdna.codecs import JpegDNA
from jpegdna.transforms import RGBYCbCr

# Choose between "from_img" and "default" for the frequencies
CHOICE = "from_img"

def color_stats(func):
    """Stats printing and exception handling decorator"""

    def inner(*args):
        try:
            code, decoded = func(*args)
        except ValueError as err:
            print(err)
        else:
            general_mean_squarred_error = 0
            code_length = 0
            for el in code:
                code_length += len(el)
            compression_rate = 24 * args[0].shape[0] * args[0].shape[1] / code_length
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

def gray_stats(func):
    """Stats printing and exception handling decorator"""

    def inner(*args):
        try:
            code, decoded = func(*args)
        except ValueError as err:
            print(err)
        else:
            code_length = 0
            for el in code:
                code_length += len(el)
            compression_rate = 8 * args[0].shape[0] * args[0].shape[1] / code_length
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
    codec = JpegDNA(alpha, verbose=False, verbosity=3)
    if CHOICE == "from_img":
        oligos = codec.encode(img, "from_img")
    elif CHOICE == "default":
        oligos = codec.encode(img, "default")
    # Decoding
    codec2 = JpegDNA(alpha, verbose=False, verbosity=3)
    decoded = codec2.decode(oligos)
    return oligos, decoded

@color_stats
def color_experiment(img, alpha):
    """Full experiment with stats and exception handling"""
    return encode_decode(img, alpha)

@gray_stats
def gray_experiment(img, alpha):
    """Full experiment with stats and exception handling"""
    return encode_decode(img, alpha)

# pylint: disable=missing-function-docstring
def main():
    img_names = []
    for i in range(1, 25):
        img_names.append(f"kodim{i:02d}.png")
    for i in range(1, 6):
        img_names.append(f"kodim_gray_{i}.png")
    for i in range(len(img_names)):
        img_name = img_names[i]
        img = io.imread(Path(jpegdna.__path__[0] +  "/../img/" + img_name))
        for alpha in [1e-5, 0.025, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2]:
            print("==================================")
            print(f"Alpha: {alpha}")
            if i < 24:
                color_experiment(img, alpha)
            else:
                gray_experiment(img, alpha)
# pylint: enable=missing-function-docstring


if __name__ == '__main__':
    main()
