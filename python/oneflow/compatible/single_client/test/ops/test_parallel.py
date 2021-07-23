import unittest
import numpy as np
from oneflow.compatible import single_client as flow
from oneflow.compatible.single_client import typing as oft


def NaiveTest(test_case):
    shape = (16, 2)
    func_config = flow.FunctionConfig()
    func_config.default_data_type(flow.float)

    @flow.global_function(function_config=func_config)
    def AddJob(a: oft.Numpy.Placeholder(shape), b: oft.Numpy.Placeholder(shape)):
        return a + b + b

    x = np.random.rand(*shape).astype(np.float32)
    y = np.random.rand(*shape).astype(np.float32)
    z = AddJob(x, y).get().numpy()
    test_case.assertTrue(np.array_equal(z, x + y + y))


class TestParallel(flow.unittest.TestCase):
    @flow.unittest.skip_unless_1n1d()
    def test_1n1c(test_case):
        flow.config.gpu_device_num(1)
        NaiveTest(test_case)

    @flow.unittest.skip_unless_1n2d()
    def test_1n2c(test_case):
        flow.config.gpu_device_num(2)
        NaiveTest(test_case)

    @flow.unittest.skip_unless_2n1d()
    def test_2n2c(test_case):
        flow.config.gpu_device_num(1)
        NaiveTest(test_case)


if __name__ == "__main__":
    unittest.main()
