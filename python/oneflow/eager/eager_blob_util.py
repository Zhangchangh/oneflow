import oneflow._oneflow_internal
import oneflow.framework.blob_trait as blob_trait
import oneflow.framework.python_callback as python_callback
import oneflow.lib.core.async_util as async_util
from oneflow.framework.dtype import convert_proto_dtype_to_oneflow_dtype


@property
def dtype(self):
    return convert_proto_dtype_to_oneflow_dtype(self.get_dtype())


def numpy(self):
    return _GetPhysicalBlobBodyCache(self.blob_object)


def numpy_list(self):
    return _GetPhysicalBlobBodyCache(self.blob_object)


def RegisterMethod4EagerPhysicalBlob():
    oneflow._oneflow_internal.EagerPhysicalBlob.dtype = dtype
    oneflow._oneflow_internal.EagerPhysicalBlob.numpy = numpy
    oneflow._oneflow_internal.EagerPhysicalBlob.numpy_list = numpy_list


def FetchTensorBlobAsNumpyList(parallel_size, blob_object):
    def AsyncFetchBlobBody(Yield):
        fetcher = _MakeFetcherEagerBlobBodyAsNumpyFromOfBlob(Yield)

        def BuildFetchBlobBodyInstruction(builder):
            builder.FetchBlobBody(
                blob_object, python_callback.GetIdForRegisteredCallback(fetcher)
            )
            builder.InsertRemoveForeignCallbackInstruction(
                blob_object.object_id,
                python_callback.GetIdForRegisteredCallback(fetcher),
            )

        oneflow._oneflow_internal.deprecated.PhysicalRun(BuildFetchBlobBodyInstruction)

    return async_util.Await(parallel_size, AsyncFetchBlobBody)


def _GetPhysicalBlobHeaderCache(blob_object):
    return _FetchBlobHeader(blob_object)


def _GetPhysicalBlobBodyCache(blob_object):
    return _FetchPhysicalBlobBody(blob_object)


def _FetchBlobHeader(blob_object):
    def AsyncFetchBlobHeader(Yield):
        fetcher = _MakeFetcherEagerPhysicalBlobHeaderFromOfBlob(Yield)

        def BuildFetchBlobHeaderInstruction(builder):
            builder.FetchBlobHeader(
                blob_object, python_callback.GetIdForRegisteredCallback(fetcher)
            )
            builder.InsertRemoveForeignCallbackInstruction(
                blob_object.object_id,
                python_callback.GetIdForRegisteredCallback(fetcher),
            )

        oneflow._oneflow_internal.deprecated.PhysicalRun(
            BuildFetchBlobHeaderInstruction
        )

    return async_util.Await(1, AsyncFetchBlobHeader)[0]


def _FetchPhysicalBlobBody(blob_object):
    return FetchTensorBlobAsNumpyList(1, blob_object)[0]


def _MakeFetcherEagerPhysicalBlobHeaderFromOfBlob(Yield):
    def Callback(ofblob):
        Yield(
            oneflow._oneflow_internal.EagerPhysicalBlobHeader(
                ofblob.static_shape,
                ofblob.shape,
                oneflow._oneflow_internal.deprecated.GetProtoDtype4OfDtype(
                    ofblob.dtype
                ),
            )
        )

    return Callback


def _MakeFetcherEagerBlobBodyAsNumpyFromOfBlob(Yield):
    def FetchFromOfBlob(ofblob):
        Yield(ofblob.CopyToNdarray())

    return FetchFromOfBlob
