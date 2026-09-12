# Python Conversion Implementation Plan

## Objective

Rebuild GeneticCompression as a Python research platform while preserving the Java project as historical reference until the Python implementation can reproduce the important byte-conversion, recipe-evaluation, and experiment-reporting behaviors.

The conversion should not be a line-by-line port. The goal is a cleaner experiment harness that can answer the research question directly:

Can a bounded recipe language reproduce byte segments exactly with fewer bytes than raw storage and standard compression baselines?

## Non-Goals

- Do not claim general-purpose compression performance during the conversion.
- Do not preserve scratch `main` flows as primary interfaces.
- Do not depend on the excluded private `data/` files.
- Do not add heavyweight dependencies before the standard-library implementation proves the harness shape.
- Do not delete the Java implementation until the Python harness has equivalent tests and documented migration status.

## Target Repository Layout

```text
genetic_compression/
  __init__.py
  bytes_model.py
  recipe.py
  codec.py
  grammar.py
  fitness.py
  baselines.py
  experiments.py
  search/
    __init__.py
    exhaustive.py
    genetic.py
tests/
  test_bytes_model.py
  test_recipe.py
  test_codec.py
  test_baselines.py
  test_exhaustive_search.py
docs/
  plans/
    python-conversion-plan.md
```

## Phase 1: Project Skeleton

Add a minimal Python package without changing Java behavior.

Tasks:

- Add `pyproject.toml` with Python version, test configuration, and package metadata.
- Add `genetic_compression/` package and `tests/`.
- Use the Python standard library first.
- Add `pytest` only if the project chooses that test runner explicitly; otherwise use `unittest` to avoid early dependency churn.
- Document Python setup commands in `docs/reference/build-and-run.md`.

Acceptance criteria:

- `python -m unittest` or the chosen test command runs.
- The package imports cleanly.
- Java source remains untouched except for documentation references if needed.

Suggested commit:

```bash
git commit -m "chore: add python research package skeleton"
```

## Phase 2: Canonical Byte Semantics

Implement exact byte/integer conversion before touching search.

Tasks:

- Implement `bytes_to_int(data: bytes) -> int` using unsigned big-endian semantics.
- Implement `int_to_bytes(value: int, length: int) -> bytes`.
- Reject negative values for file segment integers.
- Preserve segment length explicitly so leading zero bytes round-trip.
- Implement `split_segments(data: bytes, segment_size: int) -> list[bytes]`.

Test cases:

- empty byte strings
- one-byte values
- leading zero bytes
- bytes with the high bit set
- odd segment sizes
- final short segment
- random synthetic round trips with fixed seeds

Acceptance criteria:

- Every byte fixture round-trips exactly.
- Signed Java `BigInteger` behavior is documented as legacy behavior, not Python behavior.

Suggested commit:

```bash
git commit -m "feat: define unsigned byte segment model"
```

## Phase 3: Recipe Model And Decoder

Define the compression artifact before optimizing it.

Tasks:

- Add immutable recipe objects for constants, unary operations, binary operations, and literals.
- Support a small first grammar:
  - `CONST`
  - `ADD`
  - `SUB`
  - `MUL`
  - `SHL`
  - `XOR`
  - `AND`
  - `OR`
  - bounded `POW`
  - `LITERAL`
- Add deterministic `evaluate(recipe) -> int`.
- Add resource limits:
  - max tree depth
  - max operation count
  - max intermediate bit length
  - max exponent for `POW`
- Add decode path from recipe to fixed-length bytes.

Acceptance criteria:

- Recipe evaluation is deterministic.
- Invalid recipes fail predictably.
- Every successful decode proves exact byte equality.

Suggested commit:

```bash
git commit -m "feat: add deterministic recipe model and decoder"
```

## Phase 4: Real Serialization And Size Accounting

Compression requires counting actual encoded bytes, not display-string length.

Tasks:

- Implement a versioned binary recipe encoder.
- Count opcode bytes, integer varints, literal payloads, segment metadata, and grammar version.
- Implement a matching decoder for encoded recipes.
- Add `encoded_size(recipe)`.
- Keep text rendering for debugging only.

Acceptance criteria:

- `decode_recipe(encode_recipe(recipe)) == recipe` for supported recipes.
- Reported size equals the actual encoded byte length.
- Metadata cost is included in compression decisions.

Suggested commit:

```bash
git commit -m "feat: serialize recipes with exact byte accounting"
```

## Phase 5: Baselines

Add honest comparisons before reporting any wins.

Tasks:

- Implement baseline size checks for:
  - raw bytes
  - unsigned integer byte representation
  - `zlib`
  - `gzip`
  - `bz2`
  - `lzma`
- Record compressed payload size and any required metadata assumptions.
- Use small synthetic datasets first.

Acceptance criteria:

- Every trial reports recipe size next to all baseline sizes.
- No candidate is called compressed unless it is smaller than the selected baseline target.

Suggested commit:

```bash
git commit -m "feat: add compression baseline measurements"
```

## Phase 6: Exhaustive Search For Tiny Segments

Use exhaustive search to establish proof-oriented results for small cases.

Tasks:

