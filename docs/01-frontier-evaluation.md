# Frontier Evaluation Across the Four Working Organizations

This audit evaluates public research and engineering across `Moissanite-Labs`, `Foundation-0`, `Proven-Commons`, and `ahrazzle/soko`. It separates work that breaks genuine technical ground from uncharted threads worth testing and confirmed empirical dead ends.

Every claim carries an explicit status tag: `verified` (proved mathematically or backed by committed public output), `source claim` (reported upstream and not reproduced locally), or `hypothesis` (proposed mechanism with a stated kill test).

## 1. Genuine New Ground and Publishable Advancements

These six areas produce concrete methods, proofs, or empirical measurements that external systems engineers and ML researchers can test and adopt today.

### 1.1 Geometry-Driven Quantization Without Fitted Constants (`Moissanite-Labs/siliquant`)

- **Core result (`verified`):** Across 85 real matrices from a speech model and a language model, a zero-fitted-constant error formula predicts measured quantization error within 0.3 dB in 96.6 percent of 5,525 runs and selects the measured best arm out of 13 in 96 percent of 425 choices.
- **Region vs lattice separation (`verified`):** Under largest-entry row scaling on Gaussian data, the E8 lattice gains 2.3 dB over scalar rounding per row. Splitting that gain shows 1.64 dB comes from the spherical bounding region and only 0.65 dB from the E8 Voronoi cell. Plain integer levels cut by a ball capture 76 to 89 percent of E8's gain without a lattice decoder.
- **Certified whole-number selection (`verified`):** A closed-form scale rule prevents clipping in 1,308 of 1,308 runs at a cost of about 0.5 dB, and a five-arm selector runs in exact integer arithmetic with an independent zero-shared-code checker.
- **Extreme layer concentration (`verified` on `gemma-4-E4B-it`):** Keeping 0.17 percent of weights exact (costing 0.049 bits per weight) more than halves row-scale KL divergence. One matrix (`layer 10 ffn_down`) carries 0.1560 of KL clipping damage while the other 41 layers sum to 0.0182.
- **Unmerged PR 12 breakthroughs (`source claim`):** Keeping 10 weight-identifiable loud columns per `ffn_down` whole (`+0.005` bpw, `4.505`-bit packed) cuts `Llama-3.2-1B` KL `34.5%` (`0.0478` to `0.0302`, `0.0340` packed), beating `Q4_K_M` data-free on `Qwen2.5-1.5B`, `SmolLM2-1.7B`, and `Llama-3.2-1B`. Random-vocab noise-only `imatrix` (zero text read) recovers `69%` to `96%` of real-text `imatrix` gain and beats real-text `Q4_K_M --imatrix` at strength `0.25`.
- **Boundary:** The error formula underpredicts by 0.8 dB at 2 bits, `fold-path-codebooks` failed, full-strength `imatrix` degrades quality, and E8 loses to plain integer ball on `SmolLM2`.

### 1.2 Anti-Tautology Dual-Oracle Verification (`ahrazzle/soko`, `Foundation-0`, `Proven-Commons`)

