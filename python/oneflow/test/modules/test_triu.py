import unittest
from collections import OrderedDict

import numpy as np
from test_util import GenArgList

import oneflow as flow
import oneflow.nn as nn


def _test_triu(test_case, diagonal, device):
    arr_shape = (4, 4, 8)
    np_arr = np.random.randn(*arr_shape)
    input_tensor = flow.Tensor(
        np_arr, dtype=flow.float32, device=flow.device(device), requires_grad=True
    )
    output = flow.triu(input_tensor, diagonal=diagonal)
    np_out = np.triu(np_arr, diagonal)
    test_case.assertTrue(np.allclose(output.numpy(), np_out, 1e-06, 1e-06))
    output = output.sum()
    output.backward()
    np_grad = np.triu(np.ones(shape=arr_shape, dtype=np.float32), diagonal)
    test_case.assertTrue(np.allclose(input_tensor.grad.numpy(), np_grad, 1e-06, 1e-06))


@flow.unittest.skip_unless_1n1d()
class TestTriu(flow.unittest.TestCase):
    def test_triu(test_case):
        arg_dict = OrderedDict()
        arg_dict["test_fun"] = [_test_triu]
        arg_dict["diagonal"] = [2, -1]
        arg_dict["device"] = ["cuda", "cpu"]
        for arg in GenArgList(arg_dict):
            arg[0](test_case, *arg[1:])


if __name__ == "__main__":
    unittest.main()
