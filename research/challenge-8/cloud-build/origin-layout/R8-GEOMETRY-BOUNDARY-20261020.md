# Guard span boundary — proposed decision, NOT IMPLEMENTED

Exact candidate: project1651614a/tool43c1fdc2/profile845ea5a5, Build eaf02609.
Physical merge/current cell/singleton close passed on observed path. Original
Drop precondition101 then cannot prove src+8<=dst || dst+8<=src. See exact
[R8 frontier](R8-BUILD2-FRONTIER-OBSERVATION-20261020.json) and [rejoin](R8-BUILD2-REJOIN-OBSERVATION-20261020.json).
Normal Continue/break/unwind coverage, full CURRENT, B2 and qualification OPEN.

## What the current model actually supplies

Native verifast.ml997–1055 creates a path-local receipt only at checked MIR
StorageLive. Interval exclusion is an existing trusted assume, not a derived
lemma. It applies to supported live local extents with identical allocation
receipt, or supported positive original-entry generic points_to chunks still
present by physical OCaml object identity. It skips canonical incoming arrays
and points_to chunks derived later from those arrays. Qualified struct extent
admission is separate; bounds/alignment or an arbitrary RefType env entry do not
prove allocation origin. Rocq LocalAddrTaken and storage event behavior are not
native allocation proof credit.

Current physical resource separation/provenance supplies no checked lemma that
entails the pure numeric interval order for tmp's guard reference versus an
interior element of the input array. Numeric address equality cannot supply
ownership. Opening array predicates does not repair the original-entry receipt.

## Exact additional trust/design decision, if pursued

A possible future extension would admit canonical owned input array extents to
the established fresh-allocation rule, with exact base/provenance/count/type,
positive physical permission and same-function current-live-owner binding,
plus separately justified qualified local ManuallyDrop<u64> extent. For this
case the additional assumed fact would be that the actual new8-byte stack
allocation is disjoint from the currently owned24-byte input allocation; the
existing checked ref-origin/address and element-offset relations must then
prove the original8-byte src/dst guard condition. No whole-array source content
or entry snapshot may be substituted for CURRENT values.

This extends a trusted allocation-admission premise and is not a checked lemma
already established by the present model. It requires an explicit owner model
scope decision before implementation, exact profile/pins, independent review,
positive/negative source-origin and current-live-owner receipts, same-address
no-owner refusal, retired/dead/hidden-borrow/nonpositive/wrong-type/count/extent
controls, and complete compatible native normal/unwind/Drop matrix. No Rocq
allocation-credit extension is implied. No proposal code has been applied.

## Authorized remaining work

First isolate the representation gap with entry-cell, entry-array and
opened-entry-array numeric-span probes under unchanged tool/model. Each probe
preserves physical normal/unwind resources and runs only in Cloud. A diagnostic
refusal is an observation, not a successful negative proof. Also retain the
independent prefix bridge/BeforeLive investigation; neither justifies a new
memory/storage model or a generic lifetime fallback.

## Owner decision and experimental implementation

Owner explicitly authorized the narrow research scope during R8: justification,
independent review, separate experimental profile and positive/negative controls;
original window/budget preserved and qualification separate. New candidate
f2e92cec uses only CURRENT array subranges with entryarray3 binding; it never
assumes the whole entry24-byte span when only prefix2 remains owned. Existing
ManuallyDrop<u64> transparent lowering supplies u64 local representation; no new
layout axiom. Default-off CLI/IDE behavior and exact profile/source pins are
explicit. This adds the authorized trusted freshness premise, not a verified
conversion lemma under the earlier model; no acceptance/qualification claimed.
See [session rationale](R8-SESSION-20261020.md), [new controls](r8-freshness-controls.py).
