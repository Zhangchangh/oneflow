import unittest
from collections import OrderedDict
import numpy as np
import oneflow as flow
from test_util import GenArgList

def _test_where(test_case, device):
    x = flow.Tensor(np.array([[-0.462, 0.3139], [0.3898, -0.7197], [0.0478, -0.1657]]), dtype=flow.float32, device=flow.device(device))
    y = flow.Tensor(np.ones(shape=(3, 2)), dtype=flow.float32, device=flow.device(device))
    condition = flow.Tensor(np.array([[0, 1], [1, 0], [1, 0]]), dtype=flow.int32, device=flow.device(device))
    of_out = flow.where(condition, x, y)
    np_out = np.array([[1.0, 0.3139], [0.3898, 1.0], [0.0478, 1.0]])
    test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-05, 1e-05))

def _test_where_broadcast(test_case, device):
    x = flow.Tensor(np.array([[[-0.462, 0.3139], [0.3898, -0.7197], [0.0478, -0.1657]]]), dtype=flow.float32, device=flow.device(device))
    y = flow.Tensor(np.ones(shape=(3, 3, 2)), dtype=flow.float32, device=flow.device(device))
    condition = flow.Tensor(np.array([[[0, 1], [1, 0], [1, 0]]]), dtype=flow.int32, device=flow.device(device))
    of_out = flow.where(condition, x, y)
    np_out = np.array([[[1.0, 0.3139], [0.3898, 1.0], [0.0478, 1.0]], [[1.0, 0.3139], [0.3898, 1.0], [0.0478, 1.0]], [[1.0, 0.3139], [0.3898, 1.0], [0.0478, 1.0]]])
    test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-05, 1e-05))

def _test_where_scalar(test_case, device):
    x = 0.5
    y = 2.0
    condition = flow.Tensor(np.array([1]), dtype=flow.int32)
    of_out = flow.where(condition, x, y)
    np_out = np.array([0.5])
    test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-05, 1e-05))

def _test_where_dim4(test_case, device):
    x = flow.Tensor(np.array([[[[-0.462, 0.3139], [0.3898, -0.7197], [0.0478, -0.1657]]]]), dtype=flow.float32, device=flow.device(device))
    y = flow.Tensor(np.ones(shape=(1, 1, 3, 2)), dtype=flow.float32, device=flow.device(device))
    condition = flow.Tensor(np.array([[[[0, 1], [1, 0], [1, 0]]]]), dtype=flow.int32, device=flow.device(device))
    of_out = flow.where(condition, x, y)
    np_out = np.array([[[[1.0, 0.3139], [0.3898, 1.0], [0.0478, 1.0]]]])
    test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-05, 1e-05))

def _test_where_backward(test_case, device):
    x = flow.Tensor(np.array([[-0.462, 0.3139], [0.3898, -0.7197], [0.0478, -0.1657]]), dtype=flow.float32, device=flow.device(device), requires_grad=True)
    y = flow.Tensor(np.ones(shape=(3, 2)), dtype=flow.float32, device=flow.device(device), requires_grad=True)
    condition = flow.Tensor(np.array([[0, 1], [1, 0], [1, 0]]), dtype=flow.int32, device=flow.device(device))
    of_out = flow.where(condition, x, y)
    of_out = of_out.sum()
    of_out.backward()
    test_case.assertTrue(np.allclose(x.grad.numpy(), condition.numpy() == 1, 1e-05, 1e-05))
    test_case.assertTrue(np.allclose(y.grad.numpy(), condition.numpy() == 0, 1e-05, 1e-05))

def _test_where_broadcast_backward(test_case, device):
    x = flow.Tensor(np.array([[[-0.462, 0.3139], [0.3898, -0.7197], [0.0478, -0.1657]]]), dtype=flow.float32, device=flow.device(device), requires_grad=True)
    y = flow.Tensor(np.ones(shape=(3, 3, 2)), dtype=flow.float32, device=flow.device(device), requires_grad=True)
    condition = flow.Tensor(np.array([[[0, 1], [1, 0], [1, 0]]]), dtype=flow.int32, device=flow.device(device))
    of_out = flow.where(condition, x, y)
    of_out = of_out.sum()
    of_out.backward()
    x_grad = [[[0.0, 3.0], [3.0, 0.0], [3.0, 0.0]]]
    test_case.assertTrue(np.allclose(x.grad.numpy(), x_grad, 1e-05, 1e-05))
    y_grad = [[[1.0, 0.0], [0.0, 1.0], [0.0, 1.0]], [[1.0, 0.0], [0.0, 1.0], [0.0, 1.0]], [[1.0, 0.0], [0.0, 1.0], [0.0, 1.0]]]
    test_case.assertTrue(np.allclose(y.grad.numpy(), y_grad, 1e-05, 1e-05))

def _test_where_broadcast_x_backward(test_case, device):
    x = flow.Tensor(np.array([[[-0.462, 0.3139], [0.3898, -0.7197], [0.0478, -0.1657]]]), dtype=flow.float32, device=flow.device(device), requires_grad=True)
    y = flow.Tensor(np.ones(shape=(3, 3, 2)), dtype=flow.float32, device=flow.device(device))
    condition = flow.Tensor(np.array([[[0, 1], [1, 0], [1, 0]]]), dtype=flow.int32, device=flow.device(device))
    of_out = flow.where(condition, x, y)
    of_out = of_out.sum()
    of_out.backward()
    x_grad = [[[0.0, 3.0], [3.0, 0.0], [3.0, 0.0]]]
    test_case.assertTrue(np.allclose(x.grad.numpy(), x_grad, 1e-05, 1e-05))

@flow.unittest.skip_unless_1n1d()
class TestWhere(flow.unittest.TestCase):

    def test_where(test_case):
        arg_dict = OrderedDict()
        arg_dict['test_fun'] = [_test_where, _test_where_broadcast, _test_where_scalar, _test_where_dim4, _test_where_backward, _test_where_broadcast_backward, _test_where_broadcast_x_backward]
        arg_dict['device'] = ['cpu', 'cuda']
        for arg in GenArgList(arg_dict):
            arg[0](test_case, *arg[1:])
if __name__ == '__main__':
    unittest.main()