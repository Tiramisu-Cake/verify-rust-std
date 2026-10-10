# Native opaque prefix checkpoint — closure in preparation

Session start2026-10-10 19:27:14UTC; main deadline21:27:14UTC;
finish-only21:57:14UTC. Worktree /root/verify-rust-std-select-night, branch
research/night-select-sort4-cloud-2026-10-09, owner select-sort4. Initial
e5f3f1aec688b944482e6c450b6d12f75ad6fc69; separate3600Cloudsec, no carry.
Policyc7ca8c467aecf10a4b53039372ee97714f854ee3 and existing adoption/ACK retained.
The initial branch/HEAD, own git-dir/index and clean working tree were checked;
newer own work and peer worktrees/ledgers/pins were preserved. Hour progress
delivered20:27UTC. No automatic continuation session is authorized.

## Proof status by obligation

| Obligation | Status and exact scope |
| --- | --- |
| opaque scratch frame | Fresh1ba7 VF0/73; CURRENT source4 rejoin + F/thread/types + native MU storage/owners, helper bodies before native consumer; full native normal posts/unit/free/leak |
| native early return | Fresh1ba7 VF0/81, actual len<2 return resources; no callback |
| pointer implementation expression | Freshd776 VF0/90, source-linked slice casts/full normal posts; actual external method edge absent |
| native→actual C1 | NOT_PROVED; freshd776 strict entry refuses172:1–30 before callback; no direct-unwind/post credit |
| native→actual C4 | NOT_PROVED; no connected actual C1 theorem to extend |
| actual C1→C4 | PRIOR PASS d5/a518 VF0/370, normal + all4direct unwinds, CURRENT recovery/full original prefix posts/unit/leak; separately supplied input resources |
| actual external as_mut_ptr binding | NOT_PROVED; expression-component PASS does not establish method-call summary |
| external caller / len+16 | NOT_PROVED; fresh checked MIR AddWithOverflow+Assert/unwind captured, frozen exporter forces unchecked ordinary add and VF refuses |
| narrow native capture | Build081275a9 pending at checkpoint preparation; diagnostic only, always refuses before proof |
| C5/select/copy, strict-cut draft | NOT_RUN in this session; excluded |

The minimal prefix interface keeps source4/tail, F cell/owner, current thread
and T/F interpretations; native MU scratch storage/owners remain opaque.
Neither new(inner(old))==old nor an optional-T destination bridge is used.
Source permissions and owners come from actual native reference resources in
the proved components. Pointer equality supplies no ownership. T/F type
interpretations use stock proved producers. Positive T size and the selected
non-ZST/len>=8 internal path remain explicit conditions of the candidate;
the real selected branch does not imply positive size (len8,size0 witness).

Existing C4 still has separately supplied raw entry/source4/F/thread/types,
positive size and optional destination at its own boundary. Component proofs
do not discharge that boundary or the actual sort4 call edge. Native automatic
reference resources are derived in the isolated components, not substituted
for a proved native→C4 composition. Actual caller guard/abort/inline-const,
scratch method binding, branch/call edge, generic layout/ZST and later writes
remain separate obligations. No runtime std/signature/final guarantee changed.

## Effective tool and experimental profile

HEADf76012fb518703b1d98e243ac4f487f16877cfcb, nightly2026-09-25;
frozen snapshot ../sort4-native-c4/FROZEN-C4-SNAPSHOT.json, SHA
004dab0f90e2abf75a422c83302015f593ec9273a78fc72d0e09ef71c1a2432b.
Frozen translator1eab6eb54fe5c23d53ca72a6d9dfcbbff09c09ffaf26c48a4f450f5068a8d313,
kernel37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c,
console8d686fef29ae6fe5b6adb91a946ff9942aef682baf934b273cc61d71a625527b.
Full parser/schema/exporter/refiner/libspec identities are pinned by that
snapshot and fresh effective-profile artifacts; tool HEAD alone is insufficient.

