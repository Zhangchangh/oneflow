"""
Copyright 2020 The OneFlow Authors. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from typing import Optional

from oneflow.python.framework.tensor import Tensor
from oneflow.python.oneflow_export import oneflow_export
from oneflow.python.nn.module import Module


@oneflow_export("nn.PixelShuffle")
class PixelShufflev2(Module):
    r"""
    Part of the documentation is referenced from:
    https://pytorch.org/docs/stable/generated/torch.nn.PixelShuffle.html#torch.nn.PixelShuffle

    Rearranges elements in a tensor of shape :math:`(*, C \times r_h \times r_w, H, W)`
    to a tensor of shape :math:`(*, C, H \times r_h, W \times r_w)`, where r_h and r_w are upscale factors.

    This is useful for implementing efficient sub-pixel convolution
    with a stride of :math:`1/r`.

    See the paper:
    `Real-Time Single Image and Video Super-Resolution Using an Efficient Sub-Pixel Convolutional Neural Network`_
    by Shi et. al (2016) for more details.

    Args:
        upscale_factor (int, optional): factor to increase spatial resolution by, only use when factors of height and width spatial are the same.

        h_upscale_factor (int, optional): factor to increase height spatial resolution by, only one of h_upscale_factor and upscale_factor can be used.
        w_upscale_factor (int, optional): factor to increase width spatial resolution by, only one of w_upscale_factor and upscale_factor can be used.

    Shape:
        - Input: :math:`(*, C_{in}, H_{in}, W_{in})`, where * is zero or more batch dimensions
        - Output: :math:`(*, C_{out}, H_{out}, W_{out})`, where

    if use upscale_factor:

    .. math::
        C_{out} = C_{in} \div \text{h_upscale_factor}^2

        H_{out} = H_{in} \times \text{upscale_factor}

        W_{out} = W_{in} \times \text{upscale_factor}

    if use h_upscale_factor and w_upscale_factor:

    .. math::
        C_{out} = C_{in} \div \text{h_upscale_factor} \div \text{w_upscale_factor}

        H_{out} = H_{in} \times \text{h_upscale_factor}

        W_{out} = W_{in} \times \text{w_upscale_factor}

    For example:

    .. code-block:: python

        >>> import oneflow as flow
        >>> import numpy as np
        >>> m = flow.nn.PixelShuffle(upscale_factor=2)
        >>> x = flow.Tensor(np.random.randn(3, 4, 5, 5))
        >>> y = m(x)
        >>> y.shape
        flow.Size([3, 1, 10, 10])

        >>> m = flow.nn.PixelShuffle(h_upscale_factor=3, w_upscale_factor=4)
        >>> x = flow.Tensor(np.random.randn(1, 24, 2, 2))
        >>> y = m(x)
        >>> y.shape
        flow.Size([1, 2, 6, 8])

    .. _Real-Time Single Image and Video Super-Resolution Using an Efficient Sub-Pixel Convolutional Neural Network:
        https://arxiv.org/abs/1609.05158
    """

    def __init__(
        self,
        upscale_factor: Optional[int] = None,
        h_upscale_factor: Optional[int] = None,
        w_upscale_factor: Optional[int] = None,
    ) -> None:
        super().__init__()

        if upscale_factor is None:
            assert (
                h_upscale_factor is not None and w_upscale_factor is not None
            ), "h_upscale_factor and w_upscale_factor should be None if use upscale_factor"
        else:
            assert (
                h_upscale_factor is None and w_upscale_factor is None
            ), "upscale_factor should be None if use h_upscale_factor and w_upscale_factor"
            h_upscale_factor = upscale_factor
            w_upscale_factor = upscale_factor

        assert (
            h_upscale_factor > 0 and w_upscale_factor > 0
        ), "The scale factor of height and width must larger than zero"
        self.h_upscale_factor = h_upscale_factor
        self.w_upscale_factor = w_upscale_factor

    def forward(self, input: Tensor) -> Tensor:
        assert len(input.shape) == 4, "Only Accept 4D Tensor"

        _batch, _channel, _height, _width = input.shape
        assert (
            _channel % (self.h_upscale_factor * self.w_upscale_factor) == 0
        ), "The channels of input tensor must be divisible by (upscale_factor * upscale_factor) or (h_upscale_factor * w_upscale_factor)"

        _new_c = int(_channel / (self.h_upscale_factor * self.w_upscale_factor))

        out = input.reshape(
            [
                _batch,
                _new_c,
                self.h_upscale_factor * self.w_upscale_factor,
                _height,
                _width,
            ]
        )
        out = out.reshape(
            [
                _batch,
                _new_c,
                self.h_upscale_factor,
                self.w_upscale_factor,
                _height,
                _width,
            ]
        )
        out = out.permute(0, 1, 4, 2, 5, 3)
        out = out.reshape(
            [
                _batch,
                _new_c,
                _height * self.h_upscale_factor,
                _width * self.w_upscale_factor,
            ]
        )

        return out

    def extra_repr(self) -> str:
        return f"w_upscale_factor={self.w_upscale_factor}, h_upscale_factor={self.h_upscale_factor}"


if __name__ == "__main__":
    import doctest

    doctest.testmod(raise_on_error=True)
