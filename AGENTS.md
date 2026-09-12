# AGENTS.md - GeneticCompression Repository Guidelines

Owner: Chris Steel / FortMoon Consulting, Inc.
Status: active
Last reviewed: 2026-09-11

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

GeneticCompression is a Java/Maven research experiment that explores whether a genetic-programming system can evolve a compact algebraic recipe that regenerates bytes from an input file. The intended compression artifact is not a traditional entropy-coded stream; it is a program-like representation whose decoder evaluates expressions to reproduce byte segments.

The repository has two related packages:

- `com.precognizant.genpress`: compression experiments, file/number conversion, utilities, and ad hoc executable probes.
- `com.precognizant.genetics`: a small genetic-programming engine with populations, chromosomes, genes, expression nodes, operands, randomness, and support utilities.

The original `data/` sample files are intentionally excluded because they contained private image data. Do not require private sample files for normal tests.

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
- Preserve the package split unless there is a clear migration plan:
  - `genpress` owns compression domain concepts.
  - `genetics` owns generic GA/GP machinery.
- Do not turn scratch `main` methods into the primary interface. Add a clear CLI or tests when behavior becomes stable.

## Coding Standards

- Language: Java.
- Build system: Maven (`pom.xml`).
- Test framework: JUnit 4.
- Keep formatting consistent with nearby code unless doing an intentional formatting-only pass.
- Use meaningful names for experimental parameters: `populationSize`, `segmentSize`, `maxDepth`, `maxGenerations`, `mutationRate`, `seed`.
- Do not add new external dependencies without a reason documented in `docs/TODO.md` or a plan.
- Avoid broad rewrites that obscure research behavior. First stabilize tests and data semantics, then refactor.
- Add or update tests whenever changing conversion, fitness, selection, mutation, serialization, or decoder behavior.

## Verification

Preferred local checks when Maven is available:

```bash
mvn test
```

Useful targeted checks:

```bash
mvn -Dtest=NumUtilsTest test
mvn -Dtest=FileUtilsTest test
```

If Maven is not installed, state that explicitly and use source inspection or any available compiled artifacts only as supporting evidence. Do not claim a clean build without running it.

## Security, Privacy, and IP

- Do not commit `data/`, private images, generated binary test artifacts, credentials, or machine-local IDE caches.
- Keep public examples synthetic and small.
- Preserve MIT license headers and third-party attribution, including the BigDecimal square-root attribution.
- Do not make compression-performance claims without reproducible experiments and exact byte counts.

## Documentation Rules

- Keep `docs/README.md` as the navigation hub.
- Put stable design explanations under `docs/architecture/`.
- Put commands, package maps, and operational notes under `docs/reference/`.
- Put future work and step-by-step execution plans under `docs/plans/`.
- Put open research questions and literature notes under `docs/research/`.
- Update `docs/TODO.md` when adding, discovering, or completing restoration work.
