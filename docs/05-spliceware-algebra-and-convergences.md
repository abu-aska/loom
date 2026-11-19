# Spliceware Algebra and Deep Cross-Layer Convergences

This paper pulls three deep cross-layer threads across Layers 5 through 1 (`mde`, `exo`, `warp`, `weft`, `loom`) to their mathematical limits. Every claim separates what holds by proof or exact simulation from where each mechanism breaks.

All derivations, simulations, and numerical tables below are verified reproducibly by [`scripts/verify_convergences.py`](../scripts/verify_convergences.py) using standard-library Python with zero external packages.

## 1. The Unified Splice Algebra (L5 to L1) and Vertical Zone Compilation

All five layers of the Siliconcordat stack instantiate one shared algebraic structure: a **Verified Splice System** `S = (B, D, (+), V, I, rho)`:

- **Immutable base state `S0` in `B`:** Addressed by cryptographic digest `h(S0)` (Git `base_tree` at L5, signed memory root at L4, btrfs snapshot and `W0` digest at L3, 4-layer checkpoint fingerprint at L2, write-protected `W0` memory bank at L1).
- **Content-addressed bounded delta `Delta` in `D`:** Bound strictly to `h(S0)` via digest `h(Delta) = H(Delta || h(S0))`.
- **Application `S0 (+) Delta` with `O(1)` rollback `rho`:** `S0` never mutates in place, so `rho(S0 (+) Delta) = S0` with a 0-byte diff.
- **External Anti-Goodhart verifier `V(S0, Delta) in {0, 1}`:** Owned outside `Delta`'s trust boundary (`docs/02-unified-verification-primitive.md`).
- **Fail-closed composition and interference metric `I(Delta_1, Delta_2; S0)`:** Two individually verified deltas compose only when `I(Delta_1, Delta_2; S0) <= tau` AND post-composition verification passes `V(S0, Delta_1 * Delta_2) = 1`.

### 1.1 Partial Commutative Monoid Condition (Where Composition Works and Where It Breaks)

On general overlapping domains, splice composition is neither commutative nor closed under `V`. Two individually valid code edits in separate files can conflict semantically at link time, and two individually valid weight adapters can drift nonlinearly across transformer layers.

**Theorem 1 (Zone-Isolated Partial Commutative Monoid, `verified`):** Let `Z = {z_1, ..., z_k}` partition the workspace into deterministic syntax zones. Suppose two verified deltas `Delta_a` (supported on `z_a`) and `Delta_b` (supported on `z_b`, `z_a != z_b`) satisfy:

1. **Strict zone isolation:** Each delta acts as the exact identity outside its zone (untouched byte spans at L5, scale `g_a(z_b) = 0.0` at L4/L3/L2, disjoint hardware capability tag at L1).
2. **No shared mutable cross-zone effect:** Neither delta mutates shared global state, contested policy heads, or uncheckpointed recurrent state.

Then composition over zone-disjoint deltas forms a commutative partial monoid with exact zero interference `I(Delta_a, Delta_b; S0) = 0` and order-independent application `Delta_a * Delta_b = Delta_b * Delta_a`. Inside the same zone (`z_a = z_b`), commutativity fails and full post-composition verification `V(S0, Delta_a * Delta_b) = 1` remains mandatory.

### 1.2 Vertical Zone Compilation From One Typed Manifest

Can one typed Zone Manifest `M = (Z, A, Pi, Phi)` anchored at Plane 1 and parsed at L5 mechanically generate all five layers with zero cross-layer drift?

**Sufficient conditions (`verified` in `compile_vertical_zone_manifest`):**

1. Every cell in the precedence matrix `Pi(z, a)` takes values strictly in `{0, 1, CONTESTED}`. Any `CONTESTED` entry aborts compilation immediately (Hard Veto 2).
2. All five layers derive deterministically from the single root digest `H(M)`:
   - **L5 (`mde`):** CST zone predicates and protected oracle path rules.
   - **L4 (`exo`):** Exact deterministic zone-to-scale map `g(z)` in `{0.0, 1.0}^|A|`.
   - **L3 (`warp-modeld`):** Only the reachable active adapter bitmasks require joint canary suites. For our 5 zones (`prose`, `formal_proof`, `ui_module`, `condensed_json`, `code`) and 4 adapters, theoretical combinations drop from `2^4 - 1 = 15` down to `4` reachable masks (`0b0010`, `0b0011`, `0b0110`, `0b1010`).
   - **L2 (`weft`):** Exact out-of-zone `y = 0` preservation sets and co-active partner lists per adapter (for example, `formal_verification` preserves `{prose, ui_module, condensed_json, code}` at zero shift and shares active covariance only with `corpus_epistemic`).
   - **L1 (`loom`):** Unique 64-bit hardware capability tag `H_64(H(M) || z_idx || z || bitmask)` per zone. Any 1-bit change in `M` rotates `H(M)` and every L1 bank tag atomically.

