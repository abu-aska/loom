# Latent Lattice Convergence Across Layers 5 Through 1

This paper derives the cross-layer mathematical, security, and hardware physics consequences of **Latent Lattice Language Models** ([`arXiv:2611.21608v1`](https://arxiv.org/abs/2611.21608), Duggal et al., MIT CSAIL and Adobe, 16 Nov 2026) for the Siliconcordat stack (`mde`, `exo`, `warp`, `weft`, `loom`).

As of 2026-11-19, the authors' project page ([`latent-lattice-language-models`](https://shivamduggal4.github.io/latent-lattice-language-models/)) lists `Code (coming soon)` with zero public code or model weights released. All upstream paper measurements below are tagged `source claim`. Every mathematical proof, rollout simulation, and hardware roofline is tagged `verified` and checked reproducibly by [`scripts/verify_lattice.py`](../scripts/verify_lattice.py).

## 1. Primary-Source Mechanism and Reported Benchmarks (`source claim`)

A standard autoregressive Transformer routes all active computation through one vertical residual stream $h_t^\ell \in \mathbb{R}^{d_{\mathrm{model}}}$ across layers $\ell \in \{1, \dots, N\}$, appending keys and values to a passive KV cache $\mathcal{M}_t^\ell$.

The Lattice of Latents partitions the backbone into Early (`E`), Lattice (`L`), and Late (`D`) blocks (such as `E1/L20/D1` or `E4/L16/D4`) and adds one persistent horizontal latent $r_t^\ell \in \mathbb{R}^{d_r}$ per layer $\ell \in L$, initialized from a learned $r_0^\ell$.

### 1.1 Horizontal Update and Vertical Conditioning Equations

Each Lattice layer $\ell \in L$ updates its horizontal latent through an affine diagonal gated recurrence (run in `fp32` for scan stability, admitting an exact token-parallel associative scan during training):

```text
n_t^l     = Norm_in(h_t^{l-1})
Delta_t^l = softplus(W_Delta^l n_t^l + W_{e,Delta}^l Norm_e(h_t^0) + b_Delta^l)
g_t^l     = exp(-exp(a^l) * Delta_t^l)           in (0, 1)^{d_r}
c_t^l     = SiLU(W_r^l n_t^l + W_{e,c}^l Norm_e(h_t^0) + b_r^l)
b_t^l     = (1 - g_t^l) * (c_t^l + N_t^l)        (N_t^l = 0 except optional J3 bottom feedback)
r_t^l     = g_t^l * r_{t-1}^l + b_t^l
```

Here input injection (`inj`) adds zero-initialized token-embedding terms $W_{e,\Delta}^\ell, W_{e,c}^\ell$. An optional same-timestep readout stream (`vstream` or `vs`) accumulates $s_t^\ell \in \mathbb{R}^{d_r}$ upward from $s_t^{\ell_0-1} = 0$, forming $\tilde{r}_t^\ell = \mathrm{Norm}(r_t^\ell) + \mathrm{Norm}(s_t^\ell)$ without modifying raw carried $r_t^\ell$.

An optional Jacobi refiner (`J3`, three sweeps, `~2.6x` train FLOPs) feeds a SwiGLU transform of $r_{t-1}^{\mathrm{top}}$ into the bottom Lattice layer $\ell_0$.

Every conditioning projection is zero-initialized (identity at initialization) and acts directly on the vertical stream:

1. **Attention and KV-cache writes via FiLM (`fp32`):** For each projection $p \in \{q, k, v\}$, $p_t^\ell = (W_p^\ell \hat{h}) \odot (1 + \tanh(W_p^\gamma \tilde{r}_t^\ell)) + W_p^\beta \tilde{r}_t^\ell$ (gain shared across 4 channel groups per head, shift per channel). Crucially, the modulated $(k_t^\ell, v_t^\ell)$ are written directly into $\mathcal{M}_t^\ell$.
2. **SwiGLU MLP modulation:** Additive shifts $\beta_{\mathrm{gate}}(\tilde{r}_t^\ell)$ and $\beta_{\mathrm{up}}(\tilde{r}_t^\ell)$ modify the gate and up pre-activations of `MLP^l`.
3. **Optional decoding head (used only at $d_{\mathrm{model}} = 256$):** Projects $\mathrm{Norm}(h_t^N)$ and $\mathrm{Norm}_{\mathrm{head}}(r_t^{\mathrm{top}})$ into a shared readout space of width $d_s$.
4. **Recurrent backbones (`GDN`, `Mamba-2`, `Triadic GDN`, `GDN-Mamba-2` hybrid):** Leaves native fixed-size memory matrices intact and applies FiLM to every memory read, write, decay, gate, and routing pre-activation.

### 1.2 Reported Paper Measurements and Scope Boundaries (`source claim`)

| Comparison (FineWeb-Edu, `2048` Context) | Baseline | Latent Lattice Variant | Reported Delta |
| --- | --- | --- | --- |
| **400M Transformer (20B tokens, Table 1)** | `Base-24L` (`406.7M`, `15.410` PPL) | `LLLM(908,256) inj+vs` (`405.6M`, `14.400` PPL) | Matches 609M `Base-40L` (`14.400`) with `33%` fewer params |
| **600M Transformer (20B / 30B, Tables 1 & 3)** | `Base-40L` (`609.1M`, `14.400` / `13.802`) | `LLLM(1024,1024)` (`603.0M`, `13.704` / `13.189`) | `-4.8%` / `-4.4%` PPL, `+2.00` pts 5-shot avg |
| **Residual-stream composition (20B, Sec. 4.2)** | `Base` `15.41`, `HC+x0` `14.22` | `Lattice+HC+x0` (`405.9M`, `13.61` PPL) | `-11.7%` vs plain, `-4.3%` over `HC+x0` |
| **GSM8K-Aug math transfer (Table 5)** | `Base-40L` (`33.5%`, iso-PPL `14.40`) | `LLLM(908,256) re+vs` (`43.6%`), `J3` (`44.9%`) | `+10.1` to `+11.4` GSM8K pts at matched pretrain PPL |
| **GDN recurrent backbones (10B, Sec. 4.3)** | `256K` pure GDN (`16.11` PPL, `44.45%` 0-shot) | `64K` Lattice GDN (`16.05`), `32K` (`44.88%` 0-shot) | Beats `4x` larger native state in PPL (`8x` in 0-shot) |
| **GDN memory geometry (Table 2, `256K`)** | Pure: `r_ent 37.92`, `r_stable 2.50`, `G_1 7.96` | Lattice: `r_ent 33.42`, `r_stable 2.13`, `G_1 13.32` | `-11.9%` `r_ent`, `-15.0%` `r_stable`, `+67.4%` alignment `G_1` |
| **Stateless FiLM control (10B, Fig. 10)** | Stateless QKV `16.29`, QKV+MLP `16.32` | Recurrent QKV `15.99`, QKV+MLP `15.63` | Recurrent history drives MLP gain (stateless hurts MLP) |

**Honest upstream boundaries:** All published experiments top out at `603M` parameters and `2048` context tokens. Fixed-sweep `J3` models lose perplexity under single-pass sequential inference (`14.026` to `14.733`), and zero inference wall-clock or multi-adapter measurements exist in the paper.

## 2. Three-Axis Convergence: Vertical Weights x Horizontal Lattice x L5 Zones

In Siliconcordat, static Layer 2 weight compilation (`weft`) acts along the vertical axis, Layer 5 syntactic zones (`mde`) partition context deterministically, and Lattice streams act along the horizontal time axis. Combining all three solves one fundamental vertical wall while introducing two sharp new failure modes.

### 2.1 Theorem 1: Shared-Token Disambiguation Without Vertical Capacity Loss (`verified`)

In `docs/03-zone-subspace-duality.md`, static vertical adapters $\Delta W = \Delta W_1 + \Delta W_2$ hit an irreducible wall whenever two domains (`prose` vs `formal_proof`) share an identical token activation $h_t^{\ell-1}$ with opposing targets $y_A \neq y_B$. Any single static linear map incurs minimum mean squared error $\|y_A - y_B\|_2^2 / 4$.

Now partition horizontal capacity into an immutable Base bank plus $M$ capability-scoped MDE side-channels $r_t^\ell = [r_{t,0}^\ell \mid r_{t,1}^\ell \mid \dots \mid r_{t,M}^\ell]$ gated by L5 `zone-manifest/v0.1` masks $z_m(t) \in \{0, 1\}$, with zero-initialized per-slot FiLM shifts $\beta_m(\mathrm{Norm}(r_{t,m}^\ell))$. Because FiLM conditioning is additive over channels:

- Inactive slots ($z_m = 0$) inject exact `0.0` perturbation into `Q`, `K`, `V`, MLP pre-activations, and `K0` outputs while consuming `0` dimensions of vertical null-space capacity $m(t) = d_{\mathrm{in}} - \mathrm{rank}(K_0)$.
- Active orthogonal slots separate 100 percent identical shared-token activations cleanly (`scripts/verify_lattice.py` Part 1: static vertical MSE floor **`8.877435`** drops to **`1.150e-31`**, with **`0.0`** inactive base drift).

### 2.2 Global `RMSNorm` Cross-Channel Bleed Catch (`verified`)

`arXiv:2611.21608` normalizes the full horizontal vector through one global $\hat{r}_t^\ell = \mathrm{RMSNorm}(r_t^\ell)$. Appending a capability channel $r_{\mathrm{slot}}$ into that shared vector before normalization creates a subtle nonlinear leak even when $r_{\mathrm{slot}} \perp r_{\mathrm{base}}$: the shared RMS denominator rescales the base channel by

```text
s = sqrt((||r_base||_2^2 / d_tot + eps) / ((||r_base||_2^2 + ||r_slot||_2^2) / d_tot + eps)) != 1
```

In `scripts/verify_lattice.py` Part 1, activating an orthogonal slot under global `RMSNorm` causes **`24.77 percent`** (`0.247742`, matching `|1 - s|` to 12 decimal places) relative distortion of the untouched base slice. Replacing global normalization with **per-bank `RMSNorm`** (normalizing $r_{t,0}^\ell$ separately from each $r_{t,m}^\ell$) and isolating `vstream` and `J3` per bank restores exact **`0.0`** cross-channel bleed.

### 2.3 Theorem 2: Persistent Horizontal-to-KV-Write Poisoning Law (`verified`)

Because FiLM-modulated keys and values write directly into $\mathcal{M}_t^\ell$ (`Sec. 1.1`), horizontal persistence introduces a double-vector rollback hazard that does not exist in stateless Transformers. Suppose a revoked or adversarial adapter perturbs $r_{t_0}^\ell$ by $\delta r_{t_0}^\ell \neq 0$ at step $t_0$ and the OS kill switch disables the adapter before $t_0 + 1$.

For all $t > t_0$, the affine update propagates the perturbation with exact closed-form decay:

```text
delta_r_t^l = (prod_{tau = t_0 + 1..t} g_tau^l) * delta_r_{t_0}^l
```

With Mamba-2 style slow decay gates (`g` in `[0.80, 0.995]`), poisoning half-lives $t_{1/2} = \ln(0.5) / \ln(g)$ span **`3.11`** tokens (`g = 0.80`), **`13.51`** tokens (`g = 0.95`), and **`138.28`** tokens (`g = 0.995`). Worse, on recurrent backbones like GDN, Table 2 shows the Lattice concentrates memory into lower stable rank while boosting dominant-direction query alignment $G_1$ up to `13.32x` above chance, amplifying contamination directly along the highest-leverage readout axis.

Measured on a faithful 12-step Latent Lattice attention rollout (`scripts/verify_lattice.py` Part 2, persistence formula verified to `4.40e-16`, poisoning at $t_0 = 3$, revocation before $t = 4$):

| Rollback Regime at `t = 4` | Horizontal Drift `t = 4` | Key Write Drift `t = 4` | Attention Output Drift `t = 4` | Output Drift `t = 11` | Safe Rollback? |
| --- | ---: | ---: | ---: | ---: | --- |
| **Regime A: Adapter scale zeroed only** | `2.412059` | `5.985623` | `1.995165` | `3.133528` | **FAIL** (stale KV + ongoing writes) |
| **Regime B: KV cache erased only** | `2.412059` | `5.985623` | `4.415328` | `5.487759` | **FAIL** (re-poisons fresh KV immediately) |
| **Regime C: Atomic KV + horizontal restore** | `0.000000` | `0.000000` | `0.000000` | `0.000000` | **PASS** (bit-exact `W0` recovery) |

**Direct L3 `warp` consequence:** Erasing only KV pages (`POST /slots/{id}?action=erase`) fails closed on Latent Lattice checkpoints because surviving $\delta r_4^\ell$ immediately writes poisoned keys and values into the freshly cleared cache. Layer 3 Stage 4 kill switches MUST verify atomic flush or snapshot restore across all active banks (`kv_cache`, `ssm_recurrent`, `lattice_horizontal_streams`, and any `J3` top buffer) and quarantine the slot (`ERR_LATTICE_FLUSH_FAILED`) if horizontal reset is unconfirmed.

## 3. Capability-Partitioned `L_0` Cartridges and Asymmetric FiLM Packing

### 3.1 Deterministic `L_0` Latent Cartridges Under Hard Vetoes 1 to 5 (`verified`)

Every Lattice layer starts from an initial state $r_0^\ell \in \mathbb{R}^{d_r}$. An MDE compiler can therefore compile a zone-scoped initial horizontal state cartridge $L_0 = \{r_{0,m}^\ell\}_{\ell \in L}$ deterministically on CPU `float64` directly from Plane 1 anchors and `W0` digests:

- **Hard Veto 1 (0-byte re-derivable):** `scripts/verify_lattice.py` Part 3 verifies exact SHA-256 identity on re-derivation and immediate rejection on a 1-byte Plane 1 change.
- **Extreme compactness:** A 36-layer `d_r = 256` `L_0` cartridge occupies **`18,432` bytes (`18.0 KiB`) in BF16** or **`36,864` bytes (`36.0 KiB`) in FP32**, which is **`640.0x`** (BF16) or **`320.0x`** (FP32) smaller than a 4B rank-16 F16 LoRA (`11.25 MiB` in `docs/04`).
- **Hard Vetoes 2 to 5:** Conflicting zones remain `CONTESTED` in `zone-manifest/v0.1`, base weights `W0` stay untouched, and Plane 1 remains the sole source of authority.

### 3.2 Honest Boundary: The `L_0` Exponential Decay Horizon (`verified`)

Injecting a pure initial state $L_0$ into an unmodified base channel with forgetting gate $g < 1$ decays exponentially as $g^t$. In `scripts/verify_lattice.py` Part 3, an unmodified channel at `g = 0.95` retains only **`0.989 percent`** (`0.009888`) by token `90`, and even a slow channel at `g = 0.995` drops below half amplitude (`0.498205`) by token `139`.

Two architectural rules resolve this without violating Hard Vetoes:

1. **Zone-locked persistent side-channels (`g_m = 1.0`):** Locking $g_t^{\ell,m} \equiv 1.0$ while inside zone $z_m$ preserves `100.0 percent` (`1.0`) of $L_0$ across `10,000+` tokens and zeroes cleanly (`z_m = 0`) on zone exit.
2. **Coupled dynamic FiLM adapters:** Where input-dependent rules exceed a constant per-zone state shift, attach low-rank FiLM adapters $\Delta W_{\mathrm{FiLM}} = B_F A_F$ reading the horizontal trajectory $R_0$.

### 3.3 Asymmetric Factor Leakage on FiLM Conditioning Adapters (`verified`)

Applying `docs/05`'s Asymmetric Factor Leakage Theorem to low-rank FiLM adapters compiled orthogonal to preserved base horizontal trajectories ($A_F R_0 = 0$) yields exact cancellation of left-factor quantization error $E_B$:

```text
Q(B_F) * Q(A_F) * R_0 = Q(B_F) * (E_A * R_0)
```

Measured across `N = 6` sequential FiLM adapters (`d_out = 32`, `d_r = 24`, `k0 = 6`, `r = 2`) in `scripts/verify_lattice.py` Part 3:

| FiLM Quantization Format (`B_F / A_F`) | Relative Base Trajectory Leakage (`N = 6`) | Comparison |
| --- | ---: | --- |
| **`fp64 / fp64` (reference)** | `1.503e-16` | Machine epsilon |
| **`int4 / fp64` (asymmetric exact `A`)** | `1.498e-16` | Zero added leakage from 4-bit `B_F` |
| **`int8 / int8` (uniform INT8)** | `3.856e-03` | INT8 baseline |
| **`int4 / int8` (asymmetric sweet spot)** | `3.870e-03` | Within `0.35%` of `int8/int8`, **`22.60x`** lower than `int4/int4` |
| **`int8 / int4` (reversed control)** | `8.758e-02` | Confirms `E_A` alone drives collapse (`22.63x` worse) |
| **`int4 / int4` (uniform INT4)** | `8.744e-02` | Crosses `8.7%` leakage collapse |

## 4. L1 `loom` Hardware Physics and Roofline Update (Extending `docs/04` Thesis 3)

Because `arXiv:2611.21608` carries horizontal latents in `fp32` (`4` bytes/scalar, Table 6) while `vstream` is strictly same-timestep (`0` carried bytes), the persistent state footprint of a Latent Lattice is dramatically smaller than matrix-valued SSM states in `docs/04` Thesis 3.

### 4.1 Exact FP32 State Footprints and DMA Restore Rooflines (`verified`)

| Model Profile (FP32 Horizontal State) | Lattice Layers and Width | One Snapshot | `8` Tagged Checkpoints | Share of Memory | DMA Restore | Comparison vs `docs/04` SSM |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| **Paper 406M (`E1/L20/D1`)** | `20` layers, `d_r = 256` | `20.0 KiB` | `160.0 KiB` | `n/a` | `n/a` | Tiny fixed carry vector |
| **Paper 603M (`E1/L20/D1`)** | `20` layers, `d_r = 1024` | `80.0 KiB` | `640.0 KiB` | `n/a` | `n/a` | Fits inside L2 cache |
| **4B Scaled (`RTX 3080`, `8 GiB @ 350 GB/s`)** | `32` layers, `d_r = 512` | `64.0 KiB` | `512.0 KiB` | `0.0061%` | `0.187 us` | **`48.0x`** smaller than `3.00 MiB` 4B SSM |
| **27B Scaled (`M1 Max`, `64 GiB @ 320 GB/s`)** | `60` layers, `d_r = 1024` | `240.0 KiB` | `1.875 MiB` | `0.0029%` | `0.768 us` | **`51.2x`** smaller than `12 MiB` (`204.8x` vs `48 MiB`) |
| **Paper `64K` Lattice-GDN vs `256K` Pure GDN** | `22` GDN BF16 + `20` Lattice FP32 | `2.770 MiB` | `22.156 MiB` | `n/a` | `n/a` | **`3.97x`** smaller than `11.000 MiB` pure `256K` GDN |

### 4.2 Honest Trade-Off: Decode Weight-Streaming Cost of FiLM Projections (`verified`)

While horizontal *state* is sub-megabyte, FiLM and update projection *weights* stream from HBM on every decode token (`B = 1`). Bolting full-rank FiLM projections naively onto an unchanged 4B Transformer (`32` layers, `d_v = 2560`, `d_attn = 2560`, `H = 20`, `d_ff = 9728`, `d_r = 512`) adds **`532.41M` parameters** (`285.61 MiB` at `4.5`-bit `siliquant` quantization), adding **`+0.856 ms/tok`** (`+13.28 percent` of the `6.44 ms/tok` base decode floor on RTX 3080).

That arithmetic explains why `arXiv:2611.21608` narrows vertical width $d_{\mathrm{model}}$ to keep Lattice models iso-parameter (`1024 -> 908` at 400M) and why MDE side-channels should stay low-rank (`r = 4` to `16`) and asymmetrically packed (`int4 / int8`) rather than adding dense unpruned FiLM tables.

### 4.3 Thesis 3b: On-Chip SRAM Lattice Bank and Single-Cycle Multi-Bank Revocation (`hypothesis`)

Because `8` tagged FP32 horizontal checkpoints require only `512 KiB` (4B) to `1.875 MiB` (27B), future `loom` silicon can pin all active horizontal streams and zone rollback snapshots **100 percent in on-chip SRAM** (zero HBM read/write traffic for horizontal state updates).

Binding the KV page-table capability mask, SSM bank pointer, and on-chip Lattice SRAM bank pointer to one single-cycle `REVOKE_SLOT(mask)` instruction closes the horizontal-to-KV re-poisoning window in hardware.

## 5. Concrete Falsification Tests for Layers 2, 3, and 1

1. **Test L1 (`siliconcordat/weft` E7):** Run 3-domain shared-token composition comparing vertical `BetaEdit`, capability-partitioned horizontal Lattice channels, and coupled vertical+horizontal MDE alongside the KV-only vs atomic rollback proof. Refuted if horizontal isolation fails to reduce shared-token cross-domain interference or fails 0-byte re-derivation.
2. **Test L2 (`siliconcordat/warp` multi-bank Stage 4):** Enforce `ERR_LATTICE_FLUSH_FAILED` whenever a checkpoint declares horizontal lattice streams and backend reset confirmation is missing. Refuted if a KV-only flush passes Stage 4 or atomic restore leaves non-zero `W0` drift.
3. **Test L3 (Real open-weights Lattice checkpoints at `>= 1B` scale):** Measure whether per-bank `RMSNorm` side-channels and asymmetric `int4 / int8` FiLM adapters preserve `>= 95 percent` base `K0` retention across 3 composed domains when public Latent Lattice checkpoints become available.
4. **Test L4 (Thesis 3b software-before-silicon kill test):** Refuted as an L1 hardware requirement if software L2/SLC pinned horizontal checkpoints on commodity GPUs already achieve `< 5 us` atomic multi-bank rollback with zero KV re-poisoning.
