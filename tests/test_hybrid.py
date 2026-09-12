"""Hybrid artifacts must reconstruct exactly and never lose to their own baseline."""

from __future__ import annotations

import unittest

from genetic_compression.baselines import baseline_sizes
from genetic_compression.bytes_model import int_to_bytes
from genetic_compression.codec import CodecError
from genetic_compression.grammar import GRAMMAR_VERSION, POW, SHL
from genetic_compression.hybrid import (
    RESIDUAL_CODECS,
    HybridArtifact,
    build,
    decode_hybrid,
    encode_hybrid,
    generator_pool,
    predict,
    residual_of,
    search,
    structured_probes,
)
from genetic_compression.recipe import BinOp, Const, evaluate, to_text
from genetic_compression.search.genetic import GeneticConfig
from genetic_compression.search.exhaustive import EnumerationConfig

POWER_SEGMENT = int_to_bytes(3**160, 32)
NOISY_POWER = int_to_bytes(3**160 ^ 0xDEADBEEF, 32)
RANDOM_SEGMENT = bytes.fromhex(
    "9f2c4e81b307a56de1f4c29b8a6035d7c4e19b2f7a08d365be94127c5a3fd806"
)
GOOD_GENERATOR = BinOp(POW, Const(3), Const(160))


class ResidualTest(unittest.TestCase):
    def test_xor_is_its_own_inverse(self) -> None:
        original = b"\x01\x02\x03\x04"
        predicted = b"\x01\x00\x03\x00"
        residual = residual_of(original, predicted)
        self.assertEqual(residual_of(residual, predicted), original)

    def test_length_mismatch_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            residual_of(b"\x01\x02", b"\x01")

    def test_a_good_prediction_leaves_a_sparse_residual(self) -> None:
        predicted = predict(GOOD_GENERATOR, 32)
        self.assertEqual(residual_of(POWER_SEGMENT, predicted), b"\x00" * 32)

    def test_prediction_must_fit_the_segment(self) -> None:
        with self.assertRaises(ValueError):
            predict(Const(256), 1)


class RoundTripTest(unittest.TestCase):
    def test_every_codec_round_trips(self) -> None:
        for codec in RESIDUAL_CODECS:
            with self.subTest(codec=codec):
                artifact = build(POWER_SEGMENT, GOOD_GENERATOR, codec)
                self.assertEqual(decode_hybrid(encode_hybrid(artifact)), POWER_SEGMENT)

    def test_zero_generator_degenerates_to_plain_compression(self) -> None:
        """CONST 0 predicts zeros, so the residual is the segment itself."""
        artifact = build(RANDOM_SEGMENT, Const(0), "store")
        self.assertEqual(artifact.residual_payload, RANDOM_SEGMENT)
        self.assertEqual(decode_hybrid(encode_hybrid(artifact)), RANDOM_SEGMENT)

    def test_size_accounting_matches_the_encoding(self) -> None:
        artifact = build(NOISY_POWER, GOOD_GENERATOR, "zlib")
        self.assertEqual(artifact.total_bytes, len(encode_hybrid(artifact)))
        self.assertEqual(
            artifact.total_bytes,
            artifact.recipe_bytes + artifact.metadata_bytes + artifact.residual_bytes,
        )

    def test_empty_segment(self) -> None:
        artifact = build(b"", Const(0), "store")
        self.assertEqual(decode_hybrid(encode_hybrid(artifact)), b"")


class MalformedArtifactTest(unittest.TestCase):
    def test_unknown_codec_name(self) -> None:
        with self.assertRaises(ValueError):
            HybridArtifact(Const(0), 4, "brotli", b"")

    def test_unknown_codec_id(self) -> None:
        blob = bytearray(encode_hybrid(build(RANDOM_SEGMENT, Const(0), "store")))
        blob[2] = 200
        with self.assertRaises(CodecError):
            decode_hybrid(bytes(blob))

    def test_wrong_grammar_version(self) -> None:
        blob = bytearray(encode_hybrid(build(RANDOM_SEGMENT, Const(0), "store")))
        blob[0] = GRAMMAR_VERSION + 1
        with self.assertRaises(CodecError):
            decode_hybrid(bytes(blob))

    def test_truncated_artifact(self) -> None:
        blob = encode_hybrid(build(RANDOM_SEGMENT, Const(0), "zlib"))
        with self.assertRaises(CodecError):
            decode_hybrid(blob[:-3])

    def test_trailing_bytes(self) -> None:
        blob = encode_hybrid(build(RANDOM_SEGMENT, Const(0), "store")) + b"\x00"
        with self.assertRaises(CodecError):
            decode_hybrid(blob)


