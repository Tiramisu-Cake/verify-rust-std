# Merge bridge compile session — CLOSED

Actual start 2026-10-10T12:58:04Z; main deadline14:58:04Z; absolute15:28:04Z.
The hourly progress was delivered at13:58 UTC. No new Build/experiment after
main deadline; finishing work only observes the already-created proof Build,
verifies evidence, performs saved-data causal replay and closes accounting.
No automatic new session. Closure observed 2026-10-10T15:21:53.431512Z.

Assigned project `/root/verify-rust-std-merge-origin`, branch
`merge/incoming-origin-20261009`, initial HEAD
45fdb1f33dd2838e0edfb5e18ca4a7425ffef5f4. Git-dir/index are
`/root/verify-rust-std/.git/worktrees/verify-rust-std-merge-origin[/index]`.
Tool `/root/verifast-merge-incoming-span`, branch
`merge/incoming-span-lifetime-20261009`, initiale8a77a29, corrected component
HEAD e16352c4f015059ea4158be7d3205275080ce880; git-dir/index
`/root/verifast/.git/worktrees/verifast-merge-incoming-span[/index]`.
Own changes preserved; third-agent selector patches/worktrees/pins excluded.
No runtime std change, Actions, upstream publication or maintainer integration.
Policyc7ca8c467aecf10a4b53039372ee97714f854ee3, adoption1b9e3df3182d13e5adf7d2e5d04afcfbc1851f14,
ACKaec832ab25ba65a5ddc643ca325f8d8ea8b2b612 retained.

## Exact build and profile

**Fresh full compiler PASS** in compile-only ba7ca276 and repeated inside
minimal proof282324ae. Exporter, generated schema/decoder, translator and full
console all exit0, baseline0, postbuild source checks0. No stubs or omitted
compiler dependencies. The component e163 is a delta on8cb; the effective Cloud
source is f76012fb518703b1d98e243ac4f487f16877cfcb plus ten ordered frozen/
tracked-MD/span/unit/guard patches, not the component tree alone.
[EFFECTIVE-SOURCE.json](EFFECTIVE-SOURCE.json) binds the full patch chain and all
12 trusted source hashes; receipt SHA256
16d36cd9e9d0c070648525e1c2b67e3186eda75d8436cd4cf808193407f5d80e.
Profile `experimental-merge-qualified-guard-onecell-v1`, PROFILE.json SHA256
1bc74b60185b2f0c335a2467f0dd9bc53238851f2348f53f1f31737720931a9e.
Guard patch8fb38f4e48f52e24b0e11809231701f44eb00ebdc34befb8cf768bd489e40c7e.

Compile-only proof=infra7d29c93df60dbbb6e2a3bf82c761807e40f707ab; fresh minimal
proof=infraa287a0f2d1b12e3a209b8d69cb66516acdd53f50. Console binary
89494bde13a63cc547afce3c51a12b9ee724c1e8b50d2cfd2bd15d91c050e8ad,
exporter a1742ea48b402d22f4718e1d3d9ebf0d44c7cf3e079def718d84320f1fbb93a0
in the verified compile-only receipt; the minimal run binds its own actual
binaries to the identical source profile. Binary identity across build roots
is not inferred. Subsequent documentation commits are not proof runs.

The entire new OCaml delta was audited. Fixed unavailable Z arithmetic uses
with real pinned Big_int API without changing guards, and reconstructed the
single AST layout record through its exact eight-input tuple helper. Prior
pointer_width_get int correction retained. Build1 exposed component/effective
source pin confusion, repaired all three analogous pins by ten-patch replay.
Build2 exposed missing CAPNP_INCLUDE in the full console's C++ generator,
repaired both real Capnp include vars after inspecting all pinned Dune env
references. [TWO-FAILURE-REASSESSMENT.md](TWO-FAILURE-REASSESSMENT.md) precedes
Build3. No new functionality/glue/unwind/domain expansion occurred.

## Execution and resources