**Where Vertical Zone Compilation breaks:**

- **Mixed-zone single-token spans:** Inline formal identifiers inside English sentences (or prose docstrings inside code) cannot hold two contradictory scales on one token without sub-span splitting.
- **Mid-generation zone transitions:** A static CST manifest cannot see a model opening a fenced proof block mid-stream unless Layer 4 detects streaming fences and triggers a recurrent-state zone switch.

## 2. Continuous-Discrete Duality (L2 Parametric Space x L5 Structural Splicing)

Pure discrete search stalls on multi-step cliffs (`spliceware` `v3`: 0 of 106 reachable 1-step edits cross a 2-anchor gap). Pure continuous optimization glides smoothly into visible-probe reward hacks (`weft-loom`: 23x MLP and 459x transformer gaming) and shared-token interference (`docs/03-zone-subspace-duality.md`).

Coupling both spaces pairs **L5 discrete structural seams plus non-differentiable external oracles** with **L2 continuous proposal priors plus behaviorally deduplicated two-tier lexicase selection**.

### 2.1 Controlled Simulation Results (`verified` on 6-Slot Discrete Cliff, 20 Seeds, Budget 2,000)

In `scripts/verify_convergences.py`, a 6-slot program over alphabet `{0..7}` starts on an exact 2-step discrete cliff (`0/4` anchors for every 1-step edit) with a realistic 2-slot Goodhart shortcut `(7, 7)` that passes `4/4` visible anchors while failing `100 percent` of private holdouts.

We test two distinct landscapes plus two explicit failure regimes (all arms except `Fail F2` share the exact same private-holdout rejection rule for a fair ablation):

| Regime and Solver Arm | Solves (`20` Seeds) | Goodhart Hacks | Mean Evals | Structural Takeaway |
| --- | --- | --- | --- | --- |
| **Regime 1 (Separable cliff), Arm 1: Blind 1-step greedy** | `0 / 20` (`0%`) | `0` | `2000.0` | Exact single-step cliff deadlock |
| **Regime 1, Arm 2: Uniform 2-step + holdout** | `16 / 20` (`80%`) | `0` | `992.9` | Unstructured multi-step search wastes evals across non-seam pairs |
| **Regime 1, Arm 2b: L5 seams only + scalar + holdout** | `20 / 20` (`100%`) | `0` | `280.1` | On separable tasks, L5 structural seams deliver most of the gain |
| **Regime 1, Arm 3: L5 seams + L2 continuous prior + dedup lexicase** | `20 / 20` (`100%`) | `0` | `253.2` | Bounded continuous token priors refine seam search cleanly |
| **Regime 2 (Deceptive generalist trap), L5 seams + scalar** | `3 / 20` (`15%`) | `0` | `1743.2` | Scalar selection locks onto 2-anchor deceptive trap `[1,1,0,0]` |
| **Regime 2, Coupled L5 seams + L2 prior + dedup lexicase** | `20 / 20` (`100%`) | `0` | `714.5` | Keeps `[0,0,1,0]` and `[0,0,0,1]` specialists alive and recombines |
| **Failure Bound F1: Zero-specialist binary needle** | `0 / 20` (`0%`) | `0` | `2000.0` | No free lunch: zero stepping stones gives zero prior gradient |
| **Failure Bound F2: Coupled loop WITHOUT private holdout** | `7 / 20` (`35%`) | `13 / 20` (`65%`) | `n/a` | Without Axiom 2 holdouts, search collapses into visible shortcuts |

### 2.2 Ablation Findings and Failure Boundaries

