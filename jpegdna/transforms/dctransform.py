"""Discrete cosine forward and inverse transforms"""

from scipy.fftpack import dctn, idctn
from jpegdna.transforms import AbstractTransform

class DCT(AbstractTransform):
    """For Jpeg"""

    def full_forward(self, inp, *args):
        """
        Forward 2D DCT

        :param inp: input image block
        :type inp: np.array
        :param norm: Type of DCT (default: None)
        :type norm: str
        :return: DCT coefficients
        :rtype: np.array
        """
        if len(args) == 1:
            return dctn(inp, norm=args[0])
        else:
            return dctn(inp)

    def forward(self, inp):
        """
        Forward 2D DCT

        :param inp: input image block
        :type inp: np.array
        :return: DCT coefficients
        :rtype: np.array
        """
        return dctn(inp)

    def full_inverse(self, inp, *args):
        """
        Inverse 2D DCT

        :param inp: input image block
        :type inp: np.array
        :param norm: Type of DCT (default: None)
        :type norm: str
        :return: DCT coefficients
        :rtype: np.array
        """
        if len(args) == 1:
            return idctn(inp, norm=args[0])
        else:
            return idctn(inp)

    def inverse(self, inp):
        """
        Inverse 2D DCT

        :param inp: DCT coefficients
        :type inp: np.array
        :return: image block
        :rtype: np.array
        """
        return idctn(inp)
