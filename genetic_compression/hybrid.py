"""Hybrid experiments: a generated prediction plus a compressed residual.

Pure recipe search has an unforgiving failure mode. Either an expression hits
the target value exactly or it is worth nothing, so almost every segment of real
data falls straight back to a literal. The hybrid form softens that cliff
without giving up losslessness:

1. A recipe generates a *predicted* segment of the same length.
2. The residual is ``original XOR predicted``.
3. The residual is compressed with an ordinary stream codec.
4. The artifact is the recipe plus the compressed residual, and the decoder
   reproduces the original exactly by XORing the two back together.

The total that must beat the baseline is::

    recipe metadata + recipe bytes + residual metadata + residual bytes

Why this cannot cheat
---------------------

The generator ``CONST 0`` predicts all zero bytes, so its residual *is* the
original segment and the hybrid degenerates to "compress the segment with a
stream codec" -- the baseline itself. That candidate is always in the search, so
a hybrid result can never be worse than the codec it is being compared against,
and a reported win is always a win over that same codec on the same bytes.
Equally, the literal fallback stays available and is counted at full price.

The interesting question the reports answer is narrower than "did it compress":
it is whether the recipe made the residual *smaller or more compressible* than
the original. Both outcomes are recorded.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, replace
from typing import Final

from .baselines import compress_with, decompress_with
from .bytes_model import bytes_to_int, int_to_bytes
from .codec import CodecError, decode_varint, encode_expression, encode_varint, varint_size
from .codec import _parse_node  # internal parser, shared to avoid a second implementation
from .grammar import DEFAULT_LIMITS, GRAMMAR_VERSION, Limits
from .grammar import POW as POW_OP, SHL as SHL_OP
from .recipe import BinOp, Const, Expr, RecipeError, evaluate

__all__ = [
    "RESIDUAL_CODECS",
    "HybridArtifact",
    "HybridResult",
    "predict",
    "residual_of",
    "build",
    "encode_hybrid",
    "decode_hybrid",
    "structured_probes",
    "generator_pool",
    "search",
]

#: Residual codecs in a fixed order; the index is the stored codec id, so this
#: tuple is part of the wire format and may only be appended to.
RESIDUAL_CODECS: Final[tuple[str, ...]] = ("store", "zlib", "gzip", "bz2", "lzma")

ALGORITHM = "hybrid"


@dataclass(frozen=True, slots=True)
class HybridArtifact:
    """A generator expression plus a compressed residual for one segment.

    Attributes:
        expr: Generator expression; its value is the predicted segment.
        segment_length: Length of the original segment in bytes.
        codec: Residual codec name, from :data:`RESIDUAL_CODECS`.
        residual_payload: Compressed residual bytes as stored.
        grammar_version: Opcode table the expression is written against.
    """

    expr: Expr
    segment_length: int
    codec: str
    residual_payload: bytes
    grammar_version: int = GRAMMAR_VERSION

    def __post_init__(self) -> None:
        if self.codec not in RESIDUAL_CODECS:
            raise ValueError(f"unknown residual codec {self.codec!r}")
        if self.segment_length < 0:
            raise ValueError("segment_length must be non-negative")

    @property
    def recipe_bytes(self) -> int:
        """Encoded cost of the generator expression."""
        return len(encode_expression(self.expr))

    @property
    def metadata_bytes(self) -> int:
        """Encoded cost of everything a decoder needs besides the two payloads."""
        return (
            varint_size(self.grammar_version)
            + varint_size(self.segment_length)
            + 1  # codec id
            + varint_size(len(self.residual_payload))
        )

    @property
    def residual_bytes(self) -> int:
        """Stored size of the compressed residual."""
        return len(self.residual_payload)

    @property
    def total_bytes(self) -> int:
        """Total stored cost, which is what a baseline comparison must use."""
        return self.recipe_bytes + self.metadata_bytes + self.residual_bytes

    def as_dict(self) -> dict[str, object]:
        from .recipe import to_text

        return {
            "recipe_text": to_text(self.expr),
            "segment_length": self.segment_length,
            "residual_codec": self.codec,
            "recipe_bytes": self.recipe_bytes,
            "metadata_bytes": self.metadata_bytes,
            "residual_bytes": self.residual_bytes,
            "total_bytes": self.total_bytes,
            "grammar_version": self.grammar_version,
        }


def predict(expr: Expr, segment_length: int, limits: Limits = DEFAULT_LIMITS) -> bytes:
    """Evaluate ``expr`` and render it as a ``segment_length``-byte prediction.

    Raises:
        RecipeError: if evaluation breaches ``limits``.
        ValueError: if the value does not fit the segment length.
    """
    return int_to_bytes(evaluate(expr, limits), segment_length)


def residual_of(original: bytes, predicted: bytes) -> bytes:
    """Return ``original XOR predicted``.

    XOR is used rather than subtraction because it is length-preserving and
    carry-free: a single wrong byte in the prediction damages exactly one byte
    of the residual, which is what makes a near-miss prediction useful instead
    of catastrophic.
    """
    if len(original) != len(predicted):
        raise ValueError(
            f"residual needs equal lengths; got {len(original)} and {len(predicted)}"
        )
    return bytes(a ^ b for a, b in zip(original, predicted))


def build(
    segment: bytes,
    expr: Expr,
    codec: str,
    limits: Limits = DEFAULT_LIMITS,
) -> HybridArtifact:
    """Build the hybrid artifact for ``segment`` using ``expr`` as the generator."""
    predicted = predict(expr, len(segment), limits)
    residual = residual_of(segment, predicted)
    return HybridArtifact(
        expr=expr,
        segment_length=len(segment),
        codec=codec,
        residual_payload=compress_with(codec, residual),
    )


def encode_hybrid(artifact: HybridArtifact) -> bytes:
    """Serialize a hybrid artifact.

    Wire format::

        varint(grammar_version) varint(segment_length)
        byte(codec_id) varint(residual_length) residual_bytes
        expression_stream

    The residual precedes the expression so that the expression stream remains
    self-delimiting at the end of the blob, exactly as in
    :func:`genetic_compression.codec.encode_recipe`.
    """
    out = bytearray()
    out += encode_varint(artifact.grammar_version)
    out += encode_varint(artifact.segment_length)
    out.append(RESIDUAL_CODECS.index(artifact.codec))
    out += encode_varint(len(artifact.residual_payload))
    out += artifact.residual_payload
    out += encode_expression(artifact.expr)
    return bytes(out)


def decode_hybrid(blob: bytes, limits: Limits = DEFAULT_LIMITS) -> bytes:
    """Decode a hybrid artifact back to the original segment bytes.

    Raises:
        CodecError: on malformed input, an unknown codec id, or a prediction
            that does not fit the recorded segment length.
    """
    version, pos = decode_varint(blob, 0)
    if version != GRAMMAR_VERSION:
        raise CodecError(
            f"hybrid artifact uses grammar version {version}; "
            f"this build implements version {GRAMMAR_VERSION}"
        )
    segment_length, pos = decode_varint(blob, pos)
    if pos >= len(blob):
        raise CodecError("truncated hybrid artifact: missing codec id")
    codec_id = blob[pos]
    pos += 1
    if codec_id >= len(RESIDUAL_CODECS):
        raise CodecError(f"unknown residual codec id {codec_id}")
    residual_length, pos = decode_varint(blob, pos)
    if pos + residual_length > len(blob):
        raise CodecError("truncated hybrid artifact: residual payload")
    payload = bytes(blob[pos : pos + residual_length])
    pos += residual_length
    expr, pos = _parse_node(blob, pos, limits)
    if pos != len(blob):
        raise CodecError(f"{len(blob) - pos} trailing byte(s) after hybrid artifact")

    try:
        predicted = predict(expr, segment_length, limits)
    except (RecipeError, ValueError) as exc:
        raise CodecError(f"generator does not produce a valid prediction: {exc}") from exc
    residual = decompress_with(RESIDUAL_CODECS[codec_id], payload)
    if len(residual) != segment_length:
        raise CodecError(
            f"residual is {len(residual)} bytes but the segment is {segment_length}"
        )
    return residual_of(residual, predicted)


@dataclass(frozen=True, slots=True)
class HybridResult:
    """Outcome of a hybrid search over one segment."""

    artifact: HybridArtifact
    exact: bool
    baseline_bytes: int
    baseline_name: str
    generators_tried: int
    improved_residual: bool
    elapsed_seconds: float

    @property
    def total_bytes(self) -> int:
        return self.artifact.total_bytes

    @property
    def beats_baseline(self) -> bool:
        return self.exact and self.total_bytes < self.baseline_bytes

    def as_dict(self) -> dict[str, object]:
        return {
            "algorithm": ALGORITHM,
            "decode_exact": self.exact,
            "baseline": self.baseline_name,
            "baseline_bytes": self.baseline_bytes,
            "beats_baseline": self.beats_baseline,
            "generators_tried": self.generators_tried,
            "improved_residual": self.improved_residual,
            "elapsed_seconds": round(self.elapsed_seconds, 6),
            **self.artifact.as_dict(),
        }


def structured_probes(segment: bytes, max_base: int = 64) -> list[Expr]:
    """Return powers and shifts whose value is about as wide as ``segment``.

    Neither search strategy can realistically stumble onto ``POW(3, 160)``: its
    neighbours in the grammar (``POW(3, 159)``, ``POW(4, 160)``) share almost no
    bits with it, so there is no gradient to climb and no affordable enumeration
    that reaches six-byte expressions. But the *shape* is cheap to guess. For
    each small base, the exponent that lands on the target's bit width is one
    division away, and there are only a few hundred such candidates in total.

    This is a directed probe, not a search: it can only find values expressible
    as a small power or a single shift. It is here because those are exactly the
    values a bounded algebraic grammar can encode in five or six bytes, and
    missing them would make the hybrid experiments look like a negative result
    about the data when they were really a negative result about the search.
    """
    target_bits = bytes_to_int(segment).bit_length()
    if target_bits < 2:
        return []

    probes: list[Expr] = []
    for base in range(2, max_base + 1):
        # The exponent that lands on the target width is one division away.
        # log2 is only used to aim; the bit length of the actual power decides
        # which exponents are kept, so float error cannot produce a wrong probe.
        estimate = round(target_bits / math.log2(base))
        for exponent in range(max(2, estimate - 2), estimate + 3):
            if exponent > DEFAULT_LIMITS.max_exponent:
                break
            if abs((base**exponent).bit_length() - target_bits) <= 1:
                probes.append(BinOp(POW_OP, Const(base), Const(exponent)))
    for shift in range(max(1, target_bits - 2), target_bits + 1):
        probes.append(BinOp(SHL_OP, Const(1), Const(shift)))

    deduplicated: list[Expr] = []
    for probe in probes:
        if probe not in deduplicated:
            deduplicated.append(probe)
    return deduplicated


def generator_pool(
    segment: bytes,
    max_candidates: int = 24,
    enumeration: "EnumerationConfig | None" = None,
    genetic_config: "GeneticConfig | None" = None,
) -> list[Expr]:
    """Return generator candidates for ``segment``, most promising first.

    Two sources, because they fail in opposite directions:

    * **Exhaustive enumeration** contributes every cheap expression, ranked by
      the popcount of ``value XOR target`` -- the number of residual bits set.
      That is a cheap proxy for "how compressible is what's left", and only a
      proxy; the codecs still decide on real bytes in :func:`search`. It is
      complete for tiny expressions and hopeless past a handful of bytes.
    * **Structured probes** contribute the powers and shifts that land on the
      target's bit width -- see :func:`structured_probes`.
    * **Genetic search** contributes expressions that came close to the segment,
      which is what its error term already optimizes. It reaches structures the
      enumeration cannot afford -- a 32-byte segment generated by a power, say
      -- and proves nothing about what it failed to find.

    Only values that fit the segment length are kept: a prediction that
    overflows the segment cannot be rendered.
    """
    from .search.exhaustive import EnumerationConfig, enumerate_expressions
    from .search.genetic import GeneticConfig, propose_generators

    if not segment:
        return []
    cap = (1 << (8 * len(segment))) - 1
    if enumeration is None:
        enumeration = EnumerationConfig(
            max_expression_bytes=5, max_const_bytes=2, max_nodes=200_000
        )
    enumeration = replace(enumeration, value_cap=cap)

    target = bytes_to_int(segment)
    ranked: list[tuple[int, int, int, Expr]] = []
    for order, (size, value, expr) in enumerate(enumerate_expressions(enumeration)):
        ranked.append(((value ^ target).bit_count(), size, order, expr))
    for expr in structured_probes(segment):
        try:
            value = evaluate(expr)
        except RecipeError:
            continue
        if value > cap:
            continue
        ranked.append(((value ^ target).bit_count(), len(encode_expression(expr)), -1, expr))
    ranked.sort(key=lambda row: row[:3])
    candidates: list[Expr] = []
    for row in ranked:
        if row[3] not in candidates:
            candidates.append(row[3])
        if len(candidates) >= max_candidates // 2:
            break

    if genetic_config is None:
        genetic_config = GeneticConfig(
            population_size=200,
            max_generations=60,
            stop_when_beats_baseline=False,
        )
    for expr in propose_generators(segment, genetic_config, max_candidates):
        if expr not in candidates:
            candidates.append(expr)
        if len(candidates) >= max_candidates:
            break
    return candidates


def search(
    segment: bytes,
    generators: list[Expr] | None = None,
    codecs: tuple[str, ...] = RESIDUAL_CODECS,
    baseline_name: str = "raw",
    limits: Limits = DEFAULT_LIMITS,
) -> HybridResult:
    """Find the smallest exact hybrid artifact for ``segment``.

    Args:
        segment: Bytes to reproduce.
        generators: Candidate generator expressions, or ``None`` to build a pool
            with :func:`generator_pool`. ``CONST 0`` is always added, which makes
            the plain "compress the segment" candidate part of the search and
            guarantees the result is never worse than it.
        codecs: Residual codecs to try.
        baseline_name: Baseline the result is compared against in the report.
        limits: Evaluation limits.

    Every returned artifact is verified by a full decode before it is reported.
    """
    from .baselines import baseline_sizes

    started = time.perf_counter()
    if generators is None:
        generators = generator_pool(segment)
    candidates: list[Expr] = [Const(0)]
    for expr in generators:
        if expr not in candidates:
            candidates.append(expr)

    baseline = baseline_sizes(segment, (baseline_name,))[baseline_name]
    zero_residual_bytes: int | None = None

    best: HybridArtifact | None = None
    tried = 0
    for expr in candidates:
        for codec in codecs:
            try:
                artifact = build(segment, expr, codec, limits)
            except (RecipeError, ValueError):
                continue
            tried += 1
            if decode_hybrid(encode_hybrid(artifact), limits) != segment:
                continue  # pragma: no cover - would indicate a codec bug
            if expr == Const(0) and codec == "store":
                zero_residual_bytes = artifact.residual_bytes
            if best is None or artifact.total_bytes < best.total_bytes:
                best = artifact

    assert best is not None, "CONST 0 with the store codec always succeeds"
    improved = (
        zero_residual_bytes is not None
        and best.expr != Const(0)
        and best.residual_bytes < zero_residual_bytes
    )
    return HybridResult(
        artifact=best,
        exact=decode_hybrid(encode_hybrid(best), limits) == segment,
        baseline_bytes=baseline.size,
        baseline_name=baseline.name,
        generators_tried=tried,
        improved_residual=improved,
        elapsed_seconds=time.perf_counter() - started,
    )