1. **Behavioral deduplication is mathematically required:** Before deduplicating the stepping-stone pool by unique anchor-pass vector (`pool_by_sig`, behavioral deduplication gate `G5.3`), redundant `[1,1,0,0]` deceptive generalists flooded the fixed-size pool and dropped Regime 2 solve rate from `20/20` to `2/20`.
2. **Do not reinforce already-solved seam coordinates:** Reinforcing seam-group selection weights after solving one motif slowed Regime 1 from `253.2` to `427.6` evals by oversampling the solved seam. Bounded token priors paired with uniform seam coverage avoided lock-in.
3. **Strictly dominated intermediates remain unrecoverable:** If a true intermediate scores `[1,0,0,0]` while a deceptive trap scores `[1,1,0,0]`, the intermediate is strictly dominated on every visible anchor and even lexicase cannot distinguish it (`docs/02` Theorem 2 boundary).

## 3. Quantized Orthogonal Packing (`siliquant` x `weft` x `loom`)

Suppose `N` sequential `BetaEdit` low-rank adapters `Delta_j = B_j * A_j` (`B_j` is `d_out x r`, `A_j` is `r x d_in`) are compiled in `float64` so that `A_j * K_0 = 0` and `A_j * K_i = 0` for all `i < j`. What happens when `B_j` and `A_j` are quantized before simultaneous composition?

### 3.1 The Asymmetric Factor Leakage Theorem (`verified`)

Write the quantized factors as `Q(B_j) = B_j + E_B` and `Q(A_j) = A_j + E_A`. Expanding the composed action on any preserved key matrix `K_i` where `A_j * K_i = 0` yields an exact cancellation:

```text
Q(B_j) * Q(A_j) * K_i = (B_j + E_B) * (A_j + E_A) * K_i
                      = (B_j + E_B) * (A_j * K_i) + Q(B_j) * (E_A * K_i)
                      = Q(B_j) * (E_A * K_i)
```

**Consequence (`verified` analytically and numerically):** Left-factor quantization error `E_B` cancels identically. Quantizing `B_j` down to 4-bit `INT4` (or even ternary) introduces **exact zero additional null-space leakage** as long as `A_j * K_i = 0` holds. All quantization-induced cross-adapter leakage comes exclusively from `E_A` in the right factor `A_j`.

When `A_j` is quantized uniformly with precision `b_A` bits, independent rounding perturbations across `N` composed adapters accumulate as a random walk `Theta(sqrt(N) * 2^(-b_A))` relative to `||W0 K0||_F`, creating a sharp phase transition where `INT4` crosses `5 percent` relative leakage by `N = 3` adapters.

### 3.2 Measured Multi-Adapter Leakage Curves (`verified`, `d = 24`, `k0 = 6`, `r = 2`, `N = 1..6`)

Measured relative base leakage `|| (sum_{j=1..N} Q(B_j) Q(A_j)) K0 ||_F / || W0 K0 ||_F` from `scripts/verify_convergences.py`:

| Quantization Format | `N = 1` | `N = 2` | `N = 3` | `N = 4` | `N = 5` | `N = 6` |
| --- | --- | --- | --- | --- | --- | --- |
| **`fp64_both` (exact reference)** | `5.615e-17` | `6.396e-17` | `1.002e-16` | `1.113e-16` | `1.500e-16` | `1.524e-16` |
| **`asym_fp64A_int4B` (FP64 `A`, INT4 `B`)** | `5.505e-17` | `7.370e-17` | `1.047e-16` | `1.321e-16` | `1.560e-16` | `1.589e-16` |
| **`bf16_both` (BF16 `A` and `B`)** | `4.274e-04` | `5.859e-04` | `9.129e-04` | `1.112e-03` | `1.317e-03` | `1.334e-03` |
| **`int8_both` (INT8 `A` and `B`)** | `1.413e-03` | `1.770e-03` | `2.868e-03` | `3.170e-03` | `3.628e-03` | `3.705e-03` |
| **`asym_int8A_int4B` (INT8 `A`, INT4 `B`)** | `1.413e-03` | `1.771e-03` | `2.886e-03` | `3.179e-03` | `3.649e-03` | `3.729e-03` |
| **`int4_both` (INT4 `A` and `B`)** | `2.728e-02` | `3.909e-02` | `5.099e-02` | `5.773e-02` | `6.483e-02` | `6.446e-02` |

Three immediate engineering takeaways follow directly from this table:

