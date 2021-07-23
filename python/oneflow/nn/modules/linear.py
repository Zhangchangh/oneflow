import math

import oneflow as flow
from oneflow.framework.tensor import Tensor
from oneflow.nn.init import _calculate_fan_in_and_fan_out
from oneflow.nn.module import Module


class Identity(Module):
    """A placeholder identity operator that is argument-insensitive.

    Args:
        args: any argument (unused)
        kwargs: any keyword argument (unused)

    For example:

    .. code-block:: python

        import numpy as np
        import oneflow as flow

        m = flow.nn.Identity()
        input = flow.Tensor(np.random.rand(2, 3, 4, 5))

        output = m(input)

        # output = input

    """

    def __init__(self, *args, **kwargs):
        super().__init__()

    def forward(self, input: Tensor) -> Tensor:
        return input


class Linear(Module):
    """Applies a linear transformation to the incoming data: :math:`y = xA^T + b`

    Args:

        - in_features: size of each input sample

        - out_features: size of each output sample

        - bias: If set to ``False``, the layer will not learn an additive bias. Default: ``True``

    Shape:
        - Input: :math:`(N, *, H_{in})` where :math:`*` means any number of
          additional dimensions and :math:`H_{in} = {in\\_features}`

        - Output: :math:`(N, *, H_{out})` where all but the last dimension
          are the same shape as the input and :math:`H_{out} = {out\\_features}`.

    Attr:
        - :attr:`weight`: the learnable weights of the module of shape :math:`({out\\_features}, {in\\_features})`. The values are initialized from :math:`\\mathcal{U}(-\\sqrt{k}, \\sqrt{k})`, where :math:`(k = 1 / {in\\_features})`

        - :attr:`bias`: the learnable bias of the module of shape :math:`({out\\_features})`. If :attr:`bias` is ``True``, the values are initialized from :math:`\\mathcal{U}(-\\sqrt{k}, \\sqrt{k})` where :math:`(k = 1 / {in\\_features})`


    For example:

    .. code-block:: python

        >>> import numpy as np
        >>> import oneflow as flow
        

        >>> m = flow.nn.Linear(20, 30, False)
        >>> input = flow.Tensor(np.random.randn(128, 20))
        >>> output = m(input)
        >>> output.size()
        flow.Size([128, 30])

    """

    def __init__(self, in_features: int, out_features: int, bias: bool = True) -> None:
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.use_bias = bias
        self.weight = flow.nn.Parameter(flow.Tensor(out_features, in_features))
        self.bias = None
        if bias:
            self.bias = flow.nn.Parameter(flow.Tensor(out_features))
        self.reset_parameters()

    def reset_parameters(self) -> None:
        flow.nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5))
        if self.bias is not None:
            (fan_in, _) = _calculate_fan_in_and_fan_out(self.weight)
            bound = 1 / math.sqrt(fan_in)
            flow.nn.init.uniform_(self.bias, -bound, bound)

    def forward(self, x):
        assert len(x.shape) >= 2, "Tensor x's dim should >=2"
        if len(x.shape) == 2:
            res = flow.F.matmul(x, self.weight, transpose_a=False, transpose_b=True)
        else:
            res = flow.F.broadcast_matmul(
                x, self.weight, transpose_a=False, transpose_b=True
            )
        if self.use_bias:
            res += self.bias
        return res

    def extra_repr(self) -> str:
        return "in_features={}, out_features={}, bias={}".format(
            self.in_features, self.out_features, self.bias is not None
        )


if __name__ == "__main__":
    import doctest

    doctest.testmod(raise_on_error=True)
