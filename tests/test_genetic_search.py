"""The genetic search must be reproducible, honest, and never worse than fallback."""

from __future__ import annotations

import unittest

from genetic_compression.bytes_model import int_to_bytes
from genetic_compression.codec import encoded_size
from genetic_compression.grammar import BINARY_OPS, FIRST_SLICE_OPS, Limits
from genetic_compression.recipe import BinOp, Const, decode, depth
from genetic_compression.search import SearchStatus
from genetic_compression.search.exhaustive import fallback_recipe
from genetic_compression.search.genetic import (
    GeneticConfig,
    _crossover,
    _mutate,
    _paths,
    _random_expr,
    _replace,
    search,
)

FAST = GeneticConfig(population_size=60, max_generations=12, seed=2024)


class TreeOperatorTest(unittest.TestCase):
    def setUp(self) -> None:
        import random

        self.rng = random.Random(1)
        self.config = GeneticConfig(max_tree_depth=5)

    def test_random_expressions_respect_the_depth_bound(self) -> None:
        for _ in range(200):
            expr = _random_expr(self.rng, self.config, 4)
            self.assertLessEqual(depth(expr), 4)

    def test_paths_address_every_node(self) -> None:
        expr = BinOp(BINARY_OPS[0], BinOp(BINARY_OPS[1], Const(1), Const(2)), Const(3))
        self.assertEqual(len(_paths(expr)), 5)

    def test_replace_at_root_and_leaves(self) -> None:
        expr = BinOp(BINARY_OPS[0], Const(1), Const(2))
        self.assertEqual(_replace(expr, (), Const(9)), Const(9))
        self.assertEqual(
            _replace(expr, ("R",), Const(9)), BinOp(BINARY_OPS[0], Const(1), Const(9))
        )

    def test_mutation_keeps_trees_valid_and_bounded(self) -> None:
        expr = _random_expr(self.rng, self.config, 4)
        for _ in range(500):
            expr = _mutate(expr, self.rng, self.config)
            self.assertLessEqual(depth(expr), self.config.max_tree_depth)

    def test_crossover_keeps_trees_bounded(self) -> None:
        for _ in range(200):
            left = _random_expr(self.rng, self.config, 4)
            right = _random_expr(self.rng, self.config, 4)
            child = _crossover(left, right, self.rng, self.config)
            self.assertLessEqual(depth(child), self.config.max_tree_depth)

    def test_constant_mutation_never_goes_negative(self) -> None:
        """Const(-1) raises at construction, so a bad nudge would crash the run."""
        from genetic_compression.recipe import iter_nodes

        expr = Const(0)
        for _ in range(500):
            expr = _mutate(expr, self.rng, self.config)
            for node in iter_nodes(expr):
                if isinstance(node, Const):
                    self.assertGreaterEqual(node.value, 0)


class DeterminismTest(unittest.TestCase):
    def test_same_seed_reproduces_the_run(self) -> None:
        segment = int_to_bytes(1 << 31, 4)
        first = search(segment, FAST)
        second = search(segment, FAST)
        self.assertEqual(first.recipe, second.recipe)
        self.assertEqual(first.status, second.status)
        self.assertEqual(first.work["generations_run"], second.work["generations_run"])
        self.assertEqual(first.work["evaluations"], second.work["evaluations"])
        self.assertEqual(first.work["fitness_curve"], second.work["fitness_curve"])

    def test_different_seeds_explore_differently(self) -> None:
        segment = int_to_bytes(1 << 31, 4)
        curves = {
            str(
                search(
                    segment, GeneticConfig(population_size=60, max_generations=12, seed=seed)
                ).work["fitness_curve"]
            )
            for seed in (1, 2, 3)
        }
        self.assertGreater(len(curves), 1)


class ResultIntegrityTest(unittest.TestCase):
    SEGMENTS = [
        b"\x00",
        b"\xff",
        int_to_bytes(1 << 31, 4),
        int_to_bytes(10**9, 4),
        b"\xde\xad\xbe\xef",
        b"\x00" * 16,
        bytes(range(8)),
    ]

    def test_every_result_decodes_exactly(self) -> None:
        for segment in self.SEGMENTS:
            with self.subTest(segment=segment.hex()):
                result = search(segment, FAST)
                self.assertTrue(result.exact)
                self.assertEqual(decode(result.recipe), segment)

    def test_result_is_never_worse_than_the_fallback(self) -> None:
        for segment in self.SEGMENTS:
            with self.subTest(segment=segment.hex()):
                result = search(segment, FAST)
                self.assertLessEqual(result.total_bytes, encoded_size(fallback_recipe(segment)))

    def test_status_is_never_exhausted(self) -> None:
        """A stochastic search proves nothing about what does not exist."""
        for segment in self.SEGMENTS:
            with self.subTest(segment=segment.hex()):
                self.assertIsNot(search(segment, FAST).status, SearchStatus.EXHAUSTED)

    def test_a_winnable_segment_is_won(self) -> None:
        """2**63 has a five-byte recipe and a twelve-byte fallback."""
        segment = int_to_bytes(1 << 63, 8)
        result = search(segment, GeneticConfig(population_size=300, max_generations=120, seed=7))
        self.assertIs(result.status, SearchStatus.FOUND)
        self.assertFalse(result.used_fallback)
        self.assertEqual(decode(result.recipe), segment)
        self.assertLess(result.total_bytes, encoded_size(fallback_recipe(segment)))

    def test_zero_segment_stops_early_once_it_beats_the_baseline(self) -> None:
        result = search(b"\x00" * 32, FAST)
        self.assertEqual(result.work["generations_run"], 1)
        self.assertLess(result.total_bytes, 32)

    def test_fitness_curve_is_recorded(self) -> None:
        result = search(b"\xde\xad\xbe\xef", FAST)
        curve = result.work["fitness_curve"]
        self.assertEqual(len(curve), result.work["generations_run"])
        for row in curve:
            self.assertIn("best_total_bytes", row)
            self.assertIn("distinct_count", row)

    def test_result_is_serializable(self) -> None:
        import json

        json.dumps(search(b"\xde\xad\xbe\xef", FAST).as_dict())


class ConfigValidationTest(unittest.TestCase):
    def test_rejects_nonsense_parameters(self) -> None:
        for kwargs in (
            {"population_size": 1},
            {"max_generations": 0},
            {"mutation_rate": 1.5},
            {"crossover_rate": -0.1},
            {"tournament_size": 0},
            {"elitism": 999},
            {"max_tree_depth": 0},
            {"const_bits": 0},
            {"ops": ()},
        ):
            with self.subTest(**kwargs):
                with self.assertRaises(ValueError):
                    GeneticConfig(**kwargs)

    def test_restricted_operation_set_is_honored(self) -> None:
        config = GeneticConfig(
            population_size=40, max_generations=5, seed=3, ops=FIRST_SLICE_OPS
        )
        result = search(b"\x01\x00", config)
        self.assertTrue(result.exact)
        self.assertEqual(result.work["seed"], 3)

    def test_strict_limits_do_not_break_the_run(self) -> None:
        config = GeneticConfig(
            population_size=40,
            max_generations=5,
            seed=3,
            limits=Limits(max_bits=32, max_exponent=8, max_depth=4),
            max_tree_depth=4,
        )
        result = search(b"\x01\x00", config)
        self.assertTrue(result.exact)

    def test_config_is_serializable(self) -> None:
        import json

        json.dumps(FAST.as_dict())
