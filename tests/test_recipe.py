"""Recipe evaluation must be deterministic, bounded, and exact or failing."""

from __future__ import annotations

import unittest

from genetic_compression.grammar import (
    ADD,
    AND,
    MUL,
    OR,
    POW,
    SHL,
    SUB,
    XOR,
    GRAMMAR_VERSION,
    Limits,
)
from genetic_compression.recipe import (
    BinOp,
    Const,
    DecodeError,
    EvaluationError,
    GrammarError,
    Literal,
    Recipe,
    const_recipe,
    decode,
    depth,
    evaluate,
    evaluate_with_stats,
    literal_recipe,
    node_count,
    op_count,
    to_text,
    validate,
    verify,
)


class NodeConstructionTest(unittest.TestCase):
    def test_const_rejects_negative(self) -> None:
        with self.assertRaises(GrammarError):
            Const(-1)

    def test_const_rejects_non_int(self) -> None:
        with self.assertRaises(GrammarError):
            Const("7")  # type: ignore[arg-type]
        with self.assertRaises(GrammarError):
            Const(True)  # type: ignore[arg-type]

    def test_literal_requires_bytes(self) -> None:
        with self.assertRaises(GrammarError):
            Literal("abc")  # type: ignore[arg-type]

    def test_binop_requires_expressions(self) -> None:
        with self.assertRaises(GrammarError):
            BinOp(ADD, Const(1), 2)  # type: ignore[arg-type]

    def test_nodes_are_immutable_and_comparable(self) -> None:
        a = BinOp(ADD, Const(1), Const(2))
        b = BinOp(ADD, Const(1), Const(2))
        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))
        with self.assertRaises(Exception):
            a.op = MUL  # type: ignore[misc]

    def test_recipe_rejects_bad_metadata(self) -> None:
        with self.assertRaises(GrammarError):
            Recipe(Const(1), -1)
        with self.assertRaises(GrammarError):
            Recipe(Const(1), 1, grammar_version=GRAMMAR_VERSION + 1)


class StructureTest(unittest.TestCase):
    def setUp(self) -> None:
        self.expr = BinOp(ADD, BinOp(MUL, Const(3), Const(4)), Const(5))

    def test_depth(self) -> None:
        self.assertEqual(depth(Const(1)), 1)
        self.assertEqual(depth(self.expr), 3)

    def test_counts(self) -> None:
        self.assertEqual(op_count(self.expr), 2)
        self.assertEqual(node_count(self.expr), 5)

    def test_validate_rejects_deep_trees(self) -> None:
        with self.assertRaises(GrammarError):
            validate(self.expr, Limits(max_depth=2))

    def test_validate_rejects_too_many_ops(self) -> None:
        with self.assertRaises(GrammarError):
            validate(self.expr, Limits(max_ops=1))

    def test_validate_rejects_oversized_literal(self) -> None:
        with self.assertRaises(GrammarError):
            validate(Literal(b"abcdef"), Limits(max_literal_bytes=4))


class EvaluationTest(unittest.TestCase):
    def test_leaves(self) -> None:
        self.assertEqual(evaluate(Const(0)), 0)
        self.assertEqual(evaluate(Const(1234)), 1234)
        self.assertEqual(evaluate(Literal(b"\x01\x00")), 256)
        self.assertEqual(evaluate(Literal(b"")), 0)

    def test_each_binary_operation(self) -> None:
        cases = [
            (ADD, 7, 5, 12),
            (SUB, 7, 5, 2),
            (MUL, 7, 5, 35),
            (SHL, 7, 5, 224),
            (XOR, 0b1100, 0b1010, 0b0110),
            (AND, 0b1100, 0b1010, 0b1000),
            (OR, 0b1100, 0b1010, 0b1110),
            (POW, 7, 5, 16807),
        ]
        for op, left, right, expected in cases:
            with self.subTest(op=op.name):
                self.assertEqual(evaluate(BinOp(op, Const(left), Const(right))), expected)

    def test_evaluation_is_deterministic(self) -> None:
        expr = BinOp(POW, BinOp(ADD, Const(2), Const(3)), Const(7))
        results = {evaluate(expr) for _ in range(10)}
        self.assertEqual(results, {5**7})

    def test_stats_are_reported(self) -> None:
        expr = BinOp(ADD, BinOp(MUL, Const(256), Const(256)), Const(1))
        value, stats = evaluate_with_stats(expr)
        self.assertEqual(value, 65537)
        self.assertEqual(stats.ops, 2)
        self.assertEqual(stats.max_bits, 17)
        self.assertEqual(stats.depth, 3)


