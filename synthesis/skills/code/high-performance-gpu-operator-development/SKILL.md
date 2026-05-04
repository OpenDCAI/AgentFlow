---
name: high-performance-gpu-operator-development
description: Use this skill when the user wants to generate or optimize high-performance GPU kernels using languages like Triton or native C++/CUDA. This is applicable for requests like 'write a fast Triton kernel for matrix operations', 'optimize my GPU code for throughput', 'create a custom operator that outperforms the standard library', or 'debug a memory error in a parallel kernel'. It is specifically triggered when performance bottlenecks (latency/bandwidth) or hardware-specific optimizations (register pressure/memory coalescing) are the primary concerns rather than general Python logic.
---

# Skill: high-performance-gpu-operator-development

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to develop, debug, and iteratively optimize high-performance GPU operators by translating abstract mathematical operations into hardware-aware execution models. This involves utilizing Domain-Specific Languages (DSLs) like Triton or low-level native extensions (C++/CUDA) to manage memory hierarchies, perform operator fusion, coordinate block-level parallelism, and measure empirical speedups over reference implementations while maintaining strict numerical precision.
* **Dimension Hierarchy**: Data and ML Workflow Engineering->Machine Learning Engineering->high-performance-gpu-operator-development

### Real Case
**[Case 1]**
* **Initial Environment**: A development environment contains an NVIDIA or AMD GPU, the Triton DSL installed, and a reference Python implementation of a 2D tensor 'flip' operation. The workspace includes a performance profiling tool to measure memory bandwidth and register usage.
* **Real Question**: Implement a high-performance 2D flip kernel that processes blocks of data and flips each row horizontally. The kernel must be significantly faster than a standard two-pass implementation.
* **Real Trajectory**: The agent starts by identifying the inefficiency of standard 'load-then-flip' patterns which use double memory access. It implements a single-pass kernel that calculates flipped memory pointers directly during the load stage: `X + rows * M + (M - 1 - cols)`. By reading from the flipped source positions and writing directly to the destination, it avoids intermediate register storage and reduces memory bandwidth requirements. Finally, it uses tiled masks to handle boundary conditions for arbitrary tensor sizes, ensuring the kernel is robust as well as fast.
* **Real Answer**: A Triton kernel that uses direct pointer arithmetic to perform the flip during global memory access, achieving over 2x speedup by halving the total memory transactions.
* **Why this demonstrates the capability**: This demonstrates the capability because it optimizes the memory access pattern—a core bottleneck in GPU computing—by moving logic from registers into the addressing stage. It shows an understanding of hardware efficiency (memory bandwidth reduction) and robust kernel design (masking for boundary safety).
---
**[Case 2]**
* **Initial Environment**: A cloud-based GPU development container with the ROCm or CUDA toolchain and a reference implementation of a fused Conv2d-ReLU-MaxPool layer in PyTorch. The environment includes a suite of unit tests with randomized seeds to verify numerical stability.
* **Real Question**: Implement a fused native C++/CUDA kernel for the forward pass of a sequential module (Convolution -> ReLU -> MaxPool) that outperforms the eager-mode baseline.
* **Real Trajectory**: The agent analyzes the reference to identify spatial dependencies and constants. It implements a specialized kernel using shared memory to cache input tiles, minimizing the need to re-read data from high-latency global memory for the convolution. It unrolls the inner loops and fuses the activation and pooling logic directly into the tile-writing stage, preventing the creation of intermediate feature map tensors. The agent then runs the profiler to confirm that DRAM throughput is maximized and register spilling is minimized.
* **Real Answer**: A fused native kernel where convolution, ReLU, and Max-Pooling are performed in one pass, significantly reducing the memory overhead of the neural network layer.
* **Why this demonstrates the capability**: This illustrates operator fusion, a key high-performance skill. By managing shared memory and unrolling loops, the agent reduces the global memory round-trips that typically slow down sequential AI operators.

## Pipeline Execution Instructions
To synthesize data for this capability, you must strictly follow a 3-phase pipeline. **Do not hallucinate steps.** Read the corresponding reference file for each phase sequentially:

1. **Phase 1: Environment Exploration**
   Read the exploration guidelines to discover raw knowledge seeds:
   `references/EXPLORATION.md`

2. **Phase 2: Trajectory Selection**
   Once Phase 1 is complete, read the selection criteria to evaluate the trajectory:
   `references/SELECTION.md`

3. **Phase 3: Data Synthesis**
   Once a trajectory passes Phase 2, read the synthesis instructions to generate the final data:
   `references/SYNTHESIS.md`