VPS at14:21:33 UTC:1967MiB RAM,200MiB available; swap3915MiB used/0free;
disk163MiB free; load26.54/26.78/28.13. OCaml/Dune/ocamlfind/capnp/opam not
found. **Local compile NOT_RUN**, elapsed/RSS NOT_MEASURED; no installs, swap
changes, heavy local jobs or foreign process/data changes. Only lightweight
syntax/Git/source replay and isolated saved/synthetic classifier parsing.

Cloud uses pinned VFdeps archive8d022c93d51a1d13ec1e782d767c60462405f6865d5ee416f82d6234e93ee580;
OCaml4.14.0, Capnp0.10.4, decoder revision2d6606d9b59cd0c88a66729f3f076c10c0c8e0b2;
Dune executable SHA2562fb09b0245e247ee2501fdce01a18a8665bdc03d0a5fe90b8e0e18867261000a
(numeric Dune version not captured). Rust nightly2026-09-25, compiler commit
f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f, x86_64-unknown-linux-gnu.

Exact Cloud preflight is [compile-preflight.sh](compile-preflight.sh); real
commands in [COMPILE-PREFLIGHT-RECIPE.md](COMPILE-PREFLIGHT-RECIPE.md):
`cargo build --locked --jobs 1` with pinned sysroot native LLVM search;
`dune build -j 1 rust_frontend/vf_mir_decoder/vf_mir_decoder.cma`, then
`dune build -j 1 rust_frontend/vf_mir_translator/vf_mir_translator.cma`, then
`dune build -j 1 vfconsole/vfconsole.exe`. All real dependencies included.
Cloud elapsed/peak RSS: exporter47.57s/714508KiB, decoder1.89s/114076KiB,
translator3.92s/122600KiB, console49.25s/442156KiB. These are Cloud measurements.
No ready unchanged-stage cache was assumed; existing reproducible baseline
and dependency-tracked candidate copy retained. Fixed source transport bound
preserved; compile/minimal recipe omits only two unused legacy Drop modules,
which remain in Git and load only after minimal campaign's early return.

## Semantic sources and separate verdicts

Implemented extent/alignment proposal: same pinned compiler `layout_of` for
exact qualified nongeneric concrete guard DefId/instance/source/target,
bound by schema/decoder/translator/model to the verifier's own sizeof,
alignof, field offsets, storage and thin-pointer geometry. Separation proposal:
actual validated StorageLive allocation receipts, positive supported extents,
matching actual reference pointer identity and surviving physical resources;
StorageDead/lexical cleanup retire receipts. No inference from variable names,
numeric addresses, retained chunks alone, or ref_origin(self)==self. No new
permission or recovered authority. [GUARD-BRIDGE-CARD.md](GUARD-BRIDGE-CARD.md)
and its independent addressed reviews retain conservation and qualifications.
**New guard extent/alignment/root separation theorem is NOT_RUN**: fixture
preparation failed before the first guard exporter, so implementation facts
are not credited as a checked actual-consumer bridge.

Supported proposed domain remains concrete-u64/x86_64, qualified guard and
supported positive scalar/pointer live storage. Generic/ZST separation,
unrestricted comparator/user-Drop and actual compiler monomorphic Drop MIR
remain unsupported. Caller resources, mutable fields/padding/FBC, CURRENT
source quarter, destination gap/option and payload geometry, u64 own/type
interpretation and len==1 remain explicit obligations. No supplied guard-size
or root/source separation added; old count-n strong req still has its supplied
geometry premises, and the new len1 helper does not prove that old contract.

