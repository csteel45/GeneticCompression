"""Immutable recipe model, deterministic evaluator, and decoder.

A *recipe* is the compression artifact: an expression tree plus the segment
length needed to turn its value back into bytes. Two rules shape this module.

1. **The decoder is independent of the search.** Nothing here knows about
   populations, generations, or fitness. A recipe that decodes correctly here
   decodes correctly for anyone, which is what makes a compression claim
   checkable.
2. **Failure is explicit.** Every way a recipe can be invalid raises a
   :class:`RecipeError` subclass. There is no silent clamping, no saturating
   arithmetic, and no "close enough" value, because approximate reconstruction
   is worthless for lossless compression.

Evaluation is deterministic: the same recipe and limits always produce the same
value, the same statistics, and the same errors.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .bytes_model import bytes_to_int, int_to_bytes
from .grammar import (
    ADD,
    AND,
    GRAMMAR_VERSION,
    MUL,
    OR,
    POW,
    SHL,
    SUB,
    XOR,
    DEFAULT_LIMITS,
    Limits,
    OpSpec,
)

__all__ = [
    "RecipeError",
    "GrammarError",
    "EvaluationError",
    "DecodeError",
    "Expr",
    "Const",
    "Literal",
    "BinOp",
    "Recipe",
    "EvalStats",
    "validate",
    "apply_op",
    "evaluate",
    "evaluate_with_stats",
    "decode",
    "verify",
    "literal_recipe",
    "const_recipe",
    "depth",
    "op_count",
    "node_count",
    "iter_nodes",
    "to_text",
]


class RecipeError(Exception):
    """Base class for every way a recipe can fail."""


class GrammarError(RecipeError):
    """The recipe is structurally invalid or violates a structural limit."""


class EvaluationError(RecipeError):
    """Evaluation hit a resource limit or produced an invalid value."""


class DecodeError(RecipeError):
    """The evaluated value cannot be rendered as the recipe's byte segment."""


# ---------------------------------------------------------------------------
# Expression nodes
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Expr:
    """Base class for expression nodes. Never instantiated directly."""


@dataclass(frozen=True, slots=True)
class Const(Expr):
    """A non-negative integer constant."""

    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int) or isinstance(self.value, bool):
            raise GrammarError(f"CONST value must be an int; got {self.value!r}")
        if self.value < 0:
            raise GrammarError(f"CONST value must be non-negative; got {self.value}")


@dataclass(frozen=True, slots=True)
class Literal(Expr):
    """Raw bytes stored verbatim.

    This is the fallback that keeps the harness honest: any segment can always
    be represented, so a search that finds nothing clever still reports a real,
    correctly sized artifact instead of a failure that hides the true cost.
    """

    data: bytes

    def __post_init__(self) -> None:
        if not isinstance(self.data, bytes):
            raise GrammarError(f"LITERAL data must be bytes; got {type(self.data).__name__}")


@dataclass(frozen=True, slots=True)
class BinOp(Expr):
    """A binary operation over two sub-expressions."""

    op: OpSpec
    left: Expr
    right: Expr

    def __post_init__(self) -> None:
        if self.op.arity != 2:
            raise GrammarError(f"{self.op.name} is not a binary operation")
        if not isinstance(self.left, Expr) or not isinstance(self.right, Expr):
            raise GrammarError(f"{self.op.name} operands must be expressions")


@dataclass(frozen=True, slots=True)
class Recipe:
    """A complete compression artifact for one byte segment.

    Attributes:
        expr: The expression whose value reproduces the segment.
        segment_length: Length of the decoded segment in bytes. Required
            metadata: the integer value alone cannot distinguish ``b"\\x05"``
            from ``b"\\x00\\x05"``.
        grammar_version: Opcode table the expression is written against.
    """

    expr: Expr
    segment_length: int
    grammar_version: int = GRAMMAR_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.expr, Expr):
            raise GrammarError(f"recipe expr must be an Expr; got {type(self.expr).__name__}")
        if not isinstance(self.segment_length, int) or self.segment_length < 0:
            raise GrammarError(
                f"segment_length must be a non-negative int; got {self.segment_length!r}"
            )
        if self.grammar_version != GRAMMAR_VERSION:
            raise GrammarError(
                f"unsupported grammar version {self.grammar_version}; "
                f"this build implements version {GRAMMAR_VERSION}"
            )


