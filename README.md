# Genetic Compression

An experiment: use a genetic algorithm to evolve a compact **algebraic expression that
regenerates a file's bytes** — a novelty "compressor" that stores the recipe rather than
the data. Reuses the genetic-programming engine from the companion *Genetics* project.

## Build & run
```bash
mvn install
mvn exec:java
```

## Notes
- The `BigDecimal` square-root helper in `core/Gene.java` is adapted from a CodeProject
  tip by **Luciano Culacciatti** (attributed in-source with the original URL).
- The original `data/` directory (sample inputs) is intentionally excluded from this
  repository.

## History & scope

A personal research experiment built in 2015–2016 (see the commit history), reusing the
genetic-programming engine from the companion *Genetics* project. It evolves a compact
algebraic expression that regenerates a file's bytes — storing the *recipe* rather than
the data — as an exploration of whether evolutionary search can discover such encodings.

## License
MIT (own code) — see [LICENSE](LICENSE).
