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
#ifndef ONEFLOW_CORE_CUDA_ATOMIC_H_
#define ONEFLOW_CORE_CUDA_ATOMIC_H_

#if defined(__CUDACC__)

#include <cuda_runtime.h>
#include <cuda_fp16.h>

namespace oneflow {

namespace cuda {

namespace atomic {

__device__ __forceinline__ int Add(int* address, int val) { return atomicAdd(address, val); }

__device__ __forceinline__ int64_t Add(int64_t* address, int64_t val) {
  return static_cast<int64_t>(atomicAdd(reinterpret_cast<unsigned long long int*>(address),
                                        static_cast<unsigned long long int>(val)));
}

__device__ __forceinline__ half Add(half* address, half val) {
#if __CUDA_ARCH__ >= 700 && CUDA_VERSION >= 10000
  return atomicAdd(address, val);
#else
  __trap();
#endif
}

__device__ __forceinline__ float Add(float* address, float val) { return atomicAdd(address, val); }

__device__ __forceinline__ double Add(double* address, double val) {
#if __CUDA_ARCH__ >= 600
  return atomicAdd(address, val);
#else
  auto address_as_ull = reinterpret_cast<unsigned long long int*>(address);
  unsigned long long int old = *address_as_ull;
  unsigned long long int assumed = 0;
  do {
    assumed = old;
    old = atomicCAS(address_as_ull, assumed,
                    __double_as_longlong(val + __longlong_as_double(assumed)));
  } while (assumed != old);
  return __longlong_as_double(old);
#endif
}

__device__ __forceinline__ float Max(float* address, const float val) {
  int* address_as_i = (int*)address;
  int old = *address_as_i;
  int assumed = 0;
  do {
    assumed = old;
    old = atomicCAS(address_as_i, assumed, __float_as_int(fmaxf(val, __int_as_float(assumed))));
  } while (assumed != old);
  return __int_as_float(old);
}

__device__ __forceinline__ double Max(double* address, const double val) {
  unsigned long long int* address_as_i = (unsigned long long int*)address;
  unsigned long long int old = *address_as_i;
  unsigned long long int assumed = 0;
  do {
    assumed = old;
    old = atomicCAS(address_as_i, assumed,
                    __double_as_longlong(fmax(val, __longlong_as_double(assumed))));
  } while (assumed != old);
  return __longlong_as_double(old);
}

}  // namespace atomic

}  // namespace cuda

}  // namespace oneflow

#endif  // defined(__CUDACC__)

#endif  // ONEFLOW_CORE_CUDA_ATOMIC_H_
