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
import oneflow._oneflow_internal
import oneflow.eager.eager_blob_util as eager_blob_util
import oneflow.framework.blob_trait as blob_trait
import oneflow.framework.functional as functional
import oneflow.framework.generator as generator
import oneflow.framework.op_expr_util as op_expr_util
import oneflow.framework.remote_blob as remote_blob_util


def RegisterMethod4Class():
    op_expr_util.RegisterMethod4UserOpExpr()
    functional.RegisterFunctionalApis()
    eager_blob_util.RegisterMethod4EagerPhysicalBlob()
    blob_trait.RegisterBlobOperatorTraitMethod(
        oneflow._oneflow_internal.EagerPhysicalBlob
    )
    blob_trait.RegisterBlobOperatorTraitMethod(oneflow._oneflow_internal.ConsistentBlob)
    blob_trait.RegisterBlobOperatorTraitMethod(oneflow._oneflow_internal.MirroredBlob)
    remote_blob_util.RegisterMethod4EagerBlobTrait()
    remote_blob_util.RegisterMethod4LazyConsistentBlob()
    remote_blob_util.RegisterMethod4LazyMirroredBlob()
    remote_blob_util.RegisterMethod4EagerConsistentBlob()
