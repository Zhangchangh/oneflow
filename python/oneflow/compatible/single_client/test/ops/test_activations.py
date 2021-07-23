import math
import os
import unittest
from collections import OrderedDict

import numpy as np
import tensorflow as tf
import test_global_storage
from test_util import GenArgList

from oneflow.compatible import single_client as flow

gpus = tf.config.experimental.list_physical_devices("GPU")
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)


def compare_with_tensorflow(device_type, activation_type, shape, data_type):
    assert device_type in ["gpu", "cpu"]
    flow.clear_default_session()
    flow.config.enable_debug_mode(True)
    func_config = flow.FunctionConfig()
    if data_type == flow.float16:
        func_config.enable_auto_mixed_precision(True)
        data_type = flow.float
    func_config.default_data_type(data_type)
    of_activation_map = {
        "relu": flow.nn.relu,
        "sigmoid": flow.math.sigmoid,
        "tanh": flow.math.tanh,
    }
    tf_activation_map = {
        "relu": tf.nn.relu,
        "sigmoid": tf.math.sigmoid,
        "tanh": tf.math.tanh,
    }

    @flow.global_function(type="train", function_config=func_config)
    def ActivationJob():
        with flow.scope.placement(device_type, "0:0"):
            x = flow.get_variable(
                "x",
                shape=shape,
                dtype=data_type,
                initializer=flow.random_uniform_initializer(minval=-10, maxval=10),
                trainable=True,
            )
            loss = of_activation_map[activation_type](x)
            lr_scheduler = flow.optimizer.PiecewiseConstantScheduler([], [0.0001])
            flow.optimizer.SGD(lr_scheduler, momentum=0).minimize(loss)
            flow.watch(x, test_global_storage.Setter("x"))
            flow.watch_diff(x, test_global_storage.Setter("x_diff"))
            flow.watch(loss, test_global_storage.Setter("loss"))
            flow.watch_diff(loss, test_global_storage.Setter("loss_diff"))
            return loss

    of_out = ActivationJob().get()
    with tf.GradientTape(persistent=True) as tape:
        x = tf.Variable(test_global_storage.Get("x"))
        tf_out = tf_activation_map[activation_type](x)
    loss_diff = test_global_storage.Get("loss_diff")
    tf_x_diff = tape.gradient(tf_out, x, loss_diff)
    rtol = 1e-05
    atol = 1e-05
    assert np.allclose(of_out.numpy(), tf_out.numpy(), rtol, atol)
    assert np.allclose(test_global_storage.Get("x_diff"), tf_x_diff.numpy(), rtol, atol)


@flow.unittest.skip_unless_1n1d()
class TestActivations(flow.unittest.TestCase):
    def test_activations(test_case):
        arg_dict = OrderedDict()
        arg_dict["device_type"] = ["gpu", "cpu"]
        arg_dict["activation_type"] = ["relu", "sigmoid", "tanh"]
        arg_dict["shape"] = [(64, 64)]
        arg_dict["data_type"] = [flow.float, flow.double]
        for arg in GenArgList(arg_dict):
            compare_with_tensorflow(*arg)
        if os.getenv("ONEFLOW_TEST_CPU_ONLY") is None:
            for act_type in arg_dict["activation_type"]:
                compare_with_tensorflow("gpu", act_type, (64, 64), flow.float16)


if __name__ == "__main__":
    unittest.main()
