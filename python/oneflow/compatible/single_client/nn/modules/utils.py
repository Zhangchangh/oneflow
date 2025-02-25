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
from collections import abc as container_abcs
from itertools import repeat
from typing import List


def _ntuple(n):
    def parse(x):
        if isinstance(x, container_abcs.Iterable):
            return tuple(x)
        return tuple(repeat(x, n))

    return parse


_single = _ntuple(1)
_pair = _ntuple(2)
_triple = _ntuple(3)
_quadruple = _ntuple(4)


def _reverse_repeat_tuple(t, n):
    """Reverse the order of `t` and repeat each element for `n` times.
    This can be used to translate padding arg used by Conv and Pooling modules
    to the ones used by `F.pad`.
    """
    return tuple((x for x in reversed(t) for _ in range(n)))


def _list_with_default(out_size, defaults):
    if isinstance(out_size, int):
        return out_size
    if len(defaults) <= len(out_size):
        raise ValueError(
            "Input dimension should be at least {}".format(len(out_size) + 1)
        )
    return [
        v if v is not None else d
        for (v, d) in zip(out_size, defaults[-len(out_size) :])
    ]


def _check_axis(axis, shape):
    ndim = len(shape)
    if axis is None:
        axis = list(range(len(shape)))
    if isinstance(axis, int):
        axis = [axis]
    assert isinstance(axis, (list, tuple)), "Invalid axis {}".format(axis)
    axis = list(axis)
    for i in range(len(axis)):
        assert (
            -ndim <= axis[i] <= ndim - 1
        ), "Dimension out of range (expected to be in range of [{}, {}], but got {})".format(
            -ndim, ndim - 1, axis[i]
        )
        if axis[i] < 0:
            axis[i] = axis[i] + ndim
    return axis
