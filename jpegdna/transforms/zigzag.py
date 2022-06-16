"""Zigzag algorithm"""

import numpy as np
from jpegdna.transforms import AbstractTransform
from jpegdna.transforms import AutomataSetterException


class ZigZag(AbstractTransform):
    """Zig-zag transform

    :var verbose: Verbosity enabler
    :param verbose: bool
    :ivar vmax: width of the matrix
    :vartype vmax: int
    :ivar hmax: height of the matrix
    :vartype hmax: int
    """

    def __init__(self, verbose=False):
        self.vmax = None
        self.hmax = None
        self.verbose = verbose

    def set_state(self, *args, case=None):
        """Sets the state of the transform

        :param hmax:
        :type hamx: int
        :param vmax:
        :type vmax: int
        """
        if case is not None and case != 'forward' and case != 'backward':
            raise AutomataSetterException("ZigZag: Invalid parameters, expected case parameter in {None|'forward'|'backward'}" +
                                          f" but got {case}.")
        self.vmax = args[0]
        self.hmax = args[1]

    def forward(self, inp):
        """Transform the inp matrix into a sequence element following the zig-zag reading order

        :param inp: Input to be transformed
        :type inp: np.array
        :return: Zig-zag read sequence
        :rtype: np.array
        """
        (num_rows, num_cols) = np.shape(inp)
        out = np.zeros((num_rows*num_cols))
        cur_row, cur_col, cur_ind = 0, 0, 0
        while cur_row < num_rows and cur_col < num_cols:
            if cur_row == 0 and (cur_row+cur_col)%2 == 0 and cur_col != num_cols-1:
                out[cur_ind] = inp[cur_row, cur_col]
                cur_col += 1
                cur_ind += 1
            elif cur_row == num_rows-1 and (cur_row+cur_col)%2 != 0 and cur_col != num_cols-1:
                out[cur_ind] = inp[cur_row, cur_col]
                cur_col += 1
                cur_ind += 1
            elif cur_col == 0 and (cur_row+cur_col)%2 != 0 and cur_row != num_rows-1:
                out[cur_ind] = inp[cur_row, cur_col]
                cur_row += 1
                cur_ind += 1
            elif cur_col == num_cols-1 and (cur_row+cur_col)%2 == 0 and cur_row != num_rows-1:
                out[cur_ind] = inp[cur_row, cur_col]
                cur_row += 1
                cur_ind += 1
            elif cur_col != 0 and cur_row != num_rows-1 and (cur_row+cur_col)%2 != 0:
                out[cur_ind] = inp[cur_row, cur_col]
                cur_row += 1
                cur_col -= 1
                cur_ind += 1
            elif cur_row != 0 and cur_col != num_cols-1 and (cur_row+cur_col)%2 == 0:
                out[cur_ind] = inp[cur_row, cur_col]
                cur_row -= 1
                cur_col += 1
                cur_ind += 1
            elif cur_row == num_rows-1 and cur_col == num_cols-1:
                out[-1] = inp[-1, -1]
                break
        if self.verbose:
            print(f"----------\nZig-Zag forward:\n{out.astype(int)}")
        return out.astype(int)

    def full_inverse(self, inp, *args):
        self.set_state(*args)
        return self.inverse(inp)

    def inverse(self, inp):
        """Reconstruct matrix from a sequence of zig-zag read values

        :param inp: Sequence of values
        :type inp: np.array
        :return: reconstructed matrix
        :rtype: np.array
        """
        hor, ver, vmin, hmin = 0, 0, 0, 0
        out = np.zeros((self.vmax, self.hmax))
        i = 0
        while ver < self.vmax and hor < self.hmax:
            if (hor+ver)%2 == 0:
                if ver == vmin:
                    out[ver, hor] = inp[i]
                    if hor == self.hmax-1:
                        ver += 1
                    else:
                        hor += 1
                    i += 1
                elif hor == self.hmax-1 and ver < self.vmax-1:
                    out[ver, hor] = inp[i]
                    ver += 1
                    i += 1
                elif ver > vmin and hor < self.hmax-1:
                    out[ver, hor] = inp[i]
                    ver -= 1
                    hor += 1
                    i += 1
            else:
                if ver == self.vmax-1 and hor <= self.hmax-1:
                    out[ver, hor] = inp[i]
                    hor += 1
                    i += 1
                elif hor == hmin:
                    out[ver, hor] = inp[i]
                    if ver == self.vmax-1:
                        hor += 1
                    else:
                        ver += 1
                    i += 1
                elif ver < self.vmax-1 and hor > hmin:
                    out[ver, hor] = inp[i]
                    ver += 1
                    hor -= 1
                    i += 1
            if ver == self.vmax-1 and hor == self.hmax-1:
                out[ver, hor] = inp[i]
                break
        if self.verbose:
            print(f"----------\nZig-Zag inverse:\n{out.astype(int)}")
        return out
