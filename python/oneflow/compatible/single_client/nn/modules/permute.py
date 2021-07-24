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
from typing import Optional, Sequence

from oneflow.compatible import single_client as flow
from oneflow.compatible.single_client.python.framework.tensor import register_tensor_op
from oneflow.compatible.single_client.python.nn.module import Module


class Permute(Module):
    def __init__(self, *dims) -> None:
        super().__init__()
        self.perm = list(*dims)

    def forward(self, x):
        assert len(self.perm) == len(x.shape)
        new_perm = []
        for dim in self.perm:
            if dim < 0:
                dim += len(self.perm)
            assert dim >= 0 and dim < len(
                x.shape
            ), "Invalid dim0 {}, len(shape): {}".format(dim, len(x.shape))
            new_perm.append(dim)
        return flow.F.transpose(x, perm=new_perm)


if __name__ == "__main__":
    import doctest

    doctest.testmod(raise_on_error=True)
