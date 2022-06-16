"""Formatter collections for the Jpeg DNA codecs"""

from abc import ABC, abstractmethod


# pylint: disable=missing-class-docstring
class AutomataException(Exception):
    pass


class AutomataGetterException(AutomataException):
    pass

class AutomataGetterExceptionFormat(AutomataGetterException):
    pass

class AutomataGetterExceptionDeformat(AutomataGetterException):
    pass


class AutomataSetterException(AutomataException):
    pass

class AutomataSetterExceptionFormat(AutomataSetterException):
    pass

class AutomataSetterExceptionDeformat(AutomataSetterException):
    pass
# pylint: enable=missing-class-docstring


class AbstractFormatter(ABC):
    """Abstract class for formatter definition"""
    def set_state(self, *args, case=None) -> None:
        """Helper method to set the state of the codec if necessary"""

    def get_state(self, case=None) -> any:
        """Helper method to get the state of the codec if necessary"""

    def full_format(self, inp, *args):
        """Encoding method

        :param inp: Strand to format
        :type inp: str
        :param args: Header info
        :type args: any
        :return: Formatted oligos
        :rtype: list
        """

    @abstractmethod
    def format(self, inp):
        """Encoding method

        :param inp: Strand to format
        :type inp: str
        :return: Formatted oligos
        :rtype: list
        """

    def full_deformat(self, oligos, *args):
        """Encoding method

        :param code: Formated oligos to deformat
        :type code: list
        :param args: Deformatting arguments
        :type args: any
        :return: Deformated strand
        :rtype: str
        """

    @abstractmethod
    def deformat(self, oligos):
        """Decoding method

        :param code: Formated oligos to deformat
        :type code: list
        :return: Deformated strand
        :rtype: str
        """

# pylint: disable=wrong-import-position
from jpegdna.format.dataformatter import DataFormatter
from jpegdna.format.generalinfoformatter import GeneralInfoFormatter
from jpegdna.format.frequenciesformatter import RGBFrequenciesFormatter
from jpegdna.format.frequenciesformatter import GrayFrequenciesFormatter
from jpegdna.format.jpegdnaformatter import JpegDNAFormatter
