# Loom Layer 1 Hardware Physics

This paper pulls Thread 5 into four concrete Layer 1 hardware research theses. Every thesis starts from a measured software bottleneck in Layers 2 through 5 (`weft`, `warp`, `exo`, `mde`) and quantization geometry in `Moissanite-Labs/siliquant`, rather than speculative silicon aesthetics.

All bandwidth numbers use decimal `GB/s` (`10^9` bytes/s) and binary memory footprints (`MiB`, `GiB`) consistently. Every equation and roofline figure below is checked by [`scripts/verify_math.py`](../scripts/verify_math.py).

## Reference Hardware and Model Baselines

Two real local machines anchor every calculation:

| Machine Profile | Memory Capacity | Peak / Sustained Bandwidth | Target Open-Weights Model | Base Decode Floor (`B = 1`) |
| --- | --- | --- | --- | --- |
| **8 GiB Laptop GPU (`RTX 3080 Laptop`)** | `8 GiB` VRAM (+ `32 GiB` RAM) | `448 GB/s` / `350 GB/s` | 4B Q4_K_M (`2.10 GiB`, `L=36`, `d=2560`) | `6.44 ms/tok` (`155.2 tok/s`) |
| **64 GiB Unified Hub (`Apple M1 Max`)** | `64 GiB` unified RAM | `400 GB/s` / `320 GB/s` | 27B Q4_K_M (`15.24 GiB`, `L=64`, `d=5120`) | `51.14 ms/tok` (`19.56 tok/s`) |

## Thesis 1: Hardware-Enforced DMA-Boundary Verification (Zero GPU TCB Trust)

### Measured L2/L3 Bottleneck

Current software load gates (`warp-modeld`) verify an adapter on the CPU and then copy bytes across PCIe or unified memory into GPU VRAM. The GPU driver, firmware, and DMA path sit inside a large trusted computing base (TCB), leaving a time-of-check-to-time-of-use gap and relying on GPU floating-point semantics.

### Hardware Primitive (`hypothesis`)

Enforce Hard Veto 3 directly in memory-controller hardware using two simple blocks:

1. **Hardware write-protect latches on Base Weight Bank `W0`:** Once `W0` loads and hashes at boot or model load, hardware latches make `W0` strictly read-only during inference. No software command can mutate base weights.
2. **Inline Integer Verification Engine (IVE) on the Adapter Bank DMA path:** Every incoming low-rank adapter slab `(B_q, A_q)` streams through a fixed-function unit before the Adapter Bank enable latch opens. The IVE computes a streaming SHA-256 manifest digest plus a division-free integer `FixedRadixCertificate` leakage bound against a committed integer preservation basis `U0` (`d_in x k_c`):

```text
|| B_q * (A_q * U0) ||_F^2 <= tau_int^2 * S_radix
```

Using `M1 = A_q @ U0` (`r * d_in * k_c` MACs) followed by `M2 = B_q @ M1` (`d_out * r * k_c` MACs) requires strictly integer multiply-accumulates and bit-shifts with zero floating-point rounding ambiguity.

### Exact Arithmetic (`verified`)

| Model Profile | Adapted Projections (`o + down`) | Rank `r`, Basis `k_c` | Adapter F16 Size | Total Integer MACs | Time @ `64 GMAC/s` | Time @ `256 GMAC/s` |
| --- | --- | --- | --- | --- | --- | --- |
| **4B (`L=36`, `d=2560`)** | `72` projections | `r=16`, `k_c=256` | `11.25 MiB` | `1.510 GMAC` | `23.59 ms` | `5.90 ms` |
| **27B (`L=64`, `d=5120`)** | `128` projections | `r=32`, `k_c=256` | `80.00 MiB` | `10.737 GMAC` | `167.77 ms` | `41.94 ms` |

A `64`-MAC integer systolic array at `1.0 GHz` (`64 GMAC/s`) occupies under `0.5 mm^2` in modern CMOS and certifies all 72 projections of a 4B adapter in `23.59 ms` before activating the memory bank.

### Refutation Test and Kill Condition

- **Experiment:** Synthesize the streaming SHA-256 plus INT32 MAC IVE on a mid-range FPGA or cycle-accurate Verilator model and compare bit-for-bit against `weft`'s CPU `FixedRadixCertificate`.
- **Kill condition:** Refuted if real-checkpoint preservation requires `k_c > d_in / 2` (pushing verify cost near a full forward pass) or if per-layer integer leakage correlates poorly (`R^2 < 0.5`) with multi-layer behavioral drift on real transformers.

## Thesis 2: Fused Native Multi-Adapter Additive SGMV Datapaths

### Measured L2/L3 Bottleneck

