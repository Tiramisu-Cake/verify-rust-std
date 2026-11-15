# B3 T1b — existing-model text comparison

2026-11-15. Separate authorized B3 T1b preparation stage, not a C2 slice.
Task base research `b2737f00565bfa73649290cecd31ac42c4097598`; Kani CI parent
`cfa4b0c5296b1f7735b0d4a138d339431dfbf93d`. No local builds, backend execution,
push or CI. This package produces no comparison result before the coordinator's run.

One `ubuntu-24.04` job, 60 minutes, no retry. The old T1 workflow excludes
`uninit-ci/b3-t1b**`; only the new workflow matches. Checkout is read-only for
Kani source. `actions/download-artifact@v4` downloads the named artifact
`b3-t1-43701550489-1` from run `43701550489` in `Tiramisu-Cake/kani`, using
`run-id`, `github-token` and `actions: read`, into `$RUNNER_TEMP/b3-t1-input`.
It neither builds Kani nor recreates models. The output directory is separate.

## Inputs and exact tool

Reuse T1 `compare.load_arm` for strict index schema, contained-file SHA256,
15 perf rows plus control, metadata-derived harness census, original capture
exits, required tool and lock inventories. Additionally require 409 records and
131 final models per arm; every `records/*.json` is independently read, duplicate
keys rejected, file hash checked, and its map must equal the complete index. The complete
`files/` inventory must equal the recorded paths; unrecorded payloads are invalid.
Kinds, rows, harnesses, paths, final backend argv and cwd must match all arms.
Only model/content hashes may differ; tool hashes may differ for B's compiler
and driver, as in T1. A/A tool hashes and all frozen lock hashes must match.
`tools.json`'s goto-instrument SHA256 must agree with every arm's index.

Install only the Ubuntu 24.04 amd64 CBMC 6.11.0 release `.deb`, the same URL used
by A `0aac16ef62`'s `scripts/setup/ubuntu-24.04/install_cbmc.sh` and
`kani-dependencies`. This is the equivalent prebuilt-only path: no apt toolchain,
Rust installation, source checkout switching, compiler or solver invocation.
The installed `goto-instrument` must match T1 `tools.json` SHA256 and report
6.11.0. Mismatch is INVALID before any model dump. The release URL and actual /
expected hashes are recorded. The download and dpkg command exits are preserved.

## Text capture and determinism

Dump every final, linked and symtab logical record in A1/A2/B1, using both
`goto-instrument --show-symbol-table MODEL --verbosity 4` and
`--show-goto-functions MODEL --verbosity 4`. This display setting suppresses
M_STATUS path banners (level 6), retaining errors/warnings and the full direct
stdout symbol/function printer. It does not normalize or delete dump text.
CBMC 6.11.0 source: `goto-instrument/goto_instrument_parse_options.cpp`
`get_goto_program()` logs the input path at M_STATUS; both show functions print
the model independently of that status verbosity.
Metadata files are hash-validated but are not GOTO inputs. No SAT invocation.
One exact final input from each arm is dumped twice in both modes, covering
three distinct logical models (control and two perf models). Raw output hashes
must agree for each duplicate, before normalization; drift is INVALID.

Names are 32 hex characters from SHA256(logical key), checked for collisions,
plus short arm/mode suffixes. The validated source index/tools.json are copied
into `input/<arm>/` for provenance; RESULT snapshots preserve the last started
stage and completed-model count if the outer step is interrupted. `INDEX.json` maps full logical keys to input hash,
raw and normalized paths and hashes. Neither long harness names nor diff labels
are used as filesystem components. Each subprocess has a separate start/exit/
exception record and preserved stdout/stderr; no `|| true`, pipeline, retry or
successful replacement exit. Per-command limits are 60 seconds (installation
180); the aggregate display/install deadline is 42 minutes, within the
48-minute step and 60-minute job. Timeout/error retains partial evidence.
`always()` upload also runs after failure; a pre-download RESULT sentinel makes
missing download/setup visible as INVALID, never an inferred NOT_RUN.

## Normalization, comparison and interpretation

Only exact rustc `AllocId(N, ThreadLocalIndex)` identities are renumbered in
first-occurrence order independently for each complete dump. Repeated identities
remain repeated. No ordering, paths, whitespace, line endings, types, padding,
instructions, locations, other counters or numbers are removed or rewritten.
Raw output is preserved. An identifier ordering difference that this policy
cannot eliminate remains A/A noise; no alternative normalizer is added.
Synthetic controls check alias consistency and preservation of meaningful changes.

All A1/A2 normalized pairs are compared first. `AA_EQUAL_AFTER_NORMALIZATION`
counts final inputs out of 131, including control; `AA_DIFF` covers all selected
stages with classifications and unified diffs. Only afterward compare A1/B1 and
A2/B1. `B_PAIR_DIFFS` records both pairs even for unstable models, explicitly
flagged `aa_equal: false`; `B_DIFF` is the census of A1=A2!=B1, with normalized
unified diffs for each changed mode and auxiliary classifications. Unstable
pairs never establish a B3 effect.

The control gate requires exact `final/control/array_typed_copy` A1=A2!=B1 and
structural confirmation of the expected wrapper payload replacement (bound to
Pretty name and the full raw Base name, as emitted by `Symbol::aggr_ty`), with no
off-wrapper/function change. Failure is status INVALID, reason INVALID_CONTROL.
Unrecognized type/dump syntax fails this gate conservatively rather than granting
wrapper-only credit. Shared classifier checks type flags, one positive-width
unchanged arm padding field, identical declaration order/all other text, and
recursively observed empty struct types (including Unit) for zero width. Multiple
verified wrapper symbols are supported; unknown forms remain OTHER_CHANGES. Mixed
function changes also retain the separate symbol class. Classifier details and synthetic validation are recorded
with the package; human interpretation remains the coordinator's responsibility.

With valid control, any remaining A/A difference gives INCONCLUSIVE_AA. Otherwise
perf models across the captured final/linked/symtab stages give MODELS_EQUAL,
WRAPPER_ONLY or OTHER_CHANGES. Control records are reported separately and excluded
from the perf census. Classes are auxiliary; WRAPPER_ONLY does not mean harmless.
The task and `t1/RESULT-template.md` limit auditor answer 9: equality is only absence
of differences in the captured perf profile, with no guarantee about memory,
runner loss or resource regressions. OTHER_CHANGES requires the next bounded
investigation and no PR submission. No B1/B2 formal-proof or SAT credit is claimed.
