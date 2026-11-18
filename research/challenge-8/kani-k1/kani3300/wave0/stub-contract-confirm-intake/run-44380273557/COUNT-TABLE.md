# Expected predicates and actual observations

Owner22:31 authorizes an exception for pinned counts only. The preserved runner
contains relational count predicates, not literal expected counts for these
native harnesses. Its synthetic service fixture uses a one-property example;
that is not an observed native count. Owner's report that counts were
source-guessed is retained as authorization context, not substituted for the
actual oracle source.

| Dimension / exact field | Frozen expectation | Provider actual | Verified actual |
| --- | --- | --- | --- |
| `feature` | provider / verified | provider | verified |
| `selected_harness` | provider / verified_control | provider | verified_control |
| `process.exit` / `signal` / `termination` | 0 / null / EXITED | 0 / null / EXITED | 0 / null / EXITED |
| `process.verification_success` | 1 | 1 | 1 |
| `process.property_inventory[harness]` length | same as export `checks.total` | 89 | 52 |
| stdout property `status=SUCCESS` | every property | 88 | 51 |
| stdout property `status=UNREACHABLE` | none | 1 | 1 |
| stdout FAILURE / other status | none | 0 / 0 | 0 / 0 |
| stdout SUMMARY | zero failed | 0 of 89 failed (1 unreachable) | 0 of 52 failed (1 unreachable) |
| stdout semantic property | postcondition / assertion SUCCESS | index5 `f::{closure#2}.assertion.1`, postcondition SUCCESS | index7 `verified_control.assertion.2`, assertion SUCCESS |
| export `harnesses[0].checks.total` | integer, 0 < total <= 256 | UNKNOWN: unretained | UNKNOWN: unretained |
| export `harnesses[0].n_properties` | equals checks.total | UNKNOWN | UNKNOWN |
| export `harnesses[0].checks.success` | integer equal to checks.total | UNKNOWN | UNKNOWN |
| export `checks.failure` | [] | UNKNOWN | UNKNOWN |
| export `checks.unreachable` | [] | UNKNOWN | UNKNOWN |
| export `checks.undetermined/error/unknown/other` | each [] | UNKNOWN | UNKNOWN |
| export `n_failed/failed_properties/covers.total` | 0 / [] / 0 | UNKNOWN | UNKNOWN |
| export `unsupported_constructs` | each matches a SUCCESS stdout property | UNKNOWN | UNKNOWN |
| export schema / run_state / outcome | 0.1.0 / COMPLETE / COMPLETED | UNKNOWN | UNKNOWN |
| export target | x86_64-unknown-linux-gnu | UNKNOWN | UNKNOWN |
| export exact selection / matched count / verdict | exact single selected harness, SUCCESS | UNKNOWN | UNKNOWN |
| export safety / overflow / unwind / undefined-function / reach checks | enabled | UNKNOWN | UNKNOWN |
| export prove_safety_only / ignore_global_asm / coverage / cbmc_args | false / false / false / [] | UNKNOWN | UNKNOWN |
| `export_inventory.present/complete` | true / true and retained valid doc | true / true, doc unretained | true / true, doc unretained |
| `export_inventory.bytes` | <= 2097152 | 2886 | 2735 |
| producer `observation` | SUCCESS | INCONCLUSIVE: check counts | INCONCLUSIVE: check counts |

Both UNREACHABLE entries are exactly `f.assertion.1`, description `attempt to
add with overflow`, location `src/lib.rs:8:5 in function f`. The semantic
postcondition and caller assertion are SUCCESS and distinct from this property.
The status of that body property has a separate frozen predicate after the
count predicate. It cannot be converted to SUCCESS or silently waived as a
numeric mismatch. Native successful verification remains an established
observation.

Each invocation uses `--lib --no-default-features`, its exact feature and
`--exact --harness`, `-j1`, `-Z function-contracts -Z stubbing -Z export-json`,
regular output, and separate fresh export/target paths. Full argv/cwd/env,
request/manifest/fixture/invocation digests are retained in result.json and
SLOTS.json; their checks pass. Export configuration, target and check buckets
cannot be independently inspected from argv or an export digest.

The exact original exports have SHA256
`23c5152fae077f595abfa68a651994dbea2fc63c1f818bb1da72bda340556aa3`
and `ea465cde645c90a9364fa721678ba9664a3fd1f82f75fe8964283401261effc6`.
The collector retains a doc only inside a successful observation; its
check-count exception discards both docs. Present/complete metadata therefore
does not establish retained export completeness for intake. Actual exported
counts must remain UNKNOWN; stdout counts above must not be relabelled as
export counts.
