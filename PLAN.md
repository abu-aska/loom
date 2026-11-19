# Loom Research Plan

This plan defines the research agenda for `siliconcordat/loom`, the Layer 1 hardware theory and frontier evaluation repository in the Siliconcordat stack. Every document in this plan grounds unfamiliar architectural ideas in first principles, explicit mathematics, and falsifiable tests rather than hand-waving or reflexive dismissal.

## Scope Boundary

- **In scope:** Cross-layer mathematical derivations, empirical frontier audits across public repositories, exact memory-bandwidth and roofline models, hardware architecture theses derived directly from Layer 2 through Layer 5 bottlenecks, and pure Python scripts that verify every equation and number in the papers.
- **Out of scope:** Production firmware, FPGA bitstreams, kernel patches, OS imaging, and model training pipelines. Those remain in upper layers (`mde`, `exo`, `warp`, `weft`) or later hardware phases.

## Six Deep Threads

The research program pulls six interconnected threads across the stack to their logical and mathematical conclusions:

1. **Thread 1 (Shared-Token Subspace Collapse):** Why naive null-space projection works for sparse factual edits yet degrades when multiple behavioral style packs share common tokens, and what structural conditions restore composability.
2. **Thread 2 (Anti-Goodhart Verification Unification):** Why committed behavioral checks, dual-oracle formal audits, external multi-kernel verification bars, and two-tier lexicase anchors are instances of one formal game against adaptive optimizers.
3. **Thread 3 (L5 Syntax Zone to L2 Weight Subspace Duality):** How deterministic concrete syntax tree (CST) zone boundaries at Layer 5 (`prose`, `code`, `formal_proof`, `ui_module`) partition Layer 2 activation subspaces and drive Layer 4 dynamic adapter gating.
4. **Thread 4 (Cross-Generation Recompilable Software):** How causal self-improvement memory, durable capability charters, and text-first policy histories allow software habits and weight adapters to recompile or retire cleanly across base model upgrades.
5. **Thread 5 (L1 Hardware Physics From Real Bottlenecks):** Four concrete hardware theses derived from measured bottlenecks in verifiable multi-adapter inference: DMA-boundary integer certificate checking, fused native multi-adapter datapaths, capability-tagged KV and recurrent-state banks, and exact-radix deterministic verification units.
6. **Thread 6 (External-Pinned Multi-Tier Selection):** Exact boundary conditions separating valid multi-objective search from specification gaming, visible-probe overfitting, and single-step evolutionary cliffs.

## Deliverables

| Order | Artifact | Core Question Answered | Falsification Bar |
| --- | --- | --- | --- |
| 1 | `docs/01-frontier-evaluation.md` | Where has the public 4-org work broken real ground vs hit empirical dead ends? | Every entry cites a public repo, measured number, or open falsifier with explicit claim tags |
| 2 | `docs/02-unified-verification-primitive.md` | What formal conditions defeat reward hacking across both code synthesis and weight compilation? | Explicit theorem conditions, failure counterexamples, and quantitative attack bounds |
| 3 | `docs/03-zone-subspace-duality.md` | How do L5 CST zones, L4 failure traces, and L2 orthogonal slabs form composable parametric software? | Exact rank/interference equations, failure regimes, and convergence predictions |
| 4 | `docs/04-loom-hardware-physics.md` | What minimal silicon primitives remove the memory-bandwidth, rollback, and TCB walls of multi-adapter serving? | Closed-form bandwidth arithmetic, rooflines for 8 GiB to 64 GiB systems, and software/FPGA refutation tests |
| 5 | `scripts/verify_math.py` | Do all derived bounds, rank counts, and roofline tables hold numerically? | Standard-library `unittest` suite checking every table and equation in `docs/01` through `docs/04` |

## Quality Gates

1. Every markdown file and GitHub issue body passes `check-prose.py` and `check-prose.py --dupes` with exit code 0.
2. Zero private repository content, zero secrets, zero local filesystem paths, and zero `Co-authored-by` trailers appear in any commit or issue.
3. Every numerical table and roofline equation in `docs/` is verified by `scripts/verify_math.py` before tagging independent verification.
4. Proposals and synthetic derivations are never presented as real-checkpoint or silicon-measured results.
