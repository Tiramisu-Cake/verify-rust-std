# W14 combined S2 r2 — APPROVE

The source component and repaired diagnostic runner are approved within the
static and bounded synthetic scope of task
`6b67c00b73e7ccd3f226ffecb6bfb3c3326ceb9b`. B-01/P1 and B-02/P2 are independently
**CLOSED**. The final integration gate is **CLOSED** for this exact binding:

| Identity | Approved value |
| --- | --- |
| Final g0 package | `5a9e715ad9e303fbd10600ee379313301c87e9b3`, `batch-r2-r1/` |
| Source | `efb1aba7fc6445cba6cd75154713b598c9e2579d` |
| Source tree | `4563e06722871ae5eafdf6d288afa21a406b6ba8` |
| Source parent | `97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a` |
| Final control | `2ce62b5bb31abd44824dc8e358f77e63d539ed98` |
| Final control tree | `dadbd710770720cd360529188c81c6d19a8de61c` |
| Required sole control parent | `9e14e033f9ee31522b571c127609dcdff76d230b` |
| Request SHA256 | `008c6868bd466fc7dfb2c1e3239f94157262b0d5c5ac14fac00be0e37fdaae38` |
| Workflow SHA256 | `973944169dd4d7f2fc169582b1327cc8e31fa96710a2a597ed0a126ef37e4a2e` |
| Stock tool | `0aac16ef62da9e9d5645782d458593e5d78143ba` |
| Stock tool tree | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |

The coordinator delivered these final pins during the active review; the
committed packet independently matches them. This does not approve old composed
control `2d00b9cc14f5a093ccaa0288a0f691fddf3ee84a` or rejected runner
`b678fb6cdd5edf69a4e952167422f36a45a3d6cb`. There are no open blocking findings.
Owner **13** owns source/composition; original owner **11** owns runner repairs.

## Source/model and CFG review

Source-component g0 `714c1ca56dd7cf352ae6feebe5e252178cdb63b2` has 40 exact
committed files and 39 manifest entries. The delta from source
`9fd558c9dab5ec26abdb1226eb5f2b9cd9ffbff6` touches only
`library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_batch.rs`.
It replaces both sort8 verified stubs at lines 54/155 with ordinary
`diagnostic_sort8` stubs, removes all 13 registration lines, and adds the explicit
model at line 169. Original root bodies, signatures, assertions, covers, weak
controls and constructive witness are exactly retained. Production SmallSort and
all other source files are unchanged from the frozen source.

The model has the callee's generic unsafe signature, including the existing
`FreezeMarker` and `FnMut(&T,&T)->bool` bounds; it adds no Copy constraint.
`span::active::<T,F>()` is asserted before casts, reads or writes and specializes
only to `u8/KeyLess<u8>`. The readable source8, writable destination8/temp8 and
three pairwise disjointness checks match the applicable original requires.
The owned pre-state is captured before writes. Every destination and temporary
byte is initialized with an independent arbitrary u8; no uninitialized output is
read. Only destination8/temp8 are written; source, comparator, other storage and
allocation remain untouched. The stateless concrete comparator has no observable
state to transfer.

The final assume requires sorted full-byte output and equal multiplicity for
each input value through the unchanged `sorting_s2_span` and `sorting_model`.
Equal length excludes novel output values: summing the preserved counts over all
distinct input values already accounts for all eight output elements. This is
the applicable full-value relation of the replaced summary. Temporary bytes are
unconstrained and not observed by these callers. No new PFC, old()/modifies
mechanism or runtime algorithm change is introduced by the model.

For positive general32, the two source8 spans begin at original array offsets
1/17 inside initialized u8[34]; canaries remain at 0/33. Destination scratch
offsets are 0/16, temporary offsets 32/40, inside MaybeUninit<u8>[48]. Weak
general32 instead starts at input offsets 0/16 in u8[32], with the same scratch
topology. Both produce initialized sorted8 prefixes for the unchanged insert-tail
extensions to 16, followed by the merge. The weak row alone substitutes
`weak_merge`: copying sorted [2;16] then [1;16] leaves the intended inversion,
so its sole original assertion remains the `S2_NEG_GENERAL32_WEAK` oracle.

For every finite input a sorted permutation exists, so the model relation has a
returning witness; it does not assume false or discard the input domain. The
unchanged constructive witness covers lengths 8..16 and 32 plus the pair relation.
Useful-return/nonconstant/duplicate/unsorted covers remain required. This is
static reasoning about the explicit diagnostic premise, not executed Rust
nonvacuity or qualification. Sort13/general32 remain DIAGNOSTIC_ASSUMED and
proof credit stays NONE. The semantic/model change must be recorded in any cost
comparison; missing r1 roots provide no measured speedup baseline.

All 11 effective root contexts regenerate the exact CFG map. Remaining verified
references resolve to active insert_tail/merge/swap registrations; both ordinary
sort8 references resolve to the exact active model. The scan includes compiled
unselected items and all verified-use files, with six supplemental uses and
their inherited direct/macro registrations retained. Registration and static
macro inspection establish no callee proof. The 19 Python CFG/model controls
(15 legacy, four r2) pass once, including either reintroduced verified sort8,
unselected uses, missing/wrong-cfg/foreign replacements, unsupported syntax and
domain/post/frame/assertion mutations. No required gate or expected count was
weakened to conceal a missing registration.

## Independent runner finding closure