class StructuredProbeTest(unittest.TestCase):
    def test_probes_land_on_the_target_width(self) -> None:
        probes = structured_probes(POWER_SEGMENT)
        target_bits = int.from_bytes(POWER_SEGMENT, "big").bit_length()
        for probe in probes:
            self.assertLessEqual(abs(evaluate(probe).bit_length() - target_bits), 1)

    def test_probes_find_an_exact_power(self) -> None:
        matches = [p for p in structured_probes(POWER_SEGMENT) if evaluate(p) == 3**160]
        self.assertTrue(matches, "no probe reproduced the power exactly")
        self.assertIn("POW", to_text(matches[0]))

    def test_probes_are_deduplicated(self) -> None:
        probes = structured_probes(POWER_SEGMENT)
        self.assertEqual(len(probes), len(set(probes)))

    def test_tiny_segments_produce_no_probes(self) -> None:
        self.assertEqual(structured_probes(b"\x00"), [])
        self.assertEqual(structured_probes(b"\x01"), [])


class SearchTest(unittest.TestCase):
    def test_result_always_decodes_exactly(self) -> None:
        for segment in (POWER_SEGMENT, NOISY_POWER, RANDOM_SEGMENT, b"\x00" * 16):
            with self.subTest(segment=segment[:4].hex()):
                result = search(segment, generators=[GOOD_GENERATOR])
                self.assertTrue(result.exact)
                self.assertEqual(
                    decode_hybrid(encode_hybrid(result.artifact)), segment
                )

    def test_never_worse_than_the_zero_generator(self) -> None:
        """CONST 0 with every codec is always in the search, so it is a ceiling."""
        for segment in (RANDOM_SEGMENT, bytes(range(32))):
            with self.subTest(segment=segment[:4].hex()):
                floor = min(
                    build(segment, Const(0), codec).total_bytes for codec in RESIDUAL_CODECS
                )
                self.assertLessEqual(search(segment, generators=[]).total_bytes, floor)

    def test_a_generated_segment_beats_every_baseline(self) -> None:
        result = search(POWER_SEGMENT, generators=[GOOD_GENERATOR])
        sizes = {name: b.size for name, b in baseline_sizes(POWER_SEGMENT).items()}
        self.assertTrue(result.exact)
        self.assertTrue(result.beats_baseline)
        self.assertLess(result.total_bytes, min(sizes.values()))

    def test_a_noisy_generated_segment_still_wins(self) -> None:
        """The point of the hybrid: the prediction need not be exact."""
        result = search(NOISY_POWER, generators=[GOOD_GENERATOR])
        self.assertTrue(result.exact)
        self.assertTrue(result.improved_residual)
        self.assertLess(result.total_bytes, baseline_sizes(NOISY_POWER)["raw"].size)

    def test_random_data_reports_no_improvement(self) -> None:
        result = search(RANDOM_SEGMENT, generators=[GOOD_GENERATOR])
        self.assertTrue(result.exact)
        self.assertFalse(result.improved_residual)
        self.assertFalse(result.beats_baseline)

    def test_result_is_serializable(self) -> None:
        import json

        json.dumps(search(NOISY_POWER, generators=[GOOD_GENERATOR]).as_dict())


class GeneratorPoolTest(unittest.TestCase):
    POOL_ENUMERATION = EnumerationConfig(
        max_expression_bytes=4, max_const_bytes=1, max_nodes=20_000
    )
    POOL_GENETIC = GeneticConfig(
        population_size=40, max_generations=6, seed=11, stop_when_beats_baseline=False
    )

    def test_pool_predictions_fit_the_segment(self) -> None:
        pool = generator_pool(
            POWER_SEGMENT,
            max_candidates=8,
            enumeration=self.POOL_ENUMERATION,
            genetic_config=self.POOL_GENETIC,
        )
        self.assertTrue(pool)
        for expr in pool:
            self.assertLessEqual(evaluate(expr).bit_length(), 8 * len(POWER_SEGMENT))

    def test_pool_contains_the_exact_power(self) -> None:
        pool = generator_pool(
            POWER_SEGMENT,
            max_candidates=8,
            enumeration=self.POOL_ENUMERATION,
            genetic_config=self.POOL_GENETIC,
        )
        self.assertIn(3**160, [evaluate(expr) for expr in pool])

    def test_pool_is_deduplicated(self) -> None:
        pool = generator_pool(
            NOISY_POWER,
            max_candidates=12,
            enumeration=self.POOL_ENUMERATION,
            genetic_config=self.POOL_GENETIC,
        )
        self.assertEqual(len(pool), len(set(pool)))

    def test_empty_segment_has_no_generators(self) -> None:
        self.assertEqual(generator_pool(b""), [])
