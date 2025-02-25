"""
Copyright 2020 The OneFlow Authors. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import unittest
from collections import OrderedDict

import numpy as np
from automated_test_util import *
from test_util import GenArgList

import oneflow as flow
import oneflow.unittest


def _test_atan2_forward(test_case, shape, scalar, device):
    np_input_x = 10 * np.random.rand(*shape)
    np_input_y = 10 * np.random.randn(*shape)
    of_input_x = flow.Tensor(np_input_x, dtype=flow.float32, device=flow.device(device))
    of_input_y = flow.Tensor(np_input_y, dtype=flow.float32, device=flow.device(device))
    of_out = flow.atan2(of_input_x, of_input_y)
    np_out = np.arctan2(np_input_x, np_input_y)
    test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-05, 1e-05))


def _test_atan2_backward(test_case, device):
    np_input_x = np.random.rand(2, 3)
    np_input_y = np.random.rand(2, 3)
    np_y_grad = -1 * np_input_x / (np_input_x * np_input_x + np_input_y * np_input_y)
    np_x_grad = np_input_y / (np_input_x * np_input_x + np_input_y * np_input_y)

    def test_x_y_grad():
        of_input_x = flow.Tensor(
            np_input_x,
            dtype=flow.float32,
            device=flow.device(device),
            requires_grad=True,
        )
        of_input_y = flow.Tensor(
            np_input_y,
            dtype=flow.float32,
            device=flow.device(device),
            requires_grad=True,
        )
        of_out = flow.atan2(of_input_x, of_input_y)
        of_out_sum = of_out.sum()
        of_out_sum.backward()
        test_case.assertTrue(
            np.allclose(of_input_x.grad.numpy(), np_x_grad, 0.0001, 0.0001)
        )
        test_case.assertTrue(
            np.allclose(of_input_y.grad.numpy(), np_y_grad, 0.0001, 0.0001)
        )

    def test_x_grad():
        of_input_x = flow.Tensor(
            np_input_x,
            dtype=flow.float32,
            device=flow.device(device),
            requires_grad=True,
        )
        of_input_y = flow.Tensor(
            np_input_y, dtype=flow.float32, device=flow.device(device)
        )
        of_out = flow.atan2(of_input_x, of_input_y)
        of_out_sum = of_out.sum()
        of_out_sum.backward()
        test_case.assertTrue(
            np.allclose(of_input_x.grad.numpy(), np_x_grad, 0.0001, 0.0001)
        )

    def test_y_grad():
        of_input_x = flow.Tensor(
            np_input_x, dtype=flow.float32, device=flow.device(device)
        )
        of_input_y = flow.Tensor(
            np_input_y,
            dtype=flow.float32,
            device=flow.device(device),
            requires_grad=True,
        )
        of_out = flow.atan2(of_input_x, of_input_y)
        of_out_sum = of_out.sum()
        of_out_sum.backward()
        test_case.assertTrue(
            np.allclose(of_input_y.grad.numpy(), np_y_grad, 0.0001, 0.0001)
        )

    test_x_y_grad()
    test_x_grad()
    test_y_grad()


@flow.unittest.skip_unless_1n1d()
class TestAtan2(flow.unittest.TestCase):
    def test_atan2_forward(test_case):
        arg_dict = OrderedDict()
        arg_dict["shape"] = [(2,), (2, 3), (2, 3, 4), (2, 3, 4, 5)]
        arg_dict["scalar"] = [2.1, 0.8]
        arg_dict["device"] = ["cpu", "cuda"]
        for arg in GenArgList(arg_dict):
            _test_atan2_forward(test_case, *arg)

    def test_atan2_backward(test_case):
        arg_dict = OrderedDict()
        arg_dict["device"] = ["cpu", "cuda"]
        for arg in GenArgList(arg_dict):
            _test_atan2_backward(test_case, *arg)

    def test_flow_atan2_with_random_data(test_case):
        for device in ["cpu", "cuda"]:
            test_flow_against_pytorch(
                test_case,
                "atan2",
                extra_annotations={"other": flow.Tensor},
                extra_generators={
                    "input": random_tensor(ndim=1, dim1=1),
                    "other": random_tensor(ndim=1, dim1=1),
                },
                device=device,
            )


if __name__ == "__main__":
    unittest.main()
