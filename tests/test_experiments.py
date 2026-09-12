"""Trials must be reproducible from their own records, and report failures too."""

from __future__ import annotations

import io
import json
import unittest
from dataclasses import replace

from genetic_compression.bytes_model import split_segments
from genetic_compression.experiments import (
    ALGORITHMS,
    DATASETS,
    TrialSpec,
    main,
    make_dataset,
    run_trial,
    summarize,
)
from genetic_compression.grammar import GRAMMAR_VERSION

FAST = TrialSpec(
    input_class="shift",
    input_size=16,
    segment_size=8,
    seed=4,
    algorithm="exhaustive",
    max_expression_bytes=5,
    max_const_bytes=1,
    max_nodes=50_000,
)


class DatasetTest(unittest.TestCase):
    def test_every_dataset_is_deterministic(self) -> None:
        for name in DATASETS:
            with self.subTest(dataset=name):
                first = make_dataset(name, 48, 7, 8)
                second = make_dataset(name, 48, 7, 8)
                self.assertEqual(first, second)

    def test_every_dataset_has_the_requested_size(self) -> None:
        for name in DATASETS:
            for size in (0, 1, 7, 32):
                with self.subTest(dataset=name, size=size):
                    self.assertEqual(len(make_dataset(name, size, 3, 8)), size)

    def test_seed_changes_the_stochastic_classes(self) -> None:
        self.assertNotEqual(make_dataset("random", 32, 1, 8), make_dataset("random", 32, 2, 8))

    def test_algebraic_classes_are_segment_aligned(self) -> None:
        """A power spanning segments would leave each segment looking like noise."""
        data = make_dataset("power", 32, 5, 16)
        for segment in split_segments(data, 16):
            value = int.from_bytes(segment, "big")
            self.assertGreater(value.bit_length(), 100)

    def test_unknown_dataset_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            make_dataset("mnist", 16, 1, 8)

    def test_negative_size_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            make_dataset("zeros", -1, 1, 8)


class TrialSpecTest(unittest.TestCase):
    def test_rejects_unknown_parameters(self) -> None:
        with self.assertRaises(ValueError):
            TrialSpec(input_class="mnist")
        with self.assertRaises(ValueError):
            TrialSpec(input_class="zeros", algorithm="annealing")
        with self.assertRaises(ValueError):
            TrialSpec(input_class="zeros", baseline="brotli")
        with self.assertRaises(ValueError):
            TrialSpec(input_class="zeros", segment_size=0)

    def test_spec_is_serializable_and_carries_the_grammar_version(self) -> None:
        record = FAST.as_dict()
        json.dumps(record)
        self.assertEqual(record["grammar_version"], GRAMMAR_VERSION)


class RecordTest(unittest.TestCase):
    def test_one_record_per_segment(self) -> None:
        records = run_trial(FAST)
        self.assertEqual(len(records), 2)
        self.assertEqual([r["segment_index"] for r in records], [0, 1])

    def test_records_are_self_contained_and_serializable(self) -> None:
        required = {
            "input_class",
            "segment_size",
            "seed",
            "grammar_version",
            "algorithm",
            "recipe_bytes",
            "metadata_bytes",
            "residual_bytes",
            "total_bytes",
            "baseline_bytes",
            "baselines",
            "decode_exact",
            "decode_seconds",
            "search_seconds",
            "segment_hex",
        }
        for record in run_trial(FAST):
            json.dumps(record)
            self.assertTrue(required.issubset(record), required - set(record))

    def test_every_record_decodes_exactly(self) -> None:
        for record in run_trial(FAST):
            self.assertTrue(record["decode_exact"])

    def test_sizes_add_up(self) -> None:
        for record in run_trial(FAST):
            self.assertEqual(
                record["total_bytes"],
                record["recipe_bytes"] + record["metadata_bytes"] + record["residual_bytes"],
            )

    def test_a_trial_is_reproducible_from_its_parameters(self) -> None:
        first = run_trial(FAST)
        second = run_trial(FAST)
        volatile = {"search_seconds", "decode_seconds", "work"}
        for a, b in zip(first, second):
            self.assertEqual(
                {k: v for k, v in a.items() if k not in volatile},
                {k: v for k, v in b.items() if k not in volatile},
            )

    def test_structured_input_can_beat_every_baseline(self) -> None:
        records = run_trial(FAST)
        self.assertTrue(any(r["beats_all_baselines"] for r in records))

    def test_random_input_is_reported_as_a_failure_not_hidden(self) -> None:
        spec = replace(FAST, input_class="random")
        records = run_trial(spec)
        self.assertTrue(records)
        for record in records:
            self.assertTrue(record["decode_exact"])
            self.assertFalse(record["beats_baseline"])
            self.assertTrue(record["used_fallback"])

    def test_empty_input_produces_no_records(self) -> None:
        self.assertEqual(run_trial(replace(FAST, input_size=0)), [])


