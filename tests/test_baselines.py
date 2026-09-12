"""Baselines must be reproducible, honest about metadata, and reversible."""

from __future__ import annotations

import random
import unittest

from genetic_compression.baselines import (
    BASELINE_NAMES,
    STREAM_CODECS,
    Baseline,
    baseline_sizes,
    best_baseline,
    compress_with,
    decompress_with,
    raw_size,
    unsigned_int_size,
)
from genetic_compression.bytes_model import bytes_to_int, int_to_bytes

FIXTURES = {
    "empty": b"",
    "one_byte": b"\x2a",
    "zeros": b"\x00" * 16,
    "counter": bytes(range(16)),
    "repeated": b"ABCD" * 16,
    "high_bit": b"\xff\x80\xff\x80",
    "random": bytes(random.Random(7).randrange(256) for _ in range(64)),
}


class StreamCodecTest(unittest.TestCase):
    def test_all_codecs_round_trip(self) -> None:
        for name in STREAM_CODECS:
            for label, data in FIXTURES.items():
                with self.subTest(codec=name, fixture=label):
                    self.assertEqual(decompress_with(name, compress_with(name, data)), data)

    def test_codecs_are_deterministic(self) -> None:
        """Identical input must give identical bytes, not just identical sizes."""
        data = FIXTURES["repeated"]
        for name in STREAM_CODECS:
            with self.subTest(codec=name):
                self.assertEqual(compress_with(name, data), compress_with(name, data))

    def test_unknown_codec_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            compress_with("brotli", b"abc")
        with self.assertRaises(ValueError):
            decompress_with("brotli", b"abc")


class BaselineSizeTest(unittest.TestCase):
    def test_every_baseline_is_measured(self) -> None:
        results = baseline_sizes(FIXTURES["counter"])
        self.assertEqual(set(results), set(BASELINE_NAMES))
        for name, baseline in results.items():
            with self.subTest(baseline=name):
                self.assertIsInstance(baseline, Baseline)
                self.assertGreaterEqual(baseline.size, 0)

    def test_raw_size_is_the_segment_length(self) -> None:
        for data in FIXTURES.values():
            self.assertEqual(raw_size(data), len(data))

    def test_stream_sizes_match_real_payloads(self) -> None:
        data = FIXTURES["repeated"]
        results = baseline_sizes(data)
        for name in ("zlib", "gzip", "bz2", "lzma"):
            with self.subTest(baseline=name):
                self.assertEqual(results[name].size, len(compress_with(name, data)))

    def test_unsigned_int_pays_for_its_length_metadata(self) -> None:
        """Leading zeros are free in the value and must be paid for in metadata."""
        self.assertEqual(unsigned_int_size(b"\x00" * 16), 1)
        self.assertEqual(unsigned_int_size(b"\x05"), 2)
        self.assertEqual(unsigned_int_size(b""), 1)

    def test_unsigned_int_is_decodable_with_its_stated_metadata(self) -> None:
        for data in FIXTURES.values():
            with self.subTest(data=data[:8]):
                self.assertEqual(int_to_bytes(bytes_to_int(data), len(data)), data)

    def test_stream_codecs_expand_tiny_inputs(self) -> None:
        """Small segments are where general codecs lose; the report must show it."""
        results = baseline_sizes(b"\x80\x00\x00\x00")
        self.assertEqual(results["raw"].size, 4)
        for name in ("zlib", "gzip", "bz2", "lzma"):
            self.assertGreater(results[name].size, results["raw"].size)

    def test_unknown_baseline_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            baseline_sizes(b"abc", ("raw", "brotli"))


class BestBaselineTest(unittest.TestCase):
    def test_picks_the_smallest(self) -> None:
        data = FIXTURES["repeated"]
        results = baseline_sizes(data)
        best = best_baseline(data)
        self.assertEqual(best.size, min(b.size for b in results.values()))

    def test_ties_resolve_deterministically_toward_raw(self) -> None:
        data = bytes(range(16))
        self.assertEqual(baseline_sizes(data)["unsigned_int"].size, 16)
        self.assertEqual(best_baseline(data).name, "raw")

    def test_zlib_wins_on_redundant_data(self) -> None:
        self.assertEqual(best_baseline(b"\x00" * 4096).name, "unsigned_int")
        self.assertEqual(best_baseline(b"ABCD" * 1024, ("raw", "zlib")).name, "zlib")
