"""Sampler class for 3-channels management"""

import numpy as np
from jpegdna.transforms import AbstractTransform

class ChannelSampler(AbstractTransform):
    """Channel Sampler

    :var sampler: Sampler name (default: "4:2:2")
    :param sampler: str
    """
    def __init__(self, sampler="4:2:2"):
        self.sampler = sampler.replace(":", "_")

    def get_sampler(self):
        """Get sampler name"""
        sampler = self.sampler
        return sampler.replace("_", ":")

    def set_sampler(self, sampler):
        """Set sampler from its name"""
        self.sampler = sampler.replace(":", "_")

    def forward(self, inp):
        """Sampling method

        :param inp: 3-channel image
        :type inp: np.array
        :returns: Tuple of the 3 sampled channels (Y not subsampled usually)
        :rtype: tuple
        """
        method_name = "_ChannelSampler__forward_" + self.sampler
        forward_func = getattr(self, method_name)
        return forward_func(inp)

    def inverse(self, inp):
        """Desampling method

        :param inp: Tuple of the 3 sampled channels (Y not subsampled usually)
        :type inp: np.array
        :returns: 3-channel image
        :rtype: np.array
        """
        method_name = "_ChannelSampler__inverse_" + self.sampler
        inverse_func = getattr(self, method_name)
        return inverse_func(inp)

    # pylint: disable=unused-private-member
    @staticmethod
    def __forward_4_2_0(inp):
        return (inp[:, :, 0], inp[::2, ::2, 1], inp[::2, ::2, 2])

    @staticmethod
    def __inverse_4_2_0(inp):
        return np.stack((inp[0],
                         inp[1].repeat(2, axis=0).repeat(2, axis=1)[:np.shape(inp[0])[0], :np.shape(inp[0])[1]],
                         inp[2].repeat(2, axis=0).repeat(2, axis=1)[:np.shape(inp[0])[0], :np.shape(inp[0])[1]]),
                        axis=-1)

    @staticmethod
    def __forward_4_2_2(inp):
        return (inp[:, :, 0], inp[:, ::2, 1], inp[:, ::2, 2])

    @staticmethod
    def __inverse_4_2_2(inp):
        return np.stack((inp[0],
                         inp[1].repeat(2, axis=1)[:np.shape(inp[0])[0], :np.shape(inp[0])[1]],
                         inp[2].repeat(2, axis=1)[:np.shape(inp[0])[0], :np.shape(inp[0])[1]]),
                        axis=-1)

    @staticmethod
    def __forward_4_1_1(inp):
        return (inp[:, :, 0], inp[:, ::4, 1], inp[:, ::4, 2])

    @staticmethod
    def __inverse_4_1_1(inp):
        return np.stack((inp[0],
                         inp[1].repeat(4, axis=1)[:np.shape(inp[0])[0], :np.shape(inp[0])[1]],
                         inp[2].repeat(4, axis=1)[:np.shape(inp[0])[0], :np.shape(inp[0])[1]]),
                        axis=-1)

    @staticmethod
    def __forward_4_4_0(inp):
        return (inp[:, :, 0], inp[::2, :, 1], inp[::2, :, 2])

    @staticmethod
    def __inverse_4_4_0(inp):
        return np.stack((inp[0],
                         inp[1].repeat(2, axis=0)[:np.shape(inp[0])[0], :np.shape(inp[0])[1]],
                         inp[2].repeat(2, axis=0)[:np.shape(inp[0])[0], :np.shape(inp[0])[1]]),
                        axis=-1)

    @staticmethod
    def __forward_4_4_4(inp):
        return (inp[:, :, 0], inp[:, :, 1], inp[:, :, 2])

    @staticmethod
    def __inverse_4_4_4(inp):
        return np.stack((inp[0], inp[1], inp[2]), axis=-1)
    # pylint: enable=unused-private-member
