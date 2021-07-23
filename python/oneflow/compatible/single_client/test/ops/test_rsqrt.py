import unittest
import numpy as np
from oneflow.compatible import single_client as flow
from oneflow.compatible.single_client import typing as oft

def _check(test_case, x, y):
    np_rsqrt = 1.0 / np.sqrt(x)
    test_case.assertTrue(np.allclose(np_rsqrt, y))

def _run_test(test_case, x, dtype, device):
    func_config = flow.FunctionConfig()
    func_config.default_data_type(flow.float)
    func_config.default_logical_view(flow.scope.consistent_view())

    @flow.global_function(function_config=func_config)
    def RsqrtJob(x: oft.Numpy.Placeholder(x.shape, dtype=dtype)):
        return flow.math.rsqrt(x)
    y = RsqrtJob(x).get()
    _check(test_case, x, y.numpy())

@flow.unittest.skip_unless_1n2d()
class TestRsqrt(flow.unittest.TestCase):

    def test_rsqrt_random_gpu(test_case):
        flow.config.gpu_device_num(2)
        x = np.random.rand(10, 3, 32, 1024).astype(np.float32)
        _run_test(test_case, x, flow.float, 'gpu')

    def test_rsqrt_random_cpu(test_case):
        flow.config.gpu_device_num(2)
        x = np.random.rand(10, 3, 32, 1024).astype(np.float32)
        _run_test(test_case, x, flow.float, 'cpu')
if __name__ == '__main__':
    unittest.main()