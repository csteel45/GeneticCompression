# AGENTS.md - GeneticCompression Repository Guidelines

Owner: Chris Steel / FortMoon Consulting, Inc.
Status: active
Last reviewed: 2026-09-12

This file is the single source of truth for coding assistants working in this repository. Agent-specific stubs such as `CLAUDE.md` should point here and avoid duplicating architecture, coding standards, or task workflow.

## Every Session Starts Here

1. Read this file first.
2. Read `docs/README.md` for the current project map, known issues, and priorities.
3. Check DevMem for relevant prior context when the local service is available; see "DevMem Workflow" below.
4. Open targeted docs under `docs/architecture/`, `docs/reference/`, `docs/plans/`, or `docs/research/` as needed.
5. Inspect the relevant source before changing behavior.
6. Update DevMem with useful decisions, artifacts, and task status as you go.
7. Run the narrowest useful verification available in the current environment and report anything that could not be run.

```
genetic_compression/   # active Python harness
tests/                 # Python tests
legacy-java/           # original Java/Maven project, unmodified
docs/
├── README.md
├── TODO.md
├── SECURITY.md
├── lessons-learned.md
├── architecture/
│   ├── README.md
│   ├── current-codebase.md
│   └── genetic-compression-model.md
├── reference/
│   ├── README.md
│   ├── build-and-run.md
│   └── code-map.md
├── plans/
│   ├── README.md
│   ├── revival-roadmap.md
│   ├── experiment-design.md
│   └── python-conversion-plan.md
└── research/
    └── README.md
```

## Project Overview

GeneticCompression is a research experiment that explores whether search can find a compact algebraic recipe that regenerates bytes from an input file. The intended compression artifact is not a traditional entropy-coded stream; it is a program-like representation whose decoder evaluates expressions to reproduce byte segments.

The repository has two implementations, and only one is active:

- **`genetic_compression/` (Python, active).** The research harness: byte model, grammar, recipes and decoder, binary serialization, baselines, staged fitness, exhaustive and genetic search, hybrid residual experiments, and a reproducible experiment runner. Standard library only. Tests in `tests/`.
- **`legacy-java/` (Java/Maven, historical).** The original 2015-2016 implementation, moved there unmodified. Two packages: `com.precognizant.genpress` (compression experiments, file/number conversion, ad hoc probes) and `com.precognizant.genetics` (a small genetic-programming engine). Nothing in the Python harness depends on it. Do not develop new behavior here; see `legacy-java/README.md`.

The original `data/` sample files are intentionally excluded because they contained private image data. Do not require private sample files for normal tests; every Python fixture is synthetic and generated.

## Current Technical State

This is exploratory legacy code, not a production compressor. Treat current behavior honestly:

- `Compress` and `FileUtils` convert file bytes into `BigInteger` segments.
- `Population`, `Chromosome`, and `Gene` search for sums of large powered constants whose value approaches a `BigInteger` goal.
- `NodeFactory`, `FunctionNode`, `ConstNode`, and `MathOperand` form an expression-tree layer, currently limited to plus, times, and power in the random factory.
- Several `main` methods are scratch probes rather than stable CLIs.
- Tests are sparse; `FileUtilsTest` is mostly placeholder coverage.
- Existing Surefire output in `target/surefire-reports/` shows `NumUtilsTest.testConvertToNumber` failing because the negative-number assertion expects an absolute value while `new BigInteger(byte[])` preserves sign.

## Genetic Compression Direction

Use genetic algorithms here as a search process over executable descriptions of data:

1. Segment input bytes into fixed-size chunks.
2. Convert each chunk into a canonical unsigned integer representation.
3. Evolve compact expression trees, instruction lists, or parameterized generators that reproduce each segment.
4. Score candidates by a multi-objective fitness function:
   - exact reconstruction error, with zero error mandatory for lossless compression
   - encoded recipe length
   - decoder cost and bounded runtime
   - robustness across repeated seeds
5. Store enough metadata to decode deterministically: segment size, signedness/byte-order policy, seed, grammar/version, constants, and expression encoding.

Compression claims require proof. A result is only interesting if `encoded_recipe_bytes + metadata_bytes < original_segment_bytes` and the decoder reconstructs bytes exactly on independent verification.

## DevMem Workflow

