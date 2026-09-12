# GeneticCompression Docs

Start here after reading `AGENTS.md`.

## Snapshot

GeneticCompression explores whether evolved algebraic recipes can reproduce data
segments more compactly than storing raw bytes. The active implementation is the
Python harness in `genetic_compression/`; the original Java source is retained
unmodified under `legacy-java/` as historical reference.

The key risk has not changed: exact reconstruction is a hard constraint, while
expression search easily produces large, expensive recipes that do not actually
compress. The harness is built so that this shows up in the numbers rather than
being argued about -- real serialized bytes, real baselines, and a decode check
on every reported result.

## Current State

Implemented and tested in Python:

- unsigned byte/segment semantics with explicit lengths
- versioned grammar with hard evaluation limits
- immutable recipes and a search-independent decoder
- binary serialization with exact byte accounting
- raw, unsigned-integer, zlib, gzip, bz2, and lzma baselines
- bounded exhaustive search that distinguishes "not found in budget" from
  "not present within the enumerated bound"
- deterministic seeded genetic search
- hybrid generated-prediction plus compressed-residual experiments
- a reproducible experiment runner writing JSONL records

What the experiments say so far, on synthetic data at 16-byte segments: segments
that *are* a small power or a single shift beat every baseline; counters,
arithmetic and quadratic byte patterns, and random controls do not, and fall
back to literals. That is the expected shape of the result and is reported as
such.

## Current Priorities

1. Widen the exhaustive enumeration reach without losing the exhaustion proof.
2. Improve genetic search on structured-but-not-algebraic byte patterns, or
   document that the grammar is the limitation rather than the search.
3. Extend the hybrid experiments to larger segments where residual compression
   has room to pay for itself.

## Documentation Map

- `TODO.md`: active backlog and known restoration tasks.
- `SECURITY.md`: data, secrets, licensing, and publishing rules.
- `lessons-learned.md`: gotchas discovered from the codebase and the experiments.
- `architecture/current-codebase.md`: package-level analysis, the Java/Python
  byte-semantics comparison, and migration status.
- `architecture/genetic-compression-model.md`: proposed model for GA-based byte
  regeneration.
- `reference/build-and-run.md`: commands and current verification status.
- `reference/code-map.md`: source file map for both implementations.
- `plans/revival-roadmap.md`: staged plan for the original Java revival.
- `plans/python-conversion-plan.md`: the phased Python conversion plan.
- `plans/experiment-design.md`: reproducible experiment design for compression
  claims.
- `research/README.md`: open research questions.
