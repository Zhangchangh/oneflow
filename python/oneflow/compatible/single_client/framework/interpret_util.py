from oneflow.compatible.single_client.python.framework import compile_context as compile_ctx
from oneflow.compatible.single_client.python.framework import hob as hob
from oneflow.compatible.single_client.python.lib.core import enable_if as enable_if
from oneflow.compatible.single_client.python.eager import op_executor as op_executor
from oneflow.compatible.single_client.python.eager import gradient_util as gradient_util
from oneflow.compatible import single_client as flow
import oneflow._oneflow_internal
blob_register = oneflow._oneflow_internal.GetDefaultBlobRegister()

def Forward(op_conf, scope_symbol=None):
    if scope_symbol is None:
        scope_symbol = flow.current_scope()
    func = enable_if.unique([LazyInfer, EagerForward])
    return func(compile_ctx.CurJobAddOp, op_conf, scope_symbol)

def OpKernelForward(op_conf, opkernel_object):
    func = enable_if.unique([LazyOpKernelInfer, EagerOpKernelForward])
    return func(compile_ctx.CurJobAddOp, op_conf, opkernel_object)

def ConsistentForward(op_conf, scope_symbol=None):
    if scope_symbol is None:
        scope_symbol = flow.current_scope()
    func = enable_if.unique([LazyInfer, EagerForward])
    return func(compile_ctx.CurJobAddConsistentOp, op_conf, scope_symbol)

def OpKernelConsistentForward(op_conf, opkernel_object):
    func = enable_if.unique([LazyOpKernelInfer, EagerOpKernelForward])
    return func(compile_ctx.CurJobAddConsistentOp, op_conf, opkernel_object)

@enable_if.condition(hob.in_global_mode & ~hob.eager_execution_enabled)
def LazyInfer(add_and_infer, op_conf, scope_symbol=None):
    return add_and_infer(op_conf, scope_symbol)

@enable_if.condition(hob.in_global_mode & ~hob.eager_execution_enabled)
def LazyOpKernelInfer(add_and_infer, op_conf, opkernel_object):
    return add_and_infer(op_conf, opkernel_object.scope_symbol)

@enable_if.condition(hob.in_global_mode & hob.eager_execution_enabled)
def EagerForward(add_and_infer, op_conf, scope_symbol=None):
    op_attribute = add_and_infer(op_conf, scope_symbol)
    parallel_conf = scope_symbol.device_parallel_desc_symbol.parallel_conf
    op_executor.Interpret(op_attribute, parallel_conf, blob_register)
    bw_blob_register = gradient_util.GetDefaultBackwardBlobRegister()
    gradient_util.TrySetBackwardUsedBlobObject(op_attribute, blob_register, bw_blob_register)
    return op_attribute

@enable_if.condition(hob.in_global_mode & hob.eager_execution_enabled)
def EagerOpKernelForward(add_and_infer, op_conf, opkernel_object):
    op_attribute = add_and_infer(op_conf, opkernel_object.scope_symbol)
    op_executor.OpKernelCall(opkernel_object, op_attribute, blob_register)
    bw_blob_register = gradient_util.GetDefaultBackwardBlobRegister()
    gradient_util.TrySetBackwardUsedBlobObject(op_attribute, blob_register, bw_blob_register)
    return op_attribute