- Enumerate recipes in increasing encoded-size order.
- Deduplicate equivalent or already-seen values where practical.
- Stop when an exact recipe is found below the configured byte limit.
- Report when no recipe exists within the configured grammar and size bound.

Acceptance criteria:

- Tiny structured inputs find compact recipes when they exist.
- Tiny random inputs usually fall back to literals.
- Reports distinguish "not found within bound" from "proven impossible within enumerated bound."

Suggested commit:

```bash
git commit -m "feat: add bounded exhaustive recipe search"
```

## Phase 7: Genetic Search

Only add GA/GP after exact decode, size accounting, and baselines exist.

Tasks:

- Represent individuals as recipe trees or instruction lists.
- Make mutation and crossover preserve grammar validity.
- Use deterministic seeds.
- Score candidates with staged fitness:
  1. exact reconstruction
  2. encoded byte size
  3. baseline improvement
  4. decode cost
  5. intermediate value limits
- Save best candidate and generation metrics.

Acceptance criteria:

- Re-running with the same seed reproduces the same search behavior.
- Wrong candidates cannot outrank exact candidates in final output.
- Runs terminate by generation, time, or cost bound.

Suggested commit:

```bash
git commit -m "feat: add deterministic genetic recipe search"
```

## Phase 8: Hybrid Residual Experiments

This is the most promising path for useful compression.

Tasks:

- Add recipes that generate a predicted byte segment.
- Encode residuals as `original XOR generated`.
- Compress residuals with baseline codecs.
- Score the total size:

```text
recipe metadata + recipe bytes + residual metadata + residual bytes
```

Acceptance criteria:

- Hybrid trials reconstruct exactly.
- Reports show whether the recipe made residuals smaller or more compressible.
- Literal fallback remains available and honestly counted.

Suggested commit:

```bash
git commit -m "feat: add hybrid generated-residual experiments"
```

## Phase 9: Experiment Harness

Make results reproducible and reviewable.

Tasks:

- Add CLI entry point for running experiments on synthetic data.
- Record JSON or JSONL output with:
  - input class
  - segment size
  - seed
  - grammar version
  - search algorithm
  - max generations or enumeration bound
  - recipe bytes
  - metadata bytes
  - baseline bytes
  - exact reconstruction result
  - decode runtime
- Add fixtures for structured and random negative-control inputs.

Acceptance criteria:

- A full trial can be rerun from recorded parameters.
- Successes and failures are both reported.
- Documentation includes example commands and sample output.

Suggested commit:

```bash
git commit -m "feat: add reproducible experiment runner"
```

## Phase 10: Java Migration Decision

Keep Java until Python is credible, then decide whether to archive or remove it.

Tasks:

- Add a migration status note to `README.md`.
- Compare Java and Python byte-conversion semantics in docs.
- Decide whether Java remains as:
  - `legacy-java/`
  - a Git tag only
  - deleted source after an archival release

Acceptance criteria:

- No Java functionality is silently lost.
- The active research path is clearly Python.
- Build/test instructions point to the Python harness first.

Suggested commit:

```bash
git commit -m "docs: mark python harness as primary research path"
```

### Outcome

Completed 2026-09-12. The Java source was **moved unmodified to `legacy-java/`**
— not deleted, and not reduced to a Git tag, because the Java byte semantics are
the reference the Python model was designed against and that comparison should
stay inspectable in the working tree. See
`docs/architecture/current-codebase.md` for the full reasoning and
`legacy-java/README.md` for the directory's own notes.

## Branch, Commit, And Merge Workflow

Recommended workflow:

```bash
git checkout main
git pull --ff-only
git checkout -b python-conversion
```

Work in the phase commits above. Before merge:

```bash
python -m unittest discover -s tests -t .
mvn -f legacy-java/pom.xml test
git status --short
```

If Maven is unavailable, record that explicitly in the merge notes and do not claim Java verification.

Merge when the current phase acceptance criteria pass:

```bash
git checkout main
git merge --no-ff python-conversion
```

For a multi-phase conversion, merge after each phase or small group of phases rather than waiting for a large rewrite.

## First Implementation Slice

The first useful conversion slice should include only:

- Python skeleton
- unsigned byte model
- deterministic recipe objects for `CONST`, `ADD`, `SUB`, `MUL`, `SHL`, and `LITERAL`
- binary serialization for those recipes
- raw and `zlib` baselines
- exhaustive search for 1-4 byte segments

This slice is small enough to verify, but it tests the real research premise: exact reconstruction, real byte accounting, and comparison against a baseline.

## Research Risks

- Arbitrary data often has no compact recipe under any small grammar.
- Search may find numerically close values that are useless for lossless compression.
- Formula display strings can look small while binary serialization is not.
- Large constants can smuggle the original data into the recipe.
- Powerful operations can hide unbounded decoder cost.
- Baselines may beat generated recipes on nearly all natural files.

## Success Signal

The first meaningful success is not beating every compressor. It is a reproducible report like:

```text
input: synthetic quadratic byte pattern
segment_size: 16
recipe_bytes: 9
metadata_bytes: 5
zlib_bytes: 19
raw_bytes: 16
decode_exact: true
seed: 12345
grammar_version: 1
```

That kind of result would show the platform can detect a compact generative explanation when one exists.
