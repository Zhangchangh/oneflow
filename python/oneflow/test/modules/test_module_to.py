import unittest
from collections import OrderedDict

import numpy as np
from test_util import GenArgList

import oneflow as flow

dummy_val = np.random.randn(2, 3)
in_val = np.full((2, 3), -2)
cpu0_device = flow.device("cpu")
gpu0_device = flow.device("cuda")


class DummyModule(flow.nn.Module):
    def __init__(self):
        super().__init__()
        self.register_buffer("dummy_buf", flow.Tensor(dummy_val))
        self.dummy_para = flow.nn.Parameter(flow.Tensor(dummy_val))

    def forward(self, x):
        return self.dummy_para * x + self.dummy_buf


def _test_dummy_module(test_case):
    m = DummyModule()
    test_case.assertEqual(m.dummy_buf.device, cpu0_device)
    test_case.assertEqual(m.dummy_para.device, cpu0_device)
    input = flow.Tensor(in_val)
    output = m(input)
    test_case.assertTrue(np.allclose(output.numpy(), -dummy_val, 0.0001, 0.0001))
    test_case.assertEqual(m.dummy_buf.grad, None)
    test_case.assertEqual(m.dummy_para.grad, None)
    test_case.assertEqual(input.device, cpu0_device)
    test_case.assertEqual(output.device, cpu0_device)


def _test_dummy_module_to(test_case):
    m = DummyModule()
    test_case.assertEqual(m.dummy_buf.device, cpu0_device)
    test_case.assertEqual(m.dummy_para.device, cpu0_device)
    m.to(gpu0_device)
    test_case.assertEqual(m.dummy_buf.device, gpu0_device)
    test_case.assertTrue(m.dummy_buf.is_leaf)
    test_case.assertTrue(not m.dummy_buf.requires_grad)
    test_case.assertEqual(m.dummy_para.device, gpu0_device)
    test_case.assertTrue(m.dummy_para.is_leaf)
    test_case.assertTrue(m.dummy_para.requires_grad)
    input = flow.Tensor(in_val).to(gpu0_device)
    output = m(input)
    test_case.assertTrue(np.allclose(output.numpy(), -dummy_val, 0.0001, 0.0001))
    test_case.assertEqual(m.dummy_buf.grad, None)
    test_case.assertEqual(m.dummy_para.grad, None)
    test_case.assertEqual(input.device, gpu0_device)
    test_case.assertEqual(output.device, gpu0_device)
    output_grad = flow.ones((2, 3)).to(gpu0_device)
    output.backward(output_grad)
    test_case.assertEqual(output_grad.device, gpu0_device)
    test_case.assertEqual(m.dummy_buf.grad, None)
    test_case.assertTrue(np.allclose(m.dummy_para.grad.numpy(), in_val, 0.0001, 0.0001))
    test_case.assertEqual(m.dummy_para.grad.device, gpu0_device)


@flow.unittest.skip_unless_1n1d()
class TestModuleTo(flow.unittest.TestCase):
    def test_module_to(test_case):
        arg_dict = OrderedDict()
        arg_dict["test_fun"] = [_test_dummy_module, _test_dummy_module_to]
        for arg in GenArgList(arg_dict):
            arg[0](test_case, *arg[1:])


if __name__ == "__main__":
    unittest.main()
