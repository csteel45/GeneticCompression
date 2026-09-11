"""Serialization must be canonical, bounded, and the only source of size claims."""

from __future__ import annotations

import random
import unittest

from genetic_compression.codec import (
    CodecError,
    decode_expression,
    decode_recipe,
    decode_varint,
    encode_expression,
    encode_recipe,
    encode_varint,
    encoded_size,
    expression_size,
    metadata_size,
    size_breakdown,
    varint_size,
)
from genetic_compression.grammar import (
    ADD,
    AND,
    GRAMMAR_VERSION,
    MUL,
    POW,
    SHL,
    SUB,
    XOR,
    Limits,
)
from genetic_compression.recipe import BinOp, Const, Literal, Recipe, decode, to_text


class VarintTest(unittest.TestCase):
    VALUES = [0, 1, 127, 128, 255, 300, 16383, 16384, 2**32, 2**128, 2**1000]

    def test_round_trip(self) -> None:
        for value in self.VALUES:
            with self.subTest(value=value):
                encoded = encode_varint(value)
                decoded, pos = decode_varint(encoded, 0)
                self.assertEqual(decoded, value)
                self.assertEqual(pos, len(encoded))

    def test_size_matches_encoding(self) -> None:
        for value in self.VALUES:
            with self.subTest(value=value):
                self.assertEqual(varint_size(value), len(encode_varint(value)))

    def test_known_boundaries(self) -> None:
        self.assertEqual(encode_varint(0), b"\x00")
        self.assertEqual(encode_varint(127), b"\x7f")
        self.assertEqual(encode_varint(128), b"\x80\x01")
        self.assertEqual(varint_size(127), 1)
        self.assertEqual(varint_size(128), 2)

    def test_rejects_negative(self) -> None:
        with self.assertRaises(CodecError):
            encode_varint(-1)
        with self.assertRaises(CodecError):
            varint_size(-1)

    def test_rejects_truncated(self) -> None:
        with self.assertRaises(CodecError):
            decode_varint(b"\x80", 0)

    def test_rejects_non_canonical(self) -> None:
        # 1 encoded with a redundant continuation group.
        with self.assertRaises(CodecError):
            decode_varint(b"\x81\x00", 0)


def _sample_recipes() -> list[Recipe]:
    return [
        Recipe(Const(0), 0),
        Recipe(Const(5), 1),
        Recipe(Literal(b""), 0),
        Recipe(Literal(b"\x00\x00\x05"), 3),
        Recipe(BinOp(ADD, Const(1), Const(2)), 1),
        Recipe(BinOp(MUL, Const(255), Const(256)), 2),
        Recipe(BinOp(SHL, Const(1), Const(31)), 4),
        Recipe(BinOp(POW, Const(2), Const(16)), 3),
        Recipe(BinOp(SUB, BinOp(POW, Const(3), Const(5)), Const(43)), 1),
        Recipe(BinOp(XOR, Literal(b"\xaa\x55"), Const(0xFFFF)), 2),
        Recipe(
            BinOp(AND, BinOp(ADD, Const(2**70), Const(1)), Const(2**64 - 1)),
            8,
        ),
    ]


class RoundTripTest(unittest.TestCase):
    def test_recipe_round_trip(self) -> None:
        for recipe in _sample_recipes():
            with self.subTest(recipe=to_text(recipe.expr)):
                self.assertEqual(decode_recipe(encode_recipe(recipe)), recipe)

    def test_expression_round_trip(self) -> None:
        for recipe in _sample_recipes():
            with self.subTest(recipe=to_text(recipe.expr)):
                self.assertEqual(decode_expression(encode_expression(recipe.expr)), recipe.expr)

    def test_encoding_is_canonical(self) -> None:
        """One recipe has exactly one encoding, so re-encoding is a fixed point."""
        for recipe in _sample_recipes():
            with self.subTest(recipe=to_text(recipe.expr)):
                blob = encode_recipe(recipe)
                self.assertEqual(encode_recipe(decode_recipe(blob)), blob)

    def test_random_trees_round_trip(self) -> None:
        rng = random.Random(4242)
        ops = [ADD, SUB, MUL, XOR, AND]

        def build(remaining_depth: int):
            if remaining_depth <= 1 or rng.random() < 0.3:
                if rng.random() < 0.5:
                    return Const(rng.randrange(0, 2**40))
                return Literal(bytes(rng.randrange(256) for _ in range(rng.randrange(0, 5))))
            return BinOp(rng.choice(ops), build(remaining_depth - 1), build(remaining_depth - 1))

        for _ in range(200):
            expr = build(5)
            recipe = Recipe(expr, rng.randrange(0, 33))
            self.assertEqual(decode_recipe(encode_recipe(recipe)), recipe)


