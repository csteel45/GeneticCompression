"""Bounded exhaustive search: enumerate recipes in increasing encoded size.

Exhaustive search is the proof-oriented half of this harness. For tiny segments
it answers the research question directly, with no stochastic excuses: either a
compact expression exists inside the stated bound, or none does.

Method
------

Expressions are enumerated by **encoded expression size**, smallest first, with
values deduplicated:

* ``best_by_value[v]`` keeps the smallest expression seen for value ``v``.
* ``bucket[s]`` holds the values whose smallest expression costs ``s`` bytes.
* An expression of size ``s`` is built as ``op(left, right)`` where
  ``size(left) + size(right) == s - 1``, drawing both sides from earlier
  buckets.

Substituting the minimal expression for each subtree never makes a tree larger,
so enumerating only minimal representatives still reaches every value that any
expression of size ``s`` can produce. Because sizes are processed in increasing
order, the first expression that hits the target is a smallest one.

What "exhausted" does and does not prove
----------------------------------------

:attr:`SearchStatus.EXHAUSTED` means the configured space was fully enumerated
and held no exact expression. That space is narrowed by four knobs, all recorded
in the result: the operation set, ``max_expression_bytes``,
``max_const_bytes`` (constants are enumerated only up to that varint width), and
``value_cap`` (sub-expression values above it are pruned). It is a real negative
result about a stated bound, not a claim about the grammar in general. When the
node or time budget runs out first, the status is
:attr:`SearchStatus.BUDGET_EXHAUSTED` and nothing is proven.

The fallback
------------

Whatever the enumeration finds, the result is the smallest *exact* artifact,
compared against the literal and constant fallbacks for the segment. Random data
is expected to fall back; that outcome is reported, not hidden.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from ..bytes_model import bytes_to_int
from ..codec import encoded_size, expression_size, varint_size
from ..grammar import DEFAULT_LIMITS, FIRST_SLICE_OPS, Limits, OpSpec
from ..recipe import (
    BinOp,
    Const,
    EvaluationError,
    Expr,
    Recipe,
    RecipeError,
    apply_op,
    const_recipe,
    literal_recipe,
)
from . import SearchResult, SearchStatus, make_result

__all__ = ["EnumerationConfig", "fallback_recipe", "enumerate_expressions", "search"]

ALGORITHM = "exhaustive"


@dataclass(frozen=True, slots=True)
class EnumerationConfig:
    """Bounds that define the enumerated search space.

    Attributes:
        max_expression_bytes: Largest encoded expression size to enumerate.
            Costs grow steeply with this; 6-8 is a practical range for 1-4 byte
            segments.
        max_const_bytes: Widest varint constant to enumerate. 1 gives constants
            0-127, 2 gives 0-16383, 3 gives 0-2097151.
        ops: Operations to combine. Every added operation multiplies the work.
        value_cap: Sub-expression values above this are pruned. ``None`` derives
            a cap from the target, which must allow room above it because
            ``SUB`` reaches the target from above.
        max_nodes: Work budget in candidate combinations.
        time_limit: Optional wall-clock budget in seconds.
        limits: Evaluation limits applied to every candidate.
    """

    max_expression_bytes: int = 6
    max_const_bytes: int = 2
    ops: tuple[OpSpec, ...] = FIRST_SLICE_OPS
    value_cap: int | None = None
    max_nodes: int = 2_000_000
    time_limit: float | None = None
    limits: Limits = DEFAULT_LIMITS

    def __post_init__(self) -> None:
        if self.max_expression_bytes < 2:
            raise ValueError("max_expression_bytes must be at least 2 (a one-byte constant)")
        if self.max_const_bytes < 1:
            raise ValueError("max_const_bytes must be at least 1")
        if not self.ops:
            raise ValueError("at least one operation is required")
        if self.max_nodes < 0:
            raise ValueError("max_nodes must be non-negative")

    def as_dict(self) -> dict[str, object]:
        return {
            "max_expression_bytes": self.max_expression_bytes,
            "max_const_bytes": self.max_const_bytes,
            "ops": [op.name for op in self.ops],
            "value_cap": self.value_cap,
            "max_nodes": self.max_nodes,
            "time_limit": self.time_limit,
            "limits": self.limits.as_dict(),
        }


@dataclass(slots=True)
class _Enumeration:
    """Mutable enumeration state."""

    best_by_value: dict[int, Expr] = field(default_factory=dict)
    size_by_value: dict[int, int] = field(default_factory=dict)
    buckets: dict[int, list[int]] = field(default_factory=dict)
    nodes: int = 0
    budget_exhausted: bool = False


def fallback_recipe(segment: bytes) -> Recipe:
    """Return the smallest always-available artifact for ``segment``.

    Either the raw literal or a single constant wins, depending on how many
    leading zero bytes the segment has and how the varint and length encodings
    compare. Whichever it is, this is the honest cost of *not* finding a
    generative explanation, and every search result is measured against it.
    """
    candidates = [literal_recipe(segment)]
    try:
        candidates.append(const_recipe(segment))
    except RecipeError:  # pragma: no cover - const_recipe cannot fail on bytes
        pass
    return min(candidates, key=encoded_size)


def _leaf_values(config: EnumerationConfig, size: int) -> range:
    """Return the constants whose encoded leaf size is exactly ``size``."""
    width = size - 1  # one opcode byte plus the varint
    if width < 1 or width > config.max_const_bytes:
        return range(0)
    low = 0 if width == 1 else 1 << (7 * (width - 1))
    high = 1 << (7 * width)
    return range(low, high)


def _derive_value_cap(config: EnumerationConfig, target: int) -> int:
    """Return the sub-expression value ceiling.

    ``SUB`` reaches a target from above, so the cap must exceed the target;
    doubling it and adding a byte of slack is a pragmatic default that keeps
    ``ADD``/``SUB`` pairs reachable without letting ``MUL`` and ``POW`` run
    away.
    """
    if config.value_cap is not None:
        return config.value_cap
    return max(target * 2 + 0xFF, 0xFFFF)


def enumerate_expressions(
    config: EnumerationConfig = EnumerationConfig(),
    target: int | None = None,
    deadline: float | None = None,
):
    """Yield ``(size, value, expr)`` in non-decreasing encoded-expression size.

    When ``target`` is given, values above the derived cap are pruned and the
    generator stops as soon as the target is produced, so the final yielded item
    is the exact match.

    This is the inspectable form of the enumeration, useful for studying which
    values a bound can reach. It discards the work counters; callers that need
    them should use :func:`search`.
    """
    state = _Enumeration()
    yield from _enumerate(config, target, deadline, state)


def _enumerate(
    config: EnumerationConfig,
    target: int | None,
    deadline: float | None,
    state: _Enumeration,
):
    limits = config.limits
    cap = _derive_value_cap(config, target) if target is not None else config.value_cap

    def record(value: int, size: int, expr: Expr) -> bool:
        """Register ``value`` if this is the cheapest way seen to reach it."""
        if cap is not None and value > cap:
            return False
        previous = state.size_by_value.get(value)
        if previous is not None and previous <= size:
            return False
        state.size_by_value[value] = size
        state.best_by_value[value] = expr
        state.buckets.setdefault(size, []).append(value)
        return True

    for size in range(2, config.max_expression_bytes + 1):
        # Leaves: constants of exactly this encoded width.
        for value in _leaf_values(config, size):
            state.nodes += 1
            if state.nodes > config.max_nodes:
                state.budget_exhausted = True
                return
            expr = Const(value)
            if record(value, size, expr):
                yield size, value, expr
                if target is not None and value == target:
                    return

        # Interior nodes: one opcode byte plus two earlier sub-expressions.
        body = size - 1
        for left_size in range(2, body - 1):
            right_size = body - left_size
            left_values = state.buckets.get(left_size)
            right_values = state.buckets.get(right_size)
            if not left_values or not right_values:
                continue
            for op in config.ops:
                # Commutative operations only need each unordered pair once;
                # the mirrored split has the same encoded size.
                if op.commutative and left_size > right_size:
                    continue
                for left_value in left_values:
                    left_expr = state.best_by_value[left_value]
                    for right_value in right_values:
                        state.nodes += 1
                        if state.nodes > config.max_nodes:
                            state.budget_exhausted = True
                            return
                        if deadline is not None and state.nodes % 4096 == 0:
                            if time.perf_counter() > deadline:
                                state.budget_exhausted = True
                                return
                        try:
                            value = apply_op(op, left_value, right_value, limits)
                        except EvaluationError:
                            continue
                        if cap is not None and value > cap:
                            continue
                        expr = BinOp(op, left_expr, state.best_by_value[right_value])
                        if record(value, size, expr):
                            yield size, value, expr
                            if target is not None and value == target:
                                return


def search(
    segment: bytes,
    config: EnumerationConfig = EnumerationConfig(),
) -> SearchResult:
    """Search for the smallest expression that reproduces ``segment`` exactly.

    Returns the smallest exact artifact found, falling back to a literal or
    constant when the enumeration finds nothing smaller. The status distinguishes
    a completed enumeration from an exhausted budget, so a negative result can be
    read as evidence rather than silence.
    """
    started = time.perf_counter()
    deadline = started + config.time_limit if config.time_limit else None
    target = bytes_to_int(segment)
    segment_length = len(segment)

    fallback = fallback_recipe(segment)
    best = fallback
    best_size = encoded_size(fallback)
    used_fallback = True
    status = SearchStatus.EXHAUSTED

    state = _Enumeration()
    for size, value, expr in _enumerate(config, target, deadline, state):
        if value != target:
            continue
        candidate = Recipe(expr=expr, segment_length=segment_length)
        candidate_size = encoded_size(candidate)
        status = SearchStatus.FOUND
        if candidate_size < best_size:
            best, best_size, used_fallback = candidate, candidate_size, False
        break

    if status is not SearchStatus.FOUND and state.budget_exhausted:
        status = SearchStatus.BUDGET_EXHAUSTED

    elapsed = time.perf_counter() - started
    work: dict[str, object] = {
        "nodes_examined": state.nodes,
        "values_reached": len(state.best_by_value),
        "max_expression_bytes": config.max_expression_bytes,
        "max_const_bytes": config.max_const_bytes,
        "ops": ",".join(op.name for op in config.ops),
        "fallback_bytes": encoded_size(fallback),
        "fallback_expression_bytes": expression_size(fallback.expr),
        "target_varint_bytes": varint_size(target),
    }
    return make_result(
        recipe=best,
        target=segment,
        status=status,
        algorithm=ALGORITHM,
        used_fallback=used_fallback,
        work=work,
        elapsed_seconds=elapsed,
        limits=config.limits,
    )
