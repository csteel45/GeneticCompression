"""Binary serialization for recipes, and the byte accounting that follows from it.

The central failure mode this module exists to prevent: a recipe's *display
string* can look tiny while its real encoding is not. ``POW(2, 4096)`` renders
in eleven characters and its value is 4097 bits wide; ``CONST`` with a
sixteen-byte constant renders as one short number while smuggling the entire
segment into the "recipe". Size claims must come from
:func:`encoded_size`, never from ``len(to_text(expr))``.

Wire format (grammar version 1)
-------------------------------

A recipe is a metadata header followed by a preorder expression stream::

    header      := varint(grammar_version) varint(segment_length)
    expression  := node
    node        := 0x00 varint(value)              # CONST
                 | 0x01 varint(length) length*byte # LITERAL
                 | opcode node node                # binary operation

Integers are unsigned LEB128 varints, and must be canonically encoded: a
trailing continuation group of zero is rejected, so every recipe has exactly
one valid encoding and ``encode(decode(blob)) == blob``.

There is no magic number, checksum, or outer framing. Those belong to a
container file format, not to the artifact whose size is under test; adding
them here would inflate every measurement by a constant that has nothing to do
with the research question.
"""

from __future__ import annotations

from dataclasses import dataclass

from .grammar import (
    CONST,
    DEFAULT_LIMITS,
    GRAMMAR_VERSION,
    LITERAL,
    OPS_BY_CODE,
    Limits,
    OpSpec,
)
from .recipe import BinOp, Const, Expr, GrammarError, Literal, Recipe, RecipeError, validate

__all__ = [
    "CodecError",
    "encode_varint",
    "decode_varint",
    "varint_size",
    "encode_expression",
    "decode_expression",
    "encode_recipe",
    "decode_recipe",
    "encoded_size",
    "expression_size",
    "metadata_size",
    "SizeBreakdown",
    "size_breakdown",
]


class CodecError(RecipeError):
    """A recipe could not be encoded or decoded."""


# ---------------------------------------------------------------------------
# Varints
# ---------------------------------------------------------------------------


def encode_varint(value: int) -> bytes:
    """Encode a non-negative integer as an unsigned LEB128 varint."""
    if value < 0:
        raise CodecError(f"varints are unsigned; got {value}")
    out = bytearray()
    while True:
        group = value & 0x7F
        value >>= 7
        if value:
            out.append(group | 0x80)
        else:
            out.append(group)
            return bytes(out)


def decode_varint(buf: bytes, pos: int = 0) -> tuple[int, int]:
    """Decode a varint at ``buf[pos:]``; return ``(value, next_pos)``."""
    value = 0
    shift = 0
    start = pos
    while True:
        if pos >= len(buf):
            raise CodecError(f"truncated varint at offset {start}")
        byte = buf[pos]
        pos += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            if pos - start > 1 and byte == 0x00:
                raise CodecError(f"non-canonical varint at offset {start}")
            return value, pos
        shift += 7


