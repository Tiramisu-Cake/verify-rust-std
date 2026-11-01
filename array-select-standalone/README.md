# ARRAYREPRO: standalone array selection diagnostics

PRE-BUILD REVIEW: prepared locally; no Kani build, proof, push or dispatch has run.
The coordinator must issue GO before the first push of this branch. That push
is the one authorized matrix run (two jobs). Do not also dispatch it. A rerun
requires an infrastructure failure and a new GO.

This isolated, unpublished crate uses the sysroot built by each Kani revision,
not this repository's modified std. The root toolchain and library stay untouched.
D1/D2/F2/F5/F7 copy the function bodies from `experiment/kani-k1-arrayfactor-20261101`,
`library/core/src/slice/sort/shared/smallsort/verify/merge/casefive.rs`.
Reference observations: CASE5-2 and A1 ARRAYFACTOR in that branch's
`research/challenge-8/kani-k1/RESULT-CASEFIVE.md`, and its `arrayfactor/` reproducer.
These in-tree observations are context, not standalone results.

| Row | Exact harness (`check::` prefix) | Covers |
|---|---|---|
| D1 | `casefive_d1_select_read_bytes1` | 2 branch/value-difference covers |
| D2 | `casefive_d2_select_read_u8` | 2; mandatory scalar control |
| F2 | `arrayfactor_f2_if_bytes1` | 2; explicit `if` |
| F5 | `arrayfactor_f5_symbolic_indices_bytes1` | 4; symbolic index order |
| F7 | `arrayfactor_f7_witness_bytes1` | 2; x=[1], y=[2], branch asserts |
| W | `arrayrepro_w_observed_bytes1` | 2; independent observation experiment |
| C-other | `arrayrepro_cover_other_element_bytes1` | 1; c && x!=y && got==y |
| C-neither | `arrayrepro_cover_neither_element_bytes1` | 1; c && x!=y && got!=x && got!=y |

All covers precede assertions. Every check message is a unique literal.
Each classifying cover is isolated because terse output only gives aggregate counts.
W adds `observed: u8 = kani::any(); kani::assume(observed == got[0]);`
before the unchanged value oracle. Compare W's value-check failure with D1 before
using its witness. W is never reported as D1. Playback exports `any` inputs;
D1 playback alone does not print `got`. W's fourth input is `observed` (after x, y, c).
Treat an observation as evidence for this instrumented W configuration only.

## Frozen versions and commands (execute only after GO)

Pin: `9461e07af7ec929f050aa4192f29363c9be07779`, nightly-2026-10-12.
Main snapshot: `744b3e84d6eb68fd5456826997568666791bd355`, nightly-2026-10-23.
Main HEAD was checked with `git ls-remote` on 2026-11-01 before GO; both
`rust-toolchain.toml` files were read at their full upstream SHA.
The workflow builds each exact revision from source following K-5 and records
actual Kani/rustc/CBMC versions. It uses the built `scripts/cargo-kani` directly.
It exports that revision's `RUSTUP_TOOLCHAIN` for execution from the crate.
The same crate source is used for both jobs.

With `KANI_ROOT` an absolute path to that source build, and `KANI_TOOLCHAIN`
read from its `rust-toolchain.toml`, the D1 solver pair is:

```sh
cd array-select-standalone
export RUSTUP_TOOLCHAIN="$KANI_TOOLCHAIN"
timeout --verbose --kill-after=10s 300s "$KANI_ROOT/scripts/cargo-kani" \
  --harness check::casefive_d1_select_read_bytes1 --exact \
  --output-format=terse --solver cadical --harness-timeout 3m --jobs=1
timeout --verbose --kill-after=10s 300s "$KANI_ROOT/scripts/cargo-kani" \
  --harness check::casefive_d1_select_read_bytes1 --exact \
  --output-format=terse --solver minisat --harness-timeout 3m --jobs=1
```

Every other harness runs with the cadical command, substituting its exact name.
D1 and W playback are separate sequential experiments:

```sh
timeout --verbose --kill-after=10s 300s "$KANI_ROOT/scripts/cargo-kani" \
  -Z concrete-playback --concrete-playback=print \
  --harness check::casefive_d1_select_read_bytes1 --exact \
  --output-format=terse --solver cadical --harness-timeout 3m --jobs=1
timeout --verbose --kill-after=10s 300s "$KANI_ROOT/scripts/cargo-kani" \
  -Z concrete-playback --concrete-playback=print \
  --harness check::arrayrepro_w_observed_bytes1 --exact \
  --output-format=terse --solver cadical --harness-timeout 3m --jobs=1
```

CI checks CLI help/support, preserves commands, rc and full outputs as artifacts,
and emits parsed per-experiment outcomes in the job summary. CLI/backend errors,
unsupported options, timeouts and missing outcome lines remain explicit.
A green job means report collection completed, not that proofs succeeded.
Read `out/` artifacts for full playback input vectors; do not infer `got` from D1.

The final root `ARRAYREPRO-RESULT.md` will be filled after the authorized run
(40 lines maximum). If main passes, say "не воспроизводится в указанной
конфигурации main". A standalone PASS cannot override an in-tree FAILED or
establish which compiler/model/backend component caused the earlier observation.
Use `[skip ci]` for the final report commit; the push workflow also filters paths
so a root-only report does not trigger another run. No external issue/publication.
