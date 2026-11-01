# Local minimal reproducer package (no external publication)

`reproducer.rs` copies the existing D1/D2 functions verbatim, with the module's imports.
D1 is the array read reproducer; D2 is its scalar control. The package is a verify-std core
module fragment, not a standalone cargo project. The authoritative executable copies remain
in `library/core/src/slice/sort/shared/smallsort/verify/merge/casefive.rs`, reached through the
existing `#[cfg(kani_smallsort_controls)] mod casefive;` declaration. No package proof was run
locally and no result for another context is inferred from this extracted fragment.

Base: CASE5-2 result `a1e56b61cd`; task/base `db9583a0b9`.
Library: `56387d72342b9f3bd6fd17c919130a412639bde4` (D1/D2 unchanged).
Kani: `9461e07af7ec929f050aa4192f29363c9be07779`.
Toolchain: `nightly-2026-10-12`.
Environment: `RUSTFLAGS="--cfg kani_smallsort_controls"`.
Backend: existing K-1 lane, gcb-e2-standard-4, single Kani job, uninit checks off.
Harness attributes: `#[kani::proof]`, `#[kani::unwind(180)]` on both rows.

Exact selected-harness invocation for the two controls, expanded from the unchanged
`scripts/run-kani.sh` and request validator (run only within the authorized Cloud lane;
shown for reproducibility, not additional build authorization):

```sh
kani_build/scripts/kani verify-std -Z unstable-options ./library \
  -Z function-contracts -Z mem-predicates -Z float-lib -Z c-ffi \
  -Z loop-contracts -Z quantifiers -Z stubbing --no-assert-contracts \
  --harness slice::sort::shared::smallsort::verify::merge::casefive::casefive_d1_select_read_bytes1 \
  --harness slice::sort::shared::smallsort::verify::merge::casefive::casefive_d2_select_read_u8 \
  --exact --harness-timeout 3m --jobs=1 --output-format=terse \
  --cbmc-args --object-bits 12
```

The one authorized ARRAYFACTOR build includes F2–F7 too: exact request `a1.request.json`,
generated additional CLI arguments `a1.args.txt`, environment `a1.rustflags.txt`.
No pin/flags/timeout change or local proof is part of this package. A1 ran the authoritative
in-tree D1/D2 on head `0a2764a562`: D1 FAILED on `casefive D1: read through the selection`,
D2 SUCCESS, both covers satisfied in each. Build `cc350da7-7c1a-4acf-abc0-6ee6eda702ad`;
bounded evidence `a1.summary.md`, `a1.rows.txt`, `a1.tooling.txt`. These repeat the CASE5-2
observation; this extracted fragment was not separately compiled or run in a different context.
F7 also reproduces with x=[1], y=[2]: only c=true's first-selected check fails. It does not
print the wrong byte. F5's symbolic index order suppresses the failure in this fixture.
