import datetime
import os
import shutil
import numpy as np
from oneflow.compatible.single_client.python.framework import hob as hob
from oneflow.compatible.single_client.python.framework import (
    job_instance as job_instance,
)
from oneflow.compatible.single_client.python.framework import (
    check_point_v2 as check_point_v2,
)
from oneflow.compatible.single_client.python.framework import config_util as config_util
from oneflow.compatible.single_client.python.framework import (
    session_context as session_ctx,
)
from oneflow.compatible.single_client.python.lib.core import enable_if as enable_if
from oneflow.compatible.single_client.python.eager import op_executor as op_executor
from typing import List, Union


class CheckPoint(object):
    """Create a `CheckPoint` object to manage checkpoint manually.

    """

    def __init__(self) -> None:
        if not config_util.api_legacy_model_io_enabled():
            print(
                "\x1b[1mWARNING: 'flow.train.CheckPoint' is deprecated. Please use the new API:\x1b[0m\nflow.train.CheckPoint().save(path) => \x1b[1m\x1b[92mflow.checkpoint.save(path)\x1b[0m\nflow.train.CheckPoint().load(path) => \x1b[1m\x1b[92mflow.load_variables(flow.checkpoint.get(path))\x1b[0m\nflow.train.CheckPoint().init() is not needed any more.\n"
            )

    @session_ctx.try_init_default_session
    def save(self, path: str) -> None:
        """save a checkpoint to `path`.

        Args:
            path: A `string` of path to save checkpoint. 
        """
        if not config_util.api_legacy_model_io_enabled():
            check_point_v2.SaveVarDict(path)
            return
        assert type(path) is str
        enable_if.unique([lazy_checkpoint_save, eager_checkpoint_save])(path)

    @session_ctx.try_init_default_session
    def init(self) -> None:
        """Initialize models by default initializer of op or Job.
        """
        if not config_util.api_legacy_model_io_enabled():
            return
        enable_if.unique([lazy_checkpoint_init, eager_checkpoint_init])()

    @session_ctx.try_init_default_session
    def load(self, path: str) -> None:
        """load a checkpoint from `path` and initialize models.

        Args:
            path: A `string` of path to load checkpoint.
        """
        if not config_util.api_legacy_model_io_enabled():
            check_point_v2.LoadVariables(check_point_v2.GetCheckpoint(path))
            return
        assert type(path) is str
        enable_if.unique([lazy_checkpoint_load, eager_checkpoint_load])(path)


@enable_if.condition(hob.in_normal_mode & ~hob.eager_execution_enabled)
def lazy_checkpoint_save(path):
    session_ctx.GetDefaultSession().LaunchJob(_MakeModelSaveJobFunc(path))


@enable_if.condition(hob.in_normal_mode & ~hob.eager_execution_enabled)
def lazy_checkpoint_init():
    session_ctx.GetDefaultSession().LaunchJob(_MakeModelInitJobFunc())


@enable_if.condition(hob.in_normal_mode & ~hob.eager_execution_enabled)
def lazy_checkpoint_load(path):
    session_ctx.GetDefaultSession().LaunchJob(_MakeModelLoadJobFunc(path))


@enable_if.condition(hob.in_normal_mode & hob.eager_execution_enabled)
def eager_checkpoint_save(path):
    op_executor.EagerSaveVariableBlob(path)


@enable_if.condition(hob.in_normal_mode & hob.eager_execution_enabled)
def eager_checkpoint_init():
    pass


@enable_if.condition(hob.in_normal_mode & hob.eager_execution_enabled)
def eager_checkpoint_load(path):
    session_ctx.GetDefaultSession().snapshot_mgr.load(path)


def _MakeModelInitJobFunc():
    def push_cb(blob):
        pass

    def finish_cb():
        pass

    sess = session_ctx.GetDefaultSession()
    return job_instance.MakeJobInstance(
        str(sess.inter_user_job_info.global_model_init_job_name),
        push_cb=push_cb,
        finish_cb=finish_cb,
    )


def _MakeModelLoadJobFunc(path):
    def push_cb(blob):
        blob.CopyFromNdarray(np.frombuffer(path.encode("ascii"), dtype=np.int8))

    def finish_cb():
        pass

    sess = session_ctx.GetDefaultSession()
    return job_instance.MakeJobInstance(
        str(sess.inter_user_job_info.global_model_load_job_name),
        push_cb=push_cb,
        finish_cb=finish_cb,
    )


def _MakeModelSaveJobFunc(path):
    def push_cb(blob):
        blob.CopyFromNdarray(np.frombuffer(path.encode("ascii"), dtype=np.int8))

    def finish_cb():
        pass

    sess = session_ctx.GetDefaultSession()
    return job_instance.MakeJobInstance(
        str(sess.inter_user_job_info.global_model_save_job_name),
        push_cb=push_cb,
        finish_cb=finish_cb,
    )


class SimpleCheckPointManager(object):
    """`SimpleCheckPointManager` is a simple automatic checkpoint manager.

    Args:
        root_path: root path of snapshot
        prefix: prefix of snapshot
    """

    def __init__(self, root_path: str, prefix: str = "snapshot_") -> None:
        if not os.path.exists(root_path):
            os.makedirs(root_path)
        else:
            assert os.path.isdir(root_path)
        self._root_path = root_path
        self._prefix = prefix

    def list_checkpoints(self) -> List[str]:
        def is_snapshot(name):
            if not name.startswith(self._prefix):
                return False
            snapshot_done = os.path.join(self._GetSnapshotPath(name), "snapshot_done")
            return os.path.exists(snapshot_done) and os.path.isfile(snapshot_done)

        return sorted([f for f in os.listdir(self._root_path) if is_snapshot(f)])

    def latest_checkpoint(self) -> Union[str, None]:
        names = self.list_checkpoints()
        if not names:
            return None
        else:
            return names[-1]

    def initialize_or_restore(self) -> None:
        name = self.latest_checkpoint()
        if name:
            check_point_v2.LoadVariables(
                check_point_v2.GetCheckpoint(self._GetSnapshotPath(name))
            )
        else:
            self.save()

    def save(self) -> None:
        check_point_v2.SaveVarDict(self._GetSnapshotPath(self._NextSnapshotName()))

    def _NextSnapshotName(self) -> str:
        return self._prefix + datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    def _GetSnapshotPath(self, name: str) -> str:
        return os.path.join(self._root_path, name)


class SnapshotManager(object):
    def __init__(self):
        self.name2path_ = dict()

    def load(self, root_dir, refresh=True):
        assert os.path.isdir(root_dir)
        if refresh:
            self.name2path_ = dict()
        for file in os.listdir(root_dir):
            file_path = os.path.join(root_dir, file)
            if not os.path.isdir(file_path):
                continue
            has_out_subfile = False
            for f in os.listdir(file_path):
                fpath = os.path.join(file_path, f)
                if f == "out" and os.path.isfile(fpath):
                    has_out_subfile = True
            if not has_out_subfile:
                continue
            assert file not in self.name2path_
            self.name2path_[file] = os.path.join(file_path, "out")

    def get_snapshot_path(self, name):
        try:
            return self.name2path_[name]
        except KeyError:
            return None
