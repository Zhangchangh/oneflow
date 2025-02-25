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
#include "oneflow/core/kernel/kernel.h"
#include "oneflow/core/kernel/kernel_helper.h"
#include "oneflow/core/kernel/runtime_blob_shape_infer_helper.h"
#include "oneflow/core/profiler/profiler.h"
#include "oneflow/core/profiler/kernel.h"

namespace oneflow {

Kernel::~Kernel() {
  if (shape_infer_helper_ != nullptr) { delete shape_infer_helper_; }
}

void Kernel::InitBase(const JobDesc* job_desc, const KernelConf& kernel_conf) {
  if (!(job_desc_ == nullptr || shape_infer_helper_ == nullptr)) { return; }
  job_desc_ = job_desc;
  kernel_conf_ = kernel_conf;
  shape_infer_helper_ =
      new RuntimeBlobShapeInferHelper(this->op_conf(), this->kernel_conf(), &this->job_desc());
}

void Kernel::Init(const JobDesc* job_desc, const KernelConf& kernel_conf, DeviceCtx* device_ctx) {
  InitBase(job_desc, kernel_conf);
  VirtualKernelInit(device_ctx);
}

void Kernel::Launch(const KernelCtx& ctx,
                    std::function<Blob*(const std::string&)> BnInOp2Blob) const {
  Forward(ctx, BnInOp2Blob);
}

const LogicalBlobId& Kernel::BnInOp2Lbi(const std::string& bn_in_op) const {
  return op_attribute().arg_signature().bn_in_op2lbi().at(bn_in_op);
}

void Kernel::CheckSameDim0ValidNum(
    const PbRpf<std::string>& bns,
    const std::function<Blob*(const std::string&)>& BnInOp2Blob) const {
  UNIMPLEMENTED();
}

void Kernel::SetOutputBlobProducerInferAccessChecker(
    std::function<Blob*(const std::string&)> BnInOp2Blob) const {
  ForEachObnAndIsHeaderInferedBeforeCompute(BnInOp2Blob, [&](const std::string& obn, bool _) {
    BnInOp2Blob(obn)->set_blob_access_checker(Global<BlobAccessCheckerIf<true, false>>::Get());
  });
}

void Kernel::SetOutputBlobProducerComputeAccessChecker(
    std::function<Blob*(const std::string&)> BnInOp2Blob) const {
  ForEachObnAndIsHeaderInferedBeforeCompute(
      BnInOp2Blob, [&](const std::string& obn, bool is_header_infered_before_compute) {
        const BlobAccessChecker* checker = nullptr;
        if (is_header_infered_before_compute) {
          checker = Global<BlobAccessCheckerIf<false, true>>::Get();
        } else {
          checker = Global<BlobAccessCheckerIf<true, true>>::Get();
        }
        BnInOp2Blob(obn)->set_blob_access_checker(checker);
      });
}

void Kernel::SetOutputBlobConsumerAccessChecker(
    std::function<Blob*(const std::string&)> BnInOp2Blob) const {
  ForEachObnAndIsMutableByConsumer(BnInOp2Blob, [&](const std::string& obn, bool is_mutable) {
    const BlobAccessChecker* checker = nullptr;
    if (is_mutable) {
      checker = Global<BlobAccessCheckerIf<false, true>>::Get();
    } else {
      checker = Global<BlobAccessCheckerIf<false, false>>::Get();
    }
    BnInOp2Blob(obn)->set_blob_access_checker(checker);
  });
}

void Kernel::Forward(const KernelCtx& ctx,
                     std::function<Blob*(const std::string&)> BnInOp2Blob) const {
  SetOutputBlobProducerInferAccessChecker(BnInOp2Blob);
  ForwardHeader(ctx, BnInOp2Blob);
  if (IsAllBlobEmpty(op_attribute().output_bns(), BnInOp2Blob) && IsStateless()) { return; }
  SetOutputBlobProducerComputeAccessChecker(BnInOp2Blob);
  OF_PROFILER_ONLY_CODE(profiler::TraceKernelForwardDataContentStart(this, ctx, BnInOp2Blob));
  ForwardDataContent(ctx, BnInOp2Blob);
  OF_PROFILER_ONLY_CODE(profiler::TraceKernelForwardDataContentEnd(this, ctx, BnInOp2Blob));
  SetOutputBlobConsumerAccessChecker(BnInOp2Blob);
}

void Kernel::ForwardHeader(const KernelCtx& ctx,
                           std::function<Blob*(const std::string&)> BnInOp2Blob) const {
  if (kernel_conf_.need_do_shape()) { ForwardShape(ctx, BnInOp2Blob); }
}

void Kernel::ForwardShape(const KernelCtx& ctx,
                          std::function<Blob*(const std::string&)> BnInOp2Blob) const {
  return shape_infer_helper_->InferShape(BnInOp2Blob);
}

std::unique_ptr<const Kernel> ConstructKernel(const JobDesc* job_desc, const KernelConf& conf,
                                              DeviceCtx* device_ctx) {
  auto op_type = conf.op_attribute().op_conf().op_type_case();
  CHECK_NE(op_type, OperatorConf::OpTypeCase::OP_TYPE_NOT_SET)
      << " ERROR! KernelConf: " << conf.DebugString() << " has NOT set op_type_case";
  Kernel* rptr = kernel_registration::CreateKernel(conf);
  if (rptr == nullptr) { rptr = NewObj<int32_t, Kernel>(op_type, conf); }
  CHECK_NOTNULL(rptr);
  rptr->Init(job_desc, conf, device_ctx);
  return std::unique_ptr<const Kernel>(rptr);
}

#define INSTANTIATE_KERNEL_IF(device_type) template class KernelIf<device_type>;

OF_PP_FOR_EACH_TUPLE(INSTANTIATE_KERNEL_IF, DEVICE_TYPE_SEQ);

}  // namespace oneflow
