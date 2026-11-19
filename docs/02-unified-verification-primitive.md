# The Unified Anti-Goodhart Verification Primitive

Four verification designs evolved independently across our public repositories: Committed Behaviour Change in `weft-loom`, dual-oracle anti-tautology auditing in `soko` and `Foundation-0`, the external multi-kernel verified bar in `Proven-Commons`, and two-tier lexicase anchor gating in `spliceware`.

This paper derives from first principles why all four are projections of one formal object: **Anti-Goodhart Verifier-Owned Behavioral Commitments (AG-VBC)**. It states exact conditions under which external pinning, commit-before-reveal holdouts, structural checks, and two-tier lexicase filtering defeat reward hacking across both code synthesis and weight compilation.

All numerical bounds in this paper are checked programmatically by [`scripts/verify_math.py`](../scripts/verify_math.py).

## 1. Structural Isomorphism Across Four Systems

Each mechanism defends a verifier against an adaptive optimizer that tries to maximize a proxy score while violating the intended specification.

| System | Optimizer (Proposer `P`) | Candidate Artifact | External Structural Gate `C` | Verifier-Owned Behavioral Check | Observed Failure Mode Stopped |
| --- | --- | --- | --- | --- | --- |
| **Committed Behaviour Change (`weft-loom`)** | Weight adapter / trainer | Weight delta `dW` digest | Replay check + commit-bound expiry | Private behavioral probes + one-input refutation | 23x MLP and 459x transformer visible-probe gaming |
| **Dual-Oracle Audit (`soko`, `Foundation-0`)** | Fast C++20 solver or AI prover | Witness path or proof script | Static AST anti-tautology scan (`formal_audit_checkers`) + `SHA256SUMS` | Two zero-shared-code independent Python oracles | Self-written vacuous checkers, alpha-renamed tautologies, hash collisions |
| **Verified Bar (`Proven-Commons`)** | Library author or coding agent | Lean implementation commit | Independent Lean kernel typechecker | Externally pinned `bar.toml` specification hash | Weakened local specs and unverified `sorry` placeholders |
| **Two-Tier Lexicase (`spliceware` repaired)** | Code broker or evolutionary splicer | CST Splice Packet or C11 Cell | Compiler / typecheck or `verify_and_map` (`delta-sp == 0`) | External visible anchors + private holdouts + mutation floor | `0x00 HALT` fuel collapse, forged migrant anchors, 1-step cliffs |

## 2. Formal Definition of the AG-VBC Game

Let `theta_0` denote the immutable base artifact (a Git tree SHA for code, or a four-layer fingerprinted base checkpoint `W0` for weights). An adaptive Proposer `P` outputs a candidate modification `theta` over an input domain `D` with deterministic non-LLM ground-truth specification `S(x, y) in {0, 1}`.

A Verifier `V` holds five sealed objects outside `P`'s write boundary:

1. **Deterministic structural gate `C(theta, theta_0) in {0, 1}`:** A fast static or algebraic check independent of `P`'s generator (compiler plus typecheck for code, Lean kernel for proofs, `FixedRadixCertificate` plus lineage check for weights).
2. **Hard safety and preservation invariants `A_safe`:** Mandatory behavioral invariants that never relax (safety refusals, base capability canaries, protected-oracle integrity, compile and lint rules).
3. **Visible task anchors `A_vis`:** `k_v` deterministic behavioral checks drawn across a difficulty ladder (easy foothold cases up to high-complexity anti-unrolling cases), visible to `P` for local feedback.
4. **Private holdout set `A_priv`:** `k_h` deterministic behavioral checks drawn from `D` and sealed from both read and write access by `P` during synthesis or compilation.
5. **Anti-flake certificate:** Every check in `A_safe`, `A_vis`, and `A_priv` must pass `r >= 10` repeated runs under randomized execution order and load with zero variance (`flake_rate = 0`).

## 3. Four Necessary and Sufficient Axioms

Removing any one of the four axioms creates a concrete, empirically observed exploit.

### Axiom 1: External Oracle Ownership (Zero Self-Certification)

`V` must load `(C, A_safe, A_vis, A_priv, S)` from its own immutable root digest `h_oracle`. `V` never reads test expectations, expected outputs, or pass flags from `theta` or from untrusted peer metadata.

**Counterexample when violated (`verified`):** In `spliceware` `v3_evogenesis.c`, `score_anchors()` reads expected `(in, out)` pairs from the incoming migrant cell's `body[14..21]`. A 1-byte `NOP` cell carrying forged anchors `{(0, 0) x 4}` passes `4/4` with zero error in `O(1)` time and hijacks the champion slot. In code editing, giving a coding agent write access to `tests/` lets it weaken assertions to pass CI.

