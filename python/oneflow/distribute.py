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
from oneflow.framework.distribute import assert_is_valid_distribute, auto, broadcast
from oneflow.framework.distribute import (
    deprecated_consistent_strategy as consistent_strategy,
)
from oneflow.framework.distribute import (
    deprecated_consistent_strategy_enabled as consistent_strategy_enabled,
)
from oneflow.framework.distribute import (
    deprecated_mirrored_strategy as mirrored_strategy,
)
from oneflow.framework.distribute import (
    deprecated_mirrored_strategy_enabled as mirrored_strategy_enabled,
)
from oneflow.framework.distribute import split
