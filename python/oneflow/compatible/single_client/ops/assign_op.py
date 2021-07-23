import os
from oneflow.compatible import single_client as flow
from oneflow.compatible.single_client.core.operator import op_conf_pb2 as op_conf_util
from oneflow.compatible.single_client.core.register import logical_blob_id_pb2 as logical_blob_id_util
from oneflow.compatible.single_client.python.eager import boxing_util as boxing_util
from oneflow.compatible.single_client.python.framework import interpret_util as interpret_util
from oneflow.compatible.single_client.python.framework import hob as hob
from oneflow.compatible.single_client.python.framework import id_util as id_util
from oneflow.compatible.single_client.python.framework import interpret_util as interpret_util
from oneflow.compatible.single_client.python.framework import placement_context as placement_ctx
from oneflow.compatible.single_client.python.framework import remote_blob as remote_blob_util
from oneflow.compatible.single_client.python.lib.core import enable_if as enable_if
from oneflow.compatible.single_client.python.framework import hob as hob
from oneflow.compatible import single_client as flow

def assign(ref, value, dtype=None, name=None):
    if name is None:
        name = id_util.UniqueStr('Assign_')
    op = flow.consistent_user_op_builder(name).Op('assign').Input('ref', [ref]).Input('value', [value]).Build()
    op.InferAndTryRun()

def api_system_assign(ref, value, validate_shape=None, use_locking=None, name=None):
    api = enable_if.unique([lazy_system_assign, eager_system_assign])
    return api(ref, value, validate_shape=validate_shape, use_locking=use_locking, name=name)

@enable_if.condition(hob.in_global_mode & ~hob.eager_execution_enabled)
def lazy_system_assign(ref, value, validate_shape=None, use_locking=None, name=None):
    op_conf = _SystemAssignOpConf(ref, value, name=name)
    (device_tag, machine_device_ids, hierarchy) = oneflow._oneflow_internal.GetDeviceTagAndMachineDeviceIdsAndHierarchy(ref.parallel_conf)
    if hierarchy is not None:
        hierarchy = tuple(hierarchy.dim())
    with flow.scope.placement(device_tag, machine_device_ids, hierarchy):
        interpret_util.Forward(op_conf)
    return ref

@enable_if.condition(hob.in_global_mode & hob.eager_execution_enabled)
def eager_system_assign(ref, value, validate_shape=None, use_locking=None, name=None):
    op_conf = _SystemAssignOpConf(ref, value, name=name)
    oneflow._oneflow_internal.deprecated.LogicalRun(lambda builder: boxing_util.BuildAssignInstruction(builder, ref.blob_object, value.blob_object, op_conf))
    return ref

def api_one_to_one_assign(ref, value):
    assert hob.eager_execution_enabled(None)
    oneflow._oneflow_internal.deprecated.LogicalRun(lambda builder: builder.Build121AssignInstruction(ref.blob_object, value.blob_object))
    return ref

def _SystemAssignOpConf(ref, value, name=None):
    if name is None:
        name = id_util.UniqueStr('Assign_')
    op_conf = op_conf_util.OperatorConf()
    op_conf.name = name
    op_conf.assign_conf.ref = ref.unique_name
    op_conf.assign_conf.value = value.unique_name
    return op_conf