class LimitTest(unittest.TestCase):
    def test_negative_subtraction_is_invalid(self) -> None:
        with self.assertRaises(EvaluationError):
            evaluate(BinOp(SUB, Const(3), Const(4)))

    def test_pow_exponent_bound(self) -> None:
        with self.assertRaises(EvaluationError):
            evaluate(BinOp(POW, Const(2), Const(10**6)))

    def test_pow_bit_bound_is_checked_before_computing(self) -> None:
        limits = Limits(max_bits=64, max_exponent=1000)
        with self.assertRaises(EvaluationError):
            evaluate(BinOp(POW, Const(2**32), Const(1000)), limits)

    def test_shift_bounds(self) -> None:
        limits = Limits(max_bits=64, max_shift=32)
        with self.assertRaises(EvaluationError):
            evaluate(BinOp(SHL, Const(1), Const(33)), limits)
        with self.assertRaises(EvaluationError):
            evaluate(BinOp(SHL, Const(2**40), Const(30)), limits)

    def test_mul_bit_bound(self) -> None:
        limits = Limits(max_bits=32)
        with self.assertRaises(EvaluationError):
            evaluate(BinOp(MUL, Const(2**20), Const(2**20)), limits)

    def test_add_bit_bound(self) -> None:
        limits = Limits(max_bits=8)
        with self.assertRaises(EvaluationError):
            evaluate(BinOp(ADD, Const(255), Const(1)), limits)

    def test_limits_reject_invalid_values(self) -> None:
        with self.assertRaises(ValueError):
            Limits(max_depth=0)
        with self.assertRaises(ValueError):
            Limits(max_bits=-1)


class DecodeTest(unittest.TestCase):
    def test_decode_pads_to_segment_length(self) -> None:
        self.assertEqual(decode(Recipe(Const(5), 3)), b"\x00\x00\x05")

    def test_decode_rejects_oversized_value(self) -> None:
        with self.assertRaises(DecodeError):
            decode(Recipe(Const(256), 1))

    def test_decode_empty_segment(self) -> None:
        self.assertEqual(decode(Recipe(Const(0), 0)), b"")

    def test_verify_is_exact(self) -> None:
        recipe = Recipe(BinOp(MUL, Const(16), Const(16)), 2)
        self.assertTrue(verify(recipe, b"\x01\x00"))
        self.assertFalse(verify(recipe, b"\x01\x01"))

    def test_verify_reports_false_for_invalid_recipes(self) -> None:
        self.assertFalse(verify(Recipe(BinOp(SUB, Const(0), Const(1)), 1), b"\x00"))
        self.assertFalse(verify(Recipe(Const(999), 1), b"\x00"))

    def test_fallback_constructors_round_trip(self) -> None:
        for data in (b"", b"\x00", b"\xff\x00\x01", bytes(range(8))):
            with self.subTest(data=data):
                self.assertTrue(verify(literal_recipe(data), data))
                self.assertTrue(verify(const_recipe(data), data))


class TextRenderingTest(unittest.TestCase):
    def test_rendering_is_readable(self) -> None:
        expr = BinOp(ADD, BinOp(MUL, Const(3), Const(4)), Literal(b"\xff"))
        self.assertEqual(to_text(expr), "ADD(MUL(3, 4), LITERAL[1]:ff)")
