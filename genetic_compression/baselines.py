"""Baseline measurements, so "compressed" always means "smaller than what".

A recipe that is smaller than the raw segment but larger than ``zlib`` output is
not a compression result worth reporting as a win. Every trial in this harness
records the recipe size next to all baseline sizes, and no candidate is called
compressed unless it beats the baseline target the experiment named.

Metadata honesty
----------------

Baseline sizes here include whatever the *decoder* would need:

* ``raw`` is the segment itself; its length is implied by the stored byte count.
* ``unsigned_int`` is the minimal big-endian integer encoding **plus** a varint
  segment length, because the integer alone cannot distinguish ``b"\\x05"`` from
  ``b"\\x00\\x05"``. This is the honest cost of the representation the legacy
  Java code used.
* The stream codecs (``zlib``, ``gzip``, ``bz2``, ``lzma``) are self-terminating
  and carry their own framing, so their compressed payload length is the whole
  cost. ``gzip`` and ``lzma`` include a container header that a real system
  would strip; that overhead is noted rather than quietly discounted, since
  removing it would require a format decision this harness has not made.

All codecs are invoked with fixed parameters (and ``mtime=0`` for gzip) so that
sizes are reproducible across runs and machines.
"""

from __future__ import annotations

import bz2
import gzip
import lzma
import zlib
from dataclasses import dataclass
from typing import Callable, Final

from .bytes_model import min_byte_length, bytes_to_int, int_to_bytes
from .codec import varint_size

__all__ = [
    "Baseline",
    "BASELINE_NAMES",
    "STREAM_CODECS",
    "compress_with",
    "decompress_with",
    "baseline_sizes",
    "best_baseline",
    "raw_size",
    "unsigned_int_size",
]


@dataclass(frozen=True, slots=True)
class Baseline:
    """One baseline measurement for a single byte segment.

    Attributes:
        name: Baseline identifier, stable across runs and reports.
        size: Total bytes a decoder would have to store, metadata included.
        note: What the size does and does not account for.
    """

    name: str
    size: int
    note: str = ""

    def as_dict(self) -> dict[str, object]:
        return {"name": self.name, "size": self.size, "note": self.note}


def _zlib_compress(data: bytes) -> bytes:
    return zlib.compress(data, 9)


def _gzip_compress(data: bytes) -> bytes:
    # mtime=0 keeps the header deterministic; otherwise sizes are stable but
    # the bytes are not, which makes stored results unverifiable.
    return gzip.compress(data, compresslevel=9, mtime=0)


def _bz2_compress(data: bytes) -> bytes:
    return bz2.compress(data, compresslevel=9)


def _lzma_compress(data: bytes) -> bytes:
    return lzma.compress(data, format=lzma.FORMAT_XZ, preset=9 | lzma.PRESET_EXTREME)


#: Stream codecs usable both as baselines and as residual encoders in hybrid
#: experiments. ``store`` is the identity codec: it is not compression, but it
#: is the fallback that keeps total-size accounting truthful when every real
#: codec expands the data.
STREAM_CODECS: Final[dict[str, tuple[Callable[[bytes], bytes], Callable[[bytes], bytes]]]] = {
    "store": (lambda data: data, lambda blob: blob),
    "zlib": (_zlib_compress, zlib.decompress),
    "gzip": (_gzip_compress, gzip.decompress),
    "bz2": (_bz2_compress, bz2.decompress),
    "lzma": (_lzma_compress, lzma.decompress),
}

BASELINE_NAMES: Final[tuple[str, ...]] = (
    "raw",
    "unsigned_int",
    "zlib",
    "gzip",
    "bz2",
    "lzma",
)


def compress_with(name: str, data: bytes) -> bytes:
    """Compress ``data`` with a named stream codec."""
    try:
        compress, _ = STREAM_CODECS[name]
    except KeyError:
        raise ValueError(f"unknown stream codec {name!r}") from None
    return compress(data)


def decompress_with(name: str, blob: bytes) -> bytes:
    """Reverse :func:`compress_with`."""
    try:
        _, decompress = STREAM_CODECS[name]
    except KeyError:
        raise ValueError(f"unknown stream codec {name!r}") from None
    return decompress(blob)


def raw_size(data: bytes) -> int:
    """Return the cost of storing the segment verbatim: the number to beat."""
    return len(data)


def unsigned_int_size(data: bytes) -> int:
    """Return the cost of the minimal unsigned integer encoding plus its length.

    The length varint is not optional. Without it the decoder cannot restore
    leading zero bytes, which is exactly the lossless failure the legacy Java
    conversion had.
    """
    value_bytes = min_byte_length(bytes_to_int(data))
    return value_bytes + varint_size(len(data))


def baseline_sizes(data: bytes, names: tuple[str, ...] = BASELINE_NAMES) -> dict[str, Baseline]:
    """Return every named baseline measurement for ``data``.

    Raises:
        ValueError: if ``names`` contains an unknown baseline.
    """
    results: dict[str, Baseline] = {}
    for name in names:
        if name == "raw":
            results[name] = Baseline(name, raw_size(data), "segment stored verbatim")
        elif name == "unsigned_int":
            results[name] = Baseline(
                name,
                unsigned_int_size(data),
                "minimal big-endian integer plus a varint segment length",
            )
        elif name in STREAM_CODECS and name != "store":
            payload = compress_with(name, data)
            note = "self-framing compressed payload"
            if name in ("gzip", "lzma"):
                note += "; includes container header a real format could strip"
            results[name] = Baseline(name, len(payload), note)
        else:
            raise ValueError(f"unknown baseline {name!r}")
    return results


def best_baseline(
    data: bytes, names: tuple[str, ...] = BASELINE_NAMES
) -> Baseline:
    """Return the smallest baseline for ``data``.

    Ties resolve by the order in ``names``, which keeps the choice deterministic
    and keeps ``raw`` preferred over an equally sized codec output.
    """
    measurements = baseline_sizes(data, names)
    return min((measurements[name] for name in names), key=lambda b: b.size)


def _self_check() -> None:  # pragma: no cover - exercised by the test suite
    """Confirm every stream codec round-trips; guards against a bad preset."""
    probe = bytes(range(64))
    for name in STREAM_CODECS:
        assert decompress_with(name, compress_with(name, probe)) == probe, name
    assert int_to_bytes(bytes_to_int(probe), len(probe)) == probe
