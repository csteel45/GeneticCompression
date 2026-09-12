# TODO

## Java Migration Decision

**Resolved.** The Java source moved unmodified to `legacy-java/`. It was not
deleted and not reduced to a Git tag, because the Java byte semantics are the
reference the Python model was designed against and that comparison should stay
inspectable in the working tree. See
`architecture/current-codebase.md` for the reasoning and
`../legacy-java/README.md` for the directory's own notes.

`Compression.eap` and `Compression.ldb` (the Enterprise Architect model of the
Java design) moved with it.

Remaining, low priority:

- Decide whether to untrack `Compression.eap` / `Compression.ldb`. They are
  tracked despite `.gitignore` listing `*.eap` and `*.ldb`, because the patterns
  were added after the files were committed. Untracking them would remove the
  design model from the working tree of a fresh clone.
- Consider whether `legacy-java/target/` should be deleted outright. It is stale
  2023 build output, ignored by Git, kept only because the docs cite its Surefire
  reports.

## Java Build and Test Confidence

Only relevant while the Java source is retained. All commands now need
`-f legacy-java/pom.xml` or a `cd legacy-java` first.

- Install or configure Maven in the development environment used by agents.
  `mvn` is not installed in the current agent shell, so no Java verification has
  been run there, either before or after the move.
- Fix or clarify `NumUtilsTest.testConvertToNumber`. The disagreement is now
  documented: the helper preserves negative `BigInteger` values while the first
  assertion expects an absolute value. The Python harness settled the underlying
  question in favor of unsigned semantics.
- Replace empty placeholder tests in `FileUtilsTest` with small synthetic
  fixtures.

## Python Harness

- Widen the exhaustive enumeration past six-byte expressions without giving up
  the "proven impossible within the enumerated bound" claim. Target-directed
  inversion for the invertible operations is the obvious next step.
- Improve genetic search on structured-but-not-algebraic byte patterns
  (counters, quadratics), or establish that the grammar rather than the search
  is the limitation.
- Run hybrid experiments at larger segment sizes, where residual compression has
  room to pay for the container overhead.
- Consider a residual codec that handles a near-zero residual cheaply; zlib's
  floor of about eleven bytes currently dominates small hybrid artifacts.
- Add a file-level driver that segments a real input and reports whole-file
  totals, not just per-segment ones.

## Research Questions Still Open

- Which real data classes, if any, contain segment-aligned generative structure?
- Does segment clustering (searching only segments that look structured) pay for
  the metadata it costs?
