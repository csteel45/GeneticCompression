# Current Codebase

## Packages

`com.precognizant.genpress` contains compression-facing experiments:

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

## Active Flow

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

The Python harness now covers the byte model, recipe model and decoder,
serialization and size accounting, baselines, exhaustive search, genetic search,
hybrid residual experiments, and a reproducible experiment runner, with tests
for each.

The Java source is retained in place and unmodified. No Java functionality has
been removed, and nothing in the Python harness depends on it. The remaining
decision -- whether Java stays at `src/`, moves to `legacy-java/`, survives only
as a Git tag, or is deleted after an archival release -- is deliberately left
open; see `docs/TODO.md`. Java verification has not been run in the current
environment because Maven is not installed there.
