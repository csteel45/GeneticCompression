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

## License
MIT (own code) — see [LICENSE](LICENSE).
