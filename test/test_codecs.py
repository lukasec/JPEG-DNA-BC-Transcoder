"""Test module for the codecs"""

import numpy as np
from skimage import io
from jpegdna.codecs import JPEGDNAGray, JPEGDNARGB, JpegDNA
from jpegdna.transforms import RGBYCbCr

def jpegdna_test():
    """Functionnal tests for the general jpegdna codec"""
    img = io.imread("img/kodim_gray_1.png")[:64, :64]
    codec = JpegDNA(0.1, verbose=True, verbosity=8)
    code = codec.encode(img, "from_img")
    decoded = codec.decode(code)
    squares = ((img-decoded))**2
    mse = 0
    for i in range(len(squares)):
        for j in range(len(squares[0])):
            mse += squares[i, j]
    mse /= len(squares)
    mse /= len(squares[0])
    mse_threshold = 50
    print(f"MSE: {mse}, MSE threshold: {mse_threshold}")
    assert mse <= mse_threshold
    img = io.imread("img/kodim_gray_1.png")[:64, :64]
    codec = JpegDNA(0.1, verbose=True, verbosity=8)
    code = codec.encode(img, "default")
    decoded = codec.decode(code)
    squares = ((img-decoded))**2
    mse = 0
    for i in range(len(squares)):
        for j in range(len(squares[0])):
            mse += squares[i, j]
    mse /= len(squares)
    mse /= len(squares[0])
    mse_threshold = 50
    print(f"MSE: {mse}, MSE threshold: {mse_threshold}")
    assert mse <= mse_threshold
    img = io.imread("img/kodim01.png")[:64, :64]
    codec = JpegDNA(0.1, verbose=True, verbosity=8)
    code = codec.encode(img, "from_img")
    decoded = codec.decode(code)
    squares = ((img-decoded))**2
    mse = 0
    for i in range(len(squares)):
        for j in range(len(squares[0])):
            for k in range(3):
                mse += squares[i, j, k]
    mse /= len(squares)
    mse /= len(squares[0])
    mse /= 3
    mse_threshold = 50
    print(f"MSE: {mse}, MSE threshold: {mse_threshold}")
    assert mse <= mse_threshold
    img = io.imread("img/kodim01.png")[:64, :64]
    codec = JpegDNA(0.1, verbose=True, verbosity=8)
    code = codec.encode(img, "default")
    decoded = codec.decode(code)
    squares = ((img-decoded))**2
    mse = 0
    for i in range(len(squares)):
        for j in range(len(squares[0])):
            for k in range(3):
                mse += squares[i, j, k]
    mse /= len(squares)
    mse /= len(squares[0])
    mse /= 3
    mse_threshold = 50
    print(f"MSE: {mse}, MSE threshold: {mse_threshold}")
    assert mse <= mse_threshold

def jpegdnagray_test():
    """Functionnal tests for the general gray level jpegdna codec"""
    img = np.random.randint(0, 255, size=(65, 65))
    codec = JPEGDNAGray(0.1, verbose=True, verbosity=5)
    (code, res) = codec.full_encode(img, "from_img")
    decoded = codec.full_decode(code, "from_img", res[1], res[2], res[3], res[4])
    squares = ((img-decoded))**2
    mse = 0
    for i in range(len(squares)):
        for j in range(len(squares[0])):
            mse += squares[i, j]
    mse /= len(squares)
    mse /= len(squares[0])
    mse_threshold = 50
    print(f"MSE: {mse}, MSE threshold: {mse_threshold}")
    assert mse <= mse_threshold
    img = np.random.randint(0, 255, size=(65, 65))
    codec = JPEGDNAGray(0.1, verbose=True, verbosity=5)
    (code, res) = codec.full_encode(img, "default")
    decoded = codec.full_decode(code, "default", res[1], res[2])
    squares = ((img-decoded))**2
    mse = 0
    for i in range(len(squares)):
        for j in range(len(squares[0])):
            mse += squares[i, j]
    mse /= len(squares)
    mse /= len(squares[0])
    mse_threshold = 50
    print(f"MSE: {mse}, MSE threshold: {mse_threshold}")
    assert mse <= mse_threshold
    img = np.random.randint(0, 255, size=(24, 24))
    codec = JPEGDNAGray(0.1, formatting=True, verbose=True, verbosity=5)
    oligos = codec.full_encode(img, "from_img")
    decoded = codec.full_decode(oligos, "from_img")
    squares = ((img-decoded))**2
    mse = 0
    for i in range(len(squares)):
        for j in range(len(squares[0])):
            mse += squares[i, j]
    mse /= len(squares)
    mse /= len(squares[0])
    mse_threshold = 50
    print(f"MSE: {mse}, MSE threshold: {mse_threshold}")
    assert mse <= mse_threshold
    img = np.random.randint(0, 255, size=(24, 24))
    codec = JPEGDNAGray(0.1, formatting=True, verbose=True, verbosity=5)
    oligos = codec.full_encode(img, "default")
    decoded = codec.full_decode(oligos, "default")
    squares = ((img-decoded))**2
    mse = 0
    for i in range(len(squares)):
        for j in range(len(squares[0])):
            mse += squares[i, j]
    mse /= len(squares)
    mse /= len(squares[0])
    mse_threshold = 50
    print(f"MSE: {mse}, MSE threshold: {mse_threshold}")
    assert mse <= mse_threshold

