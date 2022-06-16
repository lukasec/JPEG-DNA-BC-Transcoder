"""Hexadecimal converter"""

from jpegdna.coders import AbstractCoder


class HexCoder(AbstractCoder):
    """Hexadecimal coder"""
    def encode(self, inp):
        if inp < 0:
            return "err"
        return hex(inp)[2:].upper()
    def decode(self, code):
        return int("0x"+code.lower(), 0)
