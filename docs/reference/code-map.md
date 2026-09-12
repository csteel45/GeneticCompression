# Code Map

## Python Harness (active)

- `genetic_compression/bytes_model.py`: unsigned big-endian segment conversion, segment splitting, and the documented legacy Java comparison.
- `genetic_compression/grammar.py`: grammar version, opcode table, and `Limits`.
- `genetic_compression/recipe.py`: `Const`/`Literal`/`BinOp` nodes, `Recipe`, evaluation with limits, decoder, and verification.
- `genetic_compression/codec.py`: varints, preorder expression stream, recipe container, and `encoded_size`/`size_breakdown`.
- `genetic_compression/baselines.py`: baseline sizes and the stream codecs reused as residual encoders.
- `genetic_compression/fitness.py`: `FitnessScore` and the staged sort key.
- `genetic_compression/hybrid.py`: hybrid artifact, wire format, structured probes, and generator pool.
- `genetic_compression/experiments.py`: synthetic datasets, `TrialSpec`, `run_trial`, and the CLI.
- `genetic_compression/search/__init__.py`: `SearchStatus` and `SearchResult`.
- `genetic_compression/search/exhaustive.py`: bounded enumeration and the fallback recipe.
- `genetic_compression/search/genetic.py`: GA configuration, tree operators, `search`, and `propose_generators`.

### Python Tests

- `tests/test_bytes_model.py`, `tests/test_recipe.py`, `tests/test_codec.py`,
  `tests/test_baselines.py`, `tests/test_fitness.py`,
  `tests/test_exhaustive_search.py`, `tests/test_genetic_search.py`,
  `tests/test_hybrid.py`, `tests/test_experiments.py`.

## Java (legacy, retained unmodified)

The whole Maven project lives under `legacy-java/`: `pom.xml`, `src/`, the
Eclipse metadata, and the stale `target/` build output. Paths below are relative
to `legacy-java/src/main/java/com/precognizant/`.

### Compression Package (`genpress`)

- `genpress/Compress.java`: file segmentation and byte/number conversion probe.
- `genpress/FileUtils.java`: static file segmentation utilities.
- `genpress/NumUtils.java`: `BigInteger` conversion and integer square-root utilities.
- `genpress/Algo.java`: early operation-list experiment.
- `genpress/FunctionEnvironment.java`: thread-based population runner.
- `genpress/BigSquareRoot.java`: square-root exploration.
- `genpress/TestSquare.java`: scratch numeric probe.

### Genetic Programming Package (`genetics`)

- `genetics/core/Population.java`: population lifecycle, crossover, mutation, and fittest selection.
- `genetics/core/Chromosome.java`: list of genes scored against a `BigInteger` goal.
- `genetics/core/Gene.java`: generates a powered constant and stores its result.
- `genetics/core/Fitness.java`, `Goal.java`, `Environment.java`: early interfaces/markers.
- `genetics/node/BaseNode.java`, `ConstNode.java`, `FunctionNode.java`, `Node.java`, `NodeFactory.java`, `NodeTree.java`: expression-tree model.
- `genetics/operand/MathOperand.java`, `Operand.java`: math operation abstraction.
- `genetics/data/TestData.java`: simple input/output data holder.
- `genetics/util/Rand.java`, `Log.java`, `DataGenerator.java`: support utilities.

### Java Tests

Under `legacy-java/src/test/com/precognizant/genpress/`:

- `FileUtilsTest.java`: placeholder tests.
- `NumUtilsTest.java`: conversion test with a known failing negative-number expectation.