- **Core result (`verified`):** [`ahrazzle/soko`](https://github.com/ahrazzle/soko) (`v0.4.0`) separates fast C++20 search from two zero-shared-code Python oracles (`PuzzleScriptOracle` and `FlatBitmaskOracle`) and runs exact-state bucketed A* (`CompactNode` full-state equality). On board `III-20`, it expanded 8,475,805 nodes in 30 seconds, caught 77,437 live 64-bit hash collisions, and verified 25,096,136 heuristic edges with zero violations.
- **Anti-tautology AST auditing (`verified`):** [`Foundation-0/formal-claims-audit`](https://github.com/Foundation-0/formal-claims-audit) and `soko`'s `formal_audit_checkers` statically scan Python verifiers for optimistic constant-`True` flags, IEEE-754 float drift in exact checkers, vacuous stubs, and alpha-renamed copy-paste tautologies.
- **Honest claim-tier typing (`verified`):** `soko_prove_floor` refuses to label an unwitnessed search bound `VERIFIED`, reporting `LOWER_BOUND_UNWITNESSED` and explicit `proof_scope` bounds instead.
- **Main-branch gap:** On `main`, [`Proven-Commons/mission`](https://github.com/Proven-Commons/mission) has zero active reviewers in `bar/reviewers.toml`, and `formal-claims-audit` holds zero published verdicts.
- **Unmerged fixes:** Open PRs already add dynamic independent maintainer checks (`mission` PR 25), repaired AST anti-tautology auditing and empty-directory fail-closed checks (`formal-claims-audit` PR 16, 17, 19), and a Lean 4 token-stream scanner (`Foundation-0/proven-commons` PR 9). Details sit in [`docs/06-unmerged-branch-excavation.md`](06-unmerged-branch-excavation.md).

### 1.2b Certified Exact Mathematics and Circuit Lower Bounds (`Foundation-0` Open PRs and `silic0n`)

- **Unmerged `Foundation-0` mathematics (`claimed` / `reproduced`, unrefereed):** Open review PRs add three 4-charge configurations with 11 equilibria vs Maxwell's bound of 9 (`point-charges` PR 22, `f0` PR 58 and PR 61) and an 11-vertex rigid graph with `2,288` of `2,288` real realizations raising the growth bound to `2.4116` (`rigid-realizations` PR 21).
- **Combinatorics and coding tables (`claimed`, unrefereed):** Open PRs also add `238` proved OEIS recurrences plus a Square Law theorem (`finite-state-proofs` PR 5) and `2,418` improved linear-code entries over GF(7) to GF(9) from `122` exact Delsarte certificates (`gfq-codes` PR 19).
- **Hardware circuits and multiplication bounds (`source claim`, Lean-checked where noted, unrefereed):** Public repositories linked from `Foundation-0/silic0n` report `o(N log N)` GF(2) Mobius/zeta XOR circuits (`ahrazzle/mobius-x1`), smaller Lean-proved `GF(2^m)` multipliers and AES S-boxes (`ahrazzle/gf2m-circuits`), and conditional `kappa > 2^-15` integer multiplication bounds (`ahrazzle/integer-mult-bounds`).

### 1.3 Compile-Do-Not-Edit Weight Governance (`Moissanite-Labs/MDE`, `Moissanite-Labs/ethos`)

- **Two-plane architecture (`verified` in design and stdlib reference):** [`Moissanite-Labs/MDE`](https://github.com/Moissanite-Labs/MDE) and [`Moissanite-Labs/ethos`](https://github.com/Moissanite-Labs/ethos) separate canonical Plane 1 text from optional Plane 2 compiled weight caches.
- **Five Hard Vetoes (`verified` in `MDE` orientation docs):** No opaque deltas, no automatic resolution of contested preferences, no closed-weight injection, no premature protocol standardization, and Plane 1 as the sole home for human authority.
- **Four-layer checkpoint binding (`verified` on synthetic fixtures):** `MDE` splices same-checkpoint `.gpatch` Safetensors binding (`vendor/splices/dawe_gpatch/`) locking `layout_sha256`, raw tensor byte fingerprints, `config`/`tokenizer`/`chat_template.jinja` digests, and Plane 1 `source.lineage`.
- **Integer post-quantization certification (`verified` on synthetic and `TinyStories-1M` weights):** The `BetaEdit` projector computes a division-free integer `FixedRadixCertificate` after quantization over immutable SGMV slabs with `O(1)` slot rollback.
- **Real-checkpoint asymmetric packing and noise-only `K0` (`verified` in [`siliconcordat/weft`](https://github.com/siliconcordat/weft) E4 @ `70a4e68` on `roneneldan/TinyStories-1M`):** Confirming `docs/05`'s Asymmetric Factor Leakage Theorem live across `N = 3` sequential adapters, `int4/int8` (`B` INT4, `A` INT8) cuts `K0` linear leakage `18.37x` vs `int4/int4` and `18.18x` vs reversed control `int8/int4` on `mlp.c_proj` (`20.03x` / `19.80x` with `39.0%` byte savings on `mlp.c_fc`). `int4/f16` beats `bf16/bf16` on both bytes and leakage (`7.4x` to `12.4x`), and 64-sequence noise-only `K0` recovers `83.9%` of real-text holdout protection.
- **Boundary:** `TinyStories-1M` has flat column norms (`1.21x` to `1.41x` max-to-mean), deferring loud-column gains and 4B-27B instruct multi-adapter composition to `weft` Milestone 3.

### 1.4 Exact-Byte Consent and OS-Enforced Agent Boundaries (`Moissanite-Labs/exo`, `Moissanite-Labs/exo-os`)

- **Exact-byte approval locking (`verified` in code):** [`Moissanite-Labs/exo`](https://github.com/Moissanite-Labs/exo) hashes the exact text, target, and arguments of every outward action. Editing one character voids consent. Sessions share one append-only hash-chained memory log and treat peer messages strictly as input, never consent.
- **Kernel-enforced tool isolation (`verified` in code):** [`Moissanite-Labs/exo-os`](https://github.com/Moissanite-Labs/exo-os) executes workspace tools inside compulsory `bubblewrap`, `Landlock`, and `seccomp` sandboxes with zero network, credentials, or host control sockets, paired with separate-UID protected ledger and egress proxy services, tamper-evident spend ceilings, and `btrfs` plus UKI boot recovery.
- **Unmerged L3/L4 hardening (`verified` in open PRs):** Companion excavations in `docs/06` surface zero-`sudo` OS images (`exo-os` PR 139), `root:root` plus `go-w` ancestor hardening (`exo-os` PR 140), archival ledger repair, per-capability replay-safe gateways (`exyber` PR 1), fail-closed read tools (`exo-desktop` PR 23 and PR 71), and Ed25519 small-order actor key rejection (`synmerit` PR 10).
- **Boundary:** Native hardware image acceptance on `exo-os` remains pending, and `exo`'s stacked Swarm PR wave (`PR 948` to `PR 1219`) remains unmerged.

### 1.5 Zero-Dependency Analytical UI Physics (`Moissanite-Labs/weft-eido`)

- **Core result (`verified`, 120 unit tests):** [`Moissanite-Labs/weft-eido`](https://github.com/Moissanite-Labs/weft-eido) implements continuous barycentric style mixing with unit-circle hue interpolation (`atan2`), area-proportional Vogel golden-angle packing, 5x7 bitmask glyphs packed in two `u32` words shared identically by WebGPU and Canvas2D, and strictly local reading-cadence adaptation (`condensed.json` keyed by FNV-1a hashes, zero runtime LLM calls).
- **Unmerged upgrades (`source claim`):** Open PR 8 fixes the CodeQL `innerHTML` XSS findings with text spans (65 tests), PR 25 adds a deterministic 360-hue WCAG contrast audit (120 tests, zero-LLM Design MDE oracle), and PR 22 adds Poincare disk Mobius isometries.
- **Boundary:** Interactive UI styling conflicts directly with static print-ready HTML rules unless scoped by L5 syntax zone.

### 1.6 Compact Executable Agent Framing (`Moissanite-Labs/abios`, `Moissanite-Labs/tokenpage`)

- **Core result (`verified`):** [`Moissanite-Labs/abios`](https://github.com/Moissanite-Labs/abios) compresses structured agent messages from 481 bytes of JSON to 101 bytes of positional `SYM-2P` s-expressions (`0.273x` to `0.277x` tokens across 7 tokenizers in `tokenpage` PR 1) and shows executable positional ASTs outperform invented text vocabularies during search.
- **Boundary (`source claim`):** `tokenpage` PR 5 shows unadapted models drop to `0.558` accuracy reading compact glyphs even though hidden states decode them linearly, and `abios` PR 41 proves prompt-level `CMD`/`DATA` envelopes fail `30/30` against hidden peer injection.

## 2. High-Potential Uncharted Threads Worth Pulling

Seven deep threads connect these separate repositories into one coherent systems research program. Each thread is treated as a falsifiable research target rather than an assumed win:

| Thread | Core Idea | Where Derived in `loom` | Primary Falsification Test |
| --- | --- | --- | --- |
| **T1: Shared-Token Subspace Collapse** | Quantify why sparse-fact null-space projection breaks on shared-token behavioral packs and measure register-scoped recovery | `docs/03-zone-subspace-duality.md` | Multi-adapter rank and logit-drift ablation on real 4B open weights |
| **T2: Anti-Goodhart Verification Unification** | Prove CBC, dual-oracle auditing, external multi-kernel bars, and two-tier lexicase are one formal game against adaptive optimizers | `docs/02-unified-verification-primitive.md` | Adversarial sabotage escape and private-holdout false-accept bounds |
| **T3: L5 Syntax Zone to L2 Subspace Duality** | Use deterministic Tree-sitter CST zone tags (`prose`, `code`, `formal_proof`, `ui_module`) to partition L2 calibration keys and drive L4 dynamic LoRA scaling | `docs/03-zone-subspace-duality.md` | Mixed-mode prompt suite checking zero cross-zone prose/proof bleed |
| **T4: Cross-Generation Recompilable Software** | Use causal failure logs (SIM) plus durable capability IDs to recompile durable rules and automatically retire obsolete model workarounds on base upgrades | `docs/03-zone-subspace-duality.md` | Upgrade test across two base checkpoints measuring automatic retirement rate |
| **T5: L1 Hardware Physics From L2-L5 Walls** | Derive DMA-boundary integer certificate units, fused multi-adapter SGMV datapaths, tagged recurrent-state banks, and exact-radix accumulators | `docs/04-loom-hardware-physics.md` | Software Triton/Metal kernel and FPGA/Verilator roofline refutation tests |
| **T6: External-Pinned Multi-Tier Selection** | Separate strict canonical safety promotion from shuffled-order lexicase stepping stones without diluting safety invariants | `docs/02-unified-verification-primitive.md` | Escape rate from discrete single-step cliffs with zero safety regression |
| **T7: Three-Axis Latent Lattice Convergence** | Combine horizontal persistent Lattice streams (`arXiv:2611.21608`) with L2 `weft` adapters and L5 zones while defeating horizontal-to-KV-write poisoning and global `RMSNorm` bleed | [`docs/07-latent-lattice-convergence.md`](07-latent-lattice-convergence.md) | 3-domain shared-token composition, KV-only vs atomic rollback, and `< 5 us` SRAM bank checks |

### 2.1 Four Serendipitous Cross-Org Convergences

Excavating all 103 verified-public repositories (`docs/06-unmerged-branch-excavation.md`) and running `weft` E4 surfaced four cross-org connections formalized in [`docs/05-spliceware-algebra-and-convergences.md`](05-spliceware-algebra-and-convergences.md) Section 4:

1. **Seeded-Noise `K0` Covariance (`siliquant` PR 12 x `weft` E4):** Random vocabulary sequences (zero real text read) recover `83.9%` of real-text holdout `K0` protection in `weft` E4 (`69%` to `96%` `imatrix` recovery in `siliquant` PR 12), enabling copyright-free, seed-reproducible Hard Veto 1 compilation.
2. **Parametric Wire-Dialect Decoders (`tokenpage` PR 5 x `weft`):** Hidden states linearly decode compact glyphs while unadapted readout drops to `0.558`. Tiny zone-scoped `int4/int8` readout adapters can unlock `0.27x` ABIOS token compression without base-model retraining.
3. **Irreducible OS + Static + 256-Bit TCB Law (`abios` PR 41 x `f0` PR 49 x `mission` PR 37):** Prompt envelopes failing `30/30` on peer injection, bare `assert` vanishing under `-O`, and `181.0M` 64-bit hash collisions prove kernel sandboxes, static code audits, and 256-bit keys cannot be substituted by prompt rules.
4. **Diversity-Preserving Selection Law (`scry` PR 1 x `weft-loom` x `docs/02`):** Nucleus truncation (`top_p = 0.95` killing `40/40` rare intents by gen 5), rival twin scoring failure, and undeduplicated pools all erase rare stepping stones before recombination.

## 3. Confirmed Dead Ends and Valuable Empirical Negative Results

Publishing negative results prevents teams and outside researchers from repeating expensive dead ends. Every item below is supported by direct public measurements.

| Dead End | Verified Empirical Finding | Public Source | Engineering Rule Derived |
| --- | --- | --- | --- |
| **Weight-distance and norm-only safety gates** | Distance thresholds failed across benign vs altered updates (0.1 to 0.3 vs 1.01 vs 28.1 benign graft). A rank-4 targeted flip attack (`norm 1.798` under budget `9.274`) broke 3 of 4 canaries while passing norm checks. | [`Moissanite-Labs/weft-loom`](https://github.com/Moissanite-Labs/weft-loom) and `MDE` prototype | Never gate weight acceptance on parameter norm alone. Require null-space certificates plus verifier-owned behavioral checks. |
| **Visible-only probe gating** | Adaptive optimization gamed visible probes by 23x on MLPs and 459x on transformers while degrading true behavior. | `weft-loom` Committed Behaviour Change records | Always pair visible feedback probes with commit-before-reveal private holdouts. |
| **Hand-maintained prose numbers and unpinned badges** | Unchecked prose figures were wrong 35 of 86 times (40.7 percent) versus 0 of 68 (0.0 percent) when regenerated from source files. Verified badges went stale silently after later commits. | `weft-loom` register audit | Generate summary tables and ledgers mechanically from pinned commits. Expire verified claims on any base-tree change. |
| **Pure fuel selection and self-reported anchors** | In [`Moissanite-Labs/spliceware`](https://github.com/Moissanite-Labs/spliceware), ungated fuel tournaments (`v1`, `v2`) collapsed immediately to 0-byte `HALT` (`FuelLeft = 512`). Reading anchors from untrusted UDP migrants (`v3`) let a 1-byte `NOP` with forged anchors hijack the champion. | `spliceware` `substrates/c11/` audit | Keep cost optimization strictly downstream of verifier-owned external anchors. Never read test expectations from the candidate. |
| **Rigid single-step discrete evolutionary cliffs** | Exhaustive check of all 106 reachable one-step mutations and self-splices of `v3_evogenesis`'s seed (107 unconstrained) produced 46 valid children and zero passing at least 2 of 4 anchors under a strict 3-of-4 gate, deadlocking evolution forever. | `spliceware` `v3_evogenesis.c` audit | Use targeted edits or guided re-synthesis by default. Where search is needed, use shuffled-order lexicase stepping stones. |
| **Unconstrained exotic quantization codebooks** | Incentre-lattice point sets scored 1.2 to 2.0 dB worse than a cube, vortex codebooks merely tied scalar rounding, 880 graph realizations lost to 880 random points, and neural persistence ranked novel arms worst of five. | [`Moissanite-Labs/siliquant`](https://github.com/Moissanite-Labs/siliquant) studies 3 to 7 | Check any proposed codebook against proved region-volume bounds before engineering packed formats. |
| **Regex shell-text gates and hot-file markdown ledgers** | Shell-command text parsers suffered repeated structural bypasses (newline pipes, option-value confusion, quoted Git paths). Shared decision and index files serialized parallel agents into constant merge conflicts. | `Moissanite-Labs/exo` issue tracker | Replace shell-text parsing with structured CST broker verbs and replace hand-edited ledgers with generated per-packet entries. |
| **Constructed text vocabularies for automated search** | Invented ASCII symbol languages produced zero evolutionary wins in `abios` trials where executable positional ASTs succeeded. | `Moissanite-Labs/abios` search records | Keep human surfaces in plain language and machine wire surfaces in typed, executable structural formats. |
| **Prompt-level `CMD`/`DATA` peer-injection envelopes** | Across 30 trials on `Qwen2.5-3B`, adding prompt envelopes failed to stop hidden peer orders (`obey_delete` rose `29/30` to `30/30`) and increased strict token leaks (`2/30` to `11/30`). | `Moissanite-Labs/abios` PR 41 | Enforce tool, credential, and oracle isolation in the OS (`Landlock`/`bubblewrap`, read-only mounts), never via prompt tags. |
| **Nucleus truncation (`top_p = 0.95`) in self-play** | In a Zipf(1.1) 400-intent simulation (40 rare), `top_p = 0.95` killed `40/40` rare intents by generation 5 even with 10 percent real data (`top_p = 1.0` preserved `~10.8/40` at gen 50). | `Moissanite-Labs/scry` PR 1 | Keep proposal distributions untrimmed during evolutionary search and protect rare specialists via deduplicated lexicase. |
| **Rival twin-building scoring incentives** | Exact game proof and Gemini relay pilot showed rival twin scoring gives zero incentive to improve twin building (`0.89-0.99` solo match, twin harnesses were weakest builders). | `weft-loom` branch `bayan/vigilant-johnson-egs6w8` | Score builders directly against verifier-owned external anchors and private holdouts, not rival zero-sum pairings. |
| **Unadapted readout of compact wire glyphs** | On `Qwen2.5-0.5B/1.5B`, hidden states linearly decoded `glyph_g1`, yet unadapted readout collapsed to `0.558` (`0.542` with legend) vs `1.000` JSON and `0.892`/`0.917` ABIOS refs. | `Moissanite-Labs/tokenpage` PR 5 | Pair compact agent wire dialects with tiny zone-scoped readout adapters (`weft`) instead of expecting zero-shot legend reading. |

## Summary of Claim Boundaries

Every positive claim in Section 1 traces to a committed public repository and test suite. `siliconcordat/weft` E3 and E4 now confirm real-checkpoint Safetensors plumbing, asymmetric `int4/int8` factor packing (`18.37x` to `20.03x` leakage reduction), and noise-only `K0` covariance (`83.9%` recovery) on `TinyStories-1M`. Multi-adapter SOP generalization, loud-column savings, and readout adaptation on real 1.5B to 27B instruct checkpoints remain open Milestone 3 falsifiers.
