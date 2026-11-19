# Syntax-Zone to Weight-Subspace Duality and Cross-Generation Recompilable Software

Pulling Threads 1, 3, and 4 together reveals a structural connection across Layers 5, 4, and 2 of the Siliconcordat stack. Naive null-space weight projection breaks when multiple behavioral style packs share common tokens, yet deterministic syntax zones from Layer 5 turn that failure mode into a clean subspace partition.

All numerical bounds cited below are verified by [`scripts/verify_math.py`](../scripts/verify_math.py).

## 1. Why Naive AlphaEdit Collapses on Shared-Token Behavioral Packs (Thread 1)

For a linear weight matrix `W0` (`d_out x d_in`) and a preserved activation key matrix `K0` (`d_in x n_0`) with covariance `C0 = K0 K0^T`, null-space editing (AlphaEdit, arXiv:2410.02355) projects a raw update `dW_raw` onto the right null space or damped low-variance subspace of `C0`:

```text
dW_safe = dW_raw * P0,   P0 = I - U_r0 U_r0^T   (or lambda * (C0 + lambda * I)^(-1))
```

In sparse factual editing (updating one entity attribute), the edited subject activation `k_new` sits nearly orthogonal to `K0`, so almost all of `dW_raw` survives projection. Multi-domain behavioral packs (plain-writing defaults, UI module idioms from `weft-eido`, and Lean proof syntax from `soko` and `Foundation-0`) break three assumptions of sparse factual editing at once.

### 1.1 Carrier-Token Subspace Overlap and Signal Collapse

Behavioral rules trigger on shared high-frequency carrier tokens: whitespace, markdown fences, punctuation, connectors, and common English or code delimiters. Under sequential history-aware covariance (`BetaEdit`, arXiv:2605.09285):

```text
C^(t) = lambda_1 * K0 K0^T + sum_{i < t} K_i K_i^T
```

Let `S_j` be the activation subspace required for adapter `j` to fire, and let `S_{<j}` be the span of previously preserved keys. Let `theta_min` be the smallest principal angle between `S_j` and `S_{<j}`. The fraction of adapter `j`'s intended update energy that survives orthogonal projection is upper-bounded by:

```text
eta_j = ||dW_j * P^(t-1) * K_j_edit||_F^2 / ||dW_j * K_j_edit||_F^2
      <= 1 - cos^2(theta_min) = sin^2(theta_min)
```

Two failure modes follow immediately (`verified` algebra):

- **High carrier overlap (`theta_min = 10 deg`):** At most `3.02 percent` (`0.030154`) of adapter `j`'s signal survives projection. Strict null-space projection silences the new adapter. Relaxing damping `lambda` to restore signal causes leakage `||dW_j K_i||_F` that degrades prior adapters.
- **Disjoint expansion (`theta_min` near `90 deg`):** Stacking `T` packs of effective rank `rho_i` linearly consumes the residual dimension `m_eff(t) = d_in - rank_tau(C^(t))`, eventually exhausting capacity.

### 1.2 Multi-Layer Nonlinear Drift Amplification

Even when per-layer linear leakage is tiny (`||dW_l k_l||_2 <= eps` on preserved prompts), feeding a perturbed hidden state `h_l + delta_h_l` through nonlinear blocks (`RMSNorm`, gated MLPs, attention softmax) with local Lipschitz constants `kappa_m` amplifies residual drift across depth `L`:

```text
||delta_h_L||_2 <= sum_{l=1..L} eps_l * prod_{m=l+1..L} kappa_m
```

For `L = 36` layers, uniform per-layer residual `eps = 1e-4`, and mild per-block amplification `kappa = 1.05`, worst-case output hidden-state drift reaches `0.009584`, which is `95.8x` the single-layer residual (`verified`). Per-layer algebraic certificates (`FixedRadixCertificate`) are necessary for fast load-time rejection, yet never sufficient without end-to-end behavioral canaries.

### 1.3 Direct Normative Regime Collisions