@dataclass(frozen=True, slots=True)
class EvalStats:
    """Cost measurements collected while evaluating a recipe.

    These feed decode-cost fitness terms and let a report state what a decoder
    actually had to do, rather than assuming evaluation is free.
    """

    ops: int = 0
    max_bits: int = 0
    depth: int = 0


# ---------------------------------------------------------------------------
# Structure
# ---------------------------------------------------------------------------


def iter_nodes(expr: Expr):
    """Yield every node in ``expr`` in preorder."""
    stack = [expr]
    while stack:
        node = stack.pop()
        yield node
        if isinstance(node, BinOp):
            stack.append(node.right)
            stack.append(node.left)


def depth(expr: Expr) -> int:
    """Return the tree depth of ``expr``; a leaf has depth 1."""
    if isinstance(expr, BinOp):
        return 1 + max(depth(expr.left), depth(expr.right))
    return 1


def op_count(expr: Expr) -> int:
    """Return the number of binary operations in ``expr``."""
    return sum(1 for node in iter_nodes(expr) if isinstance(node, BinOp))


def node_count(expr: Expr) -> int:
    """Return the total number of nodes in ``expr``."""
    return sum(1 for _ in iter_nodes(expr))


def validate(expr: Expr, limits: Limits = DEFAULT_LIMITS) -> None:
    """Check ``expr`` against structural limits.

    Raises:
        GrammarError: if the tree is too deep, has too many operations, or
            contains an oversized literal.
    """
    tree_depth = depth(expr)
    if tree_depth > limits.max_depth:
        raise GrammarError(f"depth {tree_depth} exceeds max_depth {limits.max_depth}")
    ops = op_count(expr)
    if ops > limits.max_ops:
        raise GrammarError(f"operation count {ops} exceeds max_ops {limits.max_ops}")
    for node in iter_nodes(expr):
        if isinstance(node, Literal) and len(node.data) > limits.max_literal_bytes:
            raise GrammarError(
                f"literal of {len(node.data)} bytes exceeds "
                f"max_literal_bytes {limits.max_literal_bytes}"
            )


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------


class _Counter:
    """Mutable evaluation state, kept off the public surface."""

    __slots__ = ("ops", "max_bits")

    def __init__(self) -> None:
        self.ops = 0
        self.max_bits = 0


def apply_op(op: OpSpec, left: int, right: int, limits: Limits = DEFAULT_LIMITS) -> int:
    """Apply ``op`` to two non-negative values, with pre-checks on the result size.

    The checks run *before* the arithmetic. Computing ``2 ** 10**9`` and then
    noticing it is too large is not a bound; it is a way to exhaust memory.

    Search code calls this directly on already-known child values, which avoids
    re-walking a subtree that was evaluated a moment ago.

    Raises:
        EvaluationError: if the operation would breach ``limits`` or produce a
            negative value.
    """
    if op is ADD:
        return left + right
    if op is SUB:
        result = left - right
        if result < 0:
            raise EvaluationError(
                f"SUB produced a negative value ({left} - {right}); "
                "segment values are unsigned"
            )
        return result
    if op is MUL:
        if left.bit_length() + right.bit_length() > limits.max_bits + 1:
            raise EvaluationError(
                f"MUL would exceed max_bits {limits.max_bits}"
            )
        return left * right
    if op is SHL:
        if right > limits.max_shift:
            raise EvaluationError(
                f"SHL shift {right} exceeds max_shift {limits.max_shift}"
            )
        if left.bit_length() + right > limits.max_bits:
            raise EvaluationError(f"SHL would exceed max_bits {limits.max_bits}")
        return left << right
    if op is XOR:
        return left ^ right
    if op is AND:
        return left & right
    if op is OR:
        return left | right
    if op is POW:
        if right > limits.max_exponent:
            raise EvaluationError(
                f"POW exponent {right} exceeds max_exponent {limits.max_exponent}"
            )
        if left > 1 and left.bit_length() * right > limits.max_bits + 1:
            raise EvaluationError(f"POW would exceed max_bits {limits.max_bits}")
        return left**right
    raise GrammarError(f"unknown operation {op.name}")