Third batch has a separately named EXPERIMENTAL_EXACT_NATIVE_C1_CAPTURE_ONLY
profile: translator86952a6ac4a61ac854d8a9886cff98ee143a0e75ccf8148fb84e07c0a14ce544,
patch4a549366920559f7042e07bb54ad182568b5549c7c4e6dfd518312407b337def,
kernel unchanged. Source7ebcf7cd435c31b3f4669ac6f31a62fd45fcb2c7fa03500bdfbc44ccaca01742,
MIR call210:21–92, marker194/cut212. Exact-one/source/full-check gates retained;
capture never executes or erases the cut and never yields an accepted summary.
General lifetime/alias/checked-arithmetic/MU rules remain peer-owned. No strict
draft, selector profile or unfinished peer patch is included. All profiles
remain experimental and unaccepted.

## Builds and accounting

| Build | proof=infra | charged seconds | evidence |
| --- | --- | ---: | --- |
| 1ba7fdb3-c2ba-470a-84e5-e6b4077ffda4 | 9b86096ec897577d11cd8efa4302aaccbf15b8ef |415| terminal/accounted/download verified |
| d77612a5-5620-47a7-819d-3fa499cd15c0 | 86e38e3a74cca49b2be8e12aa101bdd797d4a917 |344| terminal/accounted/download verified |
| 081275a9-032a-4053-a088-c173f12f05c9 | 7fc22c0452ee1fb89677da13de52a9433a383906 |pending| token dispatch-8e3ce5fb68d34f2c8a1f302fce5a5dfc |

First two collector SUCCESS results do not mean a connected proof. Canonical
archive hashes/reviews are in FRESH-1BA7-REVIEW.md/FRESH-D776-REVIEW.md and the
artifact indexes. Previous sessions'1165/1469seconds are closed and excluded.
84616990 source-package transport rejection preceded reservation/API creation:
no Build ID/token liability and zero charge;7fc pack188/191 passes unchanged
transport ceiling. Saved classifier replays and dependency-closure/static
checks preceded each dispatch; historical proof matrix was not rerun.

Reproduce only within a separately authorized window, with published exact
proof/infra SHAs and canonical coordinator capacity/account checks:

```sh
python3 research/challenge-8/cloud-build/control.py \
  --phase-id SORT4-NATIVE-OPAQUE-CLOUD-2026-10-10 \
  --ledger /root/verify-rust-std-select-night/research/challenge-8/cloud-build/sort4-native-opaque/BUDGET.json \
  --state-dir /tmp/smallsort-cloud-native-opaque-20261010 --owner select-sort4 \
  submit --infra-sha 7fc22c0452ee1fb89677da13de52a9433a383906 \
  --proof-sha 7fc22c0452ee1fb89677da13de52a9433a383906 \
  --lane o26-sort4-c1-current-recovery --source-mode pinned-objects --timeout 1200
```

The same explicit global arguments followed by `status BUILD_ID`, then
`download BUILD_ID --output NEW_DIRECTORY` reconcile charge and verify archive,
submitted config, pinned inputs, inventory/upload/text index. No local proof
toolchain or Research Actions was run. Small local saved/synthetic classifier
tests and deterministic file/Git transport packing used no compiler/verifier.

## First blocker and next concrete step

Native C1 strict entry rejects unresolved outer type inference before the call.
The full log does not identify the first failing local; erased references
exist both before callback (_5 from v.len()) and in callback packaging.
Review the fresh single-declaration capture and callback-free preparation to
identify the exact entry type inventory. Any required general inference/alias
or strict-rule fix belongs to VeriFast agent with preserved escape/conservation
checks; do not repeat this refusal or weaken the cut. Then prove the reviewed
source-specific lifetime/Output=bool binding and actual C1 normal/direct-unwind
CURRENT posts, followed by C4 on that exact compatible profile. See
VERIFAST-DEPENDENCIES.md for the separate checked-arithmetic/external-method
minimal reproducers. A helper component is not the missing actual call edge.