### Axiom 2: Commit-Before-Reveal Against Adaptive Overfitting

`P` must publish an immutable content digest `h_theta = H(theta || h_theta_0)` before `V` evaluates `A_priv`. When `V` evaluates a sequence of `M` committed finalists `theta_1, ..., theta_M` against `A_priv`, `V` returns at most one binary verdict per finalist (never per-case gradients or detailed failure leaks from `A_priv`).

**Theorem 1 (Private Holdout False-Acceptance Bound, `verified`):** Suppose any finalist `theta_m` has true failure rate `p(theta_m) = Pr_{x ~ D}[S(x, f(theta_m, x)) = 0] >= epsilon` on distribution `D`. Because `theta_m` is committed before seeing `A_priv` and draws in `A_priv` are independent of `theta_m`, the probability that any defective finalist passes all `k_h` private holdouts satisfies:

```text
Pr[exists m <= M : p(theta_m) >= epsilon AND theta_m passes all k_h holdouts]
    <= M * (1 - epsilon)^k_h
    <= M * exp(-epsilon * k_h)
```

To guarantee false-acceptance probability at most `delta`, the required private holdout size scales only logarithmically with the number of finalists `M`:

```text
k_h >= ceil( (1 / epsilon) * ln(M / delta) )
```

| True Error Floor `epsilon` | Risk Cap `delta` | Committed Finalists `M` | Minimum Holdout `k_h` | Exact Union Bound `M * (1 - epsilon)^k_h` |
| --- | --- | --- | --- | --- |
| `0.10` (10% error) | `0.01` | `10` | `70` | `0.006266 < 0.01` |
| `0.10` (10% error) | `0.01` | `100` | `93` | `0.005561 < 0.01` |
| `0.05` (5% error) | `0.01` | `1` | `93` | `0.008469 < 0.01` |
| `0.05` (5% error) | `0.01` | `10` | `139` | `0.008023 < 0.01` |

**Why visible-only probes collapse:** When `P` observes `A_vis` during optimization, the effective number of explored hypotheses `M_eff` grows exponentially with parameter count or prompt iterations (`M_eff ~ exp(d)`). Even large `A_vis` sets lose statistical power once `k_v < d / epsilon`, allowing `P` to drive visible error to zero while true error approaches `1`. This explains the measured 23x MLP and 459x transformer probe gaming in `weft-loom` and the `0x00 HALT` collapse in ungated `spliceware`.

**Budget exhaustion rule:** Because each binary pass/fail bit returned from `A_priv` leaks up to 1 bit of information into future attempts, `V` enforces a hard cap `M <= M_max` per holdout epoch. Once `M_max` finalists are tested against an epoch, `A_priv` rotates to a fresh sealed draw before further automated search continues.

### Axiom 3: Structural Independence and Mutation Sensitivity

An oracle can still fail even when externally owned if its assertions are weak or share blind spots with `P`. Axiom 3 pairs two independent defenses:

1. **Anti-tautology separation:** `S` and `C` share zero implementation code with `P` and pass static anti-tautology checks (no vacuous `True` returns, no unguarded float equality in exact proofs, no alpha-renamed clones of the generator).
2. **Adversarial mutation floor:** Before enabling automated selection on a module or checkpoint, `A_vis union A_priv` must kill at least fraction `mu` (target `mu >= 0.80`) of a planted fault suite (code mutants for software, or targeted low-norm rank-`r` sabotage deltas for weights).

**Combined Escape Bound (`verified`):** If independent structural gate `C` rejects fraction `gamma` of adversarial perturbations (for example, compiler errors or null-space leakage violations) and the behavioral suite kills fraction `mu` of semantic faults, the combined pre-holdout escape rate is bounded by `(1 - gamma) * (1 - mu)`:

- Norm-only gate (`gamma = 0.00` against targeted low-norm rank-4 flips) plus weak tests (`mu = 0.30`) leaves a `70.0 percent` escape rate.
- Compiler or null-space certificate (`gamma = 0.90`) plus mutation-tested anchors (`mu = 0.80`) drops pre-holdout escape to `2.0 percent` before private holdout filtering even runs.

### Axiom 4: Two-Tier Lexicase Separation Without Safety Dilution

Strict all-or-nothing gates prevent regression yet create zero-gradient cliffs on multi-step changes (`spliceware` `v3_evogenesis`: 0 of 106 reachable single-step edits pass 2 of 4 anchors under a rigid 3-of-4 gate). Scalar averaging avoids cliffs yet lets a candidate hide a broken critical requirement behind high average scores.