def _eval(expr: Expr, limits: Limits, state: _Counter) -> int:
    if isinstance(expr, Const):
        value = expr.value
    elif isinstance(expr, Literal):
        value = bytes_to_int(expr.data)
    elif isinstance(expr, BinOp):
        left = _eval(expr.left, limits, state)
        right = _eval(expr.right, limits, state)
        state.ops += 1
        if state.ops > limits.max_ops:
            raise EvaluationError(f"operation count exceeds max_ops {limits.max_ops}")
        value = apply_op(expr.op, left, right, limits)
    else:  # pragma: no cover - guarded by Expr construction
        raise GrammarError(f"unknown expression node {type(expr).__name__}")

    bits = value.bit_length()
    if bits > limits.max_bits:
        raise EvaluationError(f"value of {bits} bits exceeds max_bits {limits.max_bits}")
    if bits > state.max_bits:
        state.max_bits = bits
    return value


def evaluate_with_stats(
    expr: Expr, limits: Limits = DEFAULT_LIMITS
) -> tuple[int, EvalStats]:
    """Evaluate ``expr`` and return ``(value, stats)``.

    Structural limits are checked first, so a pathological tree is rejected
    before any arithmetic runs.

    Raises:
        GrammarError: if the structure violates ``limits``.
        EvaluationError: if evaluation violates ``limits`` or produces a
            negative intermediate value.
    """
    validate(expr, limits)
    state = _Counter()
    value = _eval(expr, limits, state)
    return value, EvalStats(ops=state.ops, max_bits=state.max_bits, depth=depth(expr))


def evaluate(expr: Expr, limits: Limits = DEFAULT_LIMITS) -> int:
    """Evaluate ``expr`` and return its non-negative integer value."""
    return evaluate_with_stats(expr, limits)[0]


# ---------------------------------------------------------------------------
# Decoding
# ---------------------------------------------------------------------------


def decode(recipe: Recipe, limits: Limits = DEFAULT_LIMITS) -> bytes:
    """Decode ``recipe`` into exactly ``recipe.segment_length`` bytes.

    Raises:
        GrammarError, EvaluationError: as raised by :func:`evaluate_with_stats`.
        DecodeError: if the value does not fit the recorded segment length.
    """
    value = evaluate(recipe.expr, limits)
    try:
        return int_to_bytes(value, recipe.segment_length)
    except ValueError as exc:
        raise DecodeError(
            f"value does not fit a {recipe.segment_length}-byte segment: {exc}"
        ) from exc


def verify(recipe: Recipe, expected: bytes, limits: Limits = DEFAULT_LIMITS) -> bool:
    """Return True only if ``recipe`` decodes to exactly ``expected``.

    Any recipe error is reported as False rather than propagating: callers use
    this as the exactness gate over candidates that are allowed to be invalid.
    """
    try:
        return decode(recipe, limits) == expected
    except RecipeError:
        return False


# ---------------------------------------------------------------------------
# Convenience constructors and rendering
# ---------------------------------------------------------------------------


def literal_recipe(data: bytes) -> Recipe:
    """Return the always-available fallback recipe that stores ``data`` verbatim."""
    return Recipe(expr=Literal(data), segment_length=len(data))


def const_recipe(data: bytes) -> Recipe:
    """Return the recipe that stores ``data``'s value as a single constant."""
    return Recipe(expr=Const(bytes_to_int(data)), segment_length=len(data))


def to_text(expr: Expr) -> str:
    """Render ``expr`` for debugging and reports.

    Display only. A short rendering says nothing about encoded size; use
    :func:`genetic_compression.codec.encoded_size` for that.
    """
    if isinstance(expr, Const):
        return str(expr.value)
    if isinstance(expr, Literal):
        return f"LITERAL[{len(expr.data)}]:{expr.data.hex()}"
    if isinstance(expr, BinOp):
        return f"{expr.op.name}({to_text(expr.left)}, {to_text(expr.right)})"
    return f"<unknown {type(expr).__name__}>"  # pragma: no cover
