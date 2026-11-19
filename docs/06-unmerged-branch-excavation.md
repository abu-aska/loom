# Unmerged Branch and Open PR Excavation

Auditing only default branches (`main`) misses a large share of active research and verification engineering across our public organizations. This document records a live read-only scan conducted on 2026-11-19 across 80 verified-public repositories (`private == false` confirmed via GitHub API on every listed repository).

Every cited result keeps its upstream claim status (`claimed`, `reproduced`, `verified`, or `source claim`). Private repositories are strictly excluded.

## 1. Census Across 80 Public Repositories

| Scope (Verified Public Only) | Public Repos | Open PRs | Non-Default Branches | Primary Concentration |
| --- | ---: | ---: | ---: | --- |
| `Foundation-0` (6 private repos excluded) | `36` | `191` | `312` | November 2026 `review/F1`-`F8`, `review/O1`-`O2`, and `symbiosis/2026-11-review` branches |
| `Proven-Commons` (`0` private) | `40` | `26` | `89` | Verified Bar v2 audits, dynamic reviewer checks, and Lean parser slices |
| `ahrazzle/soko` | `1` | `3` | `45` | Unsound-certificate experience report and 9-flow transport relaxation audits |
| `silic0n`-linked circuit and math repos (`ahrazzle`) | `3` | `0` | `23` | `mobius-x1`, `gf2m-circuits`, and `integer-mult-bounds` research branches |
| **Total** | **`80`** | **`220`** | **`469`** | **Substantial certified math and verifier hardening sits unmerged** |

## 2. Major Unmerged Scientific and Mathematical Results

Reading only `main` hides seven concrete mathematical and circuit results sitting in open pull requests and unmerged branches awaiting independent human merge:

| Public Repository and Ref | Result Summary | Claim Status and Verification Scope |
| --- | --- | --- |
| `Foundation-0/point-charges` (PR 22) and `Foundation-0/f0` (PR 58, PR 61) | Three distinct configurations of four positive point charges with 11 non-degenerate equilibria against Maxwell's bound of 9 (published July 2026 counterexample starts at 5 charges). Also certifies 5, 6, and 7 charges (24, 29, 44 equilibria). | `claimed`, independently re-proved in `f0` PR 61. Narrow stability (`1e-5` perturbation breaks examples). Human refereeing pending. |
| `Foundation-0/rigid-realizations` (PR 21) | Certifies an 11-vertex planar rigid graph (`18120782205838348`) with all `2,288` of `2,288` complex realizations real, raising the asymptotic lower bound to `1144^(1/8) = 2.4116` per vertex (vs `2.3780` published and `2.3858` for `L880`). Adds a 12-vertex result (`3,904` of `6,180` real) and a stdlib zero-shared-code re-check of `L880`. | `claimed` on open PR. Pending independent human verification. |
| `Foundation-0/finite-state-proofs` (PR 5) | Expands `main`'s 11 OEIS proofs to `238` proved recurrences (`211` first-pass plus `27` via a proved Square Law theorem for grids with one marked pair), backed by `105/105` and `73/73` corruption-rejection tests. | `claimed` on open PR. Human read of transfer-matrix link pending. |
| `Foundation-0/gfq-codes` (PR 19) | Runs exact Delsarte linear-programming bounds across open GF(7), GF(8), and GF(9) linear-code tables: `94` improved entries in GF(7) from 12 base certificates, `1,408` in GF(8) from 62 bases, and `916` in GF(9) from 48 bases (`2,418` improved entries total from 122 certificates). | `claimed` on open PR. Table-lag check against specialist tables pending. |
| `Foundation-0/relative-equilibria` (PR 16) | Existence, uniqueness-in-box, and non-degeneracy certificates for 20, 42, and 67 planar central configuration classes of 8, 9, and 10 equal masses with exact Morse identities (`1/56`, `-1/72`, `1/90`). | `reproduced` (matches published numerical counts, completeness above 7 bodies not proved). |
| `Foundation-0/incentre-lattices` (PR 102, PR 43-100) | Tightens elasticity wording to `C44 = 0` with two independent exact checks, adds isolating must-fail controls across fold/packing replay scripts, and hardens `chk_independent.py` to fail closed. | Open review wave (`31` open PRs, `24` conflicting per `f0` PR 48). |
| `Foundation-0/silic0n` (Issues 1-3) -> [`ahrazzle/mobius-x1`](https://github.com/ahrazzle/mobius-x1), [`ahrazzle/gf2m-circuits`](https://github.com/ahrazzle/gf2m-circuits), [`ahrazzle/integer-mult-bounds`](https://github.com/ahrazzle/integer-mult-bounds) | Direct L1 circuit and algorithm ground: `o(N log N)` GF(2) Mobius/zeta XOR circuits (`e1-full-network-run`), Lean-proved smaller `GF(2^m)` multipliers and AES S-boxes (`contrib-fields-9-10-11-ghash`, `contrib-fields-14-15-16`), and conditional `kappa > 2^-15` integer multiplication bounds (`20` unmerged branches). | `source claim` and Lean-checked where stated. Not yet human-refereed. |

## 3. Six Systemic Verification Findings Directly Shaping Siliconcordat

Beyond domain science, the unmerged November review PRs expose six concrete verification failure modes and engineering primitives that directly strengthen Layers 1 through 5 of Siliconcordat.

### 3.1 Bare Python `assert` Statements Silently Vanish Under `python -O`

- **Source:** `Foundation-0/f0` PR 49 (`o2-method.md`, mechanical audit across 159 verifiers in normal, `-O`, and empty-cwd modes), `Foundation-0/point-charges` PR 22, `Foundation-0/vitruvian3d` PR 12 and PR 13, `Foundation-0/incentre-lattices` PR 45, and `Foundation-0/gravity` PR 29.
- **Defect discovered (`verified`):** Certificate checkers using bare `assert` statements silently skipped proof checks under `python3 -O`, allowing corrupted certificates to print `VERIFIED`.
- **Siliconcordat rule:** Zero bare `assert` checks inside any verifier (`weft`, `warp`, `exo`, `loom`). Every verification script must raise explicit errors (`VerificationError` or `ValueError`) and run corrupted-input controls under `python3 -O`.

### 3.2 Vacuous Zero-Input Pass on Empty Directories

- **Source:** `Foundation-0/formal-claims-audit` PR 19.
- **Defect discovered (`verified`):** `check_verdicts.py` printed `OK: checked 0 verdict file(s)` and exited 0 on an empty verdict directory.
- **Siliconcordat rule:** Every suite verifier (`weft` `AnchorSuite`, `mde` `splice_verify`, `warp` canary runner) must fail closed when required anchor, verdict, or holdout sets are empty.

### 3.3 Static Anti-Tautology Scanners Do Not Prove Soundness

- **Source:** `Foundation-0/formal-claims-audit` PR 16 and PR 17, `Foundation-0/f0` PR 56 (`new-ground.md`), and `Foundation-0/proven-commons` PR 9.
- **Python scanner repair (`verified`):** PR 16's initial AST anti-tautology scanner failed to parse, missed cross-scope renames, and accepted structurally distinct always-true checkers. PR 17 repaired it and set a sharp rule: `NOT_DETECTED` never certifies soundness, and unsupported comparisons return `INCONCLUSIVE`.
- **Lean scanner repair (`verified`):** `f0` PR 56 caught a proposed Lean scanner passing a file that proved `False`. `Foundation-0/proven-commons` PR 9 replaced it with a full Lean 4 token-stream surface scanner (`12/12` forbidden constructs caught, `0/4` false positives).
- **Siliconcordat rule:** Static guards (`mde guard`, AST checks, Lean surface scans) are strictly fail-closed pre-filters, never substitutes for execution against independent oracles and private holdouts.

### 3.4 64-Bit Hash Collisions Corrupt Exhaustive Search Bounds

- **Source:** `Proven-Commons/mission` PR 37, `Foundation-0/f0` PR 36, and `ahrazzle/soko` PR 18 and PR 20.
- **Defect discovered (`verified`):** `mission` PR 37 records `181.0M` observed 64-bit hash memoization collisions across `141.1M` states (alongside `22,658` tag collisions at `27.66M` states in `f0` PR 36). `soko` PR 18 packages the post-mortem as a 6-page experience report ("Green Tests, Unsound Certificates").
- **Siliconcordat rule:** Exhaustive lower bounds and cache-indexed verification tables require full canonical keys (never 64-bit hash-only deduplication) plus `O(|E|)` admissibility checks.

### 3.5 Quantified Multi-Agent Merge and Overwrite Decay Justifying L5 `mde`

- **Source:** `Foundation-0/f0` PR 48 (`O1` organization overlap and overwrite scan).
- **Measured finding (`verified`):** Across `Foundation-0`, `250` of `520` default-branch commits bypassed pull requests, `34` of `167` open PRs conflicted (`24` in `incentre-lattices`), `97` branches carried nothing new, and one silent stale-base overwrite dropped `104` lines in `gravity`.
- **Siliconcordat rule:** Confirms directly why `siliconcordat/mde` enforces `base_tree` freshness before `splice_project`, requires `read_token` locks, and replaces hot-file ledgers with generated entries.

### 3.6 Unmerged Formal Primitives Reusable Across L3, L4, and L5

- **Dynamic independent spec reviewers (`Proven-Commons/mission` PR 25):** Replaces the empty static `bar/reviewers.toml` roster on `main` with live maintainer-permission checks at the exact PR head while rejecting all spec-file authors and committers. Directly solves the reviewer deadlock noted in `docs/01-frontier-evaluation.md`.
- **Lean-proved `deny` precedence (`Proven-Commons/cedar` PR 2):** Proves five Lean theorems (`authorize_iff`, `forbid_denies`, `default_denies`, `order_invariant`, `members_invariant`) with an independent Python model. Directly reusable as a formally verified policy core for `siliconcordat/exo` and `siliconcordat/warp` authorization gates.
- **Proved path containment and parser slices (`Proven-Commons/tar` PR 2-6, `http` PR 3-4, `zip` review in `mission` PR 36, `path` PR 6):** Proved no-escape path containment (including `0x00` NUL-byte findings in `mission` PR 36) and verified wire parsers directly usable at L3/L5 parser boundaries.
- **Anchored Conservation Quotient and Convergence Loom (`Foundation-0/f0` PR 39 and PR 59):** PR 39 formalizes a 4-gate Lean `AnchoredConservationQuotient` reference package, while PR 59 builds the interactive `/loom` atlas weaving six research threads through three verification gates.

## 4. Direct Upgrades Adopted in `siliconcordat/loom`

1. Verified both `scripts/verify_math.py` and `scripts/verify_convergences.py` under `python3 -O -B -m unittest` (zero bare `assert` statements, using explicit `unittest` assertions and raised exceptions only).
2. Updated [`docs/01-frontier-evaluation.md`](01-frontier-evaluation.md) to reflect the `silic0n` circuit/multiplication repositories and the unmerged `Foundation-0` / `Proven-Commons` verification wave.
3. Scoped Section 5 below for appending the companion `Moissanite-Labs` L2/L3/L4/L5 unmerged branch excavations once those layer audits land.

## 5. Pending Companion Excavation Scope

This revision covers all 80 verified-public repositories across `Foundation-0`, `Proven-Commons`, `ahrazzle/soko`, and `silic0n`'s linked circuit repositories. Companion public branch excavations for `Moissanite-Labs` Layer 2 (`MDE`, `weft-loom`, `siliquant`, `weft-eido`, `nullmodem`, `spliceware`) and Layers 3 through 5 (`exo-os`, `exo`, `exyber`, `synbios`, `ethos`, `abios`, `synmerit`) will append here as independent public audits complete.
