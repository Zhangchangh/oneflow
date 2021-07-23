import oneflow._oneflow_internal
from oneflow.compatible import single_client as flow


def create_generator(device=None):
    if device is None:
        device = "auto"
    return oneflow._oneflow_internal.create_generator(device)


def default_generator(device=None):
    if device is None:
        device = "auto"
    return oneflow._oneflow_internal.default_generator(device)


def manual_seed(seed):
    oneflow._oneflow_internal.manual_seed(seed)
