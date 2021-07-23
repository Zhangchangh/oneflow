import traceback
from contextlib import contextmanager

from google.protobuf import text_format

import oneflow._oneflow_internal
import oneflow._oneflow_internal.oneflow.core.job.job_conf as job_conf_cfg
import oneflow.core.job.scope_pb2 as scope_pb2_util
import oneflow.framework.attr_util as attr_util
import oneflow.framework.session_context as session_ctx
from oneflow import oneflow_deprecate


def api_scope_config(**kwargs):
    name2default = session_ctx.GetDefaultSession().scope_attr_name2default_val

    def SetScopeProto(scope_proto):
        for (attr_name, py_value) in kwargs.items():
            assert attr_name in name2default
            attr_util.SetAttrValue(
                scope_proto.mutable_attr_name2attr_value()[attr_name],
                py_value,
                name2default[attr_name],
            )

    sess = session_ctx.GetDefaultSession()
    scope = MakeScope(
        lambda old_scope, builder: builder.BuildScopeByProtoSetter(
            old_scope, SetScopeProto
        )
    )
    return ScopeContext(scope)


def api_current_scope():
    """ Return current scope
    """
    return oneflow._oneflow_internal.GetCurrentScope()


from oneflow import oneflow_deprecate


@oneflow_deprecate()
def deprecated_current_scope(*args, **kwargs):
    print(
        "WARNING:",
        "oneflow.scope.current_scope",
        "will be removed in the future, use {} instead.".format(
            "oneflow.current_scope"
        ),
    )
    print(traceback.format_stack()[-2])
    return api_current_scope(*args, **kwargs)


def MakeScope(build_func):
    scope = None
    old_scope = oneflow._oneflow_internal.GetCurrentScope()
    assert old_scope is not None

    def BuildScope(builder):
        nonlocal scope
        scope = build_func(old_scope, builder)
        assert scope is not None

    oneflow._oneflow_internal.deprecated.LogicalRun(BuildScope)
    return scope


def MakeInitialScope(job_conf, device_tag, machine_device_ids, hierarchy, is_mirrored):
    scope = None

    def BuildInitialScope(builder):
        nonlocal scope
        session_id = session_ctx.GetDefaultSession().id
        scope = builder.BuildInitialScope(
            session_id, job_conf, device_tag, machine_device_ids, hierarchy, is_mirrored
        )

    oneflow._oneflow_internal.deprecated.LogicalRun(BuildInitialScope)
    return scope


def InitScopeStack():
    job_conf = job_conf_cfg.JobConfigProto()
    job_conf.mutable_predict_conf()
    job_conf.set_job_name("")
    scope = MakeInitialScope(job_conf, "cpu", ["0:0"], None, is_mirrored=False)
    oneflow._oneflow_internal.InitGlobalScopeStack(scope)


@contextmanager
def ScopeContext(scope):
    old_scope = oneflow._oneflow_internal.GetCurrentScope()
    oneflow._oneflow_internal.GlobalScopeStackPush(scope)
    try:
        yield
    finally:
        assert oneflow._oneflow_internal.GetCurrentScope() is scope
        oneflow._oneflow_internal.GlobalScopeStackPop()
        assert oneflow._oneflow_internal.GetCurrentScope() is old_scope
