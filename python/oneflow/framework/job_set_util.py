from typing import Optional, TypeVar
from oneflow.core.job.job_set_pb2 import JobSet
_VT = TypeVar('_VT')

def inter_job_reuse_mem_strategy(strategy_str: str, job_set: Optional[JobSet]=None, **kwargs: _VT) -> None:
    """Set memory sharing strategy for job set.

    Args:
        strategy_str: An optional `string` from: `mem_sharing_priority`, `parallelism_priority` 
        or `custom_parallelism`. 
        job_set: A `JobSet` object. If None, set default job set.
    """
    assert type(strategy_str) is str
    if job_set == None:
        job_set = _default_job_set
    if strategy_str == 'reuse_mem_priority':
        job_set.inter_job_reuse_mem_strategy.reuse_mem_priority.SetInParent()
        assert job_set.inter_job_reuse_mem_strategy.HasField('reuse_mem_priority')
    elif strategy_str == 'parallelism_priority':
        job_set.inter_job_reuse_mem_strategy.parallelism_priority.SetInParent()
        assert job_set.inter_job_reuse_mem_strategy.HasField('parallelism_priority')
    elif strategy_str == 'custom_parallelism':
        assert kwargs['job_name_groups'] is not None
        for job_name_group in kwargs['job_name_groups']:
            group = job_set.inter_job_reuse_mem_strategy.custom_parallelism.nonparallel_group.add()
            for job_name in job_name_group:
                assert type(job_name) is str
                group.job_name.append(job_name)
_default_job_set = JobSet()