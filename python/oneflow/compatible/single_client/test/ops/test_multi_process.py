import os
import unittest

from oneflow.compatible import single_client as flow


@unittest.skipIf(flow.sysconfig.has_rpc_backend_grpc() == False, "lacks grpc")
@flow.unittest.skip_unless_1n4d()
@unittest.skipIf(
    os.getenv("ONEFLOW_TEST_GITHUB_HOSTED"),
    "this will fail because github hosted VM has only two CPU cores",
)
class TestMultiProcess(flow.unittest.TestCase):
    def test_multi_process(test_case):
        flow.config.gpu_device_num(4)
        func_config = flow.FunctionConfig()
        func_config.concurrency_width(1)

        @flow.global_function()
        def Foo():
            with flow.scope.placement("gpu", "0:0-3"):
                x = flow.get_variable(
                    "x",
                    shape=(2, 5),
                    dtype=flow.float,
                    initializer=flow.random_uniform_initializer(minval=0, maxval=1),
                    trainable=False,
                )
            return x

        of_ret = Foo().get()
        test_case.assertEqual(of_ret.numpy().shape, (2, 5))

    def test_worker_to_master_communication(test_case):
        flow.config.gpu_device_num(4)
        func_config = flow.FunctionConfig()
        func_config.concurrency_width(1)

        @flow.global_function()
        def Foo():
            with flow.scope.placement("gpu", "0:0"):
                x = flow.get_variable(
                    "x",
                    shape=(2, 5),
                    dtype=flow.float,
                    initializer=flow.random_uniform_initializer(minval=0, maxval=1),
                    trainable=False,
                )
            with flow.scope.placement("gpu", "0:3"):
                y = flow.get_variable(
                    "y",
                    shape=(2, 5),
                    dtype=flow.float,
                    initializer=flow.constant_initializer(0),
                    trainable=False,
                )
                flow.assign(y, x)
            return y

        of_ret = Foo().get()
        test_case.assertEqual(of_ret.numpy().shape, (2, 5))

    def test_worker_to_worker_communication(test_case):
        flow.config.gpu_device_num(4)
        func_config = flow.FunctionConfig()
        func_config.concurrency_width(1)

        @flow.global_function()
        def Foo():
            with flow.scope.placement("gpu", "0:1"):
                x = flow.get_variable(
                    "x",
                    shape=(2, 5),
                    dtype=flow.float,
                    initializer=flow.random_uniform_initializer(minval=0, maxval=1),
                    trainable=False,
                )
            with flow.scope.placement("gpu", "0:2"):
                y = flow.get_variable(
                    "y",
                    shape=(2, 5),
                    dtype=flow.float,
                    initializer=flow.constant_initializer(0),
                    trainable=False,
                )
                flow.assign(y, x)
            return y

        of_ret = Foo().get()
        test_case.assertEqual(of_ret.numpy().shape, (2, 5))


if __name__ == "__main__":
    unittest.main()
