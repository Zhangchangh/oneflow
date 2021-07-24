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
from oneflow.compatible import single_client as flow
from oneflow.compatible.single_client.python.framework.tensor import register_tensor_op
from oneflow.compatible.single_client.python.nn.module import Module


class Atan2(Module):
    def __init__(self) -> None:
        super().__init__()
        self.atan2_op = (
            flow.builtin_op("atan2").Input("x").Input("y").Output("z").Build()
        )

    def forward(self, x, y):
        return self.atan2_op(x, y)[0]


if __name__ == "__main__":
    import doctest

    doctest.testmod(raise_on_error=True)
