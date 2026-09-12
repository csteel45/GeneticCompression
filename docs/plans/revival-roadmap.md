# Revival Roadmap

> **Superseded.** This was the plan for reviving the Java implementation in
> place. It was overtaken by `python-conversion-plan.md`, which rebuilt the
> project in Python; the Java source now sits unmodified under `legacy-java/`.
> Kept for the record, because the phase ordering below (byte semantics before
> search, artifacts before evaluation) is what the Python conversion actually
> followed. Commands here predate the move and would need
> `-f legacy-java/pom.xml`.

## Phase 1: Make the Project Buildable

- Install Maven or add a documented wrapper.
- Set explicit Java source/target levels in `pom.xml`.
- Run `mvn test` and fix compile/test failures.
- Remove reliance on missing `data/` files from automated checks.

## Phase 2: Lock Down Byte Semantics

- Decide unsigned segment representation.
- Implement tested `bytesToNumber` and `numberToBytes` helpers.
- Preserve original segment length for exact reconstruction.
- Add fixtures covering leading zeros, high-bit bytes, empty input, and odd segment lengths.

## Phase 3: Stabilize the GA Engine

- Make seeds reproducible.
- Fix recursive/string and fitness type issues.
- Add limits for exponentiation, expression size, and evaluation time.
- Record generation metrics.

## Phase 4: Define Compression Artifacts

- Create a recipe model with versioned serialization.
- Implement a decoder independent of the evolutionary search.
- Add end-to-end tests for compress/decode on tiny synthetic byte arrays.

## Phase 5: Research Evaluation

- Compare against raw and gzip baselines.
- Run multiple seeds per dataset.
- Report exact byte counts and failures.
- Keep claims modest unless results are reproducible.

