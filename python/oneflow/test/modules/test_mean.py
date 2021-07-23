import unittest
from collections import OrderedDict

import numpy as np
from automated_test_util import *
from test_util import GenArgList

import oneflow as flow


def _test_mean(test_case, shape, device):
    input = flow.Tensor(
        np.random.randn(*shape), dtype=flow.float32, device=flow.device(device)
    )
    of_out = flow.mean(input, dim=1)
    np_out = np.mean(input.numpy(), axis=1)
    test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 0.0001, 0.0001))
    input = flow.Tensor(
        np.random.randn(*shape), dtype=flow.float32, device=flow.device(device)
    )
    of_out = flow.mean(input, dim=0)
    np_out = np.mean(input.numpy(), axis=0)
    test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 0.0001, 0.0001))


def _test_mean_negative_dim(test_case, shape, device):
    if len(shape) < 4:
        shape = (2, 3, 4, 5)
    input = flow.Tensor(
        np.random.randn(*shape), dtype=flow.float32, device=flow.device(device)
    )
    of_out = flow.mean(input, dim=(-2, -1, -3))
    np_out = np.mean(input.numpy(), axis=(-2, -1, -3))
    test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 0.0001, 0.0001))


def _test_mean_backward(test_case, shape, device):
    np_arr = np.random.randn(*shape)
    x = flow.Tensor(
        np_arr, dtype=flow.float32, device=flow.device(device), requires_grad=True
    )
    y = flow.mean(x, dim=1)
    z = y.sum()
    z.backward()
    np_grad = np.zeros(shape=np_arr.shape)
    np_grad[:] = 1 / x.size(1)
    test_case.assertTrue(np.allclose(x.grad.numpy(), np_grad, 1e-05, 1e-05))


@flow.unittest.skip_unless_1n1d()
class TestMean(flow.unittest.TestCase):
    def test_mean(test_case):
        arg_dict = OrderedDict()
        arg_dict["test_fun"] = [
            _test_mean,
            _test_mean_negative_dim,
            _test_mean_backward,
        ]
        arg_dict["shape"] = [(2, 3), (2, 3, 4), (2, 4, 5, 6)]
        arg_dict["device"] = ["cpu", "cuda"]
        for arg in GenArgList(arg_dict):
            arg[0](test_case, *arg[1:])

    def test_mean_against_pytorch(test_case):
        arg_dict = OrderedDict()
        arg_dict["test_type"] = [test_flow_against_pytorch, test_tensor_against_pytorch]
        arg_dict["device"] = ["cpu", "cuda"]
        for arg in GenArgList(arg_dict):
            arg[0](test_case, "mean", device=arg[1])


if __name__ == "__main__":
    unittest.main()
