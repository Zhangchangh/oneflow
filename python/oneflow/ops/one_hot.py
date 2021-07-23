import os
from typing import Optional, Union

import oneflow as flow
import oneflow._oneflow_internal
import oneflow.core.operator.op_conf_pb2 as op_conf_util
import oneflow.core.register.logical_blob_id_pb2 as logical_blob_id_util
import oneflow.framework.distribute as distribute_util
import oneflow.framework.id_util as id_util
import oneflow.framework.remote_blob as remote_blob_util


def one_hot(
    indices: oneflow._oneflow_internal.BlobDesc,
    depth: int,
    on_value: Union[int, float] = 1,
    off_value: Union[int, float] = 0,
    axis: int = -1,
    dtype: Optional[flow.dtype] = None,
    name: Optional[str] = None,
) -> oneflow._oneflow_internal.BlobDesc:
    """This operator generates a onehot Blob from input Blob.

    If input Blob's rank is `N`, the corresponding onehot Blob's rank is `N+1`. The new axis is generated on the specified dimension according to the parameter `axis`.

    The locations represented by `indices` take value `on_value`, while other locations take `off_value`

    Args:
        indices (oneflow._oneflow_internal.BlobDesc): The input Blob.
        depth (int): The length of onehot Blob.
        on_value (Union[int, float], optional): The fill value when `indices[i] == i`. Defaults to 1.
        off_value (Union[int, float], optional): The fill value when `indice[i] != i`. Defaults to 0.
        axis (int, optional): The specified dimension that the new axis is generated on. Defaults to -1.
        dtype (Optional[flow.dtype], optional): The output data type, it can be "oneflow.int32", "oneflow.int64", "oneflow.float", "oneflow.double". Defaults to None.
        name (Optional[str], optional): The name for the operation. Defaults to None.

    Note:

        The data type of input blob should be `int32` or `int64`

    For example:

    Example 1:

    .. code-block:: python

        import oneflow as flow
        import oneflow.typing as tp
        import numpy as np


        @flow.global_function()
        def onehot_Job(x: tp.Numpy.Placeholder((4, ), dtype=flow.int32)
        ) -> tp.Numpy:
            return flow.one_hot(indices=x,
                                depth=5,
                                axis=-1,
                                dtype=flow.int32)


        x = np.array([0, 3, 1, 2]).astype(np.int32)
        out = onehot_Job(x)

        # out [[1 0 0 0 0]
        #      [0 0 0 1 0]
        #      [0 1 0 0 0]
        #      [0 0 1 0 0]]

    Example 2:

    .. code-block:: python

        import oneflow as flow
        import oneflow.typing as tp
        import numpy as np


        @flow.global_function()
        def onehot_Job(x: tp.Numpy.Placeholder((4, ), dtype=flow.int32)
        ) -> tp.Numpy:
            return flow.one_hot(indices=x,
                                depth=5,
                                axis=0,
                                dtype=flow.int32)


        x = np.array([0, 3, 1, 2]).astype(np.int32)
        out = onehot_Job(x)

        # out [[1 0 0 0]
        #      [0 0 1 0]
        #      [0 0 0 1]
        #      [0 1 0 0]
        #      [0 0 0 0]]

    Returns:
        oneflow._oneflow_internal.BlobDesc: [description]
    """
    out_ndims = len(indices.shape) + 1
    if axis < 0:
        axis += out_ndims
    assert axis >= 0 and axis < out_ndims, ValueError(
        "Expected axis to between [%d, %d).  But received: %d "
        % (-out_ndims, out_ndims, axis)
    )
    out = (
        flow.user_op_builder(name if name is not None else id_util.UniqueStr("OneHot_"))
        .Op("one_hot")
        .Input("indices", [indices])
        .Attr("depth", int(depth))
        .Attr("floating_on_value", float(on_value))
        .Attr("integer_on_value", int(on_value))
        .Attr("floating_off_value", float(off_value))
        .Attr("integer_off_value", int(off_value))
        .Attr("dtype", dtype)
        .Output("out")
        .Build()
        .InferAndTryRun()
        .RemoteBlobList()[0]
    )
    if axis != out_ndims - 1:
        dim_list = list(range(0, out_ndims))
        dim_list.insert(axis, out_ndims - 1)
        dim_list.pop()
        return flow.transpose(out, dim_list)
    else:
        return out
