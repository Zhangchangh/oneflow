/*
Copyright 2020 The OneFlow Authors. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

#include "oneflow/core/framework/multi_client_session_context.h"
#include "oneflow/core/framework/load_library.h"
#include "oneflow/core/job/version.h"
#include "oneflow/core/job/global_for.h"
#include "oneflow/core/job/id_manager.h"
#include "oneflow/core/job/job_instance.h"
#include "oneflow/core/job/job_build_and_infer_ctx_mgr.h"
#include "oneflow/core/common/buffer_manager.h"
#include "oneflow/core/rpc/include/global_process_ctx.h"
#ifdef WITH_CUDA
#include <cuda.h>
#endif  // WITH_CUDA

namespace oneflow {

namespace {

int32_t GetGpuDeviceNum() {
#ifndef WITH_CUDA
  return 0;
#else
  int device_count = 0;
  cudaGetDeviceCount(&device_count);
  return device_count;
#endif
}

}  // namespace

MultiClientSessionContext::~MultiClientSessionContext() {
  if (is_inited_) {
    {
      // NOTE(chengcheng): delete runtime global objects
      Global<BufferMgr<std::shared_ptr<JobInstance>>>::Delete();
    }

    Global<LazyJobBuildAndInferCtxMgr>::Delete();
    Global<IDMgr>::Delete();
    Global<const ProfilerConf>::Delete();

    // TODO(chengcheng): remove template ForEnv and ForSession
    Global<ResourceDesc, ForSession>::Delete();
    // NOTE(chengcheng): New after delete because in EnvGlobalObjectScope once created ResourceDesc.
    Global<ResourceDesc, ForSession>::New(Global<ResourceDesc, ForEnv>::Get()->resource(),
                                          GlobalProcessCtx::NumOfProcessPerNode());
  }
}

Maybe<void> MultiClientSessionContext::TryInit(const ConfigProto& config_proto) {
  if (!is_inited_) {
    CHECK_OR_RETURN(JUST(GlobalMultiClientEnv()));
    DumpVersionInfo();

    Resource resource = config_proto.resource();

    {
      // NOTE(chengcheng):
      //   In multi-client, user can NOT config gpu_device_num and cpu_device_num.
      //
      //   cpu_device_num is a confusing name, it should be explained as:
      //       gpu_device corresponding host memory and compute stream.
      //   When gpu_device_num == 0 (cpu only), cpu device num should be process num.
      //
      //   gpu_device_num is the number of visible GPUs one current machine.
      //   NOTE: gpu_device_num NOT necessarily equal to the num of process one this machine.
      resource.set_machine_num(GlobalProcessCtx::NodeSize());
      const int32_t gpu_device_num = GetGpuDeviceNum();
      resource.set_gpu_device_num(gpu_device_num);
      if (gpu_device_num == 0) {
        resource.set_cpu_device_num(GlobalProcessCtx::NumOfProcessPerNode());
      } else {
        resource.set_cpu_device_num(gpu_device_num);
      }
    }

    // NOTE(chengcheng): detele first because in EnvGlobalObjectScope has created ResourceDesc.
    if (Global<ResourceDesc, ForSession>::Get() != nullptr) {
      // TODO(chengcheng): reorganize dependency of all Global objects.
      Global<ResourceDesc, ForSession>::Delete();
    }
    Global<ResourceDesc, ForSession>::New(resource, GlobalProcessCtx::NumOfProcessPerNode());
    Global<const ProfilerConf>::New(config_proto.profiler_conf());
    Global<IDMgr>::New();
    // TODO(chengcheng): refactor JobBuildAndInferCtxMgr
    Global<LazyJobBuildAndInferCtxMgr>::New();

    for (const std::string& lib_path : config_proto.load_lib_path()) {
      // TODO(chengcheng): remove load_lib_path in config proto. using LoadLibraryNow
      JUST(LoadLibrary(lib_path));
    }

    {
      // NOTE(chengcheng): init runtime global objects
      Global<BufferMgr<std::shared_ptr<JobInstance>>>::New();
    }

    is_inited_ = true;
  }
  return Maybe<void>::Ok();
}

}  // namespace oneflow
