"""Codecs collection for jpegdna"""

from abc import ABC, abstractmethod


# pylint: disable=missing-class-docstring
class AutomataException(Exception):
    pass


class AutomataGetterException(AutomataException):
    pass

class AutomataGetterExceptionEncode(AutomataGetterException):
    pass

class AutomataGetterExceptionDecode(AutomataGetterException):
    pass


class AutomataSetterException(AutomataException):
    pass

class AutomataSetterExceptionEncode(AutomataSetterException):
    pass

class AutomataSetterExceptionDecode(AutomataSetterException):
    pass
# pylint: enable=missing-class-docstring


class AbstractCoder(ABC):
    """Abstract class for codec definition"""
    def set_state(self, *args, case=None) -> None:
        """Helper method to set the state of the codec if necessary"""

    def get_state(self, case=None) -> any:
        """Helper method to get the state of the codec if necessary"""

    def full_encode(self, inp, *args):
        """Encoding method

        :param inp: Input to encode
        :type inp: list|str
        :param args: Encoding arguments
        :type args: any
        :return: Encoded message, encoding state
        :rtype: list|str, any
        """

    @abstractmethod
    def encode(self, inp):
        """Encoding method

        :param inp: Input to encode
        :type inp: list|str
        :return: Encoded message
        :rtype: list|str
        """

    def full_decode(self, code, *args):
        """Encoding method

        :param code: Input to decode
        :type code: list|str
        :param args: Decoding arguments
        :type args: any
        :return: Decoded message, decoding state
        :rtype: list|str, any
        """

    @abstractmethod
    def decode(self, code):
        """Decoding method

        :param code: Input to decode
        :type code: list|str
        :return: Decoded message
        :rtype: list|str
        """

# pylint: disable=wrong-import-position
from jpegdna.coders.huffmancoder import HuffmanCoder
from jpegdna.coders.goldmancoder import GoldmanCoder, GoldmanCoderDNA, NonDecodableGoldman
from jpegdna.coders.hexcoder import HexCoder
from jpegdna.coders.categorycoder import ACCategoryCoder, DCCategoryCoder, NonDecodableCategory
from jpegdna.coders.valuecoder import ValueCoder
from jpegdna.coders.coefficientcoder import ACCoefficientCoder, DCCoefficientCoder
