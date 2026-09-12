# Experiment Design

## Minimal Reproducible Trial

Input:

- synthetic byte arrays from 1 to 256 bytes
- deterministic generated patterns
- fixed random-like arrays as negative controls

Recorded parameters:

- segment size
- population size
- mutation rate
- max generations
- expression grammar version
- seed
- timeout

Outputs:

- best candidate expression or recipe
- reconstruction status
- original byte count
- recipe byte count
- metadata byte count
- decode runtime
- fitness curve summary

## Success Criteria

A trial succeeds only when:

- decoded bytes exactly equal input bytes
- recipe plus metadata is smaller than the original segment
- decode completes within the configured bound
- the result can be reproduced from recorded parameters

## Baselines

Compare against:

- raw bytes
- gzip/deflate
- simple literal-plus-residual encoding
- trivial numeric encodings using `BigInteger.toByteArray()`

## Reporting

Report successes and failures together. Failed searches are useful evidence about which data classes do not benefit from this method.

