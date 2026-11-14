# Docs scope map — prepared, uncommitted

- rust-feature-support.md#uninitialized-memory: accepted Scope A storage shapes, masks,
  raw copies, typed data bytes, MIR-body calls, qualified whole immutable origins.
  General limits apply to ordinary harnesses too; narrow origin qualification permits
  eligible alias/static successes, and unqualified paths may conservatively fail.
- reference/experimental/contracts.md#limitations: links general scope; preserves Replace /
  RecursiveCheck exclusions, delayed call cycles, nested reset false-positive example.
  Companion proof presence is not proof execution.
- rust-feature-support/intrinsics.md raw_eq: modeled byte extents/shadow, padding obligation,
  layout/origin qualification, corrected relative link to general section.
- Exact required smallsort exclusion sentence retained. No SEL1/all-T,N/B2 claims.

Native doc build NOT_RUN; local links checked statically at closeout. No accepted freeze.
