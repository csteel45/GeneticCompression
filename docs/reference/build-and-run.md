# Build and Run

The Python research harness is the active development path. The Java project is
retained as historical reference; see `docs/plans/python-conversion-plan.md`.

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

### Requirements

- JDK compatible with the legacy Maven project.
- Maven.

The `pom.xml` currently has empty `source` and `target` values in
`maven-compiler-plugin`; expect this to need cleanup on modern Maven/JDK
combinations.

### Commands

Run all tests:

```bash
mvn test
```

Run a specific JUnit 4 test:

```bash
mvn -Dtest=NumUtilsTest test
mvn -Dtest=FileUtilsTest test
```

The README mentions:

```bash
mvn install
mvn exec:java
```

There is no `exec-maven-plugin` configuration yet, and several `main` methods
depend on missing `data/` files, so treat those commands as historical until
refreshed.

## Verification Status on 2026-09-11

In the current agent shell, `mvn test` could not be run because `mvn` is not
installed. Java verification has not been performed in this environment.

Existing checked workspace artifacts under `target/surefire-reports/` show:

- `FileUtilsTest`: 3 tests run, 0 failures.
- `NumUtilsTest`: 2 tests run, 1 failure in `testConvertToNumber`.

Python verification is run with the `python -m unittest discover -s tests -t .`
command above.
