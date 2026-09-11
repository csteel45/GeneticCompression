"""Search strategies over the recipe grammar, and the result type they share.

Every search in this package answers the same question for one byte segment:
what is the smallest *exactly decoding* artifact it can find, and how hard did
it look? The second half matters as much as the first. A search that finds
nothing has said something useful about the data only if it can distinguish
"I ran out of budget" from "no recipe of this shape exists".
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

from ..codec import SizeBreakdown, size_breakdown
from ..grammar import DEFAULT_LIMITS, Limits
from ..recipe import Recipe, decode, verify

__all__ = ["SearchStatus", "SearchResult", "make_result"]


class SearchStatus(str, Enum):
    """Why a search stopped.

    Attributes:
        FOUND: The search produced an expression that decodes the segment
            exactly. Check ``SearchResult.used_fallback`` to see whether that
            expression actually beat the literal/constant fallback; a tie keeps
            the fallback.
        EXHAUSTED: The search space defined by the configuration was fully
            enumerated and contained no such expression. This is a proof only
            *within the enumerated bound* — grammar, size budget, constant
            range, and value cap all narrow what "impossible" means.
        BUDGET_EXHAUSTED: The work or time budget ran out first, so nothing is
            proven; the space was not fully explored.
        LIMIT_REACHED: A generation/iteration bound ended the run before either
            success or exhaustion. Used by stochastic searches, which never
            enumerate a space completely.
    """

    FOUND = "found"
    EXHAUSTED = "exhausted"
    BUDGET_EXHAUSTED = "budget_exhausted"
    LIMIT_REACHED = "limit_reached"


@dataclass(frozen=True, slots=True)
class SearchResult:
    """The outcome of searching for a recipe for one segment.

    ``recipe`` is always present and always decodes exactly: when a search finds
    nothing better, it returns the literal or constant fallback. Reporting a
    failure as "no artifact" would hide the real cost of storing the segment,
    which is precisely the accounting mistake this harness exists to avoid.

    Attributes:
        recipe: The best exactly decoding recipe found.
        status: Why the search stopped.
        algorithm: Search identifier, recorded in experiment output.
        used_fallback: True when ``recipe`` is a bare literal or constant, i.e.
            the search found no generative explanation.
        exact: Always True; re-verified here rather than assumed.
        breakdown: Encoded expression/metadata byte split.
        work: Search-specific counters (nodes examined, generations, ...).
        elapsed_seconds: Wall-clock search time.
        decode_seconds: Wall-clock time to decode the winning recipe once.
    """

    recipe: Recipe
    status: SearchStatus
    algorithm: str
    used_fallback: bool
    exact: bool
    breakdown: SizeBreakdown
    work: dict[str, int | float | str] = field(default_factory=dict)
    elapsed_seconds: float = 0.0
    decode_seconds: float = 0.0

    @property
    def total_bytes(self) -> int:
        """Total encoded cost of the artifact, metadata included."""
        return self.breakdown.total_bytes

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serializable view for experiment records."""
        from ..recipe import to_text

        return {
            "algorithm": self.algorithm,
            "status": self.status.value,
            "used_fallback": self.used_fallback,
            "decode_exact": self.exact,
            "recipe_text": to_text(self.recipe.expr),
            "segment_length": self.recipe.segment_length,
            "grammar_version": self.recipe.grammar_version,
            **self.breakdown.as_dict(),
            "elapsed_seconds": round(self.elapsed_seconds, 6),
            "decode_seconds": round(self.decode_seconds, 6),
            "work": dict(self.work),
        }


def make_result(
    recipe: Recipe,
    target: bytes,
    status: SearchStatus,
    algorithm: str,
    used_fallback: bool,
    work: dict[str, int | float | str] | None = None,
    elapsed_seconds: float = 0.0,
    limits: Limits = DEFAULT_LIMITS,
) -> SearchResult:
    """Build a :class:`SearchResult`, re-verifying exactness and timing a decode.

    Exactness is checked here rather than trusted from the caller: a search bug
    that reports a near-miss as a win is the single most damaging failure this
    project can have.
    """
    started = time.perf_counter()
    exact = verify(recipe, target, limits)
    decode_seconds = time.perf_counter() - started
    if exact:
        decode(recipe, limits)
    return SearchResult(
        recipe=recipe,
        status=status,
        algorithm=algorithm,
        used_fallback=used_fallback,
        exact=exact,
        breakdown=size_breakdown(recipe),
        work=dict(work or {}),
        elapsed_seconds=elapsed_seconds,
        decode_seconds=decode_seconds,
    )
