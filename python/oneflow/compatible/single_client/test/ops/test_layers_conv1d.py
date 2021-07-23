import unittest
import os
from collections import OrderedDict
import numpy as np
from oneflow.compatible import single_client as flow
import tensorflow as tf
import test_global_storage
from test_util import GenArgList
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

def grouped_convolution1D(inputs, filters, padding, num_groups, strides=None, dilation_rate=None):
    input_list = tf.split(inputs, num_groups, axis=-1)
    filter_list = tf.split(filters, num_groups, axis=-1)
    output_list = []
    for (conv_idx, (input_tensor, filter_tensor)) in enumerate(zip(input_list, filter_list)):
        output_list.append(tf.nn.conv1d(input_tensor, filter_tensor, padding='VALID', stride=[1, 1, 1], data_format='NWC'))
    outputs = tf.concat(output_list, axis=-1)
    return outputs

def compare_with_tensorflow(test_case, device_type, x_shape, filters, kernel_size, groups):
    assert device_type in ['gpu', 'cpu']
    flow.clear_default_session()
    func_config = flow.FunctionConfig()
    func_config.default_data_type(flow.float)

    @flow.global_function(type='train', function_config=func_config)
    def ConvJob():
        with flow.scope.placement(device_type, '0:0'):
            x = flow.get_variable('x', shape=x_shape, dtype=flow.float, initializer=flow.random_uniform_initializer(minval=0, maxval=100), trainable=True)
            loss = flow.layers.conv1d(x, filters, kernel_size=kernel_size, strides=[1], padding='valid', data_format='NCW', dilation_rate=1, groups=groups, use_bias=False, kernel_initializer=flow.random_uniform_initializer(minval=0, maxval=100), weight_name='conv1d_weight')
            weight_shape = (filters, x.shape[1] // groups, kernel_size)
            weight = flow.get_variable(name='conv1d_weight', shape=weight_shape, dtype=flow.float, initializer=flow.random_uniform_initializer(minval=0, maxval=100))
            flow.optimizer.SGD(flow.optimizer.PiecewiseConstantScheduler([], [0.0001]), momentum=0).minimize(loss)
            flow.watch(x, test_global_storage.Setter('x'))
            flow.watch_diff(x, test_global_storage.Setter('x_diff'))
            flow.watch(weight, test_global_storage.Setter('weight'))
            flow.watch_diff(weight, test_global_storage.Setter('weight_diff'))
            flow.watch(loss, test_global_storage.Setter('loss'))
            flow.watch_diff(loss, test_global_storage.Setter('loss_diff'))
            return loss
    of_out = ConvJob().get()
    with tf.GradientTape(persistent=True) as tape:
        x = tf.Variable(test_global_storage.Get('x').transpose(0, 2, 1))
        assert groups > 0
        assert x_shape[1] % groups == 0
        assert filters % groups == 0
        if groups == 1:
            weight = tf.Variable(test_global_storage.Get('weight').transpose(2, 1, 0))
            tf_out = tf.nn.conv1d(x, weight, stride=[1, 1, 1], padding='VALID', data_format='NWC')
        else:
            weight = tf.Variable(test_global_storage.Get('weight').transpose(2, 1, 0))
            tf_out = grouped_convolution1D(x, weight, padding='VALID', num_groups=groups)
    loss_diff = test_global_storage.Get('loss_diff').transpose(0, 2, 1)
    tf_x_diff = tape.gradient(tf_out, x, loss_diff)
    tf_weight_diff = tape.gradient(tf_out, weight, loss_diff)
    of_out_np = of_out.numpy().transpose(0, 2, 1)
    tf_out_np = tf_out.numpy()
    max_abs_diff = np.max(np.absolute(of_out_np - tf_out_np))
    fail_info = '\nshape (of vs. tf): {} vs. {}\nmax_abs_diff: {}'.format(of_out_np.shape, tf_out_np.shape, max_abs_diff)
    test_case.assertTrue(np.allclose(of_out_np, tf_out_np, rtol=1e-05, atol=1e-05), fail_info)
    of_x_diff_arr = test_global_storage.Get('x_diff').transpose(0, 2, 1)
    tf_x_diff_arr = tf_x_diff.numpy()
    max_abs_diff = np.max(np.abs(of_x_diff_arr - tf_x_diff_arr))
    test_case.assertTrue(np.allclose(of_x_diff_arr, tf_x_diff_arr, rtol=1e-05, atol=0.0001))
    test_case.assertTrue(np.allclose(test_global_storage.Get('weight_diff').transpose(2, 1, 0), tf_weight_diff.numpy(), rtol=1e-05, atol=1e-05))

@flow.unittest.skip_unless_1n1d()
class TestLayersConv1d(flow.unittest.TestCase):

    def test_conv1(test_case):
        arg_dict = OrderedDict()
        arg_dict['device_type'] = ['gpu']
        arg_dict['x_shape'] = [(10, 32, 20)]
        arg_dict['filters'] = [64]
        arg_dict['kernel_size'] = [3]
        arg_dict['groups'] = [32]
        for arg in GenArgList(arg_dict):
            compare_with_tensorflow(test_case, *arg)

    def test_conv2(test_case):
        arg_dict = OrderedDict()
        arg_dict['device_type'] = ['gpu', 'cpu']
        arg_dict['x_shape'] = [(10, 32, 20)]
        arg_dict['filters'] = [32]
        arg_dict['kernel_size'] = [3, 2]
        arg_dict['groups'] = [1]
        for arg in GenArgList(arg_dict):
            compare_with_tensorflow(test_case, *arg)
if __name__ == '__main__':
    unittest.main()