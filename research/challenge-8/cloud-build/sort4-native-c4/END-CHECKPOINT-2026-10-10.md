# Closed native-entry → actual C4 session

Start2026-10-10 **13:00:22 UTC**, main end15:00:22, absolute15:30:22.
This checkpoint is finish-only. No fourth Build submitted or experiment begun
after main end. No automatic next session. Worktree
`/root/verify-rust-std-select-night`, branch
`research/night-select-sort4-cloud-2026-10-09`, initial cleanHEAD
9240f9d4a770680e531d008097a21216fc16eb3f. Separate gitdir/index verified;
newer own work preserved. Policyc7ca8c467aecf10a4b53039372ee97714f854ee3 and
existing adoption/ACK retained; no docs re-adoption or Actions dispatch.

## Outcome and exact boundary

| Obligation | Status at close |
| --- | --- |
| native→C1 | **NOT_PROVED**. No connected comparator invocation from native resources. |
| connected native→C4 | **NOT_PROVED**. Separate fresh native resource components and actual C4 theorem do not form composition. |
| actual C1→C4 | **Fresh PASS**, d5a0f8da, VF0/370. Reproduction of prior a5180cd7/203b5925; no newly extended actual operation beyond C4. |
| normal/C1/C2/C3/C4 direct unwind | Preserved in that one conditional C4 target: CURRENT source/F recovery, four-cell joins, full source/T/F/thread/type/optional-destination posts, unit return/locals free/leak. Five fresh intended false controls reject at315/365/398/447/482 after target. C1/C2 earlier unwind exits before later callbacks. |
| native resource subset on C4 tool | **Fresh PASS**, d5 VF0/78, both missing-type controls reached matching helper pre. Safe native source4/T owners/F cell/F owner/current thread, stock type producers and opaque MU scratch frame; full automatic native posts/return/leak. Stops before real pointer methods/guards/callbacks. |
| MU storage forward / inner preservation | **Fresh PASS**, d5 VF0/51 and52, one cell only. Exact-old inverse and CURRENT wrapper owner restoration separately refuse at intended assertions. No owner bridge/axiom/failed helper summary used. |
| selected guard implication/ZST witness | **Fresh PASS**,3584 VF0/53, pure lemma only. Actual inline-const/caller route not proved; len8,size0 is selected, so generic positive size does not follow. |
| runtime native guard prefix | Fresh refusal3584 at len+16 no-overflow obligation, before abort/inline-const proof. Full native guard/caller theorem remains NOT_PROVED. |
| actual as_mut_ptr native calls | Fresh d5 paired MIR/refinement; VF refuses external slice method. The native alias and C4 effective profiles differ despite common HEAD. |
| pointer implementation-expression component | Parser refusal3584. Started parenthesis/earlyreturn correction **DRAFT, Cloud NOT_RUN**, profile disabled. |
| actual caller→sort4 | **NOT_PROVED**. Neither native reference diagnostics nor C4 bounded result supplies this edge. |
| C5/select/copy | **NOT_RUN in this session**, excluded; no selector profile or competing implementation. |

Native premises at actual C4 remain **supplied**, because no composition passes:
raw initialized source4/T owners, F cell/F owner, current thread/T/F types,
positive T size and optional T destination4. Source/F/thread resources are now
independently derived from safe native pre on this same tool; T/F types come
from checked stock logical producers, not native heap entailment. They have not
been transferred through the actual pointer/guard/call edge. Destination remains
native opaque MU storage, not a proved optional-T/native-owner adapter. No
arbitrary separation/layout/positive-size facts added. Layout/ZST remain separate
merge-owned work; pure selected len>=16 implies size>16 but that is not proof of
the actual inline-const branch. CURRENT values after callbacks are never replaced
by entry snapshots.

## Tool and profiles

ToolHEADf76012fb518703b1d98e243ac4f487f16877cfcb, nightly2026-09-25;
translator1eab6eb54fe5c23d53ca72a6d9dfcbbff09c09ffaf26c48a4f450f5068a8d313;
kernel37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c;
console8d686fef29ae6fe5b6adb91a946ff9942aef682baf934b273cc61d71a625527b.
Fresh tool snapshot SHA256004dab0f90e2abf75a422c83302015f593ec9273a78fc72d0e09ef71c1a2432b
matches the reviewed C4 effective source/spec/parser/non-console/binary pins.
All exact pins in [FROZEN-C4-SNAPSHOT.json](FROZEN-C4-SNAPSHOT.json).

