# TODO

## Nightly lane queue

One unchecked item = one night's order for Chrysalis's project-work lane; it
ticks the box when the work lands. Each item is one experiment or one harness
change, with a JSONL record and a paragraph in `docs/research/README.md` as the
deliverable. Sized to land in one session with the tests green
(`python -m pytest -q`, 192 tests).

- [ ] File-level driver: `python -m genetic_compression.filedriver <path> --segment-size N --algorithm all` segments a real input, runs the harness per segment, and reports whole-file totals (raw, zlib baseline, recipe bytes, hybrid) as one JSONL summary record plus a table on stdout. Tests on a synthetic file.
- [ ] Target-directed inversion for the invertible operations, so the exhaustive enumerator reaches seven-byte expressions without giving up the "proven impossible within the bound" claim; record the bound reached and the wall time per segment size in `docs/research/README.md`.
- [ ] Experiment: genetic search on counters and quadratics (structured-but-not-algebraic) at segment sizes 8/16/32 — report whether the grammar or the search is the limit, with the JSONL evidence and a short conclusion in `docs/research/README.md`.
- [ ] Experiment: hybrid mode at segment sizes 64/128/256 on the shift and counter input classes, to find where residual compression pays for the container overhead; JSONL + a results paragraph.
- [ ] Residual codec for near-zero residuals (a run-length or bit-packed path that beats zlib's ~11-byte floor on tiny residuals), selected automatically when smaller; tests prove the selection and the round trip.
- [ ] Segment clustering experiment: score segments for "looks structured" before searching, and measure whether skipping unstructured segments pays for the metadata; JSONL + conclusion.
- [ ] Real-data survey: run the file-level driver over three real inputs of different classes (a text file, a PNG, an executable) and record which, if any, contain segment-aligned generative structure; conclusion in `docs/research/README.md`.


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