DevMem is a separate local development-memory service at `/home/csteel/python/devmem`. It provides a shared API for assistants to recall prior work and record current decisions without storing that memory in this repository.

Use it as a best-effort workflow aid:

- Before non-trivial work, check health with `/home/csteel/python/devmem/scripts/devmem_cli.py /v1/health --method GET`.
- If health is good, start a session using `namespace=devlib_v1`, `project=genetic-compression`, `repo=GeneticCompression`, and `agent=codex-cli`.
- Pull context with `/v1/context/pull`, `/v1/search/hybrid`, or `/v1/repo/search` when prior decisions or ingested source context could affect the task.
- During substantial work, commit useful artifacts and decisions through `/v1/sessions/commit` with a stable `client_commit_id`.
- Record decisions that affect byte semantics, recipe grammar, compression claims, experiment design, test strategy, migration direction, or repository workflow.
- Do not block ordinary work if DevMem is unavailable, unconfigured, or using degraded embeddings. Note the failure briefly and continue from local repo context.
- Do not commit private data, credentials, machine-local configuration, or excluded `data/` artifacts into DevMem.

## Architecture Guidelines

- Keep byte/integer conversion separate from evolutionary search.
- Define signedness and byte order explicitly before expanding experiments. Java `BigInteger(byte[])` is two's-complement signed; do not hide that behavior behind ambiguous helpers.
- Prefer immutable value objects for compression artifacts, segment metadata, and experiment results.
- Keep fitness deterministic for a fixed seed and input.
- Bound expression growth. Power operations can create enormous values and pathological runtimes.
- Avoid global mutable experiment state where practical. Current code has static and instance counters; new code should isolate state per run.
- Keep the module split in the Python harness: byte semantics, grammar, recipe/decoder, serialization, baselines, fitness, and search are separate and only depend downward. The decoder must never depend on a search.
- Preserve the legacy Java package split if that code is ever touched:
  - `genpress` owns compression domain concepts.
  - `genetics` owns generic GA/GP machinery.
- Do not turn scratch `main` methods into the primary interface. `genetic_compression.experiments` is the CLI.

## Coding Standards

Active development is Python:

- Language: Python 3.10+, standard library only.
- Test framework: `unittest`.
- Type hints on public functions; module docstrings that say *why*, not *what*.

The retained Java under `legacy-java/` is Java 8-era with Maven (`legacy-java/pom.xml`) and JUnit 4. Do not add behavior there.
- Keep formatting consistent with nearby code unless doing an intentional formatting-only pass.
- Use meaningful names for experimental parameters: `populationSize`, `segmentSize`, `maxDepth`, `maxGenerations`, `mutationRate`, `seed`.
- Do not add new external dependencies without a reason documented in `docs/TODO.md` or a plan. The Python harness has none by design.
- Avoid broad rewrites that obscure research behavior. First stabilize tests and data semantics, then refactor.
- Add or update tests whenever changing conversion, fitness, selection, mutation, serialization, or decoder behavior.

## Verification

Preferred local check, and the one that gates changes:

```bash
python -m unittest discover -s tests -t .
```

Useful targeted checks:

```bash
python -m unittest tests.test_codec
python -m genetic_compression.experiments --input-class shift --segment-size 16
```

Legacy Java, only when Maven is available:

```bash
mvn -f legacy-java/pom.xml test
```

If Maven is not installed, state that explicitly and use source inspection or any available compiled artifacts only as supporting evidence. Do not claim a clean build without running it.

## Security, Privacy, and IP

- Do not commit `data/`, private images, generated binary test artifacts, credentials, machine-local IDE caches, or experiment output (`*.jsonl`, `results/`).
- Keep public examples synthetic and small.
- Preserve MIT license headers and third-party attribution, including the BigDecimal square-root attribution in `legacy-java/.../genetics/core/Gene.java`.
- Do not make compression-performance claims without reproducible experiments and exact byte counts.

## Documentation Rules

- Keep `docs/README.md` as the navigation hub.
- Put stable design explanations under `docs/architecture/`.
- Put commands, package maps, and operational notes under `docs/reference/`.
- Put future work and step-by-step execution plans under `docs/plans/`.
- Put open research questions and literature notes under `docs/research/`.
- Update `docs/TODO.md` when adding, discovering, or completing restoration work.
