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
import os
import unittest

import numpy as np

import oneflow
import oneflow as flow
import oneflow._oneflow_internal
import oneflow.framework.c_api_util as c_api_util
import oneflow.framework.session_context as session_ctx
from oneflow.framework.multi_client_session import MultiClientSession


@flow.unittest.skip_unless_1n1d()
class TestFeedVariableTensor(unittest.TestCase):
    def test_feed_var_tensor(test_case):
        test_case.assertTrue(oneflow.distributed.is_multi_client())
        test_case.assertTrue(
            oneflow.python.framework.env_util.HasAllMultiClientEnvVars()
        )
        x = flow.Tensor(1, 1, 10, 10)
        flow.nn.init.uniform_(x, a=-1.0, b=1.0)
        session = session_ctx.GetDefaultSession()
        test_case.assertTrue(isinstance(session, MultiClientSession))
        session.TryInit()
        with oneflow._oneflow_internal.lazy_mode.gard(True):
            oneflow._oneflow_internal.JobBuildAndInferCtx_Open(
                "cc_test_variable_op_expr_job"
            )
            job_conf = (
                oneflow._oneflow_internal.oneflow.core.job.job_conf.JobConfigProto()
            )
            job_conf.set_job_name("cc_test_variable_op_expr_job")
            job_conf.mutable_predict_conf()
            c_api_util.CurJobBuildAndInferCtx_SetJobConf(job_conf)
            op_name = "cc_Variable_0"
            var_conf = (
                oneflow._oneflow_internal.oneflow.core.operator.op_conf.FeedVariableOpConf()
            )
            var_conf.set_in_0("EagerTensorInput")
            var_conf.set_out_0("out_0")
            var_op = oneflow._oneflow_internal.one.FeedVariableOpExpr(
                op_name, var_conf, ["in_0"], ["out_0"]
            )
            attrs = oneflow._oneflow_internal.MutableCfgAttrMap()
            if not x.is_determined:
                x.determine()
            x_tensor_in_c = x._local_or_consistent_tensor
            out_tensor = var_op.apply([x_tensor_in_c], attrs)[0]
            test_case.assertEqual(out_tensor.shape, (1, 1, 10, 10))
            test_case.assertTrue(out_tensor.is_lazy)
            test_case.assertTrue(out_tensor.is_local)
            oneflow._oneflow_internal.JobBuildAndInferCtx_Close()


if __name__ == "__main__":
    unittest.main()
