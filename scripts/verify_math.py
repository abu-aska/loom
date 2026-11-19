"""Deterministic verification of mathematical bounds and roofline tables in siliconcordat/loom.

Standard-library only (Apache-2.0). Run with:
    python3 -m unittest -v scripts/verify_math.py
"""

import math
import unittest


def min_holdout_size(epsilon: float, delta: float, num_finalists: int) -> int:
    """Minimum private holdout count k_h so M * exp(-epsilon * k_h) <= delta."""
    if not (0.0 < epsilon < 1.0 and 0.0 < delta < 1.0 and num_finalists >= 1):
        raise ValueError("Invalid bound parameters")
    return math.ceil(math.log(num_finalists / delta) / epsilon)


def exact_false_accept_upper(epsilon: float, k_h: int, num_finalists: int) -> float:
    """Union bound M * (1 - epsilon)^k_h on false acceptance of error >= epsilon."""
    return num_finalists * ((1.0 - epsilon) ** k_h)


def lexicase_specialist_survival(k_anchors: int, num_draws: int) -> float:
    """Lower bound 1 - (1 - 1/k)^N on selecting a unique-anchor specialist at least once."""
    return 1.0 - ((1.0 - 1.0 / k_anchors) ** num_draws)


def residual_escape_rate(structural_catch: float, mutation_kill: float) -> float:
    """Combined escape rate (1 - gamma) * (1 - mu) for independent gates."""
    return (1.0 - structural_catch) * (1.0 - mutation_kill)


def ive_macs_per_projection(d_in: int, d_out: int, rank: int, k_c: int) -> int:
    """Integer MACs for ||B_q (A_q U_0)||_F^2: (A_q @ U_0) + (B_q @ M_1)."""
    return (rank * d_in * k_c) + (d_out * rank * k_c)


def adapter_bytes_f16(num_projections: int, d_in: int, d_out: int, rank: int) -> int:
    """Exact byte footprint for F16 LoRA factors A (r x d_in) and B (d_out x r)."""
    return num_projections * rank * (d_in + d_out) * 2


def recurrent_snapshot_bytes_bf16(num_ssm_layers: int, num_heads: int, state_dim: int) -> int:
    """Exact byte footprint for one BF16 hybrid SSM/DeltaNet recurrent state snapshot."""
    return num_ssm_layers * num_heads * state_dim * state_dim * 2


