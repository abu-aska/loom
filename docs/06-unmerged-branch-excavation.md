# Unmerged Branch and Open PR Excavation

Auditing only default branches (`main`) misses a large share of active research and verification engineering across our public organizations. This document records a live read-only scan conducted on 2026-11-19 across 103 verified-public repositories (`private == false` confirmed via GitHub API on every listed repository).

Every cited result keeps its upstream claim status (`claimed`, `reproduced`, `verified`, or `source claim`). Private repositories are strictly excluded.

## 1. Census Across 103 Public Repositories

| Scope (Verified Public Only) | Public Repos | Open PRs | Non-Default Branches | Primary Concentration |
| --- | ---: | ---: | ---: | --- |
| `Foundation-0` (private repos excluded) | `36` | `191` | `312` | November 2026 `review/F1`-`F8`, `review/O1`-`O2`, and `symbiosis/2026-11-review` branches |
| `Proven-Commons` (`0` private) | `40` | `26` | `89` | Verified Bar v2 audits, dynamic reviewer checks, and Lean parser slices |
| `ahrazzle/soko` | `1` | `3` | `45` | Unsound-certificate experience report and 9-flow transport relaxation audits |
| `silic0n`-linked circuit and math repos (`ahrazzle`) | `3` | `0` | `23` | `mobius-x1`, `gf2m-circuits`, and `integer-mult-bounds` research branches |
| `Moissanite-Labs` and `aska-digital` L3/L4/L5 (private excluded) | `13` | `303` | `960` | Stacked Swarm runtime/CLI, zero-`sudo` OS hardening, capability gateway, Ed25519 fixes, peer-injection negative proofs |
| `Moissanite-Labs` L2/quantization/design (private excluded) | `10` | `21` | `72` | Loud-column quantization, noise-only `imatrix`, Episodic C2, WCAG oracle, wire readout gap, sampling collapse |
| **Total** | **`103`** | **`544`** | **`1,501`** | **Certified math, verifier hardening, and cross-layer proofs sit unmerged** |

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

## 4. Direct Upgrades Adopted Across Siliconcordat

1. Verified both `scripts/verify_math.py` and `scripts/verify_convergences.py` under `python3 -O -B -W error -m unittest` (zero bare `assert` statements, explicit `unittest` checks and raised exceptions only).
2. Updated [`docs/01-frontier-evaluation.md`](01-frontier-evaluation.md) and [`docs/05-spliceware-algebra-and-convergences.md`](05-spliceware-algebra-and-convergences.md) with real-checkpoint `weft` E4 confirmation and the four cross-org convergences.
3. Landed concrete cross-layer hardening upstream in `siliconcordat/weft` (`70a4e68`), `siliconcordat/warp` (`d3303fb`: zero-`sudo`, ancestor hardening, archival ledger repair, strict duplicate-key JSON rejection), and `siliconcordat/mde` (`52ce017`: `mde guard --code-audit`, empty-manifest and symlink-cycle fail-closed checks).

## 5. Companion Public Excavations (`Moissanite-Labs` and `aska-digital`)

Independent read-only scans of 23 additional verified-public repositories (`private == false` confirmed via GitHub API on every listed repository) complete the 103-repo audit across Layers 2 through 5.

### 5.1 L3, L4, and L5 Public Repositories (13 Repos, 303 Open PRs, 960 Non-Default Branches)

