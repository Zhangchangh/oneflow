import collections
import re

import oneflow
import oneflow._oneflow_internal
import oneflow._oneflow_internal.oneflow.core.job.placement as placement_cfg
import oneflow.core.job.placement_pb2 as placement_pb
import oneflow.framework.c_api_util as c_api_util
import oneflow.framework.op_util as op_util
import oneflow.framework.session_context as session_ctx


class PlacementScope(object):
    pass


class EmptyPlacementScope(PlacementScope):
    def __init__(self, device_tag, machine_device_ids, hierarchy):
        if isinstance(machine_device_ids, (list, tuple)) == False:
            machine_device_ids = [machine_device_ids]
        self.device_tag_ = device_tag
        self.machine_device_ids_ = machine_device_ids
        self.hierarchy_ = hierarchy

    @property
    def device_tag(self):
        return self.device_tag_

    @property
    def machine_device_ids(self):
        return self.machine_device_ids_

    @property
    def hierarchy(self):
        return self.hierarchy_

    def __enter__(self):
        pass

    def __exit__(self, *args):
        pass


class GlobalModePlacementScope(PlacementScope):
    def __init__(self, scope_ctx):
        self.scope_ctx_ = scope_ctx

    def __enter__(self):
        self.scope_ctx_.__enter__()

    def __exit__(self, *args):
        self.scope_ctx_.__exit__(*args)


def MakeParallelConf4Resource(device_tag, resource):
    if device_tag == "gpu":
        assert resource.HasField("gpu_device_num")
        machine_device_ids = GetGpuMachineDeviceIds(resource)
    elif device_tag == "cpu":
        assert resource.HasField("cpu_device_num")
        machine_device_ids = GetCpuMachineDeviceIds(resource)
    else:
        raise NotImplementedError
    return oneflow._oneflow_internal.MakeParallelConf(device_tag, machine_device_ids)


def MakeMachineId2DeviceIdList(parallel_conf):
    parallel_conf_str = str(parallel_conf)
    global _parallel_conf_str2ofrecord
    if parallel_conf_str not in _parallel_conf_str2ofrecord:
        ofrecord = c_api_util.GetMachine2DeviceIdListOFRecordFromParallelConf(
            parallel_conf
        )
        _parallel_conf_str2ofrecord[parallel_conf_str] = {
            int(k): list(v.int32_list.value) for (k, v) in ofrecord.feature.items()
        }
    return _parallel_conf_str2ofrecord[parallel_conf_str]


def GetParallelSize(key2list):
    size = 0
    for (k, v) in key2list.items():
        size += len(v)
    return size


def GetGpuMachineDeviceIds(resource):
    assert resource.machine_num > 0
    assert resource.HasField("gpu_device_num")
    return [
        "%s:0-%s" % (m_id, resource.gpu_device_num - 1)
        for m_id in range(resource.machine_num)
    ]


def GetCpuMachineDeviceIds(resource):
    assert resource.machine_num > 0
    assert resource.HasField("cpu_device_num")
    return [
        "%s:0-%s" % (m_id, resource.cpu_device_num - 1)
        for m_id in range(resource.machine_num)
    ]


_parallel_conf_str2ofrecord = {}
