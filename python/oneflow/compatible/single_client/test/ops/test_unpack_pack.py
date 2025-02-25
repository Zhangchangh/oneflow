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

import numpy as np

import oneflow.compatible.single_client.unittest
from oneflow.compatible import single_client as flow
from oneflow.compatible.single_client import typing as oft

func_config = flow.FunctionConfig()
func_config.default_logical_view(flow.scope.mirrored_view())
func_config.default_data_type(flow.float)


@flow.unittest.skip_unless_1n1d()
class TestUnpackPack(flow.unittest.TestCase):
    def test_unpack_pack(test_case):
        if flow.eager_execution_enabled():
            return

        @flow.global_function(function_config=func_config)
        def UnpackPackJob(a: oft.Numpy.Placeholder((3, 4))):
            return flow.pack(flow.unpack(a, 3), 3)

        x = np.random.rand(3, 4).astype(np.float32)
        y = UnpackPackJob(x).get().numpy()
        test_case.assertTrue(np.array_equal(y, x))


if __name__ == "__main__":
    unittest.main()
