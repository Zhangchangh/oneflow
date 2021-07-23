import os
import unittest
from collections import OrderedDict

import numpy as np
import test_global_storage
from test_util import GenArgList, type_name_to_flow_type, type_name_to_np_type

from oneflow.compatible import single_client as flow


def WatchDiff(test_case, device_type, input_shape, dtype):
    assert device_type in ["gpu", "cpu"]
    assert dtype in ["float32", "double"]
    flow.clear_default_session()
    func_config = flow.FunctionConfig()
    func_config.default_data_type(flow.float)

    def CheckOnes(diff):
        ones = np.ones(input_shape)
        test_case.assertTrue(np.allclose(diff.numpy(), ones, rtol=1e-05, atol=1e-05))

    @flow.global_function(type="train", function_config=func_config)
    def TrainJob():
        with flow.scope.placement(device_type, "0:0"):
            x = flow.get_variable(
                "in",
                shape=input_shape,
                dtype=type_name_to_flow_type[dtype],
                initializer=flow.random_uniform_initializer(),
                trainable=True,
            )
            flow.watch_diff(x, CheckOnes)
            flow.optimizer.SGD(
                flow.optimizer.PiecewiseConstantScheduler([], [0.0001]), momentum=0
            ).minimize(x)

    TrainJob()


@flow.unittest.skip_unless_1n1d()
class TestWatchDiff(flow.unittest.TestCase):
    def test_watch_diff(test_case):
        arg_dict = OrderedDict()
        arg_dict["device_type"] = ["gpu", "cpu"]
        arg_dict["input_shape"] = [(10,)]
        arg_dict["dtype"] = ["float32"]
        for arg in GenArgList(arg_dict):
            WatchDiff(test_case, *arg)


if __name__ == "__main__":
    unittest.main()
