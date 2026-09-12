# legacy-java

The original Java/Maven implementation of GeneticCompression (2015–2016),
retained unmodified as historical reference. **It is not the active research
path** — that is the Python harness at the repository root. See
[`../docs/architecture/current-codebase.md`](../docs/architecture/current-codebase.md)
for what the Python harness replaces and how the two differ.

Nothing here is imported, invoked, or tested by the Python harness. The source
moved from the repository root in 2026 with no edits; every path inside this
directory is unchanged and relative to it, so Maven and Eclipse treat
`legacy-java/` as the project root.

## Contents

- `pom.xml` — Maven build. `maven-compiler-plugin` has empty `source`/`target`
  values, which is likely to need cleanup on a modern JDK.
- `src/main/java/com/precognizant/genpress/` — compression experiments, file and
  number conversion, and ad hoc `main` probes.
- `src/main/java/com/precognizant/genetics/` — the small genetic-programming
  engine: populations, chromosomes, genes, expression nodes, operands.
- `src/test/com/precognizant/genpress/` — two JUnit 4 tests, one of them failing.
- `.classpath`, `.project`, `.settings/` — Eclipse metadata.
- `target/` — stale build output from a 2023 run, kept only for the Surefire
  reports referenced in the docs. Not in version control.

## Building

```bash
mvn -f legacy-java/pom.xml test    # from the repository root
cd legacy-java && mvn test         # or from here
```

Maven is not installed in the current development environment, so no Java
verification has been run there and none is claimed.

## Known issues

Carried over unfixed; see `../docs/architecture/current-codebase.md` and
`../docs/TODO.md`.

- `NumUtilsTest.testConvertToNumber` fails. `new BigInteger(byte[])` is
  two's-complement signed, so a segment whose first byte is `>= 0x80` becomes
  negative, while the test asserts an absolute value. The Python harness settled
  this question in favour of unsigned big-endian semantics with an explicit
  segment length.
- `Compress.main` and `FileUtils.main` depend on `./data/laxguys.jpg`, which is
  intentionally absent from the repository.
- `Gene.toString()` recurses into itself.
- `Rand.init(long)` ignores the supplied seed and uses the current time.
- `MathOperand.POWER` can request unbounded exponentiation.
- `Chromosome.getFitness()` casts a `BigInteger` to `Fitness`.

## Licensing

MIT, same as the rest of the repository. The `BigDecimal` square-root helper in
`src/main/java/com/precognizant/genetics/core/Gene.java` is adapted from a
CodeProject tip by **Luciano Culacciatti** and is attributed in-source with the
original URL. Preserve that attribution if the helper is moved or rewritten.
