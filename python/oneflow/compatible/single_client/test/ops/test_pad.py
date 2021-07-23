import unittest
import os
from collections import OrderedDict
import numpy as np
from oneflow.compatible import single_client as flow
import tensorflow as tf
from test_util import Args, CompareOpWithTensorFlow, GenArgDict

@flow.unittest.skip_unless_1n4d()
class TestPad(flow.unittest.TestCase):

    def test_pad(test_case):
        arg_dict = OrderedDict()
        arg_dict['device_type'] = ['cpu', 'gpu']
        arg_dict['flow_op'] = [flow.pad]
        arg_dict['tf_op'] = [tf.pad]
        arg_dict['input_shape'] = [(2, 2, 1, 3), (1, 1, 2, 3)]
        arg_dict['op_args'] = [Args([([1, 2], [0, 0], [1, 2], [1, 1])], tf.constant([([1, 2], [0, 0], [1, 2], [1, 1])])), Args([([0, 0], [30, 0], [0, 1], [1, 0]), 99999999999999999999999999999999], [tf.constant(([0, 0], [30, 0], [0, 1], [1, 0])), 'constant', 99999999999999999999999999999999]), Args([([10, 0], [0, 0], [10, 20], [0, 0])], tf.constant([([10, 0], [0, 0], [10, 20], [0, 0])]))]
        for arg in GenArgDict(arg_dict):
            CompareOpWithTensorFlow(**arg)

    def test_pad_5d(test_case):
        arg_dict = OrderedDict()
        arg_dict['device_type'] = ['cpu', 'gpu']
        arg_dict['flow_op'] = [flow.pad]
        arg_dict['tf_op'] = [tf.pad]
        arg_dict['input_shape'] = [(2, 2, 1, 3, 1), (1, 1, 2, 3, 1)]
        arg_dict['op_args'] = [Args([([1, 2], [3, 4], [5, 6], [7, 8], [9, 10])], tf.constant([([1, 2], [3, 4], [5, 6], [7, 8], [9, 10])])), Args([([1, 1], [2, 2], [3, 3], [4, 4], [5, 5])], tf.constant([([1, 1], [2, 2], [3, 3], [4, 4], [5, 5])])), Args([([0, 0], [0, 0], [10, 20], [0, 0], [3, 2])], tf.constant([([0, 0], [0, 0], [10, 20], [0, 0], [3, 2])]))]
        for arg in GenArgDict(arg_dict):
            CompareOpWithTensorFlow(**arg)
if __name__ == '__main__':
    unittest.main()