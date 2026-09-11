"""Staged fitness for recipe candidates.

The staging exists to stop one specific disaster: a smaller-but-wrong candidate
outranking an exact one. Lossless compression has no partial credit, so
exactness is the first comparison and nothing below it can overturn it.

Stages, in order (lower is better at every stage):

1. **Validity** -- the candidate evaluated inside its limits at all.
2. **Exact reconstruction** -- decoded bytes equal the target bytes.
3. **Reconstruction error** -- for inexact candidates only, how far off it is
   (see "Error metric" below).
4. **Encoded byte size** -- the real serialized cost, metadata included.
5. **Decode cost** -- operations evaluated, then the widest intermediate value.

Baseline improvement is recorded on every score but is *not* a separate ranking
stage: with a fixed baseline it is a monotone function of stage 4, so ranking on
it again could not change any ordering. It is reported because the decision
"this is compression" is a comparison against the baseline, not against raw
bytes alone.

Error metric
------------

For inexact candidates the primary error is ``distance = hamming + width_gap``:
the bit Hamming distance between the candidate and target values, plus the
difference in their bit lengths. The absolute magnitude difference breaks ties.
Neither term is ever allowed to matter for an exact candidate, where all of them
are zero.

Each part is there because the alternatives are measurably worse. Magnitude
alone is a needle-shaped landscape for bit-structured targets: the nearest
neighbours of ``1 << 31`` are ``1 << 30`` and ``1 << 32``, each off by a
billion, so a search has no gradient to follow toward it. Hamming alone is
actively deceptive: zero differs from any single-bit target in exactly one bit,
so ``CONST 0`` scores better than every genuine near-miss and the population
collapses onto it. The ``width_gap`` term is what breaks that trap -- it charges
``CONST 0`` the full 32 bits it is missing. Measured over a set of targets that
a compact recipe provably can beat, the composite found a recipe in 7 of 21 runs
where Hamming-first and magnitude-first each found 1.

This is a search heuristic, not a claim about the data. It changes only which
candidates get explored; whether a result is reported as compression is still
decided by exact decoding and real encoded bytes.
"""

from __future__ import annotations

from dataclasses import dataclass

from .bytes_model import bytes_to_int
from .codec import encoded_size
from .grammar import DEFAULT_LIMITS, Limits
from .recipe import Recipe, RecipeError, evaluate_with_stats

__all__ = ["FitnessScore", "score", "INVALID_SIZE"]

#: Size attributed to a candidate that could not be encoded at all. Large enough
#: to lose every size comparison, finite so that arithmetic on scores is safe.
INVALID_SIZE = 1 << 30


@dataclass(frozen=True, slots=True)
class FitnessScore:
    """A candidate's staged score against one target segment.

    Attributes:
        valid: The recipe evaluated without breaching its limits.
        exact: The recipe decoded to exactly the target bytes.
        hamming: Bit distance between candidate and target values; 0 when exact.
        width_gap: Difference in bit length between the candidate value and the
            target. Separating this from ``hamming`` matters: without it, zero
            looks one bit away from any single-bit target while being as wrong
            as a value can be.
        magnitude: Absolute difference between the values; 0 when exact.
        total_bytes: Real encoded size of the recipe, metadata included.
        baseline_bytes: Size of the baseline this candidate is judged against.
        ops: Operations the decoder had to evaluate.
        max_bits: Widest intermediate value produced during decoding.
    """

    valid: bool
    exact: bool
    hamming: int
    width_gap: int
    magnitude: int
    total_bytes: int
    baseline_bytes: int
    ops: int
    max_bits: int

    @property
    def beats_baseline(self) -> bool:
        """True only for an exact recipe strictly smaller than its baseline."""
        return self.exact and self.total_bytes < self.baseline_bytes

    @property
    def distance(self) -> int:
        """Composite reconstruction error; 0 exactly when the candidate is exact."""
        return self.hamming + self.width_gap

    @property
    def key(self) -> tuple[int, int, int, int, int, int, int]:
        """Sort key; smaller is better. Compare candidates with this, only."""
        return (
            0 if self.valid else 1,
            0 if self.exact else 1,
            self.distance,
            self.magnitude,
            self.total_bytes,
            self.ops,
            self.max_bits,
        )

    def __lt__(self, other: "FitnessScore") -> bool:
        return self.key < other.key

    def as_dict(self) -> dict[str, object]:
        return {
            "valid": self.valid,
            "exact": self.exact,
            "hamming": self.hamming,
            "width_gap": self.width_gap,
            "distance": self.distance,
            "magnitude": self.magnitude,
            "total_bytes": self.total_bytes,
            "baseline_bytes": self.baseline_bytes,
            "beats_baseline": self.beats_baseline,
            "ops": self.ops,
            "max_bits": self.max_bits,
        }


def score(
    recipe: Recipe,
    target: bytes,
    baseline_bytes: int,
    limits: Limits = DEFAULT_LIMITS,
) -> FitnessScore:
    """Score ``recipe`` against ``target``.

    A recipe that breaches its limits is scored as invalid rather than raising:
    search generates invalid candidates constantly, and they must be rankable so
    they can be discarded in the same comparison as everything else.
    """
    target_value = bytes_to_int(target)
    try:
        value, stats = evaluate_with_stats(recipe.expr, limits)
    except RecipeError:
        return FitnessScore(
            valid=False,
            exact=False,
            hamming=max(target_value.bit_length(), 1),
            width_gap=max(target_value.bit_length(), 1),
            magnitude=target_value,
            total_bytes=INVALID_SIZE,
            baseline_bytes=baseline_bytes,
            ops=0,
            max_bits=0,
        )

    exact = value == target_value and recipe.segment_length == len(target)
    if exact:
        # A value that fits the segment length is implied by equality with the
        # target value, so this cannot be an oversized-value false positive.
        hamming = width_gap = magnitude = 0
    else:
        hamming = (value ^ target_value).bit_count()
        width_gap = abs(value.bit_length() - target_value.bit_length())
        magnitude = abs(value - target_value)

    try:
        total_bytes = encoded_size(recipe)
    except RecipeError:  # pragma: no cover - encodable by construction
        total_bytes = INVALID_SIZE

    return FitnessScore(
        valid=True,
        exact=exact,
        hamming=hamming,
        width_gap=width_gap,
        magnitude=magnitude,
        total_bytes=total_bytes,
        baseline_bytes=baseline_bytes,
        ops=stats.ops,
        max_bits=stats.max_bits,
    )
