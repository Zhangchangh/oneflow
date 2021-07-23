import numpy as np
from oneflow.compatible.single_client.core.common import data_type_pb2 as data_type_pb2
from oneflow.compatible import single_client as flow
import oneflow._oneflow_internal

_dtypes = [
    flow.char,
    flow.float,
    flow.float32,
    flow.double,
    flow.float64,
    flow.float16,
    flow.int8,
    flow.int32,
    flow.int64,
    flow.uint8,
    flow.record,
    flow.tensor_buffer,
]


def dtypes():
    return _dtypes


def convert_proto_dtype_to_oneflow_dtype(proto_dtype):
    return oneflow._oneflow_internal.deprecated.GetDTypeByDataType(proto_dtype)


_ONEFLOW_DTYPE_TO_NUMPY_DTYPE = {
    flow.char: np.byte,
    flow.float: np.float32,
    flow.float16: np.float16,
    flow.float32: np.float32,
    flow.float64: np.double,
    flow.double: np.double,
    flow.int8: np.int8,
    flow.int32: np.int32,
    flow.int64: np.int64,
    flow.uint8: np.uint8,
}


def convert_oneflow_dtype_to_numpy_dtype(oneflow_dtype: flow.dtype):
    if oneflow_dtype not in _ONEFLOW_DTYPE_TO_NUMPY_DTYPE:
        raise NotImplementedError
    return _ONEFLOW_DTYPE_TO_NUMPY_DTYPE[oneflow_dtype]


def convert_numpy_dtype_to_oneflow_dtype(numpy_dtype: np.dtype):
    for (k, v) in _ONEFLOW_DTYPE_TO_NUMPY_DTYPE.items():
        if v == numpy_dtype:
            return k
    raise NotImplementedError


del data_type_pb2
del np