AG-VBC resolves both failures by separating **safety filtering** from **shuffled-order lexicase specialist retention**:

- **Tier 1 (Canonical Promotion):** Requires `100 percent` pass on `C`, `100 percent` pass on `A_safe`, `100 percent` pass on `A_vis`, AND passing `A_priv`. Secondary metrics (fuel, latency, code simplicity, token count) rank candidates strictly after all behavioral and safety gates pass.
- **Tier 2 (Stepping-Stone Pool, offline search only):** Admits candidates that pass `100 percent` of `C` and `A_safe` (safety NEVER relaxes to Tier 2), then selects breeding or re-synthesis parents using true shuffled-order lexicase selection over `A_vis`: draw a uniform random permutation `pi` of the `k_v` anchors, keep only pool members achieving the best score on `pi(1)`, break ties on `pi(2)`, and continue until one parent remains.

**Theorem 2 (Specialist Survival Guarantee, `verified`):** Under scalar averaging over `k_v` anchors, a specialist that uniquely solves one hard anchor `a*` while failing `k_v - 1` easy anchors dies whenever its mean score trails a trivial generalist.

Under uniform shuffled-order lexicase selection, `a*` lands first in permutation `pi` with probability `1 / k_v`, selecting that specialist regardless of its other scores. Across `N_sel` independent parent draws, the probability of selecting a unique specialist at least once is:

```text
Pr[specialist selected >= 1 time] >= 1 - (1 - 1 / k_v)^N_sel
```

- For `k_v = 4` anchors and `N_sel = 16` draws: survival probability is at least `99.00 percent` (`0.989977`), compared to `0 percent` under `v3_evogenesis`'s rigid scalar threshold.
- For `k_v = 8` anchors and `N_sel = 32` draws: survival probability is at least `98.61 percent` (`0.986060`).

## 4. Concrete Instantiation Across Code, Weights, and Proofs

The exact same formal protocol governs all three domains in the Siliconcordat stack without changing a single axiom:

| AG-VBC Element | Track A Code Splicing (`mde`, `exo`, `warp`) | L2 Weight Compilation (`weft`, `warp-modeld`) | Formal Proof Systems (`soko`, `Proven-Commons`) |
| --- | --- | --- | --- |
| **Base state `theta_0`** | Pinned Git `base_tree` SHA | 4-layer checkpoint + runtime-flag digest | Pinned problem spec and `SHA256SUMS` |
| **Committed digest `h_theta`** | `packet_id` (`splice-packet/v0.1`) | `.gpatch` or GGUF LoRA SHA-256 + `source.lineage` | Proof commit SHA or witness digest |
| **Structural gate `C`** | Tree-sitter CST seam + compiler / typechecker | `FixedRadixCertificate` + contested-head check | Lean kernel + `formal_audit_checkers` AST scan |
| **Hard invariants `A_safe`** | Read-only oracle lock, secret scan, complexity cap | Verifier-owned safety and base-capability canaries (`100%`) | Dual zero-shared-code oracles, exact-state edge checks |
| **Visible anchors `A_vis`** | Fast Tier 1 unit/property suite (`<= 15s`) | Difficulty-laddered visible domain calibration probes | Public benchmark boards and regression fixtures |
| **Private holdout `A_priv`** | Sealed Tier 2 holdout tests (`k_h >= 70`) | Sealed domain and base-retention holdouts (`k_h >= 64` to `100`) | Held-out test theorems and independent reviewer bar |
| **Tier 2 stepping stones** | Guided re-synthesis parent diffs (never merged) | Offline compiler hyperparameter search (never served) | Explicit `LOWER_BOUND_UNWITNESSED` records (never `VERIFIED`) |

## 5. Falsification Conditions

This unification is refuted for any concrete domain if any of the following occurs in practice:

1. **Holdout drift violation:** A candidate passes `100 percent` of `C`, `A_safe`, and `k_h >= 70` sealed non-flaky holdouts yet shows `> 10 percent` error on fresh i.i.d. draws from the same distribution `D` (proving distribution shift or information leakage from `A_priv`).
2. **Oracle cost wall:** Maintaining `k_h >= 70` deterministic non-LLM holdouts with `mu >= 0.80` mutation kill rate costs more engineering time than direct human review on routine changes (in which case Tier 2 search stays disabled and direct targeted edits remain the default).
3. **Zero-overlap cliff persistence:** Even with `N_sel >= 4 * k_v` lexicase draws, no specialist escapes a discrete synthesis valley without semantic re-synthesis (confirming guided LLM re-synthesis rather than syntactic crossover is required for high-level languages).
