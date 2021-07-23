from typing import Union

import oneflow as flow
from oneflow.nn.module import Module


class ZeroPad2d(Module):
    """The interface is consistent with PyTorch.
    The documentation is referenced from:
    https://pytorch.org/docs/stable/generated/torch.nn.ZeroPad2d.html

    Pads the input tensor boundaries with zero. User can set the amount of padding by setting the parameter `paddings`.

    Args:
        padding (Union[int, tuple]):  the size of the padding. If is `int`, uses the same padding in all boundaries. If a 4-`tuple`, uses (:math:`\\mathrm{padding_{left}}`, :math:`\\mathrm{padding_{right}}`, :math:`\\mathrm{padding_{top}}`, :math:`\\mathrm{padding_{bottom}}`)

    Shape:
        - Input: :math:`(N, C, H_{in}, W_{in})`
        - Output: :math:`(N, C, H_{out}, W_{out})` where

            :math:`H_{out} = H_{in} + \\mathrm{padding_{top}} + \\mathrm{padding_{bottom}}`

            :math:`W_{out} = W_{in} + \\mathrm{padding_{left}} + \\mathrm{padding_{right}}`

    For example:

    .. code-block:: python

        >>> import oneflow as flow
        >>> import numpy as np
        >>> zeropad_layer_int = flow.nn.ZeroPad2d(2)
        >>> zeropad_layer_tuple = flow.nn.ZeroPad2d((1,2,2,0))
        >>> input = flow.Tensor(np.arange(18).reshape((1, 2, 3, 3)).astype(np.float32))
        >>> output_int = zeropad_layer_int(input)
        >>> output_int.shape
        flow.Size([1, 2, 7, 7])
        >>> output_int
        tensor([[[[ 0.,  0.,  0.,  0.,  0.,  0.,  0.],
                  [ 0.,  0.,  0.,  0.,  0.,  0.,  0.],
                  [ 0.,  0.,  0.,  1.,  2.,  0.,  0.],
                  [ 0.,  0.,  3.,  4.,  5.,  0.,  0.],
                  [ 0.,  0.,  6.,  7.,  8.,  0.,  0.],
                  [ 0.,  0.,  0.,  0.,  0.,  0.,  0.],
                  [ 0.,  0.,  0.,  0.,  0.,  0.,  0.]],
        <BLANKLINE>
                 [[ 0.,  0.,  0.,  0.,  0.,  0.,  0.],
                  [ 0.,  0.,  0.,  0.,  0.,  0.,  0.],
                  [ 0.,  0.,  9., 10., 11.,  0.,  0.],
                  [ 0.,  0., 12., 13., 14.,  0.,  0.],
                  [ 0.,  0., 15., 16., 17.,  0.,  0.],
                  [ 0.,  0.,  0.,  0.,  0.,  0.,  0.],
                  [ 0.,  0.,  0.,  0.,  0.,  0.,  0.]]]], dtype=oneflow.float32)
        >>> output_tuple = zeropad_layer_tuple(input)
        >>> output_tuple
        tensor([[[[ 0.,  0.,  0.,  0.,  0.,  0.],
                  [ 0.,  0.,  0.,  0.,  0.,  0.],
                  [ 0.,  0.,  1.,  2.,  0.,  0.],
                  [ 0.,  3.,  4.,  5.,  0.,  0.],
                  [ 0.,  6.,  7.,  8.,  0.,  0.]],
        <BLANKLINE>
                 [[ 0.,  0.,  0.,  0.,  0.,  0.],
                  [ 0.,  0.,  0.,  0.,  0.,  0.],
                  [ 0.,  9., 10., 11.,  0.,  0.],
                  [ 0., 12., 13., 14.,  0.,  0.],
                  [ 0., 15., 16., 17.,  0.,  0.]]]], dtype=oneflow.float32)
    """

    def __init__(self, padding: Union[int, tuple]):
        super().__init__()
        if isinstance(padding, tuple):
            assert len(padding) == 4, ValueError("Length of padding must be 4")
            boundary = [padding[0], padding[1], padding[2], padding[3]]
        elif isinstance(padding, int):
            boundary = [padding, padding, padding, padding]
        else:
            raise ValueError("padding must be int  or tuple!")
        self.padding = boundary
        self.value = 0.0

    def forward(self, x):
        (_, _, h, w) = x.shape
        if x.dtype in [flow.float32, flow.float16, flow.float64]:
            floating_value = float(self.value)
            integral_value = int(0)
        else:
            floating_value = float(0)
            integral_value = int(self.value)
        self._op = (
            flow.builtin_op("constant_pad2d")
            .Input("x")
            .Output("y")
            .Attr("padding", self.padding)
            .Attr("floating_value", floating_value)
            .Attr("integral_value", integral_value)
            .Build()
        )
        res = self._op(x)[0]
        return res


if __name__ == "__main__":
    import doctest

    doctest.testmod(raise_on_error=True)
