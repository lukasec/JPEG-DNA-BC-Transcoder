"""Goldman coder"""

from jpegdna.coders import AbstractCoder

# pylint: disable=missing-class-docstring
class NonDecodableGoldman(KeyError):
    pass
# pylint: enable=missing-class-docstring


class GoldmanCoder(AbstractCoder):
    """Goldman coder

    :param alphabet: alphabet for encoding
    :type alphabet: list
    """

    def __init__(self, alphabet, verbose=False) -> None:
        if len(set(alphabet)) != len(alphabet):
            raise ValueError("Goldman coder error: All members of the alphabet must be unique")
        self.alphabet = alphabet
        self.verbose = verbose

    def encode(self, inp):
        """Function that encodes data into DNA using Goldman coder

        :param inp: Signal to be encoded
        :type inp: str
        :return: Encoded signal
        :rtype: str
        """
        d = self.alphabet.copy()
        encoded = d[int(inp[0])]
        for i in range(1, len(inp)):
            d = self.alphabet.copy()
            d.remove(encoded[i-1])
            encoded += d[int(inp[i])]
        return encoded

    def decode(self, code):
        """Function that decodes DNA data using Goldman coder

        :param code: Signal to be decoded
        :type code: str
        :return: Decoded signal
        :rtype: str
        """
        flag = -1
        decoded = ""
        if code[0] not in self.alphabet[:-1]:
            raise NonDecodableGoldman()

        decoded += str(self.alphabet.index(code[0]))

        for i in range(1, len(code)):
            b = self.alphabet.copy()
            b.remove(code[i-1])
            try:
                flag = b.index(code[i])
            except:
                flag = -1
            if flag != -1:
                decoded += str(flag)
        return decoded


class GoldmanCoderDNA(GoldmanCoder):
    """DNA Goldman Coder"""
    def __init__(self):
        super().__init__(["A", "T", "C", "G"])
