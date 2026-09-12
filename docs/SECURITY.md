# Security and Data Handling

This repository should remain safe to publish.

## Do Not Commit

- `data/` contents or other private sample files.
- Generated outputs that reconstruct private input data.
- Credentials, tokens, machine-local configuration, or IDE state.
- Large binary artifacts produced by experiments.

## Test Data

Use synthetic deterministic byte arrays in tests. If realistic data is needed, prefer tiny generated fixtures whose contents are fully documented in source.

## Licensing and Attribution

The project is MIT licensed. Keep existing copyright and SPDX headers when editing source files.

The BigDecimal square-root helper is attributed in source to Luciano Culacciatti. Preserve that attribution if the helper is moved or rewritten.

## Research Claims

Do not publish compression-ratio claims unless the experiment includes:

- exact reconstruction verification
- byte counts for original, recipe, metadata, and decoder assumptions
- fixed seeds or recorded seeds
- baseline comparisons
- runtime limits and failure cases

