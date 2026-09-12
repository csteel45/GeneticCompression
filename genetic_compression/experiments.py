"""Reproducible experiment runner.

A result from this project is only worth anything if someone else can re-run it.
Every record written here carries the full parameter set that produced it --
input class, size, segment size, seed, grammar version, algorithm, and every
search bound -- alongside the measured outcome. Re-running a trial from a
recorded line should reproduce that line, except for wall-clock timings.

Successes and failures are both written. A search that fell back to a literal on
random bytes is evidence about which data classes this method cannot help, and
suppressing it would turn the record into advertising.

Usage::

    python -m genetic_compression.experiments --help
    python -m genetic_compression.experiments --input-class quadratic \\
        --segment-size 16 --algorithm all
    python -m genetic_compression.experiments --input-class all \\
        --output results.jsonl --quiet

Datasets are generated, never loaded: the original ``data/`` directory contained
private images and is intentionally absent. Every fixture here is synthetic,
small, and fully described by its name, size, and seed.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from dataclasses import dataclass, replace
from typing import Callable, Final, Iterable, TextIO

from .baselines import BASELINE_NAMES, baseline_sizes
from .bytes_model import int_to_bytes, split_segments
from .codec import encoded_size
from .grammar import BINARY_OPS, DEFAULT_LIMITS, GRAMMAR_VERSION
from .hybrid import decode_hybrid, encode_hybrid
from .hybrid import search as hybrid_search
from .recipe import Const, decode, to_text
from .search.exhaustive import EnumerationConfig
from .search.exhaustive import search as exhaustive_search
from .search.genetic import GeneticConfig
from .search.genetic import search as genetic_search

__all__ = ["DATASETS", "make_dataset", "TrialSpec", "run_trial", "main"]

ALGORITHMS: Final[tuple[str, ...]] = ("exhaustive", "genetic", "hybrid")


# ---------------------------------------------------------------------------
# Synthetic datasets
# ---------------------------------------------------------------------------


def _zeros(size: int, seed: int, segment_size: int) -> bytes:
    return bytes(size)


def _ones(size: int, seed: int, segment_size: int) -> bytes:
    return b"\xff" * size


def _counter(size: int, seed: int, segment_size: int) -> bytes:
    return bytes(i % 256 for i in range(size))


def _arithmetic(size: int, seed: int, segment_size: int) -> bytes:
    step = 1 + (seed % 7)
    return bytes((i * step + seed) % 256 for i in range(size))


def _quadratic(size: int, seed: int, segment_size: int) -> bytes:
    return bytes((i * i + seed) % 256 for i in range(size))


def _repeated(size: int, seed: int, segment_size: int) -> bytes:
    pattern = bytes((seed + i * 37) % 256 for i in range(4))
    return (pattern * (size // 4 + 1))[:size]


def _power_segment(segment_size: int, seed: int) -> bytes:
    """Return one segment that genuinely *is* a small power.

    The best case for a recipe, and the reason it is built per segment rather
    than per file: a power that spans several segments leaves each individual
    segment looking like noise, so a segment-wise search would have nothing to
    find and the fixture would test the segmentation rather than the search.
    """
    if segment_size < 2:
        return bytes(segment_size)
    base = 3 + (seed % 5)
    exponent = max(2, int((8 * segment_size - 1) / math.log2(base)))
    value = base**exponent
    while value.bit_length() > 8 * segment_size and exponent > 2:
        exponent -= 1
        value = base**exponent
    return int_to_bytes(value, segment_size)


def _by_segment(
    builder: Callable[[int, int], bytes], size: int, seed: int, segment_size: int
) -> bytes:
    """Concatenate independently generated segments up to ``size`` bytes."""
    out = bytearray()
    index = 0
    while len(out) < size:
        out += builder(segment_size, seed + index)
        index += 1
    return bytes(out[:size])


def _power(size: int, seed: int, segment_size: int) -> bytes:
    return _by_segment(_power_segment, size, seed, segment_size)


def _power_noisy(size: int, seed: int, segment_size: int) -> bytes:
    """Powers with a few bits flipped: the case the hybrid form exists for."""

    def builder(length: int, segment_seed: int) -> bytes:
        base = bytearray(_power_segment(length, segment_seed))
        if not base:
            return bytes(base)
        rng = random.Random(segment_seed)
        for _ in range(min(3, length)):
            base[rng.randrange(length)] ^= 1 << rng.randrange(8)
        return bytes(base)

    return _by_segment(builder, size, seed, segment_size)


def _shift(size: int, seed: int, segment_size: int) -> bytes:
    def builder(length: int, segment_seed: int) -> bytes:
        if length < 1:
            return b""
        return int_to_bytes(1 << (8 * length - 1 - (segment_seed % 8)), length)

    return _by_segment(builder, size, seed, segment_size)


def _random(size: int, seed: int, segment_size: int) -> bytes:
    """Negative control. Nothing here should compress; if it does, suspect a bug."""
    rng = random.Random(seed)
    return bytes(rng.randrange(256) for _ in range(size))


#: Synthetic input classes. Structured classes are where a generative
#: explanation could plausibly exist; ``random`` is the negative control that
#: every reported win has to be checked against. Generators receive the segment
#: size so that algebraic fixtures can be built segment-aligned.
DATASETS: Final[dict[str, Callable[[int, int, int], bytes]]] = {
    "zeros": _zeros,
    "ones": _ones,
    "counter": _counter,
    "arithmetic": _arithmetic,
    "quadratic": _quadratic,
    "repeated": _repeated,
    "power": _power,
    "power_noisy": _power_noisy,
    "shift": _shift,
    "random": _random,
}


def make_dataset(name: str, size: int, seed: int, segment_size: int = 4) -> bytes:
    """Generate the named synthetic input deterministically."""
    try:
        generator = DATASETS[name]
    except KeyError:
        raise ValueError(
            f"unknown input class {name!r}; choose from {', '.join(DATASETS)}"
        ) from None
    if size < 0:
        raise ValueError("size must be non-negative")
    if segment_size < 1:
        raise ValueError("segment_size must be positive")
    return generator(size, seed, segment_size)


# ---------------------------------------------------------------------------
# Trials
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class TrialSpec:
    """Everything needed to reproduce one trial.

    Attributes:
        input_class: Key into :data:`DATASETS`.
        input_size: Bytes of synthetic input to generate.
        segment_size: Segment length the search operates on.
        seed: Seed for both the dataset and the stochastic search.
        algorithm: One of :data:`ALGORITHMS`.
        baseline: Baseline name a win is judged against.
        max_expression_bytes: Exhaustive enumeration size bound.
        max_const_bytes: Exhaustive enumeration constant-width bound.
        max_nodes: Exhaustive enumeration work budget.
        population_size: Genetic population size.
        max_generations: Genetic generation bound.
        time_limit: Optional per-segment wall-clock bound, in seconds.
    """

    input_class: str
    input_size: int = 64
    segment_size: int = 4
    seed: int = 12345
    algorithm: str = "exhaustive"
    baseline: str = "raw"
    max_expression_bytes: int = 6
    max_const_bytes: int = 2
    max_nodes: int = 500_000
    population_size: int = 200
    max_generations: int = 60
    time_limit: float | None = None

    def __post_init__(self) -> None:
        if self.input_class not in DATASETS:
            raise ValueError(f"unknown input class {self.input_class!r}")
        if self.algorithm not in ALGORITHMS:
            raise ValueError(f"unknown algorithm {self.algorithm!r}")
        if self.baseline not in BASELINE_NAMES:
            raise ValueError(f"unknown baseline {self.baseline!r}")
        if self.segment_size < 1:
            raise ValueError("segment_size must be positive")

    def as_dict(self) -> dict[str, object]:
        return {
            "input_class": self.input_class,
            "input_size": self.input_size,
            "segment_size": self.segment_size,
            "seed": self.seed,
            "algorithm": self.algorithm,
            "baseline": self.baseline,
            "grammar_version": GRAMMAR_VERSION,
            "max_expression_bytes": self.max_expression_bytes,
            "max_const_bytes": self.max_const_bytes,
            "max_nodes": self.max_nodes,
            "population_size": self.population_size,
            "max_generations": self.max_generations,
            "time_limit": self.time_limit,
            "limits": DEFAULT_LIMITS.as_dict(),
        }


def _run_exhaustive(segment: bytes, spec: TrialSpec) -> dict[str, object]:
    config = EnumerationConfig(
        max_expression_bytes=spec.max_expression_bytes,
        max_const_bytes=spec.max_const_bytes,
        max_nodes=spec.max_nodes,
        time_limit=spec.time_limit,
    )
    result = exhaustive_search(segment, config)
    started = time.perf_counter()
    decoded = decode(result.recipe)
    decode_seconds = time.perf_counter() - started
    return {
        "status": result.status.value,
        "recipe_text": to_text(result.recipe.expr),
        "recipe_bytes": result.breakdown.recipe_bytes,
        "metadata_bytes": result.breakdown.metadata_bytes,
        "residual_bytes": 0,
        "total_bytes": result.total_bytes,
        "decode_exact": decoded == segment,
        "used_fallback": result.used_fallback,
        "search_seconds": round(result.elapsed_seconds, 6),
        "decode_seconds": round(decode_seconds, 6),
        "work": result.work,
    }


def _run_genetic(segment: bytes, spec: TrialSpec) -> dict[str, object]:
    config = GeneticConfig(
        population_size=spec.population_size,
        max_generations=spec.max_generations,
        seed=spec.seed,
        ops=BINARY_OPS,
        baseline=spec.baseline,
        time_limit=spec.time_limit,
    )
    result = genetic_search(segment, config)
    started = time.perf_counter()
    decoded = decode(result.recipe)
    decode_seconds = time.perf_counter() - started
    work = dict(result.work)
    curve = work.pop("fitness_curve", [])
    work["generations_recorded"] = len(curve)
    work["final_best_total_bytes"] = curve[-1]["best_total_bytes"] if curve else None
    return {
        "status": result.status.value,
        "recipe_text": to_text(result.recipe.expr),
        "recipe_bytes": result.breakdown.recipe_bytes,
        "metadata_bytes": result.breakdown.metadata_bytes,
        "residual_bytes": 0,
        "total_bytes": result.total_bytes,
        "decode_exact": decoded == segment,
        "used_fallback": result.used_fallback,
        "search_seconds": round(result.elapsed_seconds, 6),
        "decode_seconds": round(decode_seconds, 6),
        "work": work,
    }


def _run_hybrid(segment: bytes, spec: TrialSpec) -> dict[str, object]:
    genetic_config = GeneticConfig(
        population_size=spec.population_size,
        max_generations=spec.max_generations,
        seed=spec.seed,
        stop_when_beats_baseline=False,
    )
    enumeration = EnumerationConfig(
        max_expression_bytes=min(spec.max_expression_bytes, 5),
        max_const_bytes=spec.max_const_bytes,
        max_nodes=min(spec.max_nodes, 200_000),
    )
    from .hybrid import generator_pool

    generators = generator_pool(
        segment, enumeration=enumeration, genetic_config=genetic_config
    )
    result = hybrid_search(segment, generators=generators, baseline_name=spec.baseline)
    blob = encode_hybrid(result.artifact)
    started = time.perf_counter()
    decoded = decode_hybrid(blob)
    decode_seconds = time.perf_counter() - started
    trivial = result.artifact.expr == Const(0)
    return {
        "status": "limit_reached" if trivial else "found",
        "recipe_text": to_text(result.artifact.expr),
        "recipe_bytes": result.artifact.recipe_bytes,
        "metadata_bytes": result.artifact.metadata_bytes,
        "residual_bytes": result.artifact.residual_bytes,
        "total_bytes": result.total_bytes,
        "decode_exact": decoded == segment,
        "used_fallback": trivial,
        "search_seconds": round(result.elapsed_seconds, 6),
        "decode_seconds": round(decode_seconds, 6),
        "work": {
            "residual_codec": result.artifact.codec,
            "generators_tried": result.generators_tried,
            "improved_residual": result.improved_residual,
            "encoded_blob_bytes": len(blob),
        },
    }


_RUNNERS: Final[dict[str, Callable[[bytes, TrialSpec], dict[str, object]]]] = {
    "exhaustive": _run_exhaustive,
    "genetic": _run_genetic,
    "hybrid": _run_hybrid,
}


def run_trial(spec: TrialSpec) -> list[dict[str, object]]:
    """Run one trial and return one record per segment.

    Every record is self-contained: it carries the parameters, the measured
    sizes, every baseline for the same segment, and whether the decode was
    exact. Nothing downstream needs to consult the spec to interpret a line.
    """
    data = make_dataset(
        spec.input_class, spec.input_size, spec.seed, spec.segment_size
    )
    segments = split_segments(data, spec.segment_size) if data else []
    runner = _RUNNERS[spec.algorithm]

    records: list[dict[str, object]] = []
    for index, segment in enumerate(segments):
        baselines = {name: b.size for name, b in baseline_sizes(segment).items()}
        outcome = runner(segment, spec)
        total = int(outcome["total_bytes"])
        records.append(
            {
                **spec.as_dict(),
                "segment_index": index,
                "segment_hex": segment.hex(),
                "segment_bytes": len(segment),
                **outcome,
                "baseline_bytes": baselines[spec.baseline],
                "baselines": baselines,
                "beats_baseline": bool(outcome["decode_exact"])
                and total < baselines[spec.baseline],
                "beats_all_baselines": bool(outcome["decode_exact"])
                and total < min(baselines.values()),
            }
        )
    return records


def summarize(records: Iterable[dict[str, object]]) -> dict[str, object]:
    """Aggregate segment records into one trial-level summary."""
    rows = list(records)
    if not rows:
        return {"record_type": "summary", "segments": 0}
    total = sum(int(r["total_bytes"]) for r in rows)
    original = sum(int(r["segment_bytes"]) for r in rows)
    return {
        "record_type": "summary",
        "input_class": rows[0]["input_class"],
        "algorithm": rows[0]["algorithm"],
        "segment_size": rows[0]["segment_size"],
        "seed": rows[0]["seed"],
        "segments": len(rows),
        "original_bytes": original,
        "artifact_bytes": total,
        "exact_segments": sum(1 for r in rows if r["decode_exact"]),
        "segments_beating_baseline": sum(1 for r in rows if r["beats_baseline"]),
        "segments_beating_all_baselines": sum(
            1 for r in rows if r["beats_all_baselines"]
        ),
        "fallback_segments": sum(1 for r in rows if r["used_fallback"]),
        "search_seconds": round(sum(float(r["search_seconds"]) for r in rows), 6),
    }


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m genetic_compression.experiments",
        description=(
            "Run reproducible genetic-compression trials on synthetic data. "
            "Every trial reports recipe size next to all baselines and states "
            "whether the decode was exact."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input-class",
        default="quadratic",
        help="synthetic input class, or 'all' for every class: "
        + ", ".join(DATASETS),
    )
    parser.add_argument("--input-size", type=int, default=64, help="input bytes")
    parser.add_argument("--segment-size", type=int, default=4, help="segment bytes")
    parser.add_argument("--seed", type=int, default=12345, help="dataset and search seed")
    parser.add_argument(
        "--algorithm",
        default="exhaustive",
        help="search algorithm, or 'all': " + ", ".join(ALGORITHMS),
    )
    parser.add_argument(
        "--baseline", default="raw", help="baseline a win is judged against"
    )
    parser.add_argument("--max-expression-bytes", type=int, default=6)
    parser.add_argument("--max-const-bytes", type=int, default=2)
    parser.add_argument("--max-nodes", type=int, default=500_000)
    parser.add_argument("--population", type=int, default=200)
    parser.add_argument("--generations", type=int, default=60)
    parser.add_argument(
        "--time-limit", type=float, default=None, help="per-segment seconds"
    )
    parser.add_argument(
        "--output", default=None, help="JSONL output path (default: stdout)"
    )
    parser.add_argument(
        "--quiet", action="store_true", help="suppress the human-readable summary"
    )
    parser.add_argument(
        "--list-datasets", action="store_true", help="list input classes and exit"
    )
    return parser


def _format_summary(summary: dict[str, object]) -> str:
    if not summary.get("segments"):
        return "no segments"
    return (
        f"{summary['input_class']:<12} {summary['algorithm']:<11} "
        f"seg={summary['segment_size']:<3} "
        f"exact={summary['exact_segments']}/{summary['segments']} "
        f"artifact={summary['artifact_bytes']}B "
        f"original={summary['original_bytes']}B "
        f"beats_baseline={summary['segments_beating_baseline']} "
        f"beats_all={summary['segments_beating_all_baselines']} "
        f"fallback={summary['fallback_segments']} "
        f"{summary['search_seconds']:.2f}s"
    )


def main(argv: list[str] | None = None, stdout: TextIO | None = None) -> int:
    """Run the experiment CLI. Returns a process exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    out = stdout or sys.stdout

    if args.list_datasets:
        for name in DATASETS:
            print(name, file=out)
        return 0

    classes = list(DATASETS) if args.input_class == "all" else [args.input_class]
    algorithms = list(ALGORITHMS) if args.algorithm == "all" else [args.algorithm]

    base = TrialSpec(
        input_class=classes[0],
        input_size=args.input_size,
        segment_size=args.segment_size,
        seed=args.seed,
        algorithm=algorithms[0],
        baseline=args.baseline,
        max_expression_bytes=args.max_expression_bytes,
        max_const_bytes=args.max_const_bytes,
        max_nodes=args.max_nodes,
        population_size=args.population,
        max_generations=args.generations,
        time_limit=args.time_limit,
    )

    sink = open(args.output, "w", encoding="utf-8") if args.output else out
    summaries: list[dict[str, object]] = []
    try:
        for input_class in classes:
            for algorithm in algorithms:
                spec = replace(base, input_class=input_class, algorithm=algorithm)
                records = run_trial(spec)
                for record in records:
                    print(json.dumps(record, sort_keys=True), file=sink)
                summary = summarize(records)
                summaries.append(summary)
                print(json.dumps(summary, sort_keys=True), file=sink)
    finally:
        if args.output:
            sink.close()

    if not args.quiet:
        stream = sys.stderr if sink is out else out
        for summary in summaries:
            print(_format_summary(summary), file=stream)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