def varint_size(value: int) -> int:
    """Return the encoded length of ``value`` as a varint, without encoding it."""
    if value < 0:
        raise CodecError(f"varints are unsigned; got {value}")
    return max(1, (value.bit_length() + 6) // 7)


# ---------------------------------------------------------------------------
# Expressions
# ---------------------------------------------------------------------------


def _encode_node(expr: Expr, out: bytearray) -> None:
    if isinstance(expr, Const):
        out.append(CONST.code)
        out += encode_varint(expr.value)
    elif isinstance(expr, Literal):
        out.append(LITERAL.code)
        out += encode_varint(len(expr.data))
        out += expr.data
    elif isinstance(expr, BinOp):
        out.append(expr.op.code)
        _encode_node(expr.left, out)
        _encode_node(expr.right, out)
    else:  # pragma: no cover - guarded by Expr construction
        raise CodecError(f"cannot encode {type(expr).__name__}")


def encode_expression(expr: Expr) -> bytes:
    """Encode an expression tree as a preorder opcode stream."""
    out = bytearray()
    _encode_node(expr, out)
    return bytes(out)


def _parse_node(
    buf: bytes, pos: int, limits: Limits
) -> tuple[Expr, int]:
    """Parse one preorder expression from ``buf[pos:]``.

    Uses an explicit stack rather than recursion: the input may be untrusted or
    corrupt, and a deeply nested stream must fail with a
    :class:`CodecError`, not a ``RecursionError``.
    """
    stack: list[tuple[OpSpec, list[Expr]]] = []
    ops = 0
    while True:
        if pos >= len(buf):
            raise CodecError(f"truncated expression at offset {pos}")
        code = buf[pos]
        pos += 1
        op = OPS_BY_CODE.get(code)
        if op is None:
            raise CodecError(
                f"unknown opcode 0x{code:02x} at offset {pos - 1} "
                f"for grammar version {GRAMMAR_VERSION}"
            )

        if op is CONST:
            value, pos = decode_varint(buf, pos)
            node: Expr = Const(value)
        elif op is LITERAL:
            length, pos = decode_varint(buf, pos)
            if length > limits.max_literal_bytes:
                raise CodecError(
                    f"literal of {length} bytes exceeds "
                    f"max_literal_bytes {limits.max_literal_bytes}"
                )
            if pos + length > len(buf):
                raise CodecError(f"truncated literal payload at offset {pos}")
            node = Literal(bytes(buf[pos : pos + length]))
            pos += length
        else:
            ops += 1
            if ops > limits.max_ops:
                raise CodecError(f"operation count exceeds max_ops {limits.max_ops}")
            if len(stack) + 1 > limits.max_depth:
                raise CodecError(f"nesting exceeds max_depth {limits.max_depth}")
            stack.append((op, []))
            continue

        while stack:
            frame_op, children = stack[-1]
            children.append(node)
            if len(children) < frame_op.arity:
                break
            stack.pop()
            node = BinOp(frame_op, children[0], children[1])
        else:
            return node, pos


def decode_expression(buf: bytes, limits: Limits = DEFAULT_LIMITS) -> Expr:
    """Decode a complete expression stream; reject trailing bytes."""
    expr, pos = _parse_node(buf, 0, limits)
    if pos != len(buf):
        raise CodecError(f"{len(buf) - pos} trailing byte(s) after expression")
    return expr


# ---------------------------------------------------------------------------
# Recipes
# ---------------------------------------------------------------------------


def encode_recipe(recipe: Recipe) -> bytes:
    """Encode a complete recipe: metadata header plus expression stream."""
    out = bytearray()
    out += encode_varint(recipe.grammar_version)
    out += encode_varint(recipe.segment_length)
    _encode_node(recipe.expr, out)
    return bytes(out)


def decode_recipe(blob: bytes, limits: Limits = DEFAULT_LIMITS) -> Recipe:
    """Decode a recipe encoded by :func:`encode_recipe`.

    Raises:
        CodecError: on truncation, unknown opcodes, non-canonical varints,
            trailing bytes, or a structure that exceeds ``limits``.
    """
    version, pos = decode_varint(blob, 0)
    if version != GRAMMAR_VERSION:
        raise CodecError(
            f"recipe uses grammar version {version}; "
            f"this build implements version {GRAMMAR_VERSION}"
        )
    segment_length, pos = decode_varint(blob, pos)
    expr, pos = _parse_node(blob, pos, limits)
    if pos != len(blob):
        raise CodecError(f"{len(blob) - pos} trailing byte(s) after recipe")
    try:
        recipe = Recipe(expr=expr, segment_length=segment_length, grammar_version=version)
        validate(recipe.expr, limits)
    except GrammarError as exc:
        raise CodecError(f"decoded recipe is invalid: {exc}") from exc
    return recipe


# ---------------------------------------------------------------------------
# Size accounting
# ---------------------------------------------------------------------------


def metadata_size(recipe: Recipe) -> int:
    """Return the encoded byte cost of the recipe's metadata header."""
    return varint_size(recipe.grammar_version) + varint_size(recipe.segment_length)


def expression_size(expr: Expr) -> int:
    """Return the encoded byte cost of the expression stream alone."""
    return len(encode_expression(expr))


def encoded_size(recipe: Recipe) -> int:
    """Return the total encoded byte cost of ``recipe``, metadata included.

    This is the only number that may be compared against a baseline.
    """
    return len(encode_recipe(recipe))


@dataclass(frozen=True, slots=True)
class SizeBreakdown:
    """Encoded byte cost split into the parts a report must show separately."""

    recipe_bytes: int
    metadata_bytes: int

    @property
    def total_bytes(self) -> int:
        return self.recipe_bytes + self.metadata_bytes

    def as_dict(self) -> dict[str, int]:
        return {
            "recipe_bytes": self.recipe_bytes,
            "metadata_bytes": self.metadata_bytes,
            "total_bytes": self.total_bytes,
        }


def size_breakdown(recipe: Recipe) -> SizeBreakdown:
    """Return the expression/metadata split for ``recipe``."""
    return SizeBreakdown(
        recipe_bytes=expression_size(recipe.expr),
        metadata_bytes=metadata_size(recipe),
    )
