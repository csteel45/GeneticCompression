"""Genetic compression research harness.

This package rebuilds the GeneticCompression experiment in Python. The research
question it exists to answer is narrow and falsifiable:

    Can a bounded recipe language reproduce byte segments exactly with fewer
    bytes than raw storage and standard compression baselines?

Design rules that the rest of the package follows:

* Byte/integer conversion is unsigned big-endian and keeps the segment length
  explicit, so leading zero bytes round-trip (``bytes_model``).
* A recipe is an immutable expression tree with hard resource limits, and its
  decoder is independent of any search (``recipe``).
* Size claims are measured against a real binary serialization, never against
  the length of a display string (``codec``).
* Nothing is called "compressed" until it is smaller than a stated baseline
  and reconstructs the original bytes exactly (``baselines``, ``fitness``).

See ``docs/plans/python-conversion-plan.md`` for the phased conversion plan.
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
