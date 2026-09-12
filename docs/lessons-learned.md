# Lessons Learned

- Java `BigInteger(byte[])` treats input as two's-complement signed data. That is not automatically suitable for lossless file-segment compression.
- `BigInteger.toByteArray()` may add or remove a sign byte. Round-trip tests must include leading zeros and high-bit bytes.
- Power-heavy expression search can generate enormous intermediate values quickly. Fitness evaluation needs hard bounds.
- Scratch `main` methods are useful for exploration but should not be treated as stable interfaces.
- The original sample `data/` directory is intentionally absent, so tests must not depend on it.
- Existing Surefire reports show one failing test in `NumUtilsTest`; update the test or implementation only after deciding signedness semantics.


## From the Python harness

- Hamming distance is a deceptive fitness signal for this problem. Zero differs
  from any single-bit target in exactly one bit, so `CONST 0` outranks every
  genuine near-miss and the population collapses onto it. Adding the bit-length
  gap (`distance = hamming + width_gap`) fixes it: on targets a compact recipe
  provably can beat, the composite found a recipe in 7 of 21 runs where
  Hamming-first and magnitude-first each found 1.
- Magnitude difference alone is no better. The neighbours of `1 << 31` in the
  grammar are `1 << 30` and `1 << 32`, each off by a billion, so there is no
  gradient to climb toward bit-structured values.
- Seeding the literal fallback into the GA's initial population poisons the run.
  It is exact from generation zero, so under exact-first staging it wins every
  tournament. Hold it aside as a floor on the reported result instead.
- Most small segments are *already* optimally stored as a constant. A 32-bit
  value is a five-byte varint, and the cheapest binary expression is five bytes
  plus metadata, so only values above roughly 2^28 are even worth searching for.
  Measure the fallback first or the search will look broken when it is right.
- Neither search will stumble onto `POW(3, 160)`: its grammar neighbours share
  almost no bits with it, and enumerating six-byte expressions is unaffordable.
  Cheap directed probes -- for each small base, the exponent that lands on the
  target's bit width -- find it immediately. Without them the hybrid results
  looked like a negative result about the data when they were a negative result
  about the search.
- Display strings lie about size. `POW(2, 4096)` renders in eleven characters
  and describes a 4097-bit value; a `CONST` holding the whole segment renders as
  one short number. Only the serialized length is a size.
- An all-zero residual is not free: zlib needs about eleven bytes for it, which
  is most of a small hybrid artifact's budget.
- gzip embeds a timestamp, so baseline *bytes* are not reproducible unless
  `mtime=0` is set, even though the *sizes* are.