Repaired runner g0 `a8e3cb30c617a6dee07fa847f1f23470d59783e3` has 28 exact
committed files and 27 manifest entries. Its control
`472be8c3794d7a4530760ab7d5eae4ce950aa01c`, tree
`4835c615d20e6606ddcdc64bbb8314973cec141b`, has required sole parent9e14.
Relative to b678, only packer, collector, their diagnostic tests and request
payload hashes change. The existing runner, fallback and preview test bytes are
unchanged. The old review `5db34a924329e05602bf1f8643ad0f4082653b3c` remains
immutable CHANGES_REQUIRED for b678.

**B-01/P1 CLOSED:** `pack_evidence.py:15` now unions actual captures with group
directories and structured selected-group/row/execution receipt inventories.
Eight independent bounded cases cover the exact fallback group, removal of both
main receipts, absent selected/row groups, and NOT_RUN/NOT_RUN_OR_INTERRUPTED/
IN_PROGRESS/INTERRUPTED states. Complete setup captures cannot certify these
groups. Packed completeness is false with explicit reasons and unknown
unobserved-byte counts. Source receipts and packed originals are unchanged;
native exit42 and UNKNOWN/proof NONE are retained where supplied.

**B-02/P2 CLOSED:** `rustc_diagnostics.py:15` recognizes numbered N-minus/N-plus
suggestions as context. Twelve independent combinations of stdout/stderr,
ANSI/plain and chunk sizes 1/7/4096 retain the original 165-byte suggestion and
following UTF-8 note/help context. Original raw byte spans, complete flags,
zero dropped-byte accounting and exact packed receipt text are checked below
unchanged caps. The fixture is constructed text, not a recovered compiler error.

The original 168090-byte long-middle fixture is rerun against the actual frozen
2ec reader and repaired reader: bounded previews still match and both omit the
error; the new receipt retains the exact 80-byte block at [84005,84085).
Independently executing the selected 33 Python service/diagnostic tests once
passes 33/33, including the preview test. Error blocks, context, stdout/stderr,
ANSI/chunk/EOF, retention/scan/artifact caps, producer omission/count gaps,
missing/null/wrong-type/NOT_RUN receipts, normal/failure/fallback/packing,
timeouts, signals, original exits/exceptions and shutdown/finalization controls
are exercised. This is bounded synthetic coverage, not a production guarantee.

## Preview failure remains visible

W11's earlier expanded33 attempt failed the unchanged preview test at
`test_runner.py:582` because the compile snapshot's stderr head was empty.
That transcript is preserved in the runner packet and byte-identical final
`W11-EXPANDED-ATTEMPT.txt`; the final32 and isolatedpreview1 are separate author
evidence. Our 33/33 passed once, without retries or omission. It does not prove
the earlier failure resolved.

The source permits the observed ordering: `_read_pipe_body` reads pipe data in
65536-byte reads, while `CompileMonitor.poll` snapshots preview state when it
observes the export marker. The synthetic child writes roughly5KB stderr before
the marker, but the marker does not synchronize reader consumption. Thus a
marker-time preview can be empty even when text was emitted earlier. This is a
pre-existing preview timing limitation, not an independent failure of the repaired
diagnostic collection. Finalization still attaches capture completeness and
native execution outcomes; missing/partial captures remain explicit. No preview
timing fix is claimed or required to close these two findings. The unchanged
workflow still includes the preview test and may encounter that timing failure.

## Final integration gate

All 45 files in final g0 5a9e and 44 manifest hashes match. Seven full/delta
patches match exact Git diff bytes and replay to the declared trees. The source,
source patches, model/CFG/row/root/assumption/supplemental maps are byte-identical
to reviewed source714. Packer, collector, diagnostic tests, fallback, preview
test and workflow are byte-identical to repaired472. Runner.py differs only in
STD_SHA/STD_TREE literals. All source/fixture/request/payload hashes match.

The seven-path delta from472 is limited to request, source fixture, CFG checker,
pinned old fixture, runner literals, source policy and CFG/model tests. These
source-policy changes exactly match the independently checked source draft.
The four-path delta from2d00 is request payload hashes and the three exact W11
repair files. No runner repair was authored by13 or by this reviewer.

The exact final source preflight, request/selector/oracle binding and real
temporary shallow Git checkout7/5/2 pass. Selection remains 11 roots, 20 covers,
six exact negatives; stock tool, 600s/root, compile900/group7500/internal8100/
step7560/job180min, serial1, RSS12GiB plus2GiB headroom and every output/native
metadata/artifact cap are preserved. Author final79 provenance is bound to this
exact control/source/request; it is not promoted to 79 independent tests.
Previously established component tests are inherited by exact byte identity,
without broad repeated suites. See INTEGRATION-GATE.json and FINAL-PREFLIGHT.json.

The review harness initially looked for the copied source policy's fixture in
the packet directory. Its FileNotFoundError is retained separately; the corrected
static check materializes the exact pinned9fd fixture in a temporary location.
Only that setup check was rerun. No candidate changed and no passing test suite
was repeated.

Coordinator may prepare the exact combined GO-request. Owner alone decides
publication/retry/accounting; this review performs no dispatch. Historical
run44284869572 cause remains UNKNOWN. Native compilation, actual model execution,
qualification and production diagnostic retention remain NOT_RUN. No B1/B2/R8
or other proof credit is established; zero proof obligations are closed.
No compiler/verifier/full runner, CI, push, PR, cancellation, ledger, reservation,
budget or author-path edits were performed. No subagents or model/Fast changes.
