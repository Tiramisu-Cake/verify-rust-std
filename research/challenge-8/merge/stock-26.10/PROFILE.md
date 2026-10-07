# Stock VeriFast 26.10 recheck profile

This copied harness targets the actual SmallSort bytes in upstream commit
`cd371e035c7e573760c43bf934d53e8118ee3e7d` (full source SHA-256
`85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`) using
the official stock VeriFast 26.10 archive from source commit
`f76012fb518703b1d98e243ac4f487f16877cfcb` and Rust
`nightly-2026-09-25` with only `rustc-dev` and `rust-src` added to the minimal
profile. `run.sh` checks the archive, console, exporter, refinement checker,
schema, and all 58 extracted `.rsspec`, `.gh`, and `.h` files against fixed
SHA-256 pins before running any proof.

The archive's complete 58-file tool-spec manifest is
[`vf-stock-specs.json`](vf-stock-specs.json), pinned at
`4a0911303bbb087f1f50ce85524197edbb541f31c72e8133dfbcc9cf528e03a0`.
Read-only comparison against source commit `f76012fb518703b1d98e243ac4f487f16877cfcb`
found all 58 extracted specs identical to the source tree, including all 17
Rust `.rsspec` files. Parser/schema and Rust frontend source hashes are recorded
in [`vf-profile-source.json`](vf-profile-source.json).

The copied admission harness keeps the previously accepted network rejection
classifier loaded from `research/challenge-8/networks/prove.py` with its
original SHA pin. G2/A/B proof bodies and all target preconditions/full normal
and unwind posts are copied intact. Only source admission hash/coordinates,
tool profile metadata, and harness import paths are adapted in these copies.

The Rust fixture contains the nine accepted projections, the exact
`wrong_cursor` and `address_index` negative controls, and two isolated generic
`wrapping_sub`/`wrapping_add` true-post probes. The earlier `wrapping_reentry`
and `wrapped_read` drafts are excluded. Selected cases use only the file-level
comment prefix, so neither support probe becomes a helper for another case.
