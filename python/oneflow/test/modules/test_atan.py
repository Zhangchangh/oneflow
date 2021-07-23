import unittest
from collections import OrderedDict
import numpy as np
import oneflow as flow
from test_util import GenArgList


def _test_atan(test_case, shape, device):
    np_input = np.random.randn(*shape)
    of_input = flow.Tensor(
        np_input, dtype=flow.float32, device=flow.device(device), requires_grad=True
    )
    of_out = flow.atan(of_input)
    np_out = np.arctan(np_input)
    test_case.assertTrue(
        np.allclose(of_out.numpy(), np_out, 1e-05, 1e-05, equal_nan=True)
    )
    of_out = of_out.sum()
    of_out.backward()
    np_out_grad = 1 / (1 + np_input ** 2)
    test_case.assertTrue(
        np.allclose(of_input.grad.numpy(), np_out_grad, 1e-05, 1e-05, equal_nan=True)
    )


def _test_arctan(test_case, shape, device):
    np_input = np.random.randn(*shape)
    of_input = flow.Tensor(
        np_input, dtype=flow.float32, device=flow.device(device), requires_grad=True
    )
    of_out = flow.arctan(of_input)
    np_out = np.arctan(np_input)
    test_case.assertTrue(
        np.allclose(of_out.numpy(), np_out, 1e-05, 1e-05, equal_nan=True)
    )
    of_out = of_out.sum()
    of_out.backward()
    np_out_grad = 1 / (1 + np_input ** 2)
    test_case.assertTrue(
        np.allclose(of_input.grad.numpy(), np_out_grad, 1e-05, 1e-05, equal_nan=True)
    )


@flow.unittest.skip_unless_1n1d()
class TestAtan(flow.unittest.TestCase):
    def test_atan(test_case):
        arg_dict = OrderedDict()
        arg_dict["test_fun"] = [_test_atan, _test_arctan]
        arg_dict["shape"] = [(2,), (2, 3), (2, 3, 4), (2, 4, 5, 6)]
        arg_dict["device"] = ["cpu", "cuda"]
        for arg in GenArgList(arg_dict):
            arg[0](test_case, *arg[1:])


if __name__ == "__main__":
    unittest.main()