Some cross-domain collisions are logical contradictions rather than numerical leakage. Plain-writing rules ban dense formal notation, telegraphic fragments, and full 40-character hashes in prose. Formal verification requires exact Lean axioms, exact 40-character commit SHAs, and explicit limitation sections. Interactive UI condensing in `weft-eido` requires `Terse` and `Caveman` slots inside `condensed.json`.

No single global weight sum `W0 + dW_prose + dW_ui + dW_fv` can satisfy mutually contradictory output distributions on identical ambiguous prefixes without silently choosing one norm over another, which violates Hard Veto 2.

## 2. Syntax-Zone to Weight-Subspace Duality (Thread 3)

The shared-token wall dissolves when Layer 5 deterministic parsing and Layer 2 weight subspaces work as a coupled pair rather than isolated layers.

Layer 5 (`siliconcordat/mde`) already runs Tree-sitter concrete syntax trees (CST) to locate and verify byte spans. Extending `splice_locate` and `splice_trace` to emit a deterministic **syntax zone tag** partitions every workspace span into an explicit finite set:

```text
Z = { prose, code, formal_proof, ui_module, condensed_json }
```

Three coupled mechanisms turn `Z` into **Grammar-Conditioned Composable Parametric Software**:

### 2.1 Contextual Register-Scoped Preservation (`y = 0` Partitioning)

When compiling specialist adapter `A_z` for zone `z`, the compiler builds its preservation matrix `K_preserve(z)` from two sources:

1. Base safety and general capability keys `K0`.
2. **Out-of-zone activation keys `K_{not z}`** drawn from all other zones with target shift `delta_y = 0`.

Raw unigram embedding edits (tied `embed_tokens` row shifts) cannot separate `prose` from `formal_proof` because both share punctuation and English tokens (`theta_min` near zero). In middle and upper transformer MLP layers, hidden states `h_l(x)` encode surrounding syntactic context (fenced proof blocks, Lean keywords, JS module headers, JSON keys).

Raising the contextual principal angle from `10 deg` (unigram overlap) to `60 deg` (context-separated hidden states) raises the surviving signal ceiling from `3.02 percent` to `75.00 percent` (`verified`), making orthogonal compilation viable on contextual MLP projections (`hypothesis`, directly tested in `siliconcordat/weft` Experiment E1).

### 2.2 Layer 4 Deterministic Zone-Scoped Scale Gating

Where two zones carry mutually contradictory rules (such as `prose` vs `formal_proof` or `prose` vs `condensed_json`), Layer 4 (`siliconcordat/exo`) does not leave conflicting adapters summed at static scale `1.0`. Given the Layer 5 zone tag `z` and the Layer 2 per-repo manifest (`repo-policy.json`), Layer 4 emits an exact per-request scale vector `g(z)` in `{0, 1}^M` to Layer 3 (`warp-modeld`):

```text
W_eff(z) = W0 + sum_{m=1..M} g_m(z) * dW_m
```

| Active L5 Zone `z` | Base Prose Pack | Epistemic Honesty Pack | Design (`weft-eido`) Pack | Formal Proof (`soko` / Lean) Pack |
| --- | --- | --- | --- | --- |
| `prose` | `1.0` | `1.0` | `0.0` | `0.0` |
| `formal_proof` | `0.0` | `1.0` | `0.0` | `1.0` |
| `ui_module` | `0.0` | `1.0` | `1.0` | `0.0` |
| `condensed_json` | `0.0` | `1.0` | `1.0` | `0.0` |
| `code` (general) | `0.0` | `1.0` | `0.0` | `0.0` |

Cross-zone weight interference between mutually excluded packs drops to **exact zero** (`0.0`) on every forward pass. Simultaneously active non-conflicting packs (such as epistemic honesty plus formal proof) only need orthogonality over their shared zone activations `K_z`, sharply reducing null-space rank consumption.

