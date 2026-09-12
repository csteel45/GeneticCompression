# Current Codebase

## Layout

- `genetic_compression/` and `tests/` — the Python research harness, the active
  development path.
- `legacy-java/` — the original Java/Maven project, moved there unmodified in
  2026 and retained as historical reference.

## Java Packages

Under `legacy-java/src/main/java/`, `com.precognizant.genpress` contains
compression-facing experiments:

- `Compress`: reads a hard-coded file from `data/`, segments bytes, converts bytes to `BigInteger`, and writes a reconstructed output in a scratch flow.
- `FileUtils`: static file segmentation helpers and first-segment extraction.
- `NumUtils`: number conversion and integer square-root helpers.
- `Algo`, `BigSquareRoot`, `FunctionEnvironment`, `TestSquare`: exploratory classes and probes.

`com.precognizant.genetics` contains the genetic-programming machinery:

- `core`: `Population`, `Chromosome`, `Gene`, marker interfaces, and scratch threading probes.
- `node`: expression-tree nodes and random node factory.
- `operand`: math operations over `BigInteger` values.
- `data`: small `TestData` container.
- `util`: randomness, logging, and data-generation helpers.

## Original Java Flow

The compression idea is:

1. Read a file segment as bytes.
2. Interpret the segment as a large number.
3. Search for an expression whose value equals or approximates that number.
4. Store the expression as a recipe.
5. Decode by evaluating the recipe and converting the result back to bytes.

The current code only partially implements this flow. It has byte segmentation and exploratory search primitives, but it does not yet have a stable recipe format, deterministic decoder, or verified end-to-end compression test.

## Known Fragility

- `Compress.main` and `FileUtils.main` depend on `./data/laxguys.jpg`, which is intentionally not in the repo.
- `Gene.toString()` calls itself recursively.
- `Rand.init(long)` ignores the supplied seed and uses current time.
- `MathOperand.POWER` can request very large exponentiation.
- `BaseNode.size()` assumes node values are `BigInteger`.
- `Chromosome.getFitness()` casts a `BigInteger` to `Fitness`, which does not match the interface type.


## Python Harness

The Python package `genetic_compression/` is the active research path. It is a
rebuild rather than a port: the Java classes are organized around scratch
exploration, while the Python modules are organized around the steps a
compression claim has to survive.

- `bytes_model.py`: unsigned big-endian segment conversion with explicit lengths.
- `grammar.py`: versioned opcode table and the evaluation limits.
- `recipe.py`: immutable expression trees, deterministic evaluation, decoder.
- `codec.py`: binary serialization and the byte accounting that follows from it.
- `baselines.py`: raw, unsigned-integer, zlib, gzip, bz2, and lzma measurements.
- `fitness.py`: staged scoring that keeps exactness above size.
- `search/exhaustive.py`: bounded enumeration in increasing encoded size.
- `search/genetic.py`: seeded GA over recipe trees.
- `hybrid.py`: generated prediction plus compressed residual.
- `experiments.py`: synthetic datasets, CLI, and JSONL records.

## Byte Semantics: Java vs Python

This is the single most important behavioral difference, and it is a correctness
difference rather than a style one. Java's `new BigInteger(byte[])` reads its
input as two's-complement signed data; the Python harness reads segments as
unsigned big-endian values and carries the length as metadata.

| Segment      | Python `bytes_to_int` | Java `new BigInteger(byte[])` |
| ------------ | --------------------- | ----------------------------- |
| `05`         | 5                     | 5                             |
| `00 00 05`   | 5                     | 5                             |
| `ff`         | 255                   | -1                            |
| `80 00`      | 32768                 | -32768                        |
| `7f ff`      | 32767                 | 32767                         |
| *(empty)*    | 0                     | throws                        |

Two consequences follow for lossless work:

1. Any segment whose first byte is `>= 0x80` gets a negative Java value, which
   cannot be rendered back to unsigned bytes without a policy the old code never
   stated. That is the same disagreement the existing Surefire report shows as a
   failure in `NumUtilsTest.testConvertToNumber`.
2. Neither representation recovers leading zero bytes from the value alone, and
   `BigInteger.toByteArray()` may additionally add or drop a sign byte. The
   Python model fixes this by refusing to infer the length: `int_to_bytes` takes
   the segment length as a required argument.

Java's behavior is preserved in `bytes_model.legacy_java_biginteger_value` and
pinned by tests, so the difference stays documented rather than remembered.

## Migration Status

Resolved. The Python harness covers the byte model, recipe model and decoder,
serialization and size accounting, baselines, exhaustive search, genetic search,
hybrid residual experiments, and a reproducible experiment runner, each with
tests. It is the active research path and lives at the repository root.

The Java source was **moved unmodified to `legacy-java/`** rather than deleted or
reduced to a Git tag. The reasoning:

- Nothing is lost and nothing is hidden. The history, the failing test, and the
  scratch probes stay inspectable in the working tree, which matters because the
  Java byte semantics are the thing the Python model was designed against.
- A tag-only archive would make that comparison require a checkout to verify,
  and the comparison is load-bearing for the project's main design decision.
- Keeping it at the repository root would have kept implying two active builds.

No Java functionality has been removed, nothing in the Python harness depends on
it, and every path inside `legacy-java/` is unchanged and relative to that
directory, so Maven and Eclipse treat it as the project root. Java verification
has not been run in the current environment because Maven is not installed
there; the move was a pure file relocation with no edits, verified by Git
recording every path as a rename.
