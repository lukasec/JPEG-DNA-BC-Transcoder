"""Transforms collection useful for jpegdna"""
from abc import ABC, abstractmethod


# pylint: disable=missing-class-docstring
class AutomataException(Exception):
    pass


class AutomataGetterException(AutomataException):
    pass

class AutomataGetterExceptionForward(AutomataGetterException):
    pass

class AutomataGetterExceptionInverse(AutomataGetterException):
    pass


class AutomataSetterException(AutomataException):
    pass

class AutomataSetterExceptionForward(AutomataSetterException):
    pass

class AutomataSetterExceptionInverse(AutomataSetterException):
    pass
# pylint: enable=missing-class-docstring


class AbstractTransform(ABC):
    """Abstract class for codec definition"""
    def set_state(self, *args, case=None) -> None:
        """Helper method to set the state of the codec if necessary"""

    def get_state(self, case=None) -> any:
        """Helper method to get the state of the codec if necessary"""

    def full_forward(self, inp, *args):
        """Forward transform method

        :param inp: Input to transform
        :type: any
        :param args: Supplementary arguments for the forward transforms
        :type args: any
        :return: Transformed message
        :rtype: any
        """

    @abstractmethod
    def forward(self, inp):
        """Forward transform method

        :param inp: Input to transform
        :type: any
        :return: Transformed message
        :rtype: any
        """

    def full_inverse(self, inp, *args):
        """Inverse transform wrapper method

        :param inp: Input to apply inverse transform
        :type: any
        :param args: Supplementary arguments for the inverse transforms
        :type args: any
        :return: Inverse transformed message
        :rtype: any
        """

    @abstractmethod
    def inverse(self, inp):
        """Inverse transform method

        :param inp: Input to apply inverse transform
        :type: any
        :return: Inverse transformed message
        :rtype: any
        """

# pylint: disable=wrong-import-position
from jpegdna.transforms.dctransform import DCT
from jpegdna.transforms.zigzag import ZigZag
from jpegdna.transforms.colortransform import RGBYCbCr
from jpegdna.transforms.sampler import ChannelSampler
