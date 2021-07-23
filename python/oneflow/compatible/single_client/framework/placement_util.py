import re
import traceback

import oneflow._oneflow_internal
from oneflow import oneflow_deprecate
from oneflow.compatible import single_client as flow
from oneflow.compatible.single_client.python.framework import hob as hob
from oneflow.compatible.single_client.python.framework import (
    placement_context as placement_ctx,
)
from oneflow.compatible.single_client.python.framework import scope_util as scope_util
from oneflow.compatible.single_client.python.framework import (
    session_context as session_ctx,
)
from oneflow.compatible.single_client.python.lib.core import enable_if as enable_if


@oneflow_deprecate()
def deprecated_placement(*args, **kwargs):
    print(
        "WARNING:",
        "oneflow.compatible.single_client.device_prior_placement/oneflow.compatible.single_client.fixed_placement",
        "will be removed in the future, use {} instead.".format(
            "oneflow.compatible.single_client.scope.placement"
        ),
    )
    print(traceback.format_stack()[-2])
    return api_placement(*args, **kwargs)


def api_placement(
    device_tag: str, machine_device_ids: str, hierarchy=None
) -> placement_ctx.PlacementScope:
    """Create a scope. All ops within the scope will run on specified device that placed by  "device_tag" and "machine_device_ids".

    Args:
        device_tag (str): Device tag, "cpu" or "gpu" only
        machine_device_ids (str): List of string that specifies what machine & device(s) to use, the format is "List[<NODE INDEX>:<DEVICE START INDEX>-<DEVICE END INDEX>, <NODE INDEX>:<DEVICE START INDEX>-<DEVICE END INDEX>, ...]", For example, "0:0" means use the device 0 of machine 0, and "1:4-6" means use device 4, 5, 6 of machine 1.

    Returns:
        placement_ctx.DevicePriorPlacementScope:  Placement scope

    For example:

    If you run program on single machine, you can assign the specified device like this:

    .. code-block:: python

        with flow.scope.placement("gpu", "0:0"):
            logits = lenet(images, train=False)
            loss = flow.nn.sparse_softmax_cross_entropy_with_logits(labels, logits, name="softmax_loss")
            flow.losses.add_loss(loss)

    Or you run distributed program, you can assign the specified devices like this:

    .. code-block:: python

        # configure machines ids, ips, etc.
        with flow.scope.placement("gpu", ['0:0-7', '1:0-7']):
            logits = lenet(images, train=False)
            loss = flow.nn.sparse_softmax_cross_entropy_with_logits(labels, logits, name="softmax_loss")
            flow.losses.add_loss(loss)

    """
    if oneflow._oneflow_internal.flags.with_cuda() == False and device_tag == "gpu":
        device_tag = "cpu"
    assert (
        isinstance(hierarchy, (list, tuple, oneflow._oneflow_internal.Size))
        or hierarchy is None
    )
    func = enable_if.unique(
        [
            GetEmptyPlacementScope,
            GetNormalModePlacementScope,
            GetGlobalModePlacementScope,
        ]
    )
    return func(device_tag, machine_device_ids, hierarchy)


@enable_if.condition(
    hob.in_normal_mode & hob.env_initialized & ~hob.session_initialized
)
def GetEmptyPlacementScope(device_tag, machine_device_ids, hierarchy=None):
    return placement_ctx.EmptyPlacementScope(device_tag, machine_device_ids, hierarchy)


@enable_if.condition(hob.in_normal_mode & hob.session_initialized)
def GetNormalModePlacementScope(device_tag, machine_device_ids, hierarchy=None):
    if isinstance(machine_device_ids, tuple):
        machine_device_ids = list(machine_device_ids)
    if not isinstance(machine_device_ids, list):
        machine_device_ids = [machine_device_ids]
    sess = session_ctx.GetDefaultSession()
    if hierarchy is not None:
        hierarchy = oneflow._oneflow_internal.Size(tuple(hierarchy))
    scope = scope_util.MakeScope(
        lambda old_scope, builder: builder.BuildScopeWithNewParallelDesc(
            old_scope, device_tag, machine_device_ids, hierarchy
        )
    )
    return scope_util.ScopeContext(scope)


@enable_if.condition(hob.in_global_mode)
def GetGlobalModePlacementScope(device_tag, machine_device_ids, hierarchy=None):
    if isinstance(machine_device_ids, (list, tuple)) == False:
        machine_device_ids = [machine_device_ids]
    sess = session_ctx.GetDefaultSession()
    if hierarchy is not None:
        hierarchy = oneflow._oneflow_internal.Size(tuple(hierarchy))

    def BuildScope(old_scope, builder):
        return builder.BuildScopeWithNewParallelDesc(
            old_scope, device_tag, machine_device_ids, hierarchy
        )

    scope_ctx = scope_util.ScopeContext(scope_util.MakeScope(BuildScope))
    return placement_ctx.GlobalModePlacementScope(scope_ctx)


def GetDefaultMachineDeviceIds(resource):
    if resource.HasField("gpu_device_num") and resource.gpu_device_num > 0:
        return ("gpu", placement_ctx.GetGpuMachineDeviceIds(resource))
    elif resource.HasField("cpu_device_num"):
        return ("cpu", placement_ctx.GetCpuMachineDeviceIds(resource))
    else:
        raise NotImplementedError
