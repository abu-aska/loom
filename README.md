# loom

`loom` is the Layer 1 hardware theory and frontier research repository for the Siliconcordat stack. It derives hardware physics, formal verification limits, and weight-subspace math from bottlenecks measured in Layers 2 through 5. It is for systems researchers and engineers evaluating where verifiable parametric software hits real silicon limits.

This repository holds research, mathematical proofs, roofline arithmetic, and analytical verification scripts. It contains no silicon RTL, kernel drivers, or OS images, so hardware theory never blocks delivery of the software layers above it.

## Position in the Siliconcordat Stack

| Layer | Repository | Role |
| --- | --- | --- |
| L5 Improved MCP | [`siliconcordat/mde`](https://github.com/siliconcordat/mde) | Structural editing broker, syntax zone tagging, and vendor-scoped weight controls |
| L4 Harness | [`siliconcordat/exo`](https://github.com/siliconcordat/exo) | Continuous memory, causal improvement logs, zone routing, and exact-byte human approval |
| L3 OS | [`siliconcordat/warp`](https://github.com/siliconcordat/warp) | Sandboxed execution, deterministic verification runner, and fail-closed model load gate |
| L2 Model | [`siliconcordat/weft`](https://github.com/siliconcordat/weft) | Deterministic weight compilation, null-space projection, and integer certificates |
| **L1 Hardware** | **`siliconcordat/loom`** | **Hardware physics, cross-layer theory, and falsifiable research limits (this repo)** |

## Research Documents

| Document | Topic | Status |
| --- | --- | --- |
| [`PLAN.md`](PLAN.md) | Research scope, six deep threads, and falsification standards | Active |
| [`docs/01-frontier-evaluation.md`](docs/01-frontier-evaluation.md) | Cross-org frontier audit: publishable results, open threads, and confirmed dead ends | Complete |
| [`docs/02-unified-verification-primitive.md`](docs/02-unified-verification-primitive.md) | Anti-Goodhart verifier-owned behavioral commitments across code and weights | Complete |
| [`docs/03-zone-subspace-duality.md`](docs/03-zone-subspace-duality.md) | L5 syntax zones to L2 weight subspaces and cross-generation recompilable software | Complete |
| [`docs/04-loom-hardware-physics.md`](docs/04-loom-hardware-physics.md) | Hardware verification units, fused multi-adapter datapaths, and tagged recurrent state | Complete |
| [`scripts/verify_math.py`](scripts/verify_math.py) | Standard-library `unittest` suite checking every bound and roofline table in `docs/` | Passing (7/7) |

## Check the Math

Run the deterministic verification suite with Python 3 (no external packages required):

```bash
python3 -m unittest -v scripts/verify_math.py
```

## Evidence Discipline

Every claim in `loom` carries an explicit status tag:

- `verified`: derived by closed-form math checked in `scripts/`, or backed by a committed public output file.
- `source claim`: reported in an external paper or upstream repository and not yet reproduced locally.
- `hypothesis`: proposed mechanism with an explicit test and a pre-stated kill condition.

Negative results receive the same record weight as positive results. A path closes only on a proof or a reproducible measurement.

## License

Documentation and research papers are licensed under CC BY 4.0 (see [`LICENSE-DOCS`](LICENSE-DOCS)). Code and verification scripts are licensed under Apache-2.0 (see [`LICENSE`](LICENSE)).
