"""Tests for the different transforms implemented in jpegdna.transforms"""

import numpy as np
from jpegdna.transforms import DCT
from jpegdna.transforms import ZigZag
from jpegdna.transforms import ChannelSampler


class TestDCT():
    """Tests on the DCT transform"""
    def  forward_test(self):
        """Functionnal tests for the discrete cosine transform: forward_test"""
        transform = DCT()
        inp = np.array([1., 2., 3., 4., 5., 6.])
        target = np.array([8.5732141, -4.1625618, 0., -0.40824829, 0., -0.08007889])
        transformed = transform.full_forward(inp, "ortho")
        assert (abs(target - transformed) <= abs(target) * 1e-5).all()
        inp = np.array([1., 2., 3., 4., 5., 6.])
        target = np.array([42., -14.41953704, 0., -1.41421356, 0., -0.27740142])
        transformed = transform.full_forward(inp)
        assert (abs(target - transformed) <= abs(target) * 1e-5).all()
        inp = np.array([1., 2., 3., 4., 5., 6.])
        target = np.array([42., -14.41953704, 0., -1.41421356, 0., -0.27740142])
        transformed = transform.forward(inp)
        assert (abs(target - transformed) <= abs(target) * 1e-5).all()
    def  inverse_test(self):
        """Functionnal tests for the discrete cosine transform: inverse_test"""
        transform = DCT()
        target = np.array([1., 2., 3., 4., 5., 6.])
        inp = np.array([8.5732141, -4.1625618, 0., -0.40824829, 0., -0.08007889])
        out = transform.full_inverse(inp, "ortho")
        assert ((target - out) < target * 1e-5).all()
        target = np.array([1., 2., 3., 4., 5., 6.])
        inp = np.array([42., -14.41953704, 0., -1.41421356, 0., -0.27740142])
        out = transform.full_inverse(inp)
        assert ((target - out) < target * 1e-5).all()
        target = np.array([1., 2., 3., 4., 5., 6.])
        inp = np.array([42., -14.41953704, 0., -1.41421356, 0., -0.27740142])
        out = transform.inverse(inp)
        assert ((target - out) < target * 1e-5).all()
    def  forward_inverse_test(self):
        """Functionnal tests for the discrete cosine transform: forward_inverse_test"""
        transform = DCT()
        inp = np.array([1., 2., 3., 4., 5., 6.])
        transformed = transform.full_forward(inp, "ortho")
        out = transform.full_inverse(transformed, "ortho")
        assert ((inp - out) < inp * 1e-5).all()


class TestZigZag():
    """Tests on the Zig-Zag transform"""
    def forward_test(self):
        """Functionnal tests for the zig-zag transform: forward_test"""
        transform = ZigZag()
        inp = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        target = [1, 2, 4, 7, 5, 3, 6, 8, 9]
        transformed = transform.forward(inp)
        assert (transformed == target).all()
    def inverse_test(self):
        """Functionnal tests for the zig-zag transform: inverse_test"""
        transform = ZigZag()
        target = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        transformed = [1, 2, 4, 7, 5, 3, 6, 8, 9]
        out = transform.full_inverse(transformed, 3, 3)
        assert (out == target).all()


