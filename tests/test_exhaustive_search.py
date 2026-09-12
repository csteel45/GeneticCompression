"""Exhaustive search must be minimal-first, exact, and honest about its bound."""

from __future__ import annotations

import unittest

from genetic_compression.bytes_model import bytes_to_int
from genetic_compression.codec import encoded_size, expression_size
from genetic_compression.grammar import BINARY_OPS, FIRST_SLICE_OPS, Limits
from genetic_compression.recipe import BinOp, Const, Literal, decode, verify
from genetic_compression.search import SearchStatus
from genetic_compression.search.exhaustive import (
    EnumerationConfig,
    enumerate_expressions,
    fallback_recipe,
    search,
)

SMALL = EnumerationConfig(max_expression_bytes=5, max_const_bytes=2, max_nodes=400_000)


class FallbackTest(unittest.TestCase):
    def test_fallback_always_decodes_exactly(self) -> None:
        for data in (b"", b"\x00", b"\xff", b"\x00\x00\x05", bytes(range(8))):
            with self.subTest(data=data):
                self.assertTrue(verify(fallback_recipe(data), data))

    def test_constant_wins_when_the_segment_has_leading_zeros(self) -> None:
        recipe = fallback_recipe(b"\x00\x00\x00\x05")
        self.assertIsInstance(recipe.expr, Const)
        self.assertEqual(decode(recipe), b"\x00\x00\x00\x05")

    def test_literal_wins_on_wide_high_entropy_segments(self) -> None:
        data = bytes(range(200, 216))
        recipe = fallback_recipe(data)
        self.assertIsInstance(recipe.expr, Literal)
        self.assertEqual(decode(recipe), data)


class EnumerationTest(unittest.TestCase):
    def test_sizes_are_non_decreasing(self) -> None:
        sizes = [size for size, _, _ in enumerate_expressions(SMALL)]
        self.assertEqual(sizes, sorted(sizes))

    def test_one_byte_constants_come_first(self) -> None:
        first = list(enumerate_expressions(EnumerationConfig(max_expression_bytes=2)))
        self.assertEqual(len(first), 128)
        self.assertEqual([value for _, value, _ in first], list(range(128)))
        for size, value, expr in first:
            self.assertEqual(size, 2)
            self.assertEqual(expr, Const(value))

    def test_each_value_is_reported_once_at_its_smallest_size(self) -> None:
        seen: dict[int, int] = {}
        for size, value, _ in enumerate_expressions(SMALL):
            self.assertNotIn(value, seen, f"value {value} enumerated twice")
            seen[value] = size

    def test_enumerated_expressions_evaluate_to_their_reported_value(self) -> None:
        from genetic_compression.recipe import evaluate

        for count, (size, value, expr) in enumerate(enumerate_expressions(SMALL)):
            if count % 97:  # sample; evaluating every node is needlessly slow
                continue
            self.assertEqual(evaluate(expr), value)
            self.assertEqual(expression_size(expr), size)

    def test_target_stops_the_enumeration(self) -> None:
        items = list(enumerate_expressions(SMALL, target=300))
        self.assertEqual(items[-1][1], 300)
        self.assertNotIn(300, [value for _, value, _ in items[:-1]])


