"""Staging must never let a wrong candidate outrank an exact one."""

from __future__ import annotations

import unittest

from genetic_compression.fitness import INVALID_SIZE, score
from genetic_compression.grammar import ADD, MUL, POW, SHL, SUB, Limits
from genetic_compression.recipe import BinOp, Const, Literal, Recipe

TARGET = (1 << 31).to_bytes(4, "big")
BASELINE = 4


def s(expr, target: bytes = TARGET, baseline: int = BASELINE, limits: Limits | None = None):
    return score(Recipe(expr, len(target)), target, baseline, limits or Limits())


class ExactnessTest(unittest.TestCase):
    def test_exact_candidate_scores_zero_error(self) -> None:
        result = s(BinOp(SHL, Const(1), Const(31)))
        self.assertTrue(result.exact)
        self.assertEqual((result.hamming, result.width_gap, result.magnitude), (0, 0, 0))

    def test_exact_outranks_every_inexact_candidate(self) -> None:
        exact = s(Literal(TARGET))  # exact, but the largest encoding here
        for wrong in (Const(0), Const((1 << 31) - 1), Const(1 << 30), Const(1 << 32)):
            with self.subTest(wrong=wrong):
                self.assertLess(exact.key, s(wrong).key)

    def test_a_tiny_wrong_candidate_cannot_win_on_size(self) -> None:
        """The whole point of staging: 2 bytes and wrong loses to 8 bytes and right."""
        wrong = s(Const(0))
        right = s(Literal(TARGET))
        self.assertLess(wrong.total_bytes, right.total_bytes)
        self.assertLess(right.key, wrong.key)

    def test_smaller_exact_candidate_wins(self) -> None:
        small = s(BinOp(SHL, Const(1), Const(31)))
        large = s(Literal(TARGET))
        self.assertTrue(small.exact and large.exact)
        self.assertLess(small.total_bytes, large.total_bytes)
        self.assertLess(small.key, large.key)


class ErrorMetricTest(unittest.TestCase):
    def test_width_gap_defeats_the_zero_trap(self) -> None:
        """CONST 0 differs from a single-bit target in one bit and must still lose."""
        zero = s(Const(0))
        near = s(Const(1 << 30))
        self.assertLess(zero.hamming, near.hamming)
        self.assertGreater(zero.width_gap, near.width_gap)
        self.assertLess(near.key, zero.key)

    def test_magnitude_breaks_ties_within_equal_distance(self) -> None:
        target = (1000).to_bytes(2, "big")
        closer = score(Recipe(Const(1001), 2), target, 2)
        further = score(Recipe(Const(1002), 2), target, 2)
        if closer.distance == further.distance:
            self.assertLess(closer.magnitude, further.magnitude)
            self.assertLess(closer.key, further.key)

    def test_distance_is_zero_only_when_exact(self) -> None:
        self.assertEqual(s(Literal(TARGET)).distance, 0)
        for wrong in (Const(0), Const(1), Const(1 << 31 | 1)):
            self.assertGreater(s(wrong).distance, 0)


class ValidityTest(unittest.TestCase):
    def test_invalid_candidates_are_scored_not_raised(self) -> None:
        result = s(BinOp(SUB, Const(0), Const(1)))
        self.assertFalse(result.valid)
        self.assertFalse(result.exact)
        self.assertEqual(result.total_bytes, INVALID_SIZE)

    def test_invalid_ranks_below_every_valid_candidate(self) -> None:
        invalid = s(BinOp(POW, Const(2), Const(10**6)))
        self.assertFalse(invalid.valid)
        for expr in (Const(0), Const(1 << 31), BinOp(ADD, Const(1), Const(2))):
            with self.subTest(expr=expr):
                self.assertLess(s(expr).key, invalid.key)

    def test_limit_breach_is_invalid_not_exact(self) -> None:
        strict = Limits(max_bits=16)
        result = s(BinOp(MUL, Const(1 << 20), Const(1 << 20)), limits=strict)
        self.assertFalse(result.valid)


class BaselineReportingTest(unittest.TestCase):
    def test_beats_baseline_requires_exactness(self) -> None:
        wrong_and_tiny = s(Const(0), baseline=100)
        self.assertLess(wrong_and_tiny.total_bytes, 100)
        self.assertFalse(wrong_and_tiny.beats_baseline)

    def test_beats_baseline_is_strict(self) -> None:
        recipe = BinOp(SHL, Const(1), Const(31))
        exactly_equal = s(recipe, baseline=s(recipe).total_bytes)
        self.assertFalse(exactly_equal.beats_baseline)
        self.assertTrue(s(recipe, baseline=exactly_equal.total_bytes + 1).beats_baseline)

    def test_score_is_serializable(self) -> None:
        import json

        json.dumps(s(BinOp(SHL, Const(1), Const(31))).as_dict())


class DeterminismTest(unittest.TestCase):
    def test_repeated_scoring_is_identical(self) -> None:
        expr = BinOp(ADD, BinOp(MUL, Const(3), Const(5)), Const(7))
        self.assertEqual({s(expr).key for _ in range(5)}, {s(expr).key})
