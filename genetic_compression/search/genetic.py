"""Deterministic genetic search over recipe trees.

Genetic search is added *after* exact decoding, real size accounting, and
baselines, because without those three it is only a machine for producing
confident nonsense. With them, every candidate it proposes is checked against
the same gate as any other artifact: decode exactly, or lose.

Determinism
-----------

The entire run is driven by one :class:`random.Random` seeded from the config.
Individuals are generated, selected, crossed, and mutated in a fixed order, and
fitness is memoized by expression, so the same seed and configuration reproduce
the same population, the same best candidate, and the same generation metrics.
``Rand.init(long)`` in the legacy Java engine silently ignored its seed; that
bug is the reason this module keeps no module-level random state at all.

Validity
--------

Mutation and crossover produce structurally valid trees by construction --
operands are always expressions, arity is always two, depth is checked before a
child is accepted. They can still produce trees that fail *evaluation*
(a negative ``SUB``, an oversized ``POW``); those are scored as invalid and rank
below every valid candidate rather than being silently repaired.

The fallback is a floor, not a seed
-----------------------------------

The literal/constant fallback is held aside and used as a floor on the reported
result: the search can never report something worse than simply storing the
segment. It is deliberately *not* placed in the initial population. Seeding it
poisons the run -- it is exact from generation zero, so under exact-first
staging it wins every tournament, the population collapses onto copies of it,
and the search never explores the small inexact candidates that a compact
recipe has to pass through on the way to being correct.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field

from ..baselines import baseline_sizes
from ..codec import encoded_size
from ..fitness import FitnessScore, score
from ..grammar import BINARY_OPS, DEFAULT_LIMITS, Limits, OpSpec
from ..recipe import BinOp, Const, Expr, Recipe, RecipeError, depth, evaluate
from . import SearchResult, SearchStatus, make_result
from .exhaustive import fallback_recipe

__all__ = ["GeneticConfig", "GenerationMetrics", "search", "propose_generators"]

ALGORITHM = "genetic"


@dataclass(frozen=True, slots=True)
class GeneticConfig:
    """Parameters for one genetic run.

    Attributes:
        population_size: Individuals per generation.
        max_generations: Hard generation bound.
        mutation_rate: Probability that an offspring is mutated.
        crossover_rate: Probability that an offspring comes from crossover
            rather than being a copy of a selected parent.
        tournament_size: Candidates per selection tournament.
        elitism: Best individuals copied unchanged into the next generation.
        max_initial_depth: Depth bound for the random initial population.
        max_tree_depth: Depth bound enforced on every offspring.
        const_bits: Width of randomly generated constants. Wide constants can
            smuggle the whole segment into a "recipe"; size accounting punishes
            that, but keeping this modest stops the search wasting its budget
            rediscovering the fallback.
        ops: Operations available to the search.
        seed: Seed for the run's single random source.
        time_limit: Optional wall-clock bound in seconds.
        stop_when_beats_baseline: End the run as soon as an exact candidate is
            strictly smaller than the baseline. The research question is whether
            such a candidate exists, not how far below it the search can get.
        baseline: Baseline name the result is judged against.
        limits: Evaluation limits applied to every candidate.
    """

    population_size: int = 200
    max_generations: int = 60
    mutation_rate: float = 0.35
    crossover_rate: float = 0.7
    tournament_size: int = 4
    elitism: int = 2
    max_initial_depth: int = 4
    max_tree_depth: int = 6
    const_bits: int = 16
    ops: tuple[OpSpec, ...] = BINARY_OPS
    seed: int = 12345
    time_limit: float | None = None
    stop_when_beats_baseline: bool = True
    baseline: str = "raw"
    limits: Limits = DEFAULT_LIMITS

    def __post_init__(self) -> None:
        if self.population_size < 2:
            raise ValueError("population_size must be at least 2")
        if self.max_generations < 1:
            raise ValueError("max_generations must be at least 1")
        if not 0.0 <= self.mutation_rate <= 1.0:
            raise ValueError("mutation_rate must be in [0, 1]")
        if not 0.0 <= self.crossover_rate <= 1.0:
            raise ValueError("crossover_rate must be in [0, 1]")
        if self.tournament_size < 1:
            raise ValueError("tournament_size must be at least 1")
        if not 0 <= self.elitism < self.population_size:
            raise ValueError("elitism must be in [0, population_size)")
        if self.max_initial_depth < 1 or self.max_tree_depth < 1:
            raise ValueError("depth bounds must be at least 1")
        if self.const_bits < 1:
            raise ValueError("const_bits must be at least 1")
        if not self.ops:
            raise ValueError("at least one operation is required")

    def as_dict(self) -> dict[str, object]:
        return {
            "population_size": self.population_size,
            "max_generations": self.max_generations,
            "mutation_rate": self.mutation_rate,
            "crossover_rate": self.crossover_rate,
            "tournament_size": self.tournament_size,
            "elitism": self.elitism,
            "max_initial_depth": self.max_initial_depth,
            "max_tree_depth": self.max_tree_depth,
            "const_bits": self.const_bits,
            "ops": [op.name for op in self.ops],
            "seed": self.seed,
            "time_limit": self.time_limit,
            "stop_when_beats_baseline": self.stop_when_beats_baseline,
            "baseline": self.baseline,
            "limits": self.limits.as_dict(),
        }


@dataclass(frozen=True, slots=True)
class GenerationMetrics:
    """One row of the fitness curve, recorded per generation."""

    generation: int
    best_total_bytes: int
    best_hamming: int
    exact_count: int
    valid_count: int
    distinct_count: int

    def as_dict(self) -> dict[str, int]:
        return {
            "generation": self.generation,
            "best_total_bytes": self.best_total_bytes,
            "best_hamming": self.best_hamming,
            "exact_count": self.exact_count,
            "valid_count": self.valid_count,
            "distinct_count": self.distinct_count,
        }


# ---------------------------------------------------------------------------
# Tree operators
# ---------------------------------------------------------------------------

_Path = tuple[str, ...]


def _random_const(rng: random.Random, config: GeneticConfig) -> Const:
    """Draw a constant, biased toward small values that encode cheaply."""
    if rng.random() < 0.5:
        return Const(rng.randrange(0, 256))
    bits = rng.randrange(1, config.const_bits + 1)
    return Const(rng.randrange(0, 1 << bits))


def _random_expr(rng: random.Random, config: GeneticConfig, max_depth: int) -> Expr:
    """Grow a random expression no deeper than ``max_depth``."""
    if max_depth <= 1 or rng.random() < 0.35:
        return _random_const(rng, config)
    op = rng.choice(config.ops)
    return BinOp(
        op,
        _random_expr(rng, config, max_depth - 1),
        _random_expr(rng, config, max_depth - 1),
    )


def _paths(expr: Expr) -> list[_Path]:
    """Return every node address in ``expr``, root first."""
    found: list[_Path] = []
    stack: list[tuple[Expr, _Path]] = [(expr, ())]
    while stack:
        node, path = stack.pop()
        found.append(path)
        if isinstance(node, BinOp):
            stack.append((node.right, path + ("R",)))
            stack.append((node.left, path + ("L",)))
    return found


def _at(expr: Expr, path: _Path) -> Expr:
    node = expr
    for step in path:
        assert isinstance(node, BinOp)
        node = node.left if step == "L" else node.right
    return node


def _replace(expr: Expr, path: _Path, replacement: Expr) -> Expr:
    if not path:
        return replacement
    assert isinstance(expr, BinOp)
    step, rest = path[0], path[1:]
    if step == "L":
        return BinOp(expr.op, _replace(expr.left, rest, replacement), expr.right)
    return BinOp(expr.op, expr.left, _replace(expr.right, rest, replacement))


def _mutate(expr: Expr, rng: random.Random, config: GeneticConfig) -> Expr:
    """Return a mutated copy of ``expr``.

    Three mutation kinds, chosen at random: nudge a constant, swap an operator,
    or regrow a subtree. The constant nudge matters most -- it is the only
    operator that can make small, local progress on the Hamming gradient without
    discarding structure that already works.
    """
    paths = _paths(expr)
    path = rng.choice(paths)
    node = _at(expr, path)
    kind = rng.random()

    if isinstance(node, Const) and kind < 0.6:
        delta = rng.choice((1, -1, 2, -2, 16, -16, 256, -256))
        if rng.random() < 0.3:
            bit = rng.randrange(0, max(node.value.bit_length(), 1) + 1)
            replacement: Expr = Const(node.value ^ (1 << bit))
        else:
            replacement = Const(max(0, node.value + delta))
    elif isinstance(node, BinOp) and kind < 0.3:
        replacement = BinOp(rng.choice(config.ops), node.left, node.right)
    else:
        remaining = config.max_tree_depth - len(path)
        if remaining < 1:
            return expr
        replacement = _random_expr(rng, config, remaining)

    mutated = _replace(expr, path, replacement)
    return mutated if depth(mutated) <= config.max_tree_depth else expr


def _crossover(
    left: Expr, right: Expr, rng: random.Random, config: GeneticConfig
) -> Expr:
    """Graft a random subtree of ``right`` into a random point of ``left``."""
    left_path = rng.choice(_paths(left))
    donor = _at(right, rng.choice(_paths(right)))
    child = _replace(left, left_path, donor)
    return child if depth(child) <= config.max_tree_depth else left


def _tournament(
    population: list[Expr],
    scores: dict[Expr, FitnessScore],
    rng: random.Random,
    config: GeneticConfig,
) -> Expr:
    best = rng.choice(population)
    for _ in range(config.tournament_size - 1):
        challenger = rng.choice(population)
        if scores[challenger].key < scores[best].key:
            best = challenger
    return best


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class _Run:
    """Everything one evolution produced, before it is turned into a report."""

    best_expr: Expr
    best_score: FitnessScore
    history: list[GenerationMetrics]
    scores: dict[Expr, FitnessScore]
    generations_run: int
    baseline_name: str
    baseline_bytes: int
    timed_out: bool


def _evolve(segment: bytes, config: GeneticConfig) -> _Run:
    """Run the evolution loop; shared by :func:`search` and :func:`propose_generators`."""
    started = time.perf_counter()
    deadline = started + config.time_limit if config.time_limit else None
    rng = random.Random(config.seed)
    segment_length = len(segment)

    baseline = baseline_sizes(segment, (config.baseline,))[config.baseline]
    fallback = fallback_recipe(segment)

    cache: dict[Expr, FitnessScore] = {}

    def evaluate(expr: Expr) -> FitnessScore:
        cached = cache.get(expr)
        if cached is None:
            cached = score(
                Recipe(expr=expr, segment_length=segment_length),
                segment,
                baseline.size,
                config.limits,
            )
            cache[expr] = cached
        return cached

    population: list[Expr] = [
        _random_expr(rng, config, config.max_initial_depth)
        for _ in range(config.population_size)
    ]

    best_expr = population[0]
    best_score = evaluate(best_expr)
    history: list[GenerationMetrics] = []
    generations_run = 0
    status = SearchStatus.LIMIT_REACHED

    for generation in range(config.max_generations):
        generations_run = generation + 1
        scores = {expr: evaluate(expr) for expr in population}

        ranked = sorted(population, key=lambda expr: scores[expr].key)
        if scores[ranked[0]].key < best_score.key:
            best_expr, best_score = ranked[0], scores[ranked[0]]

        history.append(
            GenerationMetrics(
                generation=generation,
                best_total_bytes=best_score.total_bytes,
                best_hamming=best_score.hamming,
                exact_count=sum(1 for s in scores.values() if s.exact),
                valid_count=sum(1 for s in scores.values() if s.valid),
                distinct_count=len(set(population)),
            )
        )

        if config.stop_when_beats_baseline and best_score.beats_baseline:
            break
        if deadline is not None and time.perf_counter() > deadline:
            status = SearchStatus.BUDGET_EXHAUSTED
            break
        if generation == config.max_generations - 1:
            break

        offspring: list[Expr] = ranked[: config.elitism]
        while len(offspring) < config.population_size:
            parent = _tournament(population, scores, rng, config)
            if rng.random() < config.crossover_rate:
                mate = _tournament(population, scores, rng, config)
                child = _crossover(parent, mate, rng, config)
            else:
                child = parent
            if rng.random() < config.mutation_rate:
                child = _mutate(child, rng, config)
            offspring.append(child)
        population = offspring

    return _Run(
        best_expr=best_expr,
        best_score=best_score,
        history=history,
        scores=cache,
        generations_run=generations_run,
        baseline_name=baseline.name,
        baseline_bytes=baseline.size,
        timed_out=status is SearchStatus.BUDGET_EXHAUSTED,
    )


def search(
    segment: bytes,
    config: GeneticConfig = GeneticConfig(),
) -> SearchResult:
    """Evolve a recipe for ``segment``.

    Returns the best exactly decoding artifact found, floored by the
    literal/constant fallback so the result is never worse than simply storing
    the segment. The status is never ``EXHAUSTED``: a stochastic search proves
    nothing about what does not exist.
    """
    started = time.perf_counter()
    run = _evolve(segment, config)
    fallback = fallback_recipe(segment)

    best_recipe = Recipe(expr=run.best_expr, segment_length=len(segment))
    used_fallback = False
    if not run.best_score.exact or encoded_size(best_recipe) > encoded_size(fallback):
        best_recipe, used_fallback = fallback, True

    if run.timed_out:
        status = SearchStatus.BUDGET_EXHAUSTED
    elif run.best_score.exact and not used_fallback:
        status = SearchStatus.FOUND
    else:
        status = SearchStatus.LIMIT_REACHED

    work: dict[str, object] = {
        "generations_run": run.generations_run,
        "population_size": config.population_size,
        "seed": config.seed,
        "evaluations": len(run.scores),
        "baseline": run.baseline_name,
        "baseline_bytes": run.baseline_bytes,
        "best_hamming": run.best_score.hamming,
        "fallback_bytes": encoded_size(fallback),
        "beats_baseline": run.best_score.beats_baseline,
        "best_score": run.best_score.as_dict(),
        "fitness_curve": [row.as_dict() for row in run.history],
    }
    return make_result(
        recipe=best_recipe,
        target=segment,
        status=status,
        algorithm=ALGORITHM,
        used_fallback=used_fallback,
        work=work,
        elapsed_seconds=time.perf_counter() - started,
        limits=config.limits,
    )


def propose_generators(
    segment: bytes,
    config: GeneticConfig = GeneticConfig(),
    count: int = 16,
) -> list[Expr]:
    """Return the expressions that came closest to ``segment``, best first.

    Written for the hybrid experiments. A generator does not need to be exact --
    it needs to predict well enough that the residual compresses -- and that is
    precisely what this search's error term already optimizes. Only expressions
    whose value fits the segment length are returned, since a prediction that
    overflows the segment cannot be rendered.
    """
    run = _evolve(segment, config)
    width = 8 * len(segment)
    ranked = sorted(run.scores.items(), key=lambda item: item[1].key)
    proposals: list[Expr] = []
    for expr, _ in ranked:
        try:
            value = evaluate(expr, config.limits)
        except RecipeError:
            continue
        if value.bit_length() > width:
            continue
        proposals.append(expr)
        if len(proposals) >= count:
            break
    return proposals
