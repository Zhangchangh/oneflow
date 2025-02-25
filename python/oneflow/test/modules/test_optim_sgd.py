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
from test_util import GenArgDict

import oneflow as flow
import oneflow.unittest
from oneflow.nn.parameter import Parameter


def compare_with_numpy_sgd(
    test_case,
    device,
    x_shape,
    scale,
    momentum,
    weight_decay,
    learning_rate,
    train_iters,
):
    random_grad_seq = []
    for _ in range(train_iters):
        random_grad_seq.append(np.random.uniform(size=x_shape).astype(np.float32))
    init_value = np.random.uniform(size=x_shape).astype(np.float32)

    def train_by_oneflow():
        x = Parameter(flow.Tensor(init_value, device=flow.device(device)))
        sgd = flow.optim.SGD(
            [
                {
                    "params": [x],
                    "lr": learning_rate,
                    "momentum": momentum,
                    "scale": scale,
                    "weight_decay": weight_decay,
                }
            ]
        )

        def train_one_iter(grad):
            grad_tensor = flow.Tensor(
                grad, requires_grad=False, device=flow.device(device)
            )
            loss = flow.sum(x * grad_tensor)
            loss.backward()
            sgd.step()
            sgd.zero_grad()

        for i in range(train_iters):
            train_one_iter(random_grad_seq[i])
        return x

    def train_by_numpy():
        x = init_value
        vt = np.zeros_like(x)

        def train_one_iter(grad):
            grad = grad * scale + weight_decay * x
            v = momentum * vt - learning_rate * grad
            param = x + v
            return (param, v)

        for i in range(train_iters):
            (x, vt) = train_one_iter(random_grad_seq[i])
        return x

    oneflow_res = train_by_oneflow().numpy()
    numpy_res = train_by_numpy()
    test_case.assertTrue(
        np.allclose(
            oneflow_res.flatten(), numpy_res.flatten(), rtol=0.0001, atol=0.0001
        )
    )


@flow.unittest.skip_unless_1n1d()
class TestOptimizers(flow.unittest.TestCase):
    def test_sgd(test_case):
        arg_dict = OrderedDict()
        arg_dict["device"] = ["cpu", "cuda"]
        arg_dict["x_shape"] = [(10,)]
        arg_dict["scale"] = [1.0, 0.9]
        arg_dict["momentum"] = [0.0, 0.9]
        arg_dict["weight_decay"] = [0.0, 0.9]
        arg_dict["learning_rate"] = [1, 0.1]
        arg_dict["train_iters"] = [10]
        for arg in GenArgDict(arg_dict):
            compare_with_numpy_sgd(test_case, **arg)


if __name__ == "__main__":
    unittest.main()