class SearchTest(unittest.TestCase):
    def test_finds_a_compact_recipe_for_a_structured_segment(self) -> None:
        result = search(b"\x80\x00\x00\x00", SMALL)
        self.assertIs(result.status, SearchStatus.FOUND)
        self.assertFalse(result.used_fallback)
        self.assertTrue(result.exact)
        self.assertEqual(decode(result.recipe), b"\x80\x00\x00\x00")
        self.assertEqual(result.breakdown.recipe_bytes, 5)

    def test_result_is_the_smallest_expression(self) -> None:
        """1024 is reachable as SHL(1, 10) at 5 bytes and as a constant at 3."""
        result = search(b"\x04\x00", SMALL)
        self.assertIs(result.status, SearchStatus.FOUND)
        self.assertEqual(result.breakdown.recipe_bytes, 3)
        self.assertEqual(decode(result.recipe), b"\x04\x00")

    def test_every_result_decodes_exactly(self) -> None:
        segments = [
            b"",
            b"\x00",
            b"\x7f",
            b"\xff",
            b"\x01\x00",
            b"\x03\xe8",
            b"\x80\x00\x00\x00",
            b"\xde\xad\xbe\xef",
            b"\x00\x00\x00\x00",
        ]
        for segment in segments:
            with self.subTest(segment=segment.hex()):
                result = search(segment, SMALL)
                self.assertTrue(result.exact)
                self.assertEqual(decode(result.recipe), segment)
                self.assertEqual(result.total_bytes, encoded_size(result.recipe))

    def test_random_segments_fall_back(self) -> None:
        """High-entropy bytes have no compact recipe; the report must say so."""
        result = search(b"\xde\xad\xbe\xef", SMALL)
        self.assertTrue(result.used_fallback)
        self.assertTrue(result.exact)
        self.assertEqual(decode(result.recipe), b"\xde\xad\xbe\xef")

    def test_exhausted_is_distinguished_from_budget_exhausted(self) -> None:
        segment = b"\xde\xad\xbe\xef"
        tiny_space = EnumerationConfig(
            max_expression_bytes=4, max_const_bytes=1, max_nodes=1_000_000
        )
        self.assertIs(search(segment, tiny_space).status, SearchStatus.EXHAUSTED)

        starved = EnumerationConfig(
            max_expression_bytes=7, max_const_bytes=2, max_nodes=500
        )
        self.assertIs(search(segment, starved).status, SearchStatus.BUDGET_EXHAUSTED)

    def test_search_is_deterministic(self) -> None:
        segment = b"\x03\xe8"
        first = search(segment, SMALL)
        second = search(segment, SMALL)
        self.assertEqual(first.recipe, second.recipe)
        self.assertEqual(first.status, second.status)
        self.assertEqual(first.work["nodes_examined"], second.work["nodes_examined"])

    def test_work_counters_are_recorded(self) -> None:
        result = search(b"\x03\xe8", SMALL)
        for key in ("nodes_examined", "values_reached", "ops", "fallback_bytes"):
            self.assertIn(key, result.work)
        self.assertEqual(result.work["ops"], ",".join(op.name for op in FIRST_SLICE_OPS))

    def test_full_operation_set_is_usable(self) -> None:
        config = EnumerationConfig(
            max_expression_bytes=5, max_const_bytes=1, ops=BINARY_OPS, max_nodes=400_000
        )
        result = search(b"\x10\x00", config)
        self.assertTrue(result.exact)
        self.assertEqual(decode(result.recipe), b"\x10\x00")

    def test_evaluation_limits_are_respected(self) -> None:
        """A grammar with POW must not be able to smuggle in a huge intermediate."""
        config = EnumerationConfig(
            max_expression_bytes=5,
            max_const_bytes=1,
            ops=BINARY_OPS,
            max_nodes=200_000,
            limits=Limits(max_bits=64, max_exponent=8),
        )
        result = search(b"\x00\x01", config)
        self.assertTrue(result.exact)

    def test_serializable_report(self) -> None:
        import json

        record = search(b"\x80\x00\x00\x00", SMALL).as_dict()
        json.dumps(record)
        self.assertTrue(record["decode_exact"])
        self.assertEqual(record["algorithm"], "exhaustive")


class ConfigValidationTest(unittest.TestCase):
    def test_rejects_nonsense_bounds(self) -> None:
        with self.assertRaises(ValueError):
            EnumerationConfig(max_expression_bytes=1)
        with self.assertRaises(ValueError):
            EnumerationConfig(max_const_bytes=0)
        with self.assertRaises(ValueError):
            EnumerationConfig(ops=())
        with self.assertRaises(ValueError):
            EnumerationConfig(max_nodes=-1)

    def test_config_is_serializable(self) -> None:
        import json

        json.dumps(SMALL.as_dict())
