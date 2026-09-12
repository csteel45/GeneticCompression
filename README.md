# Genetic Compression

An experiment: use evolutionary and exhaustive search to find a compact
**algebraic recipe that regenerates a byte segment exactly** — storing the
recipe rather than the data. The research question is narrow and falsifiable:

> Can a bounded recipe language reproduce byte segments exactly with fewer bytes
> than raw storage and standard compression baselines?

## Status

The **Python harness in `genetic_compression/` is the active research path**.
The original Java implementation (2015–2016) has been moved unmodified to
[`legacy-java/`](legacy-java/) and is retained as historical reference; see
`docs/architecture/current-codebase.md` for what the Python harness replaces and
how the two differ on byte semantics.

## Quick start

Python 3.10+, standard library only — no dependencies.

```bash
python -m unittest discover -s tests -t .
python -m genetic_compression.experiments --help
python -m genetic_compression.experiments --input-class shift --segment-size 16 --algorithm all
```

Each trial writes one JSONL record per segment, carrying the parameters that
produced it alongside the measured result:

```text
input_class: shift        segment_size: 16   seed: 12345   grammar_version: 1
recipe_bytes: 5           metadata_bytes: 2  total_bytes: 7
raw: 16  zlib: 11  gzip: 24  bz2: 39  lzma: 60
decode_exact: true        algorithm: exhaustive
```

## What it does and does not show

Working, tested, and honest about its own results:

- unsigned byte/segment semantics with explicit lengths
- a versioned grammar with hard limits on depth, operations, intermediate bit
  width, and exponents
- immutable recipes with a decoder independent of any search
- binary serialization, so every size claim is a real serialized byte count
- raw, unsigned-integer, zlib, gzip, bz2, and lzma baselines
- bounded exhaustive search, deterministic seeded genetic search, and hybrid
  generated-prediction-plus-compressed-residual experiments

On synthetic 16-byte segments, segments that *are* a small power or a single
shift beat every baseline; counters, arithmetic and quadratic byte patterns, and
random controls do not and fall back to storing literals. **This is not a
general-purpose compressor and makes no general compression claim.** High-entropy
data has no compact recipe under any small grammar, and the reports say so.

## Java (legacy)

The original Maven project is in [`legacy-java/`](legacy-java/), unmodified.

```bash
mvn -f legacy-java/pom.xml test
```

Maven is not installed in the current development environment, so no Java
verification has been run there. Several `main` methods depend on the excluded
`data/` directory and are historical scratch probes, not interfaces.

## Notes

- The `BigDecimal` square-root helper in `legacy-java/.../genetics/core/Gene.java`
  is adapted from a CodeProject tip by **Luciano Culacciatti** (attributed
  in-source with the original URL).
- The original `data/` directory (sample inputs) is intentionally excluded from
  this repository: it contained photos of identifiable people. All test and
  experiment data is synthetic and generated.

## History & scope

A personal research experiment begun in 2015–2016 as a Java project reusing the
genetic-programming engine from the companion *Genetics* project, rebuilt in
Python in 2026 as a reproducible experiment harness. The rebuild was not a
line-by-line port: the goal was a harness that can answer the research question
with real byte counts and exact-decode checks rather than demonstrate the idea.

## License

MIT (own code) — see [LICENSE](LICENSE).
