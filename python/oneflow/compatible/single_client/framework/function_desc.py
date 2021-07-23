from oneflow.compatible.single_client.python.framework import (
    session_context as session_ctx,
)
from oneflow.compatible.single_client.python.framework import hob as hob
from oneflow.compatible.single_client.python.lib.core import enable_if as enable_if
from oneflow.compatible.single_client.python.framework import (
    session_context as session_ctx,
)
from oneflow._oneflow_internal.oneflow.core.job import job_conf as job_conf_cfg
import oneflow._oneflow_internal


class FunctionAttribute(object):
    def __init__(self):
        self.default_placement_scope = None
        self.default_distribute_strategy = None
        self.allow_cpu_return_op = True


class FunctionDesc(object):
    def __init__(self, job_func=None, job_config_proto=None, function_attribute=None):
        if job_config_proto is None:
            job_config_proto = job_conf_cfg.JobConfigProto()
        if function_attribute is None:
            function_attribute = FunctionAttribute()
        self.job_func = job_func
        self.job_config_proto = job_config_proto
        self.job_config_proto.mutable_predict_conf()
        self.function_attribute = function_attribute

    def IsTrainable(self):
        if self.job_config_proto.has_train_conf():
            return True
        if self.job_config_proto.has_predict_conf():
            return False
        raise NotImplementedError

    def HasAttr(self, attr_name):
        if attr_name == "flag_name2flag_value":
            return False
        name2default = session_ctx.GetDefaultSession().function_flag_name2default_val
        if attr_name in self.job_config_proto.flag_name2flag_value():
            return True
        return getattr(self.job_config_proto, "has_" + attr_name)()

    def __getattr__(self, attr_name):
        assert attr_name != "flag_name2flag_value"
        flag_name2flag_value = self.job_config_proto.flag_name2flag_value()
        name2default = session_ctx.GetDefaultSession().function_flag_name2default_val
        if attr_name not in name2default:
            assert getattr(self.job_config_proto, "has_" + attr_name)()
            return getattr(self.job_config_proto, attr_name)()
        attr_value = name2default[attr_name]
        if attr_name in flag_name2flag_value:
            attr_value = flag_name2flag_value[attr_name]
        if attr_value.HasField("at_bool"):
            return attr_value.at_bool
        elif attr_value.HasField("at_int64"):
            return attr_value.at_int64
        elif attr_value.HasField("at_double"):
            return attr_value.at_double
        elif attr_value.HasField("at_string"):
            return attr_value.at_string
        else:
            raise NotImplementedError()


@enable_if.condition(hob.in_global_mode & hob.eager_execution_enabled)
def GetCurrentEagerGlobalFunctionDesc():
    sess = session_ctx.GetDefaultSession()
    ret = sess.CurrentEagerGlobalFunctionDesc()
    assert ret is not None
    return ret


@enable_if.condition(hob.in_global_mode & ~hob.eager_execution_enabled)
def GetCurrentLazyGlobalFunctionDesc():
    sess = session_ctx.GetDefaultSession()
    job_name = oneflow._oneflow_internal.JobBuildAndInferCtx_GetCurrentJobName()
    ret = sess.GetLazyFunctionDesc(job_name)
    assert ret is not None
    return ret


def api_current_global_function_desc() -> FunctionDesc:
    api_func = enable_if.unique(
        [GetCurrentLazyGlobalFunctionDesc, GetCurrentEagerGlobalFunctionDesc]
    )
    return api_func()
