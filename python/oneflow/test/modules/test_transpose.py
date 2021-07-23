import unittest
from collections import OrderedDict

import numpy as np
from test_util import GenArgList

import oneflow as flow


def _test_transpose(test_case, device):
    input = flow.Tensor(
        np.random.randn(2, 6, 5, 3), dtype=flow.float32, device=flow.device(device)
    )
    of_out = flow.transpose(input, 0, 1)
    np_out = input.numpy().transpose((1, 0, 2, 3))
    test_case.assertTrue(np.array_equal(of_out.numpy().flatten(), np_out.flatten()))


def _test_tensor_transpose(test_case, device):
    input = flow.Tensor(
        np.random.randn(2, 6, 5, 3), dtype=flow.float32, device=flow.device(device)
    )
    of_out = input.transpose(0, 1)
    np_out = input.numpy().transpose((1, 0, 2, 3))
    test_case.assertTrue(np.array_equal(of_out.numpy().flatten(), np_out.flatten()))


def _test_tranpose_negative_dim(test_case, device):
    input = flow.Tensor(
        np.random.randn(2, 6, 5, 3), dtype=flow.float32, device=flow.device(device)
    )
    of_out = flow.transpose(input, -4, -3)
    np_out = input.numpy().transpose((1, 0, 2, 3))
    test_case.assertTrue(np.array_equal(of_out.numpy().flatten(), np_out.flatten()))


def _test_transpose_backward(test_case, device):
    x = flow.Tensor(
        np.random.randn(2, 6, 5, 3),
        dtype=flow.float32,
        device=flow.device(device),
        requires_grad=True,
    )
    y = flow.transpose(x, 0, 1).sum()
    y.backward()
    test_case.assertTrue(
        np.allclose(x.grad.numpy(), np.ones((2, 6, 5, 3)), 1e-05, 1e-05)
    )


def _test_transpose_backward_v2(test_case, device):
    x = flow.Tensor(
        np.random.randn(2, 3, 4, 5),
        dtype=flow.float32,
        device=flow.device(device),
        requires_grad=True,
    )
    y = flow.transpose(x, 3, 1).sum()
    y.backward()
    test_case.assertTrue(
        np.allclose(x.grad.numpy(), np.ones((2, 3, 4, 5)), 1e-05, 1e-05)
    )


@flow.unittest.skip_unless_1n1d()
class TestTranspose(flow.unittest.TestCase):
    def test_transpose(test_case):
        arg_dict = OrderedDict()
        arg_dict["fun"] = [
            _test_transpose,
            _test_tensor_transpose,
            _test_tranpose_negative_dim,
            _test_transpose_backward,
            _test_transpose_backward_v2,
        ]
        arg_dict["device"] = ["cpu", "cuda"]
        for arg in GenArgList(arg_dict):
            arg[0](test_case, *arg[1:])


if __name__ == "__main__":
    unittest.main()
