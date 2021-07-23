import numpy as np
import oneflow.core.common.data_type_pb2 as data_type_pb2
import oneflow
import oneflow._oneflow_internal
_dtypes = [oneflow.char, oneflow.float, oneflow.float32, oneflow.double, oneflow.float64, oneflow.float16, oneflow.int8, oneflow.int32, oneflow.int64, oneflow.uint8, oneflow.record, oneflow.tensor_buffer]

def dtypes():
    return _dtypes

def convert_proto_dtype_to_oneflow_dtype(proto_dtype):
    return oneflow._oneflow_internal.deprecated.GetDTypeByDataType(proto_dtype)
_ONEFLOW_DTYPE_TO_NUMPY_DTYPE = {oneflow.char: np.byte, oneflow.float: np.float32, oneflow.float16: np.float16, oneflow.float32: np.float32, oneflow.float64: np.double, oneflow.double: np.double, oneflow.int8: np.int8, oneflow.int32: np.int32, oneflow.int64: np.int64, oneflow.uint8: np.uint8}

def convert_oneflow_dtype_to_numpy_dtype(oneflow_dtype: oneflow.dtype):
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