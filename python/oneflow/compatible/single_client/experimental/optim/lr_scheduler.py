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
from oneflow.compatible.single_client.nn.optimizer.cosine_annealing_lr import (
    CosineAnnealingLR,
)
from oneflow.compatible.single_client.nn.optimizer.lambda_lr import LambdaLR
from oneflow.compatible.single_client.nn.optimizer.lr_scheduler import (
    LrScheduler as _LRScheduler,
)
from oneflow.compatible.single_client.nn.optimizer.step_lr import StepLR