Any contested overlap (for example, static print HTML rules vs reactive `weft-eido` styling on an untagged page) sets conflicting scales to `0.0` and escalates to an explicit Plane 1 precedence flag in `repo-policy.json`, preserving Hard Veto 2.

## 3. Cross-Generation Recompilable Software (Thread 4)

Combining Self-Improvement Memory (SIM, arXiv:2611.18856v1), durable capability identity (`capability_id`), Plane 1 causal policy DAGs (`Moissanite-Labs/ethos`), and Layer 2 deterministic compilation yields a clean lifecycle across base model upgrades (`W_old -> W_new`).

### 3.1 Serendipitous Convergence 1: Broker Gate Trips Become Exact `K_i` Calibration Sets

External deterministic gates at Layers 5 and 4 (prose lint failures, CST seam refusals, Lean kernel rejections, `weft-eido` validator errors) already catch first-draft model errors during normal work. Logging each caught failure together with its verified passing repair produces a scrubbed SIM causal record:

```text
(capability_id, zone_tag, base_checkpoint_sha, plane1_rule_sha, failed_draft, passing_repair, oracle_id)
```

These real-world failure pairs supply the exact edit keys `K_i_edit` and target directions `V_i_edit` needed by the Layer 2 boring compiler, while already-passing turns in other zones supply `K_i_preserve`. The external deterministic broker generates the exact non-synthetic calibration signal that cuts its own future rejection rate without ever granting authority to weights.

### 3.2 Serendipitous Convergence 2: Automated Recompile vs Retire Decision Law

Traditional fine-tunes and sprawling system prompts carry obsolete workarounds forever when a stronger base model arrives. Under Cross-Generation Recompilable Software, upgrading from `W_old` to `W_new` executes a deterministic three-way decision per `capability_id`:

1. **Test bare `W_new` first:** Run `W_new` with zero adapters and zero workaround prompt against the pinned SIM failure fixtures and deterministic oracle for `capability_id`.
2. **Automatic retirement (`retire_candidate`):** If bare `W_new` already passes 100 percent of the deterministic checks, the old adapter or rule only patched a weakness in `W_old`. Retire it cleanly instead of porting dead weight.
3. **Deterministic recompilation (`recompile`):** If bare `W_new` still trips the deterministic oracle and the Plane 1 rule head is uncontested, compile a fresh `.gpatch` or GGUF LoRA on `W_new` from the pinned Plane 1 text and SIM corpus, certify it via `FixedRadixCertificate` and private holdouts, and mount it.
4. **Human escalation (`escalate_human`):** If the Plane 1 rule head is contested or if `W_new` triggers a new cross-zone clash, halt and ask the owner.

### 3.3 Serendipitous Convergence 3: Parser Boundaries Become Serving Cache Partitions

Because Layer 5 CST zones determine the active adapter mask `g(z)` before tokens enter Layer 2, Layer 3 (`warp-modeld`) knows exact zone boundaries up front. That removes the need for speculative per-token router networks inside the GPU and maps directly onto capability-tagged KV and recurrent-state hardware banks derived in [`docs/04-loom-hardware-physics.md`](04-loom-hardware-physics.md).

## 4. Falsification Conditions

The zone-subspace duality is refuted if real-checkpoint experiments (`siliconcordat/weft`) show any of the following:

1. **Contextual overlap remains near zero:** On a real 4B transformer, principal angles between contextual MLP activations of `prose` and `formal_proof` stay below `15 deg` across all layers, preventing `y = 0` out-of-zone preservation from retaining `>= 50 percent` of solo adapter gain (leaving pure Layer 4 dynamic scale gating as the sole working mechanism).
2. **Zone-switch stall dominance:** Frequent mid-turn transitions between `prose` and `formal_proof` force recurrent-state flushes whose re-prefill latency exceeds the token savings of dropping Plane 1 SOP prompts (motivating Thesis 3 in `docs/04`).
3. **Zero retirement value:** Across a real base-model upgrade (`W_old -> W_new`), SIM causal records fail to distinguish obsolete model workarounds from durable user rules more accurately than manual review.