| Public Repository | Open PRs / Non-Default Branches | Highest-Signal Unmerged Findings (`source claim` / `verified`) |
| --- | --- | --- |
| `Moissanite-Labs/exo-os` | `3` PRs, `8` br | **PR 139 (`fix/no-sudo-in-image`):** Omits `sudo` from the OS image. **PR 140:** Adds `harden-image-modes.sh` normalizing `root:root` plus `go-w` on trusted ancestor paths. **Branch `fix/ledger-repair-reseed` (`dcf936e15e`):** Archives prior history instead of silently resetting ledgers. |
| `Moissanite-Labs/exyber` | `1` PR, `1` br | **PR 1 (`codex/exyber-synthetic-gateway`):** Scoped expiring per-capability grants above transport encryption, `(principal, request_id)` replay rejection, duplicate JSON key ban, and explicit timeout/idempotency/audit boundaries. |
| `aska-digital/hydro-os` | `6` PRs, `9` br | **PR 8 (`exo-watch`):** Memory-guarded 10-minute systemd canary timer. **PR 16 (`pin-downloads`):** Pins download SHA-256 digests and deletes mismatches. **PR 18:** Documents host risks from shared `777` directories and ambient `600` key files. |
| `Moissanite-Labs/exo` | `216` PRs, `775` br | **Stacked Swarm PRs (PR 948 to 1024, PR 1199 to 1219):** Saved groups + private sessions, explicit audiences + delivery/consumption receipts, concurrent runner + stop receipts, principal-only lifecycle/observation and `GroupKnowledge`, conductor vs Socratic launch modes, durable claims + plan liveness. **Orphan canaries:** `alpha/memory-efficiency-canary-20261110` (61 ahead), `alpha/continuation-canary-20261105` (takeover fencing), `alpha/canary-full-only-20261027` (pre-escape secret redaction), PR 1244 (signed thinking replay model binding). |
| `Moissanite-Labs/exo-cli` | `19` PRs, `19` br | Mirrors stacked Swarm CLI across PR 6 to PR 22 (`exo swarm`, `--plan/--grants`, `--durable-attempts`, `--knowledge`, `swarm-group`, `exo profile`). |
| `Moissanite-Labs/exo-desktop` | `37` PRs, `66` br | **PR 23:** Fails closed for read tools on internal error. **PR 71:** Keeps scrubbed tool env authoritative instead of restoring parent credentials. **PR 74:** Returns 400 on malformed `Content-Length`. **PR 48:** Checkout-independent packaged runtime. |
| `Moissanite-Labs/exo-tui` | `2` PRs, `2` br | **PR 1 and PR 3:** Opt-in local mock OpenTUI frontend with scripted approval queue and open-questions surface. |
| `Moissanite-Labs/ethos` | `2` PRs, `6` br | **Branch `mep-v0-20261113`:** Working `mep/` Python reference MCP server (`ethos_decide` adds `decline` so decided records stop shadowing base preferences). **Branch `research-mcp-session-20261114`:** Notes W-MCP gauge/basis bottlenecks (`arXiv:2611.08070`). **PR 4:** Scoped continuity on synthetic fixtures. |
| `Moissanite-Labs/abios` | `8` PRs, `28` br | **PR 41 (`study/peer-injection-pilot`, `verified` negative):** On `Qwen2.5-3B` (30 trials), prompt `CMD`/`DATA` envelopes failed against hidden peer orders (`obey_delete` went `29/30` plain to `30/30` envelope, `envelope_report` raised strict leaks `2/30` to `11/30`). **PR 45:** Domain-separates string vs JSON content digests. **PR 38-51 + `feat/abios3-sealed-sessions`:** ABIOS/3 spec and sealed sessions. |
| `Moissanite-Labs/synbios` | `2` PRs, `27` br | **PR 64:** Continuous synthesis capability charters + local negotiation loop. **PR 63:** Crystal Lattice mission control. Orphan branches harden SYM-2P packet binding (`fix/sym2p-bind-packets`) and hermetic SYM-3 benches (`fix/sym3-hermetic-bench`). |
| `Moissanite-Labs/synmerit` | `3` PRs, `8` br | **PR 10:** Critical Ed25519 hardening rejecting the 8 small-order actor keys (fixing OpenSSL 3.5.4 vs 3.5.9 forgery discrepancy). **PR 17:** 36 language-neutral signed JSON conformance vectors (14 positive, 22 negative). **PR 6:** Permissionless concurrent signed contributions. |
| `Moissanite-Labs/siliconcordat` | `4` PRs, `9` br | **PR 19 (`mithrax-exo-patch-1`):** 13 brainstorm/sketch files extending spliceware direction (`arena.rs`, `flow.py`, `gauntlet.md`, `graft.md`, `mgp.md`, `splice.md`). **PR 9 and PR 12:** Venture thesis and contextual product decisions. |
| `aska-digital/musarchy` | `0` PRs, `2` br | Zero unmerged code commits ahead of `main`. |

### 5.2 L2, Quantization, and Design Public Repositories (10 Repos, 21 Open PRs, 72 Non-Default Branches)

