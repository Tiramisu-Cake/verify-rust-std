# M2-B/S coordinator request — binding first, no dispatch authorization

Status PREPARED/BLOCKER. Worker Cloud $0, no local compiler/verifier or CI dispatch.
Exact5f7 base and documentation-only local candidate `35fab624af19b8c724ddc9c80a7cc79289541459`;
there is no semantic fix to accept. Use existing authorized singleton Quick/probe only, one compiler root
and one solver at a time. Do not edit workflows/runners or activate full Quick/heavy PFC suite.

## A. Required before semantic repair: targeted C03 receipt

First return any existing curated receipt from run43243491671 C03 with its exact source/tool/argv and
completeness identities. A run summary is insufficient. Otherwise use unchanged M2-A C03 source/root/hash
from TEST-MANIFEST, expected actual default Assert. Existing non-solving path, coordinator only:

- Existing normal build/fmt/clippy preflight first when required by the source/tool transport; report each stage.
- Reuse C03 argv array, append `--only-codegen` and set RUSTFLAGS to `--edition 2021 -D warnings --emit=mir`.
  Retain `--crate-name m2a`, `--harness legal_ordinary_transfer --exact --keep-temps` and both unstable flags.
  Copy exact source into an isolated existing directory at the manifest-relative path; record actual cwd/argv.
- Validate exactly one compiled/selected root and actual Assert wrapper/ensures. Codegen exit0 is not a verdict.
  DumpMirPass reads transformer.body_ref; request only curated excerpts for the target and relevant generated
  closures, compared to original bodies/constants used by prepare_immutable_allocations. No full/global MIR dump.
- Use the existing non-solving property inventory over that singleton emitted model. There is no dedicated
  Kani --show-properties switch at the pin; do not invent one or combine only-codegen with a solver option
  and claim it executed. If unavailable report PROPERTY_INVENTORY_UNKNOWN.
- At body:30, ensures:14, root:39 bind BOTH operands to raw_eq/CheckAs specialization and exact retained
  property ID/class/location. Return all failing/extra/Unsupported checks with stage exits, not only a substring.
- For each operand: original/emitted ConstOperand and ty, all origin alternatives, carrier slots/options,
  initialized addend/width/endian, referent AllocId/type/Freeze/mutability/extent and original Some/None mask;
  emitted requested-key to actual returned symbol on insertion/reuse, full descriptor and exact byte layout;
  actual object/offset/extent, reset completion, qualified seed, first effect and last setter/retarget/copy/read.
  Identify immutable RHS, mutable out referent and generated stack/capture copies separately.
- Registry/emission snapshots or runtime fields unavailable through the existing path stay UNKNOWN. Do not
  add a new diagnostic framework or treat static source names/coordinates as a complete binding.

If a reached witness history is still needed, request a bounded diagnostic trace for an already identified
property using existing source/version-supported probe options. Preserve original exits and all extra failures;
property-filtered output earns no full-harness proof credit. Reuse timeout300s and CBMC RSS>6GiB watchdog,
record actual limits, sampling interval, bytes/KiB/GiB units, per-process/process-tree and overshoot. Cutoff is
INCOMPLETE. No new resource infrastructure or repeated PFC heavy solver is authorized by this request.
Missing typed origin, missing initial seed, later witness corruption and relevance loss remain distinct diagnoses.

## B. Conditional acceptance request after a reviewed semantic candidate exists

This section is HELD, not execution for a purported fix in this docs-only candidate. After A establishes
a repairable gap, prepare the narrow delta, per-expression TYPE-AUDIT and continuation of bounded review.
First CI must perform build/fmt/clippy; setup failure means solver NOT_RUN. Then sequentially:

1. Unchanged C03 default Assert with retained array3 body/ensures/root checks; C04 no-assert diagnostic;
   unchanged C05/C06 undecorated companions. C04 is not an ensures proof or replacement for C03.
2. Up to four needed small contract-immutable-masks selectors, only after gap binding: legal reversed operand
   if needed, lawful flat MU promoted-hole in each operand direction. None stays false; require intended
   ensures payload read, lawful companion reached SUCCESS and no earlier UB/Unsupported/extra failure.
3. Existing D0 both legal harnesses, six promoted-allocations controls, four immutable-masks selectors and
   five registry unit controls listed in TEST-MANIFEST. Copy-hole must show source-following false transfer;
   retained mutable overwrite/reset and existing false controls must not be hidden. No D0 setter change.
4. Separate mixed composition: take ALL exact16 fixture files from composition
   83ceadf0485f30548c92b77c87b3c08a53f0b019, tree15d3d3ecb5d353da3ae1c51567d9b0d04cc9f5fb,
   already fixed C1-T2-A7f9eec41e8; verify every manifest hash, then materialize test-only on the reviewed
   candidate. Record composition SHA/tree separately. Never apply only the four repair files to absent
   fixtures, import baseline production6134, or cherry-pick resource-track ablations.

Every receipt: source/production/composition/toolchain/sysroot/CBMC/target/layout/config/recipe identities,
actual argv/env (nonsecret), selected root/mode, all stage exits/signals, retained property inventories,
Some/None masks and epoch bindings, all extra failures and reachability, elapsed/RSS raw units and limits.
Correctly seeded false bytes and false/overwrite controls are mandatory. C03 requires PASS of retained intended
checks with qualified reset-only seed; C04–C06 no regression; no Unsupported/frame loss or extra failures.
No positive seeding at ensures/ref/call/return/copy entry; no carrier-as-referent or mutable destination blessing.

## Separate gates and STOP

M2-B/S is BLOCKED on A; no candidate repair or acceptance claimed. PFC resource regression predates M1 in
coordinator summaries; attribution to A1/A2/A3/B1I remains UNKNOWN. Upstream Unsupported/frame failure is
not a matched semantic baseline. M2-B/R is a separate coordinator-owned handoff; PFC controls remain
resource-unqualified. Full unchanged Quick/gates stay deferred until both tracks are resolved. M3 HELD.
Missing evidence is returned as a concrete limitation, never filled by raw archives/logs or a guessed patch.
