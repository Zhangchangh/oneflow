import unittest
from collections import OrderedDict
from oneflow.framework.tensor import register_tensor_op
import numpy as np
import oneflow as flow
from test_util import GenArgList


def _test_ones(test_case, device, shape):
    y = flow.ones(shape, device=flow.device(device))
    test_case.assertTrue(np.array_equal(np.ones(shape), y.numpy()))


def _test_different_dtype(test_case, device, shape):
    y1 = flow.ones(shape, dtype=flow.int32, device=flow.device(device))
    test_case.assertTrue(np.array_equal(np.ones(shape, dtype=np.int32), y1.numpy()))
    y2 = flow.ones(shape, dtype=flow.uint8, device=flow.device(device))
    test_case.assertTrue(np.array_equal(np.ones(shape, dtype=np.uint8), y2.numpy()))
    y3 = flow.ones(shape, dtype=flow.float64, device=flow.device(device))
    test_case.assertTrue(np.array_equal(np.ones(shape, dtype=np.float64), y3.numpy()))


def _test_ones_backward(test_case, device, shape):
    x = flow.ones(shape, device=flow.device(device), requires_grad=True)
    y = x.sum()
    y.backward()
    test_case.assertTrue(np.array_equal(np.ones(shape), x.grad.numpy()))


def _test_zeros(test_case, device, shape):
    y = flow.zeros(shape, device=flow.device(device))
    test_case.assertTrue(np.array_equal(np.zeros(shape), y.numpy()))
    y2 = flow.zeros(10, device=flow.device(device))
    test_case.assertTrue(np.array_equal(np.zeros(10), y2.numpy()))
    y3 = flow.zeros(10, dtype=flow.int, device=flow.device(device))
    test_case.assertTrue(np.array_equal(np.zeros(10, dtype=int), y3.numpy()))


def _test_zeros_backward(test_case, device, shape):
    x = flow.zeros(shape, device=flow.device(device), requires_grad=True)
    y = x.sum()
    y.backward()
    test_case.assertTrue(np.array_equal(np.ones(shape), x.grad.numpy()))


def _test_ones_like(test_case, device, shape):
    x = flow.Tensor(np.ones(shape, dtype=np.float64))
    test_case.assertTrue(
        np.array_equal(np.ones_like(x.numpy()), flow.ones_like(x).numpy())
    )
    x2 = flow.Tensor(np.ones([2, 4], dtype=int))
    test_case.assertTrue(
        np.array_equal(np.ones_like(x2.numpy()), flow.ones_like(x2).numpy())
    )


def _test_zeros_like(test_case, device, shape):
    x = flow.Tensor(np.ones(shape, dtype=np.float64))
    test_case.assertTrue(
        np.array_equal(np.zeros_like(x.numpy()), flow.zeros_like(x).numpy())
    )
    x2 = flow.Tensor(np.ones(shape, dtype=int))
    test_case.assertTrue(
        np.array_equal(np.zeros_like(x2.numpy()), flow.zeros_like(x2).numpy())
    )


def _test_new_ones(test_case, device, shape):
    x = flow.Tensor(np.ones(shape), device=flow.device(device))
    y = x.new_ones(shape, device=device)
    test_case.assertTrue(x.dtype == y.dtype)
    test_case.assertTrue(x.device == y.device)
    test_case.assertTrue(x.requires_grad == y.requires_grad)
    x = flow.Tensor(np.ones(shape), device=flow.device(device))
    y = x.new_ones(x.shape, device=device)
    test_case.assertTrue(x.dtype == y.dtype)
    test_case.assertTrue(x.device == y.device)
    test_case.assertTrue(x.requires_grad == y.requires_grad)
    x = flow.Tensor(np.ones(shape), device=flow.device(device))
    x = x.new_ones(shape, device=device, requires_grad=True)
    y = x.sum()
    y.backward()
    test_case.assertTrue(np.array_equal(np.ones_like(x.numpy()), x.grad.numpy()))


@flow.unittest.skip_unless_1n1d()
class TestConstantModule(flow.unittest.TestCase):
    def test_cast(test_case):
        arg_dict = OrderedDict()
        arg_dict["test_fun"] = [
            _test_ones,
            _test_different_dtype,
            _test_zeros,
            _test_ones_backward,
            _test_zeros_backward,
            _test_ones_like,
            _test_zeros_like,
            _test_new_ones,
        ]
        arg_dict["device"] = ["cpu", "cuda"]
        arg_dict["shape"] = [(2, 3), (2, 3, 4), (2, 3, 4, 5)]
        for arg in GenArgList(arg_dict):
            arg[0](test_case, *arg[1:])


if __name__ == "__main__":
    unittest.main()
