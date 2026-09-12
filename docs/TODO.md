# TODO

## Java Migration Decision

The Python harness now covers every phase of `plans/python-conversion-plan.md`,
so the open question is what happens to `src/`. Options, unchanged from the plan:

- keep it in place (current state)
- move it to `legacy-java/`
- keep it only as a Git tag
- delete it after an archival release

Nothing should be deleted until this is decided deliberately. See
`architecture/current-codebase.md` for what the Python harness replaces.

## Java Build and Test Confidence

Only relevant while the Java source is retained.

- Install or configure Maven in the development environment used by agents.
  `mvn` is not installed in the current agent shell, so no Java verification has
  been run there.
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
