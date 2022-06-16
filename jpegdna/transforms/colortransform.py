"""YCbCr converter for RGB management"""

import cv2
from jpegdna.transforms import AbstractTransform


class RGBYCbCr(AbstractTransform):
    """RGB YCbCr color converter"""
    def forward(self, inp):
        """Wrapper method to covert RGB to YCbCr

        :param inp: Input image
        :type inp: np.array
        :return: YCbCr image
        :rtype: np.array
        """
        res = cv2.cvtColor(inp, cv2.COLOR_RGB2YCrCb)
        res[:, :, 1], res[:, :, 2] = res[:, :, 2], res[:, :, 1].copy()
        return res

    def inverse(self, inp):
        """Wrapper method to covert YCbCr to RGB

        :param inp: Input YCbCr image
        :type inp: np.array
        :return: RGB image
        :rtype: np.array
        """
        inp[:, :, 1], inp[:, :, 2] = inp[:, :, 2], inp[:, :, 1].copy()
        return cv2.cvtColor(inp, cv2.COLOR_YCrCb2RGB)