Single-batch decode (`B = 1`) is memory-bandwidth bound. Serving `N` simultaneous adapters (for example `corpus` + `weft-eido` + `formal-verification`, or future `N = 5` to `8` packs) traps software between two bad options:

1. **Offline pre-merge:** Storing `2^N - 1` composite checkpoints (`7` for `N=3`, `31` for `N=5`, `255` for `N=8`) exhausts VRAM and kills `O(1)` per-request toggling.
2. **Unfused per-adapter launches:** Stock GPU stacks launch separate small kernels per adapter and projection, round-tripping intermediate activations through HBM (`216` extra launches per token for `N=3` on 4B `o+down`, or `3,584` extra launches per token for `N=8` all-linear on 27B).

### Hardware Primitive (`hypothesis`)

Pair the main base-weight GEMV stream with a **Fused Multi-Slot SGMV Accumulator** backed by a small on-chip **Adapter SRAM Scratchpad**. While input vector `x` stays resident in registers, the low-rank unit reads active scaled slices `(A_m, B_m)` for all `g_m(z) != 0`, sums `sum_m g_m(z) * B_m * (A_m * x)` in one fused reduction register, and adds directly into the base GEMV accumulator before normalization.

### Exact Bandwidth Roofline (`verified`)

| Configuration | Base Decode Floor | Adapter Footprint (`F16`) | Fused HBM Stream Overhead | Unfused Launch Overhead (`8 us`/launch) | With `siliquant` 4.5-Bit Adapter Quant |
| --- | --- | --- | --- | --- | --- |
| **4B, `N=3` (`r=16`, `72` projs, `350 GB/s`)** | `6.44 ms/tok` | `33.75 MiB` (fits in SRAM) | `+0.101 ms` (`+1.57%`) or `0%` in SRAM | `+1.728 ms` (`+26.82%`, `17x` bytes floor) | `+0.028 ms` (`+0.44%`) |
| **27B, `N=3` (`r=32`, all-linear, `320 GB/s`)** | `51.14 ms/tok` | `912.0 MiB` (`0.891 GiB`) | `+2.99 ms` (`+5.84%`) | `+10.75 ms` (`+21.03%`) | `+0.84 ms` (`+1.64%`) |
| **27B, `N=8` (`r=32`, all-linear, `320 GB/s`)** | `51.14 ms/tok` | `2,432 MiB` (`2.375 GiB`) | `+7.97 ms` (`+15.58%`) | `+28.67 ms` (`+56.07%`) | `+2.24 ms` (`+4.38%`) |

Applying `Moissanite-Labs/siliquant`'s verified ball-cut integer quantization (4.5 bits effective including exact outlier retention for `0.17 percent` of weights) cuts fused `N=8` adapter bandwidth by `3.56x`, bringing 8 simultaneous 27B adapters down to `+4.38 percent` decode latency.

### Refutation Test and Kill Condition

- **Experiment:** Implement a single fused software Triton/CUDA/Metal multi-slot SGMV kernel (`N in {1, 3, 5, 8}`) and benchmark against stock `llama-server` multi-`--lora` on 8 GiB RTX 3080 and 64 GiB M1 Max.
- **Kill condition:** Refuted as an L1 hardware requirement if a pure software fused kernel already stays within `3 percent` of the HBM bandwidth floor at `N = 8` simultaneous adapters.

## Thesis 3: Capability-Tagged KV and Hybrid Recurrent-State Banks

### Measured L2/L3 Bottleneck

Modern hybrid attention plus linear-attention / SSM / DeltaNet models (`Qwen3.5`, `Qwen3.8`, `LFM3`) fold every past token into fixed-size recurrent state matrices `S_t`. Rolling back an adapter via `warp-modeld`'s kill switch or switching L5 syntax zones mid-session today forces flushing KV and recurrent state followed by full prompt re-prefill. Re-prefilling a `16,384`-token context on a 4B model at `1,500 tok/s` stalls for `10.92 seconds` per switch.

### Hardware Primitive (`hypothesis`)

Attach a **64-bit Adapter-Mask Capability Tag** (`tag = H_64(checkpoint_id || active_slot_mask || zone_id)`) to every KV-cache page table entry and maintain hardware copy-on-write **recurrent-state checkpoint banks** at Layer 5 zone boundaries:

1. **Shared read-only base prefix (`tag = BASE_0`):** All adapter combinations read clean `W0` KV prefix pages with zero memory duplication.
2. **Single-cycle capability revocation:** Revoking adapter bit `i` masks out every KV page whose tag carries bit `i` in one cycle with zero memory scrub.
3. **Zone-boundary recurrent snapshots:** Saving one pre-adapter BF16 recurrent state snapshot `S_entry` per zone transition restores clean pre-adapter state in microseconds without re-prefill.

### Exact Memory and Restore Arithmetic (`verified`)