def jpegdnargb_test():
    """Functionnal tests for the general rgb jpegdna codec"""
    img = io.imread("img/kodim01.png")[:64, :64]
    codec = JPEGDNARGB(0.1, verbose=True, verbosity=8)
    (code, res) = codec.full_encode(img, "from_img")
    params = (res[0][1:],
              res[1][1:],
              res[2][1:])
    decoded = codec.full_decode(code, "from_img", params)
    color_conv = RGBYCbCr()
    img_ycbcr = color_conv.forward(img)
    decoded_ycbcr = color_conv.forward(decoded)
    squares = ((img_ycbcr-decoded_ycbcr))**2
    mse = 0
    for i in range(len(squares)):
        for j in range(len(squares[0])):
            for k in range(3):
                mse += squares[i, j, k]
    mse /= len(squares)
    mse /= len(squares[0])
    mse /= 3
    mse_threshold = 50
    print(f"MSE: {mse}, MSE threshold: {mse_threshold}")
    assert mse <= mse_threshold
    img = io.imread("img/kodim01.png")[:64, :64]
    codec = JPEGDNARGB(0.1, verbose=True, verbosity=8)
    (code, res) = codec.full_encode(img, "default")
    params = (res[0][1:3],
              res[1][1:3],
              res[2][1:3])
    decoded = codec.full_decode(code, "default", params)
    color_conv = RGBYCbCr()
    img_ycbcr = color_conv.forward(img)
    decoded_ycbcr = color_conv.forward(decoded)
    squares = ((img_ycbcr-decoded_ycbcr))**2
    mse = 0
    for i in range(len(squares)):
        for j in range(len(squares[0])):
            for k in range(3):
                mse += squares[i, j, k]
    mse /= len(squares)
    mse /= len(squares[0])
    mse /= 3
    mse_threshold = 50
    print(f"MSE: {mse}, MSE threshold: {mse_threshold}")
    assert mse <= mse_threshold
    img = io.imread("img/kodim01.png")[:32, :32]
    codec = JPEGDNARGB(0.1, formatting=True, verbose=True, verbosity=8)
    oligos = codec.full_encode(img, "from_img")
    decoded = codec.full_decode(oligos, "from_img")
    color_conv = RGBYCbCr()
    img_ycbcr = color_conv.forward(img)
    decoded_ycbcr = color_conv.forward(decoded)
    squares = ((img_ycbcr-decoded_ycbcr))**2
    mse = 0
    for i in range(len(squares)):
        for j in range(len(squares[0])):
            for k in range(3):
                mse += squares[i, j, k]
    mse /= len(squares)
    mse /= len(squares[0])
    mse /= 3
    mse_threshold = 50
    print(f"MSE: {mse}, MSE threshold: {mse_threshold}")
    assert mse <= mse_threshold
    img = io.imread("img/kodim01.png")[:32, :32]
    codec = JPEGDNARGB(0.1, formatting=True, verbose=True, verbosity=8)
    oligos = codec.full_encode(img, "default")
    decoded = codec.full_decode(oligos, "default")
    color_conv = RGBYCbCr()
    img_ycbcr = color_conv.forward(img)
    decoded_ycbcr = color_conv.forward(decoded)
    squares = ((img_ycbcr-decoded_ycbcr))**2
    mse = 0
    for i in range(len(squares)):
        for j in range(len(squares[0])):
            for k in range(3):
                mse += squares[i, j, k]
    mse /= len(squares)
    mse /= len(squares[0])
    mse /= 3
    mse_threshold = 50
    print(f"MSE: {mse}, MSE threshold: {mse_threshold}")
    assert mse <= mse_threshold
    img = io.imread("img/kodim01.png")[:24, :24]
    codec = JPEGDNARGB(0.1, verbose=True, verbosity=8)
    (code, res) = codec.full_encode(img, "from_img")
    params = (res[0][1:],
              res[1][1:],
              res[2][1:])
    code = code[25:]
    decoded = codec.full_decode(code, "from_img", params)