class TestLoomMath(unittest.TestCase):
    def test_doc02_goodhart_holdout_bounds(self):
        # M = 10 finalists, epsilon = 0.10 error floor, delta = 0.01 failure risk
        k_10 = min_holdout_size(epsilon=0.10, delta=0.01, num_finalists=10)
        self.assertEqual(k_10, 70)
        self.assertLess(exact_false_accept_upper(0.10, k_10, 10), 0.01)

        # M = 100 finalists, epsilon = 0.10, delta = 0.01
        k_100 = min_holdout_size(epsilon=0.10, delta=0.01, num_finalists=100)
        self.assertEqual(k_100, 93)
        self.assertLess(exact_false_accept_upper(0.10, k_100, 100), 0.01)

        # M = 1 single committed candidate, epsilon = 0.05, delta = 0.01
        k_1_05 = min_holdout_size(epsilon=0.05, delta=0.01, num_finalists=1)
        self.assertEqual(k_1_05, 93)
        self.assertLess(exact_false_accept_upper(0.05, k_1_05, 1), 0.01)

        # M = 10 finalists, epsilon = 0.05, delta = 0.01
        k_10_05 = min_holdout_size(epsilon=0.05, delta=0.01, num_finalists=10)
        self.assertEqual(k_10_05, 139)
        self.assertLess(exact_false_accept_upper(0.05, k_10_05, 10), 0.01)

    def test_doc02_sabotage_escape_and_lexicase(self):
        # Norm-only (gamma = 0.0) + weak tests (mu = 0.30) -> 70% escape
        self.assertAlmostEqual(residual_escape_rate(0.0, 0.30), 0.70, places=6)
        # Compiler/null-space (gamma = 0.90) + mutation floor (mu = 0.80) -> 2% escape
        self.assertAlmostEqual(residual_escape_rate(0.90, 0.80), 0.02, places=6)

        # Lexicase specialist survival: k = 4 anchors, N = 16 draws -> 99.00%
        p_surv = lexicase_specialist_survival(k_anchors=4, num_draws=16)
        self.assertAlmostEqual(p_surv, 0.9899773628, places=6)
        self.assertGreater(p_surv, 0.9899)

        # k = 8 anchors, N = 32 draws -> 98.61%
        p_surv_8 = lexicase_specialist_survival(k_anchors=8, num_draws=32)
        self.assertAlmostEqual(p_surv_8, 0.9860601630, places=6)

    def test_doc03_subspace_signal_and_layer_drift(self):
        # Sandwich bound for unit vectors v in S_j projected onto S_{<j}^perp:
        #   sin^2(theta_min) <= ||P v||_2^2 <= sin^2(theta_max)
        # Verify on explicit 3D example: S_{<j} = span{e_1},
        # S_j = span{u_1 = (cos 10, sin 10, 0), u_2 = (0, 0, 1)} -> theta_min=10 deg, theta_max=90 deg
        t_min = math.radians(10.0)
        u1 = (math.cos(t_min), math.sin(t_min), 0.0)
        u2 = (0.0, 0.0, 1.0)
        # Projecting onto S_{<j}^perp zeros the e_1 coordinate
        surv_u1 = (u1[1] ** 2) + (u1[2] ** 2)
        surv_u2 = (u2[1] ** 2) + (u2[2] ** 2)
        self.assertAlmostEqual(surv_u1, math.sin(t_min) ** 2, places=12)
        self.assertAlmostEqual(surv_u1, 0.0301536896, places=6)
        self.assertAlmostEqual(surv_u2, 1.0, places=12)
        self.assertLessEqual(math.sin(t_min) ** 2, surv_u1 + 1e-12)
        self.assertLessEqual(surv_u1, surv_u2)

        # Guaranteed floor across ALL directions in S_j when theta_min = 60 deg: >= 75.00%
        eta_floor_60 = math.sin(math.radians(60.0)) ** 2
        self.assertAlmostEqual(eta_floor_60, 0.75, places=6)

        # Multi-layer drift amplification sum_{l=1..L} eps * kappa^(L-l)
        # L = 36 layers, per-layer eps = 1e-4, Lipschitz kappa = 1.05
        L, eps, kappa = 36, 1e-4, 1.05
        total_drift = eps * ((kappa ** L) - 1.0) / (kappa - 1.0)
        self.assertAlmostEqual(total_drift, 0.0095836323, places=6)  # ~95.8x single-layer eps

    def test_doc04_thesis1_dma_ive_arithmetic(self):
        # 4B model: L=36, 2 adapted projections/layer (o_proj + down_proj) = 72
        # d_in = d_out = 2560, r = 16, compressed preservation rank k_c = 256
        macs_proj_4b = ive_macs_per_projection(2560, 2560, 16, 256)
        self.assertEqual(macs_proj_4b, 20_971_520)
        total_macs_4b = macs_proj_4b * 72
        self.assertEqual(total_macs_4b, 1_509_949_440)  # 1.510 GMAC

        # 64-MAC @ 1.0 GHz = 64 GMAC/s -> 23.59 ms; 256 GMAC/s -> 5.90 ms
        latency_ms_4b = (total_macs_4b / 64e9) * 1e3
        self.assertAlmostEqual(latency_ms_4b, 23.59296, places=4)
        self.assertAlmostEqual((total_macs_4b / 256e9) * 1e3, 5.89824, places=4)

        # Adapter F16 byte size for 72 projections (r=16, d=2560): 11.25 MiB
        bytes_4b = adapter_bytes_f16(72, 2560, 2560, 16)
        self.assertEqual(bytes_4b, 11_796_480)
        self.assertAlmostEqual(bytes_4b / (1024 ** 2), 11.25, places=6)

        # 27B model: L=64, 2 projections/layer = 128, d=5120, r=32, k_c=256
        bytes_27b = adapter_bytes_f16(128, 5120, 5120, 32)
        self.assertEqual(bytes_27b, 83_886_080)
        self.assertAlmostEqual(bytes_27b / (1024 ** 2), 80.0, places=6)
        macs_proj_27b = ive_macs_per_projection(5120, 5120, 32, 256)
        self.assertEqual(macs_proj_27b, 83_886_080)
        total_macs_27b = macs_proj_27b * 128
        self.assertEqual(total_macs_27b, 10_737_418_240)  # 10.737 GMAC
        self.assertAlmostEqual((total_macs_27b / 64e9) * 1e3, 167.77216, places=4)
        self.assertAlmostEqual((total_macs_27b / 256e9) * 1e3, 41.94304, places=4)

    def test_doc04_thesis2_multi_sgmv_rooflines(self):
        # Pre-merge combinatorial explosion: 2^N - 1
        self.assertEqual((1 << 3) - 1, 7)
        self.assertEqual((1 << 5) - 1, 31)
        self.assertEqual((1 << 8) - 1, 255)

        # Case A: 4B Q4_K_M (~2.10 GiB = 2.25486 GB) on 8 GiB GPU @ 350 GB/s sustained
        base_4b_bytes = int(2.10 * (1024 ** 3))
        bw_3080 = 350e9  # bytes/s
        base_ms_4b = (base_4b_bytes / bw_3080) * 1e3
        self.assertAlmostEqual(base_ms_4b, 6.44245, places=4)
        self.assertAlmostEqual(1e3 / base_ms_4b, 155.2204, places=3)

        # 3 F16 r=16 adapters (72 projs each): 33.75 MiB = 35.38944 MB
        three_4b_bytes = 3 * adapter_bytes_f16(72, 2560, 2560, 16)
        self.assertAlmostEqual(three_4b_bytes / (1024 ** 2), 33.75, places=6)
        fused_stream_ms_4b = (three_4b_bytes / bw_3080) * 1e3
        self.assertAlmostEqual(fused_stream_ms_4b, 0.10111, places=4)
        self.assertAlmostEqual((fused_stream_ms_4b / base_ms_4b) * 100.0, 1.5695, places=3)

        # Unfused launch overhead: 3 * 72 = 216 launches @ 8 us = 1.728 ms (+26.82%)
        unfused_ms_4b = 3 * 72 * 8e-3
        self.assertAlmostEqual(unfused_ms_4b, 1.728, places=6)
        self.assertAlmostEqual((unfused_ms_4b / base_ms_4b) * 100.0, 26.8221, places=3)
        q45_3_ms_4b = fused_stream_ms_4b * (4.5 / 16.0)
        self.assertAlmostEqual(q45_3_ms_4b, 0.02844, places=4)
        self.assertAlmostEqual((q45_3_ms_4b / base_ms_4b) * 100.0, 0.4414, places=3)

        # Case B: 27B Q4_K_M (15.24 GiB = 16.36382 GB) on M1 Max @ 320 GB/s sustained
        base_27b_bytes = int(15.24 * (1024 ** 3))
        bw_m1max = 320e9
        base_ms_27b = (base_27b_bytes / bw_m1max) * 1e3
        self.assertAlmostEqual(base_ms_27b, 51.13695, places=4)
        self.assertAlmostEqual(1e3 / base_ms_27b, 19.5553, places=3)

        # 3 F16 r=32 all-linear adapters (304.0 MiB each -> 912.0 MiB = 0.890625 GiB)
        one_27b_lora = int(304.0 * (1024 ** 2))
        three_27b_bytes = 3 * one_27b_lora
        self.assertAlmostEqual(three_27b_bytes / (1024 ** 3), 0.890625, places=6)
        fused_3_ms_27b = (three_27b_bytes / bw_m1max) * 1e3
        self.assertAlmostEqual(fused_3_ms_27b, 2.98844, places=4)
        self.assertAlmostEqual((fused_3_ms_27b / base_ms_27b) * 100.0, 5.8440, places=3)
        unfused_3_ms_27b = 3 * 448 * 8e-3
        self.assertAlmostEqual(unfused_3_ms_27b, 10.752, places=6)
        self.assertAlmostEqual((unfused_3_ms_27b / base_ms_27b) * 100.0, 21.0259, places=3)
        q45_3_ms_27b = fused_3_ms_27b * (4.5 / 16.0)
        self.assertAlmostEqual(q45_3_ms_27b, 0.84050, places=4)
        self.assertAlmostEqual((q45_3_ms_27b / base_ms_27b) * 100.0, 1.6436, places=3)

        # 8 F16 r=32 adapters: 2432 MiB = 2.375 GiB -> 7.969 ms (+15.58%)
        eight_27b_bytes = 8 * one_27b_lora
        self.assertAlmostEqual(eight_27b_bytes / (1024 ** 3), 2.375, places=6)
        fused_8_ms_27b = (eight_27b_bytes / bw_m1max) * 1e3
        self.assertAlmostEqual(fused_8_ms_27b, 7.96918, places=4)
        self.assertAlmostEqual((fused_8_ms_27b / base_ms_27b) * 100.0, 15.5840, places=3)

        # Unfused 8 * 448 launches @ 8 us = 28.672 ms (+56.07%)
        unfused_8_ms_27b = 8 * 448 * 8e-3
        self.assertAlmostEqual(unfused_8_ms_27b, 28.672, places=6)
        self.assertAlmostEqual((unfused_8_ms_27b / base_ms_27b) * 100.0, 56.0690, places=3)

        # INT4 (4.5-bit effective) adapter compression: 16 / 4.5 = 3.5556x reduction
        q45_8_ms_27b = fused_8_ms_27b * (4.5 / 16.0)
        self.assertAlmostEqual(q45_8_ms_27b, 2.24133, places=4)
        self.assertAlmostEqual((q45_8_ms_27b / base_ms_27b) * 100.0, 4.3830, places=3)

    def test_doc04_thesis3_tagged_recurrent_rollback(self):
        # 4B hybrid: 24 SSM layers, 16 heads, 64x64 BF16 state -> 3.00 MiB/snapshot
        snap_4b = recurrent_snapshot_bytes_bf16(24, 16, 64)
        self.assertEqual(snap_4b, 3_145_728)
        self.assertAlmostEqual(snap_4b / (1024 ** 2), 3.0, places=6)
        self.assertAlmostEqual((8 * snap_4b) / (8 * (1024 ** 3)) * 100.0, 0.29297, places=4)

        # Restore time @ 350 GB/s vs 16384-tok re-prefill @ 1500 tok/s (10.923 s)
        restore_ms_4b = (snap_4b / 350e9) * 1e3
        prefill_ms_4b = (16384.0 / 1500.0) * 1e3
        self.assertAlmostEqual(restore_ms_4b, 0.008988, places=5)
        self.assertAlmostEqual(prefill_ms_4b, 10922.6667, places=3)
        self.assertGreater(prefill_ms_4b / restore_ms_4b, 1_200_000.0)

        # 27B hybrid: 48 SSM layers, 32 heads, 64x64 BF16 state -> 12.00 MiB/snapshot
        snap_27b = recurrent_snapshot_bytes_bf16(48, 32, 64)
        self.assertEqual(snap_27b, 12_582_912)
        self.assertAlmostEqual(snap_27b / (1024 ** 2), 12.0, places=6)
        self.assertAlmostEqual((8 * snap_27b) / (64 * (1024 ** 3)) * 100.0, 0.14648, places=4)
        restore_ms_27b = (snap_27b / 320e9) * 1e3
        self.assertAlmostEqual(restore_ms_27b, 0.03932, places=4)
        # Conservative 1500 tok/s prefill (10.92 s) -> >277,000x faster
        self.assertGreater(prefill_ms_4b / restore_ms_27b, 277_000.0)

        # 27B hybrid with larger 128x128 head state (4x): 48.00 MiB, 8 ckpts = 384 MiB (0.59%), 0.157 ms
        snap_27b_128 = recurrent_snapshot_bytes_bf16(48, 32, 128)
        self.assertAlmostEqual(snap_27b_128 / (1024 ** 2), 48.0, places=6)
        self.assertAlmostEqual((8 * snap_27b_128) / (64 * (1024 ** 3)) * 100.0, 0.58594, places=4)
        self.assertAlmostEqual((snap_27b_128 / 320e9) * 1e3, 0.15729, places=4)

    def test_doc04_thesis4_exact_radix_accumulator(self):
        # BF16 (1s, 8e, 7m): smallest subnormal = 2^(-126-7) = 2^(-133)
        # Smallest nonzero product = 2^(-266); max product = (2 - 2^-7)^2 * 2^254 < 2^256 (MSB 255)
        # Exact product bit span = 255 - (-266) + 1 = 522 bits (+ 64b carry -> 586b, fits in 640b = 10x64b)
        min_prod_exp = -133 * 2
        max_prod_msb = 255
        prod_span = max_prod_msb - min_prod_exp + 1
        self.assertEqual(prod_span, 522)
        self.assertLessEqual(prod_span + 64, 640)

        # Full two's-complement signed INT8 [-128, 127] dot product over group G=128:
        # max product (-128)*(-128) = 16384; * 128 = 2,097,152 = 2^21 (< 2^22, fits in INT32)
        max_block_sum_i8 = 128 * ((-128) ** 2)
        self.assertEqual(max_block_sum_i8, 2_097_152)
        self.assertEqual(max_block_sum_i8, 1 << 21)
        self.assertLess(max_block_sum_i8, 1 << 22)

        # Across N_groups = 2^20 blocks, max integer magnitude = 2^41 << 2^63 (signed INT64)
        self.assertEqual(max_block_sum_i8 * (1 << 20), 1 << 41)
        self.assertLess(max_block_sum_i8 * (1 << 20), (1 << 63) - 1)


if __name__ == "__main__":
    unittest.main()