1. **BF16 breaks float64 orthogonality by 13 orders of magnitude** (`5.6e-17` to `4.3e-4` at `N = 1`, reaching `1.33e-3` at `N = 6`). That confirms why `weft` must compute `FixedRadixCertificate` *after* BF16 quantization rather than on pre-quantization float64 matrices.
2. **Uniform INT4 destroys null-space guarantees** (`5.10 percent` leakage at `N = 3`, `6.45 percent` at `N = 6`).
3. **Asymmetric `INT8 A` + `INT4 B` is the practical sweet spot (`hypothesis` for real models):** Keeping `A_j` at INT8 (or BF16) while compressing `B_j` to 4-bit `siliquant` ball-cut quantization achieves `3.729e-3` leakage at `N = 6`, matching `int8_both` within `0.7 percent`, beating `int4_both` by `17.3x`, and cutting `B_j` memory bandwidth in half.

### 3.3 Exact Integer-Lattice Kernel Projection and the Siegel Explosion Catch

If the preserved basis itself lives on an integer grid `K_Z` (`d x k`), the integer right kernel `Lambda_ker = {a in Z^d : a^T K_Z = 0}` is a free integer lattice of rank `d - rank(K_Z)`. Choosing integer rows `A_Z` inside `Lambda_ker` with arbitrary quantized left factors `Q(B_j)` gives **exact zero integer leakage** across any number of composed adapters `N`:

```text
(sum_{j=1..N} Q(B_j) * A_j_Z) * K_Z = 0   (exact integer zero)
```

In `scripts/verify_convergences.py`, over ternary integer keys `K_Z` in `{-1, 0, 1}^{24 x 6}`, the integer kernel has dimension `18`, maximum coefficient magnitude `18` (fitting inside signed INT8), and exact integer leakage `0` across all `N = 6` composed adapters with INT4 `B_j` (`verified`).

**The honest Siegel and Hadamard boundary (where exact integer-lattice projection breaks):** For dense integer matrices `K_Z` in `[-M, M]^{d x k}`, even the shortest nonzero integer kernel vector has worst-case coordinate bound `(d * M)^(k / (d - k))` by Siegel's Lemma, while unreduced RREF basis vectors grow up to the Hadamard subdeterminant scale `(sqrt(k) * M)^k`. In our `d = 16`, `M = 8` test:

- At low preservation ratio `k = 4` (`k / (d - k) = 1/3`): the Siegel shortest-vector bound is `5.04` and the unreduced RREF basis peaks at `4,443` (fitting in INT16).
- At high preservation ratio `k = 10` (`k / (d - k) = 5/3`): the Siegel shortest-vector bound jumps to `3,251` (already overflowing INT8 by `25x`), and the unreduced RREF basis explodes to `13,712,411,082` (`> 2^33`, overflowing INT32).

Furthermore, even when `A_Z * K_Z = 0` holds exactly on quantized keys `K_Z`, real floating-point activations `K_real = K_Z + Delta_K` still leak `Q(B_j) * A_Z * Delta_K` unless activations themselves quantize onto the same integer grid.

## 4. Concrete Falsification Tests for Real Checkpoints

1. **Test C1 (Asymmetric `INT8 A` + `INT4 B` on real 4B weights):** Compile 3 sequential `BetaEdit` adapters on a real 4B model (`siliconcordat/weft`) and compare `fp16_both`, `int4_both`, and `asym_int8A_int4B` on `100` private `K0` retention holdouts. Refuted if `asym_int8A_int4B` fails to cut `int4_both` KL drift by at least `3x`.
2. **Test C2 (Single-manifest zero-drift audit across `mde`, `exo`, `warp`, `weft`):** Generate L5 zone tags, L4 scale maps, L3 canary masks, and L2 `y = 0` partitions from one shared `zones.json` file. Refuted if real multi-language repos exhibit `> 10 percent` mixed-zone single-token spans that break static zone routing.
3. **Test C3 (Siegel feasibility regime):** Exact integer-lattice kernel packing is restricted strictly to low-bit (`<= 4-bit`) or sparse low-rank (`k / (d - k) <= 1/2`) preservation subspaces. Above that ratio, asymmetric `BF16/INT8 A` + `4.5-bit B` plus post-quantization `FixedRadixCertificate` is the sound path.
