"""Tests for the different tools file loaders, strand manipulation tool"""

from pathlib import Path
import jpegdna
from jpegdna.tools import strand_tools, loader

def test_codebook_loader():
    """Functionnal tests for the codebook loader"""
    res = loader.load_codebook_matrix(Path(jpegdna.__path__[0] + "/data/codebook.pkl"))
    assert res is not None
    assert len(res) == 9
    lengths = [10, 24, 130, 586, 1776, 7998, 24634, 110660, 464734]
    for i, el in enumerate(res):
        assert len(el) == lengths[i]
        assert len(el[0]) == i+2

def test_lut_loader():
    """Functionnal tests for the lut matrix loader"""
    res = loader.load_lut_matrix(Path(jpegdna.__path__[0] + "/data/lut.mat"))
    assert res is not None
    assert (res == ['01', '02', '03', '04', '05', '06', '07', '08', '09', '0A',
                    '11', '12', '13', '14', '15', '16', '17', '18', '19', '1A',
                    '21', '22', '23', '24', '25', '26', '27', '28', '29', '2A',
                    '31', '32', '33', '34', '35', '36', '37', '38', '39', '3A',
                    '41', '42', '43', '44', '45', '46', '47', '48', '49', '4A',
                    '51', '52', '53', '54', '55', '56', '57', '58', '59', '5A',
                    '61', '62', '63', '64', '65', '66', '67', '68', '69', '6A',
                    '71', '72', '73', '74', '75', '76', '77', '78', '79', '7A',
                    '81', '82', '83', '84', '85', '86', '87', '88', '89', '8A',
                    '91', '92', '93', '94', '95', '96', '97', '98', '99', '9A',
                    'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'AA',
                    'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'BA',
                    'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'CA',
                    'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'DA',
                    'E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9', 'EA',
                    'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'FA']).all()

def test_generate_random_strand():
    """Functionnal tests for the random strand generator"""
    length = 200
    before = "A"
    after = "G"
    res = strand_tools.generate_random_strand(length, before, after)
    assert len(res) == length
    assert len(set(list(res))) <= 4
    assert set(list(res)) <= {'A', 'T', 'C', 'G'}
    assert res[0] != before
    assert res[-1] != after

def test_compute_len():
    """Functionnal tests for nucleotide counter"""
    length = 200
    res = strand_tools.generate_random_strand(length, "A", "G")
    assert len(res) == strand_tools.compute_length(res)
    res += "I"
    assert len(res) == 1+strand_tools.compute_length(res)
