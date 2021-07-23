import unittest

import numpy as np

from oneflow.compatible import single_client as flow
from oneflow.compatible.single_client import typing as oft


def _test(test_case, mode):
    flow.config.gpu_device_num(2)
    flow.config.enable_debug_mode(True)
    func_config = flow.FunctionConfig()
    func_config.default_logical_view(flow.scope.consistent_view())
    func_config.optimizer_placement_optimization_mode(mode)

    @flow.global_function(type="train", function_config=func_config)
    def Foo(x: oft.Numpy.Placeholder((2, 1024 * 1024))):
        w = flow.get_variable(
            "w", (1024 * 1024,), initializer=flow.constant_initializer(100)
        )
        flow.optimizer.SGD(
            flow.optimizer.PiecewiseConstantScheduler([], [5]), momentum=0
        ).minimize(x + w)

    Foo(np.ones((2, 1024 * 1024), dtype=np.float32))


@flow.unittest.skip_unless_1n2d()
class TestOptimizerPlacementOptimization(flow.unittest.TestCase):
    def test_non_distributed(test_case):
        _test(test_case, "non_distributed")

    def test_distributed_split(test_case):
        _test(test_case, "distributed_split")


if __name__ == "__main__":
    unittest.main()
