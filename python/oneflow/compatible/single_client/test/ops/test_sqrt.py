import os
import unittest
from collections import OrderedDict

import numpy as np
import tensorflow as tf
from test_util import CompareOpWithTensorFlow, GenArgDict

from oneflow.compatible import single_client as flow

gpus = tf.config.experimental.list_physical_devices("GPU")
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)


@flow.unittest.skip_unless_1n1d()
class TestSqrt(flow.unittest.TestCase):
    def test_sqrt(test_case):
        arg_dict = OrderedDict()
        arg_dict["device_type"] = ["gpu"]
        arg_dict["flow_op"] = [flow.math.sqrt]
        arg_dict["tf_op"] = [tf.math.sqrt]
        arg_dict["input_shape"] = [(10, 20, 30)]
        arg_dict["input_minval"] = [0]
        arg_dict["input_maxval"] = [100]
        for arg in GenArgDict(arg_dict):
            CompareOpWithTensorFlow(**arg)


if __name__ == "__main__":
    unittest.main()
