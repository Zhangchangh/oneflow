import oneflow as flow
from oneflow.framework.tensor import Tensor
from oneflow.framework.tensor import register_tensor_op
from oneflow.nn.module import Module
from typing import Optional, List, Tuple

class Gather(Module):

    def __init__(self, dim: int=0, sparse_grad: bool=False):
        super().__init__()
        assert sparse_grad is False, 'Only support bool = False for now!'
        self.dim = dim

    def forward(self, input, index):
        assert self.dim < len(index.shape), 'Value of dim is out of range(dim should be less than len(index.shape))'
        assert len(input.shape) == len(index.shape), 'Dimensions of input and index should equal'
        for i in range(0, len(input.shape)):
            if self.dim == i:
                continue
            else:
                assert input.shape[i] == index.shape[i], 'Dimensions of input and index should be same except at dim'
        return flow.F.dim_gather(input, index, dim=self.dim)

@register_tensor_op('gather')
def gather_op(input, index, dim=0, sparse_grad=False):
    """Gathers values along an axis specified by `dim`.

    For a 3-D tensor the output is specified by:

        out[i][j][k] = input[index[i][j][k]][j][k]  # if dim == 0
        out[i][j][k] = input[i][index[i][j][k]][k]  # if dim == 1
        out[i][j][k] = input[i][j][index[i][j][k]]  # if dim == 2

    :attr:`input` and :attr:`index` must have the same number of dimensions.
    It is also required that ``index.size(d) <= input.size(d)`` for all
    dimensions ``d != dim``.  :attr:`out` will have the same shape as :attr:`index`.
    Note that ``input`` and ``index`` do not broadcast against each other.

    Args:
        input (Tensor): the source tensor
        dim (int): the axis along which to index
        index (LongTensor): the indices of elements to gather

    For example:

    .. code-block:: python

        >>> import oneflow as flow
        >>> import numpy as np
        >>> input = np.random.randn(3, 4, 3, 5)
        >>> index = np.random.choice(np.arange(3), size=180, replace=True).reshape((3, 4, 3, 5))
        >>> output = flow.gather(flow.Tensor(input), flow.Tensor(index, dtype=flow.int), dim=1)
        >>> output.shape
        flow.Size([3, 4, 3, 5])

    """
    return Gather(dim, sparse_grad)(input, index)
if __name__ == '__main__':
    import doctest
    doctest.testmod(raise_on_error=True)