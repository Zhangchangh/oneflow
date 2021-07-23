from typing import Optional

import oneflow as flow
from oneflow.framework.tensor import Tensor, register_tensor_op
from oneflow.nn.module import Module
from oneflow.ops.array_ops import check_slice_tup_list


class Chunk(Module):
    def __init__(self) -> None:
        super().__init__()

    def forward(self, input, chunks, dim):
        if dim is not None:
            assert input.shape[dim] > 0, "chunk expects at least a 1-dimensional tensor"
            assert chunks > 0, "chunk expects `chunks` to be greater than 0"
            channel = input.dim()
            dim_size = input.shape[dim]
            chunk_size = (
                dim_size / chunks if dim_size % chunks == 0 else int(dim_size / chunks)
            )
            last_chunk_size = (
                dim_size / chunks
                if dim_size % chunks == 0
                else dim_size - chunk_size * (chunks - 1)
            )
            chunk_dim_dict = {}
            tup_ndim = []
            splits = []
            for chunk in range(0, chunks):
                if dim_size % chunks == 0:
                    start = chunk * chunk_size
                    stop = (chunk + 1) * chunk_size
                else:
                    start = (
                        chunk * chunk_size
                        if chunk < chunks - 1
                        else chunk_size * (chunks - 1)
                    )
                    stop = (chunk + 1) * chunk_size if chunk < chunks - 1 else dim_size
                step = 1
                chunk_dim_dict.setdefault(dim, []).append(
                    [int(start), int(stop), int(step)]
                )
            for (k, v) in chunk_dim_dict.items():
                for v_chunk in v:
                    tup_list = []
                    for i in range(0, channel):
                        if i != dim:
                            tup_list.append([None, None, None])
                        else:
                            tup_list.append(v_chunk)
                    (start_tup, stop_tup, step_tup) = check_slice_tup_list(
                        tup_list, input.shape
                    )
                    splits.append(
                        flow.F.slice(
                            input, start=start_tup, stop=stop_tup, step=step_tup
                        )
                    )
            return splits


@register_tensor_op("chunk")
def chunk_op(input, chunks, dim):
    """Splits a tensor into a specific number of chunks. Each chunk is a view of the input tensor. Last chunk will be smaller if the tensor size along the given dimension dim is not divisible by chunks.

    Args:
        input (oneflow.Tensor): The tensor to split.
        chunks (int): Number of chunks to return.
        dim (int): Dimension along which to split the tensor.

    Returns:
        List of Tensors.

    For example:

    .. code-block:: python
    
        >>> import oneflow as flow
        >>> import numpy as np
               
        >>> np_arr = np.random.randn(5, 3, 6, 9).astype(np.float32)
        >>> input = flow.Tensor(np_arr)
        >>> of_out = []
        >>> of_out = flow.chunk(input, chunks=3, dim=2)
        >>> chunks = 3
        >>> of_out_shape = []
        >>> for i in range(0, chunks):
        ...     of_out_shape.append(of_out[i].numpy().shape)
        >>> of_out_shape
        [(5, 3, 2, 9), (5, 3, 2, 9), (5, 3, 2, 9)]

        >>> np_arr = np.random.randn(5, 3, 6, 9).astype(np.float32)
        >>> input = flow.Tensor(np_arr)
        >>> of_out = []
        >>> of_out = flow.chunk(input, chunks=4, dim=3)
        >>> chunks = 4
        >>> of_out_shape = []
        >>> for i in range(0, chunks):
        ...     of_out_shape.append(of_out[i].numpy().shape)
        >>> of_out_shape
        [(5, 3, 6, 2), (5, 3, 6, 2), (5, 3, 6, 2), (5, 3, 6, 3)]

    """
    return Chunk()(input, chunks, dim)


if __name__ == "__main__":
    import doctest

    doctest.testmod(raise_on_error=True)
