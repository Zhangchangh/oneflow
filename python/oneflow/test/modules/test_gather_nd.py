import unittest
from collections import OrderedDict
import numpy as np
import oneflow as flow
from test_util import GenArgList


def _test_gather_nd(test_case, device):
    input = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    indices = np.array([[0], [2]])
    np_out = np.array([[1, 2, 3], [7, 8, 9]])
    output = flow.gather_nd(
        flow.Tensor(input, dtype=flow.float, device=flow.device(device)),
        flow.Tensor(indices, dtype=flow.int, device=flow.device(device)),
    )
    test_case.assertTrue(np.array_equal(output.numpy(), np_out))


def _test_gather_nd_t(test_case, device):
    input = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    indices = np.array([[0, 2], [2, 1]])
    np_out = np.array([3, 8])
    output = flow.gather_nd(
        flow.Tensor(input, dtype=flow.float, device=flow.device(device)),
        flow.Tensor(indices, dtype=flow.int, device=flow.device(device)),
    )
    test_case.assertTrue(np.array_equal(output.numpy(), np_out))


def _test_gather_nd_backward(test_case, device):
    input = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    indices = np.array([[0], [2]])
    np_out = np.array([[1, 2, 3], [7, 8, 9]])
    np_grad = np.array([[1, 1, 1], [0, 0, 0], [1, 1, 1]])
    of_input = flow.Tensor(
        input, requires_grad=True, dtype=flow.float, device=flow.device(device)
    )
    output = flow.gather_nd(
        of_input, flow.Tensor(indices, dtype=flow.int, device=flow.device(device))
    )
    out_sum = output.sum()
    out_sum.backward()
    test_case.assertTrue(np.array_equal(output.numpy(), np_out))
    test_case.assertTrue(np.array_equal(of_input.grad.numpy(), np_grad))


def _test_gather_nd_backward_t(test_case, device):
    input = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    indices = np.array([[0, 2], [2, 1]])
    np_out = np.array([3, 8])
    np_grad = np.array([[0, 0, 1], [0, 0, 0], [0, 1, 0]])
    of_input = flow.Tensor(
        input, requires_grad=True, dtype=flow.float, device=flow.device(device)
    )
    output = flow.gather_nd(
        of_input, flow.Tensor(indices, dtype=flow.int, device=flow.device(device))
    )
    out_sum = output.sum()
    out_sum.backward()
    test_case.assertTrue(np.array_equal(output.numpy(), np_out))
    test_case.assertTrue(np.array_equal(of_input.grad.numpy(), np_grad))


@flow.unittest.skip_unless_1n1d()
class TestGather_nd(flow.unittest.TestCase):
    def test_gather_nd(test_case):
        arg_dict = OrderedDict()
        arg_dict["test_fun"] = [
            _test_gather_nd,
            _test_gather_nd_t,
            _test_gather_nd_backward,
            _test_gather_nd_backward_t,
        ]
        arg_dict["device"] = ["cpu", "cuda"]
        for arg in GenArgList(arg_dict):
            arg[0](test_case, *arg[1:])


if __name__ == "__main__":
    unittest.main()