| Public Repository | Open PRs / Non-Default Branches | Highest-Signal Unmerged Findings (`source claim` / `verified`) |
| --- | --- | --- |
| `Moissanite-Labs/siliquant` | `1` PR, `12` br | **PR 12 (`bayan/charming-gates-jlas14`, `3333c42`):** Leaving 10 weight-identifiable loud columns per `ffn_down` whole (`+0.005` bpw, `4.505`-bit packed) cuts `Llama-3.2-1B` KL `34.5%` (`0.0478` to `0.0302`, `0.0340` packed), beating `Q4_K_M` data-free on `Qwen2.5-1.5B` (`0.0222`), `SmolLM2-1.7B` (`0.0528`), and `Llama-3.2-1B` (`0.0302`). **Noise-only `imatrix`:** Random vocab tokens (zero text read) recover `69%` to `96%` of real-text gain and beat real-text `Q4_K_M --imatrix` at strength `0.25` (`0.0228`, `0.0314`, `0.0284`). Honest negatives: `fold-path-codebooks` failed, full-strength `imatrix` degrades, E8 loses to integer ball on `SmolLM2`. |
| `Moissanite-Labs/weft-loom` | `5` PRs, `23` br | **PR 25:** Rejects original CBC Exp C due to token-0 task signaling to external routers and replaces it with **Episodic C2**. **Branch `bayan/vigilant-johnson-egs6w8` (11 ahead):** Exact game proof plus Gemini relay pilot proving rival twin scoring removes incentive to improve twin building (`0.89-0.99` solo match, twin-built harnesses were weakest builders). **PR 37:** Ranks single-GPU DAWE reproduction targets (`Qwen 3.5 4B` first, `Llama 3 8B` cross-family). |
| `Moissanite-Labs/weft-eido` | `10` PRs, `11` br | **PR 25:** Deterministic 360-hue WCAG contrast audit (`120` passing tests, Python cross-checked, ready as a zero-LLM Design MDE oracle). **PR 8:** Fixes CodeQL XSS findings (`innerHTML` to text spans, 65 tests). **PR 22:** Poincare disk Mobius isometries. |
| `Moissanite-Labs/tokenpage` | `2` PRs, `5` br | **PR 1:** ABIOS takes `0.273x` to `0.277x` tokens of compact JSON across 7 tokenizers. **PR 5 (`Qwen2.5-0.5B/1.5B`):** Hidden states linearly decode `glyph_g1`, yet unadapted readout drops to `0.558` (`0.542` with legend) vs `1.000` JSON and `0.892`/`0.917` ABIOS refs, proving compact dialects need explicit readout calibration. |
| `Moissanite-Labs/scry` | `1` PR, `2` br | **PR 1:** Zipf(1.1) collapse over 400 intents (40 rare): `top_p = 1.0` with 10 percent real data retains `~10.8/40` rare intents through gen 50, whereas `top_p = 0.95` kills all `40/40` rare intents by gen 5 even with 10 percent real data. |
| `Moissanite-Labs/MDE` | `1` PR, `10` br | **PR 3** stale/dirty, branch `research/q1-q4-betaedit-projector` (5 ahead) now superseded by `siliconcordat/weft` CPU `float64`, `SHA256SUMS` stale post-PR 2. |
| `Moissanite-Labs/nullmodem` | `1` PR, `3` br | **PR 3:** 3-arm wire benchmark (JSON vs ABIOS vs binary gossip, blocked on substrate fixes). |
| `Moissanite-Labs/heedle`, `spliceware`, `weft-corpus` | `0` PRs, `6` br | Zero unmerged commits ahead of `main` (`heedle` 3 br, `spliceware` 3 br, `weft-corpus` 0 br). |

### 5.3 Four Serendipitous Cross-Org Convergences Surfaced by the Excavation

Synthesizing all 103 public repositories yields four direct cross-layer laws formalized in `docs/05-spliceware-algebra-and-convergences.md` Section 4:

1. **Seeded-Noise `K0` Covariance (`siliquant` PR 12 x `weft` E4):** Random vocab noise recovers `83.9%` of real-text holdout `K0` protection on `TinyStories-1M`, enabling copyright-free, seed-reproducible Hard Veto 1 compilation.
2. **Parametric Wire-Dialect Decoders (`tokenpage` PR 5 x `weft`):** Linear hidden-state separability plus `0.558` unadapted readout drop means tiny zone-scoped `int4/int8` readout adapters can unlock `0.27x` ABIOS compression without base-model retraining.
3. **Irreducible OS + Static + 256-Bit TCB Law (`abios` PR 41 x `f0` PR 49 x `mission` PR 37):** `30/30` prompt-envelope injection failure, bare `assert` vanishing under `-O`, and `181.0M` 64-bit hash collisions prove kernel isolation (`warp`), static code audits (`mde`), and 256-bit keys are irreducible.
4. **Diversity-Preserving Selection Law (`scry` PR 1 x `weft-loom` x `docs/02`):** Nucleus truncation (`40/40` rare intents lost by gen 5), rival twin scoring, and undeduplicated pools share one failure mode that requires untrimmed proposal tails plus deduplicated lexicase under external anchors.
