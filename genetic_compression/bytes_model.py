"""Canonical byte/integer semantics for segment compression.

The legacy Java code leaned on ``new BigInteger(byte[])``, which interprets its
input as *two's-complement signed* data and whose ``toByteArray()`` may add or
drop a sign byte. That is not a usable model for lossless compression: it loses
leading zero bytes and flips the meaning of any segment whose first byte has the
high bit set.

This module defines the replacement semantics used everywhere in the Python
harness:

* A byte segment is read as an **unsigned big-endian** integer.
* The segment **length is metadata**, carried alongside the value, never
  inferred from the integer. ``b"\\x00\\x00\\x05"`` and ``b"\\x05"`` both have
  the value 5 and are distinguished only by their length.
* Negative values are not representable and are rejected.

Java's signed behavior is preserved in :func:`legacy_java_biginteger_value`
purely so tests and docs can state the difference exactly. It is legacy
behavior, not Python behavior, and nothing in the harness depends on it.
"""

from __future__ import annotations

__all__ = [
    "bytes_to_int",
    "int_to_bytes",
    "min_byte_length",
    "split_segments",
    "join_segments",
    "legacy_java_biginteger_value",
]


def bytes_to_int(data: bytes) -> int:
    """Return the unsigned big-endian integer value of ``data``.

    An empty segment has the value 0. The length of ``data`` is *not* recovered
    from the return value; callers must keep it (see :func:`int_to_bytes`).
    """
    return int.from_bytes(data, byteorder="big", signed=False)


def int_to_bytes(value: int, length: int) -> bytes:
    """Return ``value`` as exactly ``length`` unsigned big-endian bytes.

    Raises:
        ValueError: if ``value`` is negative, ``length`` is negative, or
            ``value`` does not fit in ``length`` bytes.
    """
    if value < 0:
        raise ValueError(f"segment values are unsigned; got {value}")
    if length < 0:
        raise ValueError(f"segment length must be non-negative; got {length}")
    if value.bit_length() > length * 8:
        raise ValueError(
            f"value needs {min_byte_length(value)} bytes but length is {length}"
        )
    return value.to_bytes(length, byteorder="big", signed=False)


def min_byte_length(value: int) -> int:
    """Return the fewest unsigned big-endian bytes that can hold ``value``.

    Zero needs zero bytes under this definition, which keeps
    ``min_byte_length`` consistent with ``bytes_to_int(b"") == 0``.
    """
    if value < 0:
        raise ValueError(f"segment values are unsigned; got {value}")
    return (value.bit_length() + 7) // 8


def split_segments(data: bytes, segment_size: int) -> list[bytes]:
    """Split ``data`` into ``segment_size``-byte segments.

    The final segment is short when ``len(data)`` is not a multiple of
    ``segment_size``; it is never padded, because padding would have to be
    stripped again by the decoder and that costs metadata. An empty input
    produces an empty list.
    """
    if segment_size <= 0:
        raise ValueError(f"segment_size must be positive; got {segment_size}")
    return [data[i : i + segment_size] for i in range(0, len(data), segment_size)]


def join_segments(segments: list[bytes]) -> bytes:
    """Concatenate segments produced by :func:`split_segments`."""
    return b"".join(segments)


def legacy_java_biginteger_value(data: bytes) -> int:
    """Return what Java's ``new BigInteger(byte[])`` would produce for ``data``.

    Documented for comparison only; see ``docs/lessons-learned.md``. Java treats
    the array as two's-complement signed, so a leading byte >= 0x80 yields a
    negative value, and leading zero bytes are lost on the way back out through
    ``toByteArray()``. The harness never uses this representation.
    """
    if not data:
        raise ValueError("Java BigInteger(byte[]) rejects a zero-length array")
    return int.from_bytes(data, byteorder="big", signed=True)
