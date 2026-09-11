"""Byte/integer semantics must round-trip exactly, including the awkward cases."""

from __future__ import annotations

import random
import unittest

from genetic_compression.bytes_model import (
    bytes_to_int,
    int_to_bytes,
    join_segments,
    legacy_java_biginteger_value,
    min_byte_length,
    split_segments,
)


class BytesToIntTest(unittest.TestCase):
    def test_empty_segment_is_zero(self) -> None:
        self.assertEqual(bytes_to_int(b""), 0)

    def test_single_bytes(self) -> None:
        for value in range(256):
            self.assertEqual(bytes_to_int(bytes([value])), value)

    def test_big_endian_order(self) -> None:
        self.assertEqual(bytes_to_int(b"\x01\x00"), 256)
        self.assertEqual(bytes_to_int(b"\x00\x01"), 1)

    def test_high_bit_is_unsigned(self) -> None:
        self.assertEqual(bytes_to_int(b"\xff"), 255)
        self.assertEqual(bytes_to_int(b"\x80\x00"), 32768)

    def test_leading_zeros_do_not_change_value(self) -> None:
        self.assertEqual(bytes_to_int(b"\x00\x00\x05"), bytes_to_int(b"\x05"))


class IntToBytesTest(unittest.TestCase):
    def test_pads_to_requested_length(self) -> None:
        self.assertEqual(int_to_bytes(5, 3), b"\x00\x00\x05")

    def test_zero_length_only_holds_zero(self) -> None:
        self.assertEqual(int_to_bytes(0, 0), b"")
        with self.assertRaises(ValueError):
            int_to_bytes(1, 0)

    def test_rejects_negative_values(self) -> None:
        with self.assertRaises(ValueError):
            int_to_bytes(-1, 4)

    def test_rejects_negative_length(self) -> None:
        with self.assertRaises(ValueError):
            int_to_bytes(1, -1)

    def test_rejects_overflow(self) -> None:
        with self.assertRaises(ValueError):
            int_to_bytes(256, 1)


class MinByteLengthTest(unittest.TestCase):
    def test_known_lengths(self) -> None:
        self.assertEqual(min_byte_length(0), 0)
        self.assertEqual(min_byte_length(1), 1)
        self.assertEqual(min_byte_length(255), 1)
        self.assertEqual(min_byte_length(256), 2)
        self.assertEqual(min_byte_length(2**32 - 1), 4)

    def test_rejects_negative(self) -> None:
        with self.assertRaises(ValueError):
            min_byte_length(-1)


class RoundTripTest(unittest.TestCase):
    FIXTURES = [
        b"",
        b"\x00",
        b"\x01",
        b"\xff",
        b"\x00\x00",
        b"\x00\x00\x05",
        b"\x80\x00\x00\x00",
        b"\xff\xff\xff\xff",
        b"\x00\xff\x00\xff\x00",
        bytes(range(16)),
    ]

    def test_fixtures_round_trip(self) -> None:
        for data in self.FIXTURES:
            with self.subTest(data=data):
                value = bytes_to_int(data)
                self.assertEqual(int_to_bytes(value, len(data)), data)

    def test_random_round_trips_with_fixed_seed(self) -> None:
        rng = random.Random(12345)
        for _ in range(200):
            length = rng.randrange(0, 17)
            data = bytes(rng.randrange(256) for _ in range(length))
            self.assertEqual(int_to_bytes(bytes_to_int(data), len(data)), data)


class SplitSegmentsTest(unittest.TestCase):
    def test_even_split(self) -> None:
        self.assertEqual(split_segments(b"abcd", 2), [b"ab", b"cd"])

    def test_final_short_segment_is_not_padded(self) -> None:
        self.assertEqual(split_segments(b"abcde", 2), [b"ab", b"cd", b"e"])

    def test_odd_segment_size(self) -> None:
        self.assertEqual(split_segments(b"abcdefg", 3), [b"abc", b"def", b"g"])

    def test_segment_larger_than_input(self) -> None:
        self.assertEqual(split_segments(b"ab", 16), [b"ab"])

    def test_empty_input(self) -> None:
        self.assertEqual(split_segments(b"", 4), [])

    def test_rejects_non_positive_segment_size(self) -> None:
        with self.assertRaises(ValueError):
            split_segments(b"abc", 0)

    def test_split_join_round_trip(self) -> None:
        rng = random.Random(999)
        for _ in range(50):
            data = bytes(rng.randrange(256) for _ in range(rng.randrange(0, 40)))
            size = rng.randrange(1, 9)
            self.assertEqual(join_segments(split_segments(data, size)), data)


class LegacyJavaSemanticsTest(unittest.TestCase):
    """Pin the Java behavior we are deliberately *not* using."""

    def test_high_bit_is_negative_in_java(self) -> None:
        self.assertEqual(legacy_java_biginteger_value(b"\xff"), -1)
        self.assertEqual(bytes_to_int(b"\xff"), 255)

    def test_agrees_with_python_when_high_bit_is_clear(self) -> None:
        for data in (b"\x00", b"\x7f", b"\x01\x02\x03"):
            self.assertEqual(legacy_java_biginteger_value(data), bytes_to_int(data))

    def test_java_rejects_empty_array(self) -> None:
        with self.assertRaises(ValueError):
            legacy_java_biginteger_value(b"")