d5 phase profile SHA25642d573b123ed67885cc3e4a2d5067ee07144cd1daf140804d77fd93006393b7e;
3584 follow-up profile SHA2564d8c67cbd0c65e3c0065b5b4442b940ba9a7ef74143def5c7241c736708ce47a.
Effective tool is identical; selected run scopes differ. These profiles remain
experimental/unaccepted. No production translator/kernel/spec changes implemented.
Historical strict semantics needed by C4 remain unchanged. The separate new
strict-cut draft is **excluded, not accepted, not integrated**; no evidence here
establishes a need for another strict-cut rule. Selector/foreign profiles/pins
and worktrees untouched. Runtime std and generic signatures/guarantees unchanged.

C4 verified sourceba9e6ad3633004c3d934c590462443951ddd6dec80a5df9ffb687ec940958c6f,
ghost-stripped3602050e45025745d80b308802be9e552310959abcee4b95bfe8c24f8ca04b72,
preAST0ed31137cf55a2ed47ed624a6c61591e4aaf96371df3c2979fc10ce8d95bb222.
Exact fresh MIR/new component AST/source/log hashes:
[D5 index](D5-ARTIFACT-INDEX.json), [3584 index](3584-ARTIFACT-INDEX.json).
No old AST fingerprint transferred to new source.

## Builds, reproduction and accounting

| Build | proof=infra full SHA | Outcome | create→finish charge |
| --- | --- | --- | --- |
| 07e046f8-3d43-4016-8f83-f6429a5bd9a2 | 538662831180e6b21549c12b3d1275872fc56c28 | FAILURE, missing required transport document before all target tests; all proof cases NOT_RUN |342sec |
| d5a0f8da-a2ed-416c-9eac-a9ffff926c87 | e12df71d57923d346ba0640b9bd0ea23d2835365 | FAILURE from wrong admission-marker classifier; runexit0, fresh C4/native/MU PASS and intended refusals preserved |441sec |
| 3584fb04-e237-4d66-9c85-60de4df059c4 | 285220a384d050e046d1e8709b79a52bd602e675 | SUCCESS diagnostic_complete; individual proof/refusal outcomes above, verification_accepted=false |382sec |

Canonical reproduction (Cloud-only; old session now closed):

```text
python3 research/challenge-8/cloud-build/control.py
 --phase-id SORT4-NATIVE-C4-CLOUD-2026-10-10
 --ledger /root/verify-rust-std-select-night/research/challenge-8/cloud-build/sort4-native-c4/BUDGET.json
 --state-dir /tmp/smallsort-cloud-native-c4-20261010 --owner select-sort4 submit
 --infra-sha <table SHA> --proof-sha <same SHA>
 --lane o26-sort4-c1-current-recovery --source-mode pinned-objects --timeout 1200
```

All3 terminal/accounted/download_verified. All archive payload/inventory/text-
index hashes verified, no generated source/logs/binaries committed. Configs,
tokens, source-input/archives and exact UTC times are in [BUDGET.json](BUDGET.json).
Charged **1165/3600sec**, unused2435 **closed/no carry**; active=null, no own
reservation, own ready request withdrawn. No foreign slot/account changed except
canonical v2 reconciliation. Classifier correction: saved-log/synthetic service
replay only, [replay](SAVED-ADMISSION-REPLAY-D5.json); no local compilation/proof/
extraction toolchain and no new Cloud verdict from replay. Other local checks
were static syntax/recipe/diff/hash/evidence review only.

## First blocker and next concrete step

For full native preparation, the first newly reached runtime-guard obligation
is len+16 overflow (safe ZST lengths do not provide the requested bound). The
read-only native diagnostic separately reaches the unsupported actual slice
as_mut_ptr. Even after those, the frozen C4 binding rejects a connected consumer
at exact-one-body, or a changed single-body file at source SHA. It explicitly
remains NOT_CALLABLE_SUMMARY. [Minimal source/version/behavior/rule-limits package](VERIFAST-BLOCKERS.md)
records each, including CURRENT MU ownership and the unnecessary exact-old
adapter strength. Guard/abort/inline-const setup refusals are not semantic
negatives and do not solve generic layout/ZST.

Started final draft: parenthesized native cast assertions, actual native early-
return resource component, minimal safe usize-add reproducer, admission replay
reuse and a second main-deadline check before reservation. **No fourth Build**;
Cloud source/MIR/AST/proof all NOT_RUN, profile disabled/dispatch_authorized=false.
These are reversible unfinished drafts, not proof credit or trusted semantics.
The next concrete fresh step in a separately authorized window is to run those
small components/reproducer; a connected proof then needs a separately reviewed
source/MIR/AST binding and real resource transfer, potentially an opaque MU
frame interface to avoid the old adapter. Do not simply call the truncated
sort4 summary or silently adopt aliases/strict/selector rules. No next session
starts automatically.