class AlgorithmCoverageTest(unittest.TestCase):
    def test_every_algorithm_runs_and_decodes_exactly(self) -> None:
        for algorithm in ALGORITHMS:
            with self.subTest(algorithm=algorithm):
                spec = replace(
                    FAST,
                    algorithm=algorithm,
                    input_size=8,
                    segment_size=8,
                    population_size=30,
                    max_generations=4,
                )
                records = run_trial(spec)
                self.assertEqual(len(records), 1)
                self.assertTrue(records[0]["decode_exact"])
                self.assertEqual(records[0]["algorithm"], algorithm)


class SummaryTest(unittest.TestCase):
    def test_summary_counts_match_the_records(self) -> None:
        records = run_trial(FAST)
        summary = summarize(records)
        self.assertEqual(summary["segments"], len(records))
        self.assertEqual(summary["exact_segments"], sum(1 for r in records if r["decode_exact"]))
        self.assertEqual(summary["artifact_bytes"], sum(r["total_bytes"] for r in records))
        self.assertEqual(summary["original_bytes"], sum(r["segment_bytes"] for r in records))

    def test_empty_summary(self) -> None:
        self.assertEqual(summarize([])["segments"], 0)


class CommandLineTest(unittest.TestCase):
    def _run(self, argv: list[str]) -> list[dict]:
        out = io.StringIO()
        code = main(argv + ["--quiet"], stdout=out)
        self.assertEqual(code, 0)
        return [json.loads(line) for line in out.getvalue().splitlines()]

    def test_list_datasets(self) -> None:
        out = io.StringIO()
        self.assertEqual(main(["--list-datasets"], stdout=out), 0)
        self.assertEqual(out.getvalue().split(), list(DATASETS))

    def test_jsonl_output_ends_with_a_summary(self) -> None:
        rows = self._run(
            [
                "--input-class", "shift",
                "--input-size", "16",
                "--segment-size", "8",
                "--max-expression-bytes", "5",
                "--max-const-bytes", "1",
                "--max-nodes", "50000",
            ]
        )
        self.assertEqual(rows[-1]["record_type"], "summary")
        self.assertEqual(len([r for r in rows if "segment_index" in r]), 2)

    def test_output_file(self) -> None:
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "results.jsonl")
            code = main(
                [
                    "--input-class", "zeros",
                    "--input-size", "8",
                    "--segment-size", "8",
                    "--output", path,
                    "--quiet",
                ],
                stdout=io.StringIO(),
            )
            self.assertEqual(code, 0)
            with open(path, encoding="utf-8") as handle:
                rows = [json.loads(line) for line in handle]
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[-1]["record_type"], "summary")

    def test_unknown_input_class_exits_with_an_error(self) -> None:
        with self.assertRaises(ValueError):
            main(["--input-class", "mnist", "--quiet"], stdout=io.StringIO())