| Obligation | Final verdict |
| --- | --- |
| Full candidate build | FRESH_PASS, all4 stages + posthash |
| Retained-six and exact-combined mandatory normal/unwind smoke | FRESH_PASS in282324ae |
| Six span controls incl retirement/lost authority/overlap/zero | FRESH matched6/6 |
| Bounded u64 half-FBC CURRENT copy/recovery, full normal posts/return/leak | FRESH_PASS_FRAGMENT_ONLY on new profile |
| Recovery false/FBC false/duplicate physical FBC | FRESH intended rejections; emptyu64own negative N/A |
| New qualified guard layout/separation positive and8 controls | NOT_RUN, preparation refusal before exporter |
| New minimal campaign as a whole | INCONCLUSIVE;6span +5concrete classifications (emptyown N/A),9newguard NOT_RUN |
| Historical strong-pre specialized Drop body | Retained conditional PASS on old profile |
| New len1 strong body / nonvacuous canonical interface | NOT_RUN / NOT_RUN |
| Actual insertion caller / compiler Drop glue | NOT_RUN / NOT_IMPLEMENTED |
| New mutable caller normal effect/CURRENT/full posts | NOT_RUN |
| Actual panic/unwind cleanup | NOT_EXERCISED; ordinary smoke unwind is separate |
| Other historical matrix, new domain expansions | NOT_RUN by scope |
| Profile acceptance / integration | NOT_ACCEPTED / NOT_FOR_INTEGRATION |

First blocker is exact ghost-fragment preparation accounting, not a semantic
rejection. [GUARD-PREPARATION-FAILURE.md](GUARD-PREPARATION-FAILURE.md) records
saved repro/fragment hash and next repair. Fix inserted-vs-baseline ghost
removal order, replay preparations with strict original-byte equality, then
fresh exact-SHA `bridge-minimal` on this same component/profile. No unchanged
refusal rerun. Afterwards the nonvacuous canonical len1 gates need the precise
layout and effect AST bindings described in
[LEN1-INTERFACE-REVIEW-20261010.md](LEN1-INTERFACE-REVIEW-20261010.md). Actual
Drop/glue and panic extensions remain separate subsequent work.

## Builds and accounting

| Build | Exact proof=infra | Result | create→finish seconds |
| --- | --- | --- | ---: |
| b5dacec7-d7c4-484a-97ac-475fe07ab18e | 2b4841620eb9ee8417e6d549fe6fa74f5da8843c | FAILURE | 293 |
| 101982de-2f51-4fd0-a1f0-74de7e76a665 | 8cbb5c2ff5aac385211db5f7e1be46ebcfe5a39f | FAILURE | 464 |
| ba7ca276-e559-461c-a3f6-3cf8d3373e04 | 7d29c93df60dbbb6e2a3bf82c761807e40f707ab | SUCCESS | 396 |
| 282324ae-a918-4bc6-b73b-e2861f2596e5 | a287a0f2d1b12e3a209b8d69cb66516acdd53f50 | FAILURE | 442 |

All four archives and text chunks verified; full timestamps, config/source/
archive hashes and tokens in [BUDGET.json](BUDGET.json). The latest archive is
c05f8fe9f1df66f5a276884e5121bf318071968d5a1f761d3c7e7e8847cbbc54;
compile-only archive78682b936231af806d95def85bc71d9cef5051a14e67a283ec7f278e302f8cac.
**CLOSED1595/3600Clouds;2005unused retired**, no carryover. Own active/unresolved
Builds/reservations empty, own ready request withdrawn through existing client.
Coordinatorv2/max2 and foreign accounts unchanged. No unresolved ID/token.
Earlier2662 and1099 closed accounts remain separate.

Reproduce only in a newly authorized window/account: use current committed
mode `bridge-minimal`, publish repaired exact SHA, then existing command:

```bash
python3 research/challenge-8/cloud-build/control.py \
  --phase-id NEW_AUTHORIZED_PHASE --owner merge \
  --ledger /root/verify-rust-std-merge-origin/research/challenge-8/cloud-build/origin-layout/BUDGET.json \
  --state-dir NEW_OWN_STATE submit --infra-sha FULL_PUBLISHED_SHA \
  --proof-sha FULL_PUBLISHED_SHA --lane merge --source-mode pinned-objects --timeout 1200
```

The present account is closed and rejects new submit. The recipe builds changed
exporter/decoder/translator/full verifier before minimal end-to-end targets,
then mandatory smokes,6span+5concrete+9guard controls; no old full suite/glue
expansion. Preserve all current guard/domain/contract/refinement/unwind/leak/
dead-code checks. Previous checkpoint archived separately.
