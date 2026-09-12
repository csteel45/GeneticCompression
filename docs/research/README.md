# Research Notes

## Core Question

Can evolutionary search discover an exact, compact generative description of byte segments often enough to be useful as compression?

## Promising Angles

- Hybrid recipes: evolved expression plus literal residual bytes.
- Grammars with bitwise operations, shifts, masks, and modular arithmetic instead of only arithmetic growth.
- Segment clustering: apply search only to segments that appear structured.
- Minimum description length scoring: penalize large constants and verbose expression trees.
- Deterministic seeded generators: evolve parameters for small generators while storing failures literally.

## Likely Limits

Arbitrary compressed or encrypted data should behave like high-entropy noise. Genetic search should not be expected to compress those segments. The useful target is structured data where a short program-like representation exists but is not obvious to hand-written compressors.

