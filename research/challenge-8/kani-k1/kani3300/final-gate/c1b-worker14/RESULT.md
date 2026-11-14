# Worker14 C1b — checkout-independent JSON oracles

READY `3f2c12f46e9e32899e8d84e89c65cb6483ba685a`

Local clone `/root/kani-fix-3300-c1b`, branch `fix/kani-3300-c1b`, one commit
directly above `1658f4cadfa83139e41180ce3865e23f79d889aa`. The source clone
`/root/kani-fix-3300-worker14` was not changed. No Cargo, Kani, build submission,
network fetch, or push was run.

## Exact causes

Gate A run `43514459160` executes from `/home/runner/work/kani/kani/export`.
Reviewed bindings came from `/home/runner/work/kani/kani`. The regular renderer
relativizes external Rust source paths against cwd. Consequently the bound
`../../../.rustup/toolchains/nightly-2026-10-23-x86_64-unknown-linux-gnu/...`
became `../../../../.rustup/toolchains/nightly-2026-10-23-x86_64-unknown-linux-gnu/...`.

- `uninit-contract-oracles`: `p2` and `postcondition-hole` each mismatch the
  locations of `std::ptr::read::<u8>.safety_check.1` and `.4` at
  `core/src/ptr/mod.rs:1754:9`. `clause` mismatches
  `std::mem::transmute_neo::<std::mem::MaybeUninit<u16>, u16>.safety_check.1`
  at `core/src/mem/mod.rs:1279:14`. These three FAIL observations are present
  in the supplied bounded excerpt; all are the same traversal-depth defect.
- `uninit-part1-composition`: isolated `immutable_legal` has all 39 expected
  records with identical IDs, statuses and descriptions. Exactly 10 locations
  differ by that traversal depth (`std::ptr::read::<u8>` safety_check.1–4 and
  pointer_dereference.1–6). Exact binding comparison stops there.
- Additional portability defects, hidden behind the first composition stop:
  absolute checkout paths were committed inside six closure IDs, their regular
  function locations, and the cycle diagnostic in checks/failure/Unsupported
  metadata. Normalizing only `file` and `location` would leave these failures.

`--force-warn unstable-features` is emitted by
`kani-driver/src/call_single_file.rs` (not an oracle binding field).
Its warning precedes RESULTS and is already outside the parsed inventory.
The bounded excerpt establishes no property drift caused by that flag. Synthetic
checks explicitly retain acceptance with an added warning. Meaningful backend
flags, unstable features, enabled verification checks and process exits remain
enforced exactly as before.

## Change and constraints

The shared normalizer removes only the invocation's known checkout prefix at
path boundaries, including embedded closure/function/diagnostic paths. External
rustup library paths become `rust-toolchain:<toolchain>/library/<source>` for
both absolute JSON paths and relative regular paths. The installation root and
traversal depth disappear; toolchain identity, complete library/source suffix,
line, column, function, type, generated names, statuses and full diagnostics
remain exact. Arbitrary foreign source paths are preserved.

Both manifests were mechanically canonicalized from their previous reviewed
contents. `audit.py` asserts exact recursive equality to that transformation;
there is no re-learning or amendment of expected checks, counters, statuses,
source hashes, proof modes, or evidence metadata. The existing narrow T1b rule
is unchanged. Duplicate canonical regular IDs are rejected. Composition now
normalizes every property string consistently and also runs binding synthetic
tests from its `test.sh` entry point.

## Validation and limits

- Contract-oracle Python suite: 24/24 PASS.
- Composition Python suites: 53/53 PASS, including existing subprocess/error
  receipt tests. No verifier process is launched by these suites.
- Synthetic coverage: all eight contract cases and all seven bound composition
  inventories; local/CI-export/deep checkout roots; absolute/relative rustup
  paths and custom installation roots; embedded closure IDs and cycle messages;
  unrelated warning text. Consistent mutations of source/coordinates, closure
  coordinates, functions, cycle text and toolchain versions are still rejected.
  Existing tests reject missing/extra failures/checks, status drift and disabled
  verification checks.
- `git diff --check` and `bash -n` for the changed shell entry point: PASS.
- Local replay of the supplied excerpt: required_regular rows match for all
  three failed contract cases; all 39 composition records match exactly after
  canonicalization. Detailed differences and input hashes are in `REPLAY.json`.

The replay is limited to the supplied regular-output excerpt. Full exported
JSON files and the rest of the gate were not replayed or regenerated. Full
gate/Kani/Cargo reruns are NOT_RUN by instruction. No independent proof credit
is claimed; previous source-reported evidence and historical ledgers remain
unchanged.

Reproduce the bounded replay with `python3 audit.py`. The ready commit is also
exported as `C1B.patch` for review; `CHECKS.json` records validation and hashes.