class SizeAccountingTest(unittest.TestCase):
    def test_reported_size_equals_real_length(self) -> None:
        for recipe in _sample_recipes():
            with self.subTest(recipe=to_text(recipe.expr)):
                self.assertEqual(encoded_size(recipe), len(encode_recipe(recipe)))

    def test_breakdown_sums_to_total(self) -> None:
        for recipe in _sample_recipes():
            with self.subTest(recipe=to_text(recipe.expr)):
                parts = size_breakdown(recipe)
                self.assertEqual(parts.recipe_bytes, expression_size(recipe.expr))
                self.assertEqual(parts.metadata_bytes, metadata_size(recipe))
                self.assertEqual(parts.total_bytes, encoded_size(recipe))

    def test_literal_costs_more_than_its_payload(self) -> None:
        """The fallback is never free; the accounting must show its overhead."""
        data = bytes(range(16))
        recipe = Recipe(Literal(data), len(data))
        self.assertEqual(encoded_size(recipe), 1 + 1 + len(data) + metadata_size(recipe))
        self.assertGreater(encoded_size(recipe), len(data))

    def test_short_display_string_can_be_a_large_encoding(self) -> None:
        """A pretty-printed recipe says nothing about its encoded cost."""
        smuggler = Recipe(Const(int.from_bytes(bytes(range(32)), "big")), 32)
        self.assertLess(len(to_text(smuggler.expr)), 100)
        self.assertGreater(encoded_size(smuggler), 32)

    def test_tiny_recipe_can_beat_its_segment(self) -> None:
        """The premise under test: a 4-byte segment from a 5-byte expression."""
        recipe = Recipe(BinOp(SHL, Const(1), Const(31)), 4)
        self.assertEqual(decode(recipe), b"\x80\x00\x00\x00")
        self.assertEqual(expression_size(recipe.expr), 5)
        self.assertEqual(encoded_size(recipe), 7)


class MalformedInputTest(unittest.TestCase):
    def test_unknown_opcode(self) -> None:
        with self.assertRaises(CodecError):
            decode_recipe(bytes([GRAMMAR_VERSION, 1, 0x7E]))

    def test_wrong_grammar_version(self) -> None:
        blob = bytearray(encode_recipe(Recipe(Const(1), 1)))
        blob[0] = GRAMMAR_VERSION + 1
        with self.assertRaises(CodecError):
            decode_recipe(bytes(blob))

    def test_truncated_stream(self) -> None:
        blob = encode_recipe(Recipe(BinOp(ADD, Const(1), Const(2)), 1))
        for cut in range(1, len(blob)):
            with self.subTest(cut=cut):
                with self.assertRaises(CodecError):
                    decode_recipe(blob[:cut])

    def test_trailing_bytes(self) -> None:
        blob = encode_recipe(Recipe(Const(1), 1)) + b"\x00"
        with self.assertRaises(CodecError):
            decode_recipe(blob)

    def test_truncated_literal_payload(self) -> None:
        blob = encode_recipe(Recipe(Literal(b"abcd"), 4))
        with self.assertRaises(CodecError):
            decode_recipe(blob[:-2])

    def test_oversized_literal_is_refused_before_allocation(self) -> None:
        blob = bytes([GRAMMAR_VERSION, 4, 0x01]) + encode_varint(2**40)
        with self.assertRaises(CodecError):
            decode_recipe(blob)

    def test_deep_nesting_fails_cleanly(self) -> None:
        """A hostile stream must raise CodecError, not RecursionError."""
        blob = bytes([GRAMMAR_VERSION, 1]) + bytes([ADD.code]) * 100_000
        with self.assertRaises(CodecError):
            decode_recipe(blob, Limits(max_depth=12, max_ops=64))

    def test_limits_are_enforced_on_decode(self) -> None:
        recipe = Recipe(BinOp(ADD, BinOp(ADD, Const(1), Const(2)), Const(3)), 1)
        blob = encode_recipe(recipe)
        self.assertEqual(decode_recipe(blob), recipe)
        with self.assertRaises(CodecError):
            decode_recipe(blob, Limits(max_ops=1))
        with self.assertRaises(CodecError):
            decode_recipe(blob, Limits(max_depth=2))
