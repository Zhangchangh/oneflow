import traceback
import oneflow.framework.ofblob as ofblob
import oneflow._oneflow_internal.oneflow.core.operator.op_attribute as op_attribute_cfg
import oneflow._oneflow_internal.oneflow.core.job.placement as placement_cfg
import oneflow._oneflow_internal.oneflow.core.job.job_conf as job_conf_cfg
import oneflow._oneflow_internal.oneflow.core.job.scope as scope_cfg
import oneflow._oneflow_internal


def GetIdForRegisteredCallback(cb):
    assert callable(cb)
    global unique_id2handler
    unique_id2handler[id(cb)] = cb
    return id(cb)


def DeleteRegisteredCallback(cb):
    global unique_id2handler
    assert id(cb) in unique_id2handler
    del unique_id2handler[id(cb)]


class PythonCallback(oneflow._oneflow_internal.ForeignCallback):
    def __init__(self):
        oneflow._oneflow_internal.ForeignCallback.__init__(self)

    def OfBlobCall(self, unique_id, of_blob_ptr):
        try:
            _WatcherHandler(unique_id, of_blob_ptr)
        except Exception as e:
            print(traceback.format_exc())
            raise e

    def RemoveForeignCallback(self, unique_id):
        global unique_id2handler
        try:
            del unique_id2handler[unique_id]
        except Exception as e:
            print(traceback.format_exc())
            raise e

    def EagerInterpretCompletedOp(self, op_attribute, parallel_conf):
        try:
            interpreter_callback.InterpretCompletedOp(str(op_attribute), parallel_conf)
        except Exception as e:
            print(traceback.format_exc())
            raise e

    def EagerMirroredCast(self, op_attribute, parallel_conf):
        try:
            interpreter_callback.MirroredCast(str(op_attribute), parallel_conf)
        except Exception as e:
            print(traceback.format_exc())
            raise e

    def MakeScopeSymbol(self, job_conf, parallel_conf, is_mirrored):
        try:
            return interpreter_callback.MakeScopeSymbol(
                job_conf, parallel_conf, is_mirrored
            )
        except Exception as e:
            print(traceback.format_exc())
            raise e

    def MakeParallelDescSymbol(self, parallel_conf):
        try:
            return interpreter_callback.MakeParallelDescSymbol(parallel_conf)
        except Exception as e:
            print(traceback.format_exc())
            raise e


def _WatcherHandler(unique_id, of_blob_ptr):
    global unique_id2handler
    assert unique_id in unique_id2handler
    handler = unique_id2handler[unique_id]
    assert callable(handler)
    handler(ofblob.OfBlob(of_blob_ptr))


unique_id2handler = {}
global_python_callback = PythonCallback()
interpreter_callback = None