class TestChannelSampler():
    """Tests on the chroma channels sampler"""
    def default_init_test(self):
        """Functionnal tests for the default channel sampler initializer"""
        sampler = ChannelSampler()
        assert sampler.sampler == "4_2_2"
    def default_forward_test(self):
        """Functionnal tests for the default channel sampler forward"""
        sampler = ChannelSampler()
        inp = np.zeros((64, 64, 3))
        res = sampler.forward(inp)
        assert res[0].shape == (64, 64)
        assert res[1].shape == (64, 32)
        assert res[2].shape == (64, 32)
    def default_inverse_test(self):
        """Functionnal tests for the default channel sampler inverse"""
        sampler = ChannelSampler()
        inp = (np.zeros((64, 64)), np.zeros((64, 32)), np.zeros((64, 32)))
        res = sampler.inverse(inp)
        assert res.shape == (64, 64, 3)
    def init_4_2_2_test(self):
        """Functionnal tests for the 4:2:2 channel sampler initializer"""
        sampler = ChannelSampler(sampler="4:2:2")
        assert sampler.sampler == "4_2_2"
    def forward_4_2_2_test(self):
        """Functionnal tests for the 4:2:2 channel sampler forward"""
        sampler = ChannelSampler(sampler="4:2:2")
        inp = np.zeros((64, 64, 3))
        res = sampler.forward(inp)
        assert res[0].shape == (64, 64)
        assert res[1].shape == (64, 32)
        assert res[2].shape == (64, 32)
    def inverse_4_2_2_test(self):
        """Functionnal tests for the 4:2:2 channel sampler inverse"""
        sampler = ChannelSampler(sampler="4:2:2")
        inp = (np.zeros((64, 64)), np.zeros((64, 32)), np.zeros((64, 32)))
        res = sampler.inverse(inp)
        assert res.shape == (64, 64, 3)
    def init_4_4_4_test(self):
        """Functionnal tests for the 4:4:4 channel sampler initializer"""
        sampler = ChannelSampler(sampler="4:4:4")
        assert sampler.sampler == "4_4_4"
    def forward_4_4_4_test(self):
        """Functionnal tests for the 4:4:4 channel sampler forward"""
        sampler = ChannelSampler(sampler="4:4:4")
        inp = np.zeros((64, 64, 3))
        res = sampler.forward(inp)
        assert res[0].shape == (64, 64)
        assert res[1].shape == (64, 64)
        assert res[2].shape == (64, 64)
    def inverse_4_4_4_test(self):
        """Functionnal tests for the 4:4:4 channel sampler inverse"""
        sampler = ChannelSampler(sampler="4:4:4")
        inp = (np.zeros((64, 64)), np.zeros((64, 64)), np.zeros((64, 64)))
        res = sampler.inverse(inp)
        assert res.shape == (64, 64, 3)
    def init_4_1_1_test(self):
        """Functionnal tests for the 4:1:1 channel sampler initializer"""
        sampler = ChannelSampler(sampler="4:1:1")
        assert sampler.sampler == "4_1_1"
    def forward_4_1_1_test(self):
        """Functionnal tests for the 4:1:1 channel sampler forward"""
        sampler = ChannelSampler(sampler="4:1:1")
        inp = np.zeros((64, 64, 3))
        res = sampler.forward(inp)
        assert res[0].shape == (64, 64)
        assert res[1].shape == (64, 16)
        assert res[2].shape == (64, 16)
    def inverse_4_1_1_test(self):
        """Functionnal tests for the 4:1:1 channel sampler inverse"""
        sampler = ChannelSampler(sampler="4:1:1")
        inp = (np.zeros((64, 64)), np.zeros((64, 16)), np.zeros((64, 16)))
        res = sampler.inverse(inp)
        assert res.shape == (64, 64, 3)
    def init_4_2_0_test(self):
        """Functionnal tests for the 4:2:0 channel sampler initializer"""
        sampler = ChannelSampler(sampler="4:2:0")
        assert sampler.sampler == "4_2_0"
    def forward_4_2_0_test(self):
        """Functionnal tests for the 4:2:0 channel sampler forward"""
        sampler = ChannelSampler(sampler="4:2:0")
        inp = np.zeros((64, 64, 3))
        res = sampler.forward(inp)
        assert res[0].shape == (64, 64)
        assert res[2].shape == (32, 32)
        assert res[2].shape == (32, 32)
    def inverse_4_2_0_test(self):
        """Functionnal tests for the 4:2:0 channel sampler inverse"""
        sampler = ChannelSampler(sampler="4:2:0")
        inp = np.zeros((64, 64, 3))
        inp = (np.zeros((64, 64)), np.zeros((32, 32)), np.zeros((32, 32)))
        res = sampler.inverse(inp)
        assert res.shape == (64, 64, 3)
    def init_4_4_0_test(self):
        """Functionnal tests for the 4:4:0 channel sampler initializer"""
        sampler = ChannelSampler(sampler="4:4:0")
        assert sampler.sampler == "4_4_0"
    def forward_4_4_0_test(self):
        """Functionnal tests for the 4:4:0 channel sampler forward"""
        sampler = ChannelSampler(sampler="4:4:0")
        inp = np.zeros((64, 64, 3))
        res = sampler.forward(inp)
        assert res[0].shape == (64, 64)
        assert res[1].shape == (32, 64)
        assert res[2].shape == (32, 64)
    def inverse_4_4_0_test(self):
        """Functionnal tests for the 4:4:0 channel sampler inverse"""
        sampler = ChannelSampler(sampler="4:4:0")
        inp = (np.zeros((64, 64)), np.zeros((32, 64)), np.zeros((32, 64)))
        res = sampler.inverse(inp)
        assert res.shape == (64, 64, 3)