| Hybrid Model Profile | SSM Layers / Heads / State | One Snapshot Size (`BF16`) | `8` Tagged Checkpoints | Share of System Memory | Restore Time (DMA) | Speedup vs `16k` Re-Prefill |
| --- | --- | --- | --- | --- | --- | --- |
| **4B Hybrid (`8 GiB` @ `350 GB/s`)** | `24` layers, `16` heads, `64x64` | `3.00 MiB` (`3,145,728 B`) | `24.0 MiB` | `0.29 percent` | `0.009 ms` (`9 us`) | `> 1,200,000x` vs `10.92 s` |
| **27B Hybrid (`64 GiB` @ `320 GB/s`)** | `48` layers, `32` heads, `64x64` | `12.00 MiB` (`12,582,912 B`) | `96.0 MiB` | `0.15 percent` | `0.039 ms` (`39 us`) | `> 277,000x` vs `10.92 s` (`1,500 tok/s` floor) |

### Refutation Test and Kill Condition

- **Experiment:** Prototype software KV page tagging plus zone-boundary recurrent-state checkpointing (`--ctx-checkpoints` extension in `llama.cpp`) on a hybrid 4B model and verify bit-identical output after `(mount -> generate -> rollback -> resume)` versus fresh `W0` prefill.
- **Kill condition:** Refuted as an L1 hardware requirement if pure software HBM checkpointing already achieves `< 1 ms` rollback and `< 2 percent` memory overhead, or if real workflows switch zones too rarely (`< 1` per `10` turns) for re-prefill latency to matter.

## Thesis 4: Deterministic Exact-Radix Verification Units for Zone A Replay

### Measured L2/L3/L1 Bottleneck

Non-associative IEEE-754 floating-point reductions cause identical GPU GEMM math to produce different bit patterns across warp schedules and hardware generations. This forces `weft`'s reproducible compiler (`mde-compile`) onto slower CPU `float64` to guarantee 0-byte cross-host re-derivation (Hard Veto 1), and creates the split between Zone A (CPU exact) and Zone B (GPU approximate).

### Hardware Primitive (`hypothesis`)

Add a **Kulisch-Style Exact Fixed-Radix Accumulator** dedicated to the verification and covariance-compilation datapath (not required on every training step). Integer fixed-radix addition is strictly associative and commutative regardless of parallel reduction tree order, guaranteeing 0-byte identical outputs across any conforming hardware.

### Exact Bit-Width Arithmetic (`verified`)

- **Full BF16 exact superaccumulator:** BF16 (`1` sign, `8` exponent, `7` mantissa bits) has smallest subnormal `2^-133`. The smallest nonzero product is `2^-266` and the largest product is strictly below `2^256` (MSB bit `255`), giving an exact product span of `522` bits. Adding `64` carry and sign guard bits yields `586` bits, which fits cleanly in a `640`-bit (`10 x 64-bit` word) accumulator with a single canonical round-to-nearest-even output stage.
- **Compact block-scaled integer path (aligned with `siliquant`):** `siliquant` proved that groups of `G = 128` weights are optimal on `82` of `85` real matrices at 4.5 bits. For signed INT8 weights over `G = 128`, the worst-case block dot product is `128 * 127 * 127 = 2,064,512 < 2^22`, fitting in INT32. Summing across `2^20` blocks stays below `2^42 << 2^63`, enabling 100 percent associative, zero-drift INT64 accumulation on compact hardware.

### Refutation Test and Kill Condition

- **Experiment:** Implement block-scaled INT64 and Ozaki-scheme deterministic GPU covariance accumulation (`C^(t) = K K^T`) across x86_64 CUDA (`RTX 3080`) and arm64 Metal (`M1 Max`), verifying 0-byte identical `.gpatch` digests against CPU `float64`.
- **Kill condition:** Refuted as an L1 hardware requirement if deterministic INT64 or Ozaki software kernels on commodity GPUs already achieve 0-byte cross-host re-derivation within `< 2x` of CPU `float64` compile latency.

## Priority Order Before Any Silicon Investment

Hardware work in `loom` follows strict falsification order. Software proofs run first, FPGA prototypes run second, and silicon theses survive only where software hits a proven physical wall:

1. **Test Thesis 3 in software first** (`llama.cpp` zone-boundary recurrent checkpoints on a real 4B hybrid model).
2. **Test Thesis 2 in software second** (fused Triton/Metal multi-slot SGMV kernel for `N = 1, 3, 5, 8` plus 4.5-bit adapter compression).
3. **Test Thesis 4 in software third** (cross-host deterministic INT64 / Ozaki covariance compilation between CUDA and Metal).
4. **Test Thesis 1 on FPGA only after real-checkpoint `k_c` and `R^2` bounds clear `weft`'s Q1 and Q3 experiments.**
