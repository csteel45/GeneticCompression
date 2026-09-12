# Build and Run

The Python research harness is the active development path and lives at the
repository root. The Java project is retained as historical reference under
`legacy-java/`; see `docs/plans/python-conversion-plan.md`.

## Python Harness

### Requirements

- Python 3.10 or newer (developed against 3.12).
- Standard library only. There are no runtime dependencies.

### Commands

Run the test suite:

```bash
python -m unittest discover -s tests -t .
```

Run a single test module or case:

```bash
python -m unittest tests.test_bytes_model
python -m unittest tests.test_codec.RoundTripTest
```

Optional editable install (only needed for the `genetic-compression` console
script; the package imports fine from the repository root without it):

```bash
python -m pip install -e .
```

Run an experiment:

```bash
python -m genetic_compression.experiments --help
```

## Java (legacy)

The Maven project now lives under `legacy-java/`. Every path inside it
(`pom.xml`, `src/main/java`, `src/test`, `target/`) is unchanged and relative to
that directory, so Maven and Eclipse treat `legacy-java/` as the project root.

### Requirements

- JDK compatible with the legacy Maven project.
- Maven.

The `pom.xml` still has empty `source` and `target` values in
`maven-compiler-plugin`; expect this to need cleanup on modern Maven/JDK
combinations.

### Commands

Run from the repository root with `-f`:

```bash
mvn -f legacy-java/pom.xml test
mvn -f legacy-java/pom.xml -Dtest=NumUtilsTest test
mvn -f legacy-java/pom.xml -Dtest=FileUtilsTest test
```

Or from inside the project directory:

```bash
cd legacy-java && mvn test
```

The old README mentioned `mvn install` and `mvn exec:java`. There is no
`exec-maven-plugin` configuration, and several `main` methods depend on missing
`data/` files, so treat those commands as historical until refreshed.

## Verification Status on 2026-09-11

In the current agent shell, `mvn test` could not be run because `mvn` is not
installed. Java verification has not been performed in this environment.

Existing checked workspace artifacts under `legacy-java/target/surefire-reports/`
show (from a 2023 run, before the move):

- `FileUtilsTest`: 3 tests run, 0 failures.
- `NumUtilsTest`: 2 tests run, 1 failure in `testConvertToNumber`.

Python verification is run with the `python -m unittest discover -s tests -t .`
command above.
