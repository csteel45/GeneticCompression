# Genetic Compression Model

## Goal

Find a compact executable recipe that regenerates an input byte segment exactly. The recipe only counts as compression when its serialized size plus required metadata is smaller than the raw segment.

## Candidate Representation

Reasonable candidate grammars include:

- expression trees over constants and operations such as add, subtract, multiply, shift, xor, modular arithmetic, and bounded power
- instruction lists for a tiny deterministic virtual machine
- seeded generators with evolved parameters
- mixed strategies where difficult residual bytes are stored literally

The current code is closest to expression-tree genetic programming.

## Fitness

Use a staged fitness function:

1. Reconstruction error: distance from decoded bytes to target bytes. Exact equality is mandatory for lossless success.
2. Recipe size: serialized byte length of constants, opcodes, metadata, and literals.
3. Decode cost: number of operations, maximum intermediate size, and wall-clock/runtime budget.
4. Stability: repeated success under recorded seeds and bounded generations.

For exact compression experiments, never let a smaller-but-wrong candidate outrank an exact candidate in final reporting.

## Decoder Metadata

Each compressed artifact needs:

- format version
- segment size
- original length
- byte order
- signedness policy
- recipe grammar version
- constants/opcodes
- random seed only if the decoder intentionally uses deterministic generation

## Research Hypothesis

Genetic search is unlikely to beat mature compressors on arbitrary high-entropy data. It may be useful for data with hidden generative structure, repeated numerical patterns, or segments where a short algebraic generator plus a small residual can exactly reproduce the bytes.

