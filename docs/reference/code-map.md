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

## Compression Package

- `src/main/java/com/precognizant/genpress/Compress.java`: file segmentation and byte/number conversion probe.
- `src/main/java/com/precognizant/genpress/FileUtils.java`: static file segmentation utilities.
- `src/main/java/com/precognizant/genpress/NumUtils.java`: `BigInteger` conversion and integer square-root utilities.
- `src/main/java/com/precognizant/genpress/Algo.java`: early operation-list experiment.
- `src/main/java/com/precognizant/genpress/FunctionEnvironment.java`: thread-based population runner.
- `src/main/java/com/precognizant/genpress/BigSquareRoot.java`: square-root exploration.
- `src/main/java/com/precognizant/genpress/TestSquare.java`: scratch numeric probe.

## Genetic Programming Package

- `core/Population.java`: population lifecycle, crossover, mutation, and fittest selection.
- `core/Chromosome.java`: list of genes scored against a `BigInteger` goal.
- `core/Gene.java`: currently generates a powered constant and stores its result.
- `core/Fitness.java`, `core/Goal.java`, `core/Environment.java`: early interfaces/markers.
- `node/BaseNode.java`, `node/ConstNode.java`, `node/FunctionNode.java`, `node/Node.java`, `node/NodeFactory.java`, `node/NodeTree.java`: expression-tree model.
- `operand/MathOperand.java`, `operand/Operand.java`: math operation abstraction.
- `data/TestData.java`: simple input/output data holder.
- `util/Rand.java`, `util/Log.java`, `util/DataGenerator.java`: support utilities.

## Tests

- `src/test/com/precognizant/genpress/FileUtilsTest.java`: placeholder tests.
- `src/test/com/precognizant/genpress/NumUtilsTest.java`: conversion test with a known failing negative-number expectation.

