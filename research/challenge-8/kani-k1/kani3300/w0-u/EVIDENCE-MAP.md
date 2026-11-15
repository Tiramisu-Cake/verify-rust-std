# W0-U source and evidence map

2026-11-16. Inputs read from g0 `815f97fce487d575e58f88a70c2b9eea91ec62b9`; original PR drafts at `bab3aada59` were unchanged at session entry. This is a static curation of accepted coordinator receipts, not a new verifier run or independent formal proof. All CI evidence below is from the fork. No organizer integration or challenge-completion credit is established.

## Metadata freshness and identity checks

Read-only GitHub connector refresh of [#5172](https://github.com/model-checking/kani/pull/5172) and [upstream main](https://github.com/model-checking/kani/tree/main) completed at **2026-11-15 22:26:38 UTC** (2026-11-16 in Europe/Moscow). Metadata is a snapshot; refresh before publication.

| Field | Returned value |
|---|---|
| PR title / author | Preserve memory initialization checks at unresolved calls / Tiramisu-Cake |
| State | `open`, `merged=false`, `draft=false`, `mergeable=true` |
| Base | `model-checking/kani:main`, `0aac16ef62da9e9d5645782d458593e5d78143ba` |
| Head | `Tiramisu-Cake/kani:fix/kani-uninit-unresolved-call-v3`, `6fe484b30043b3696b5f1ccc4bea0e42891ad012` |
| Created / updated | `2026-11-14T11:33:40Z` / `2026-11-15T14:59:02Z` |
| Closed / merged at | `null` / `null` |
| Requested reviewers / teams | `null` / `null` in normalized PR metadata |
| Commits / files / additions / deletions | `1` / `50` / `954` / `73` |
| Current main | `0aac16ef62da9e9d5645782d458593e5d78143ba`, tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |

The separate read-only reviews endpoint returned `[]` at **2026-11-15 22:34:45 UTC**. No CI logs were accessed. `mergeable=true` is metadata, not review approval. #5172 already exists and must not be resubmitted.

Local Git object reads in `/root/kani-fix-3300-c2-slices-w14` independently confirmed every immediate parent in the table below, B1's parent equal to upstream, final C2 tree `9829702c1aa0ecb73c860fc0ad5451757917d6cb`, and SEL1's parent/tree. The clean upstream contains `063204a177272585352b6942ae2b04709fe58b48` and generic-method fix `f046b70644e113be0df9c22c2e6ea44a65a57566` by ancestry checks. Read-only issue metadata reports [#4908](https://github.com/model-checking/kani/issues/4908) and [#5116](https://github.com/model-checking/kani/issues/5116) closed/completed; that is not organizer pin adoption.

## Seven dependent source slices

Each row's parent is the preceding source row; PR-01's parent is B1 `6fe484b30043b3696b5f1ccc4bea0e42891ad012`. Against `main`, an unmerged stacked PR includes its unmerged ancestors. CI-only overlays are not PR source.

| Slice / scope | Exact source head | Fork run / accepted receipt | Claim and limit |
|---|---|---|---|
| PR-01 selected-body analysis | `d82752c8bc878398e672bffaa631ca6a28430acc` | [43696666260](https://github.com/Tiramisu-Cake/kani/actions/runs/43696666260), [acceptance](../c2-slices/slice-01/ci-43696666260/ACCEPTANCE.md) | 9 ActiveCalls units; 302 regression passes, 9 existing ignores. No new analysis end-to-end tests on this head; regression/unit evidence only. |
| PR-02 immutable masks | `932fb8395a58f8c86c0d702ba2cae835823b2962` | [43701587141](https://github.com/Tiramisu-Cake/kani/actions/runs/43701587141), [acceptance](../c2-slices/slice-02/ci-43701587141/ACCEPTANCE.md) | 9 immutable registry units; 308 regression passes, 9 existing ignores; six new descriptor cases. Later raw-equality/mask integration is separate. |
| PR-03 layout/raw equality | `5ca51679e3f433718807a2e44add0d5abac128e7` | [43706759714](https://github.com/Tiramisu-Cake/kani/actions/runs/43706759714), [acceptance](../c2-slices/slice-03/ci-43706759714/ACCEPTANCE.md) | Regression qualification; nested-layout/raw-equality integration waits for cumulative head 4. |
| PR-04 storage/direct transfers | `345cedfd67df679e326474385308349d609fc43d` | [43710024495](https://github.com/Tiramisu-Cake/kani/actions/runs/43710024495), [acceptance](../c2-slices/slice-04/ci-43710024495/ACCEPTANCE.md) | 404 regression passes, 9 existing ignores, 20 category units. Deferred analysis DAG/cycles/root-order/ordinary-slot and layout/raw-equality tests run here, not on heads 1/3. |
| PR-05 closure masks | `96f5d5dc8dedd369c6986a4f1dd5e698b6167f0f` | [43715788377](https://github.com/Tiramisu-Cake/kani/actions/runs/43715788377), [acceptance](../c2-slices/slice-05/ci-43715788377/ACCEPTANCE.md) | 451 regression passes, 9 existing ignores; remaining selected-closure/contract/mode cases; 4/4 mutations detected, fourth manually reviewed. |
| PR-06 edge tests/docs | `3f5242bb1539fb88196d7e503b722f0905f2b46c` | [43720042056](https://github.com/Tiramisu-Cake/kani/actions/runs/43720042056), [acceptance](../c2-slices/slice-06/ci-43720042056/ACCEPTANCE.md) | Eleven edge fixtures and automated sensitivity; no production-code delta. |
| PR-07 delayed-body isolation | `8e299aa6243bc5f06a29c51e98aafa9564478220` | [43723531871](https://github.com/Tiramisu-Cake/kani/actions/runs/43723531871), [acceptance](../c2-slices/slice-07/ci-43723531871/ACCEPTANCE.md) | Cache6/scope2 units, 11 invocations/18 exact mixed-vs-own-isolated comparisons, LLBC and cumulative qualification. Bounded structural checks, not universal isolation proof. |

The early runs are selected ubuntu-24.04 qualification, not the full three-platform regression matrix. Deferred tests on heads 4/5 do not establish standalone PR-01 behavior. Final-tree equivalence and per-slice coordinator acceptances supersede older static NOT_RUN views only for their stated runs/claims.

Architecture navigation: [dependencies](../c2-slices/source-map/DEPENDENCIES.md), [seams](../c2-slices/source-map/SEAMS.md), [file/hunk map](../c2-slices/source-map/FILE-HUNK-MAP.md), [recomposition](../c2-slices/RECOMPOSE.json). These describe source seams and lexical bindings; coordinates alone do not prove AST/MIR causality.

## Final C2 versus separately qualified SEL1

| Evidence | Source binding | Supported result / boundary |
|---|---|---|
| C2 full regression [43665002636](https://github.com/Tiramisu-Cake/kani/actions/runs/43665002636) | Accepted export `ad499e41dd2db9ccd432f89721638a1f3a0bbd44`; same tree as final C2 `8e299aa6243bc5f06a29c51e98aafa9564478220` | 33 ordered stages per platform, ubuntu-24.04 / ubuntu-24.04-arm / macos-15, exit zero. Final-tree regression evidence, not intermediate-head or challenge proof. Authority: [final acceptance](../c2-slices/slice-07/ci-43723531871/ACCEPTANCE.md) and [INDEX](../c2-slices/pr-texts/INDEX.md#final-tree-evidence-and-scope). |
| C2 bounded replay [43683557088](https://github.com/Tiramisu-Cake/kani/actions/runs/43683557088) | Same accepted C2 tree; its own std/test binding | Two merge successes (0/572 and 0/1030); sort4 has one `select_unpredictable` boundary out of 760, return unreachable. This is historical C2 evidence, not SEL1 success. |
| SEL1 Quick [43740679160](https://github.com/Tiramisu-Cake/kani/actions/runs/43740679160) | `14bc57fdb99960240c4944845a3d985c8af4dcf7`, parent C2, tree `1efb6e4dfa69d346df8e23741d11839b1932403d`; CI overlay `568f10ed6540bc46046e3571044e10a262a14b42` | [Acceptance](../sel1-c2/quick/ci-43740679160/ACCEPTANCE.md): expected402/0/6, +29/29 select controls; compiler76, kani50/0/3, UI17, script3, JSON17, std2; units9/9/1/1/6/2; 4/4 mutations and 18 structural comparisons. Preparation wiring failures are not proof failures/successes. |
| SEL1 Gate A [43744142824](https://github.com/Tiramisu-Cake/kani/actions/runs/43744142824) | Same SEL1 freeze; trigger `ce2227aa9b` | [Acceptance](../sel1-c2/gatea/run-43744142824/ACCEPTANCE.md): 33/33 ordered stages on each of three platforms; expected773/0/13 versus C2 744/0/13, exactly +29. Rounded times: ubuntu-24.04 **41 min**, ubuntu-24.04-arm **40 min**, macos-15 **76 min**. RSS not reported there. Regression acceptance only. |
| SEL1 six-row replay [43751703000](https://github.com/Tiramisu-Cake/kani/actions/runs/43751703000) | Same SEL1 freeze; trigger `1ce0b1e5b6`; std `70ba5befc617627073738e26cb1466bd4fb76e41` plus test-only overlay `6075e7ce17179f45642c9ffe8fe09e3ec9395726` | [Accepted result](../sel1-c2/replay/run-43751703000/RESULT.md), row table below. Ubuntu-24.04, six serial jobs, closures, uninit ON, valid-value OFF, object-bits12, controls cfg ON. No timing or RSS reported: both **UNKNOWN**. |

SEL1 replay preparation [request](../sel1-c2/replay/CI-REQUEST.json) records `--no-assert-contracts`, default standard checks/reachability/slicing, source unwinds and exact selectors. Its NOT_RUN/null fields are preparation state, not a replacement for the later accepted result. Bound selected library tree `6ea9d3425f6d0478cfc2517cbdd2fb7d7b32a53f`, patched library tree `12e87bd4a4e141a8f829d8a0519efc09260c5059`, test patch SHA256 `473526895d6d57a99bd356a060195745cc6aba9ee2b70fcc7ae90fecb6676f06` (independently matched against the embedded patch). Local std base70ba resolves to tree `84ab170ccdcc29fba69e55e0a46e6acdf52d9704`. The overlay commit object was unavailable in the two local std/research repositories checked, and the read-only public GitHub commit endpoint returned 404; its commit identity remains receipt/request-backed, not independently revalidated here. This availability limit is not a differing identity. No source was changed.

| SEL1 replay row / geometry | Mode; unwind | Accepted failures / total (unreachable); covers |
|---|---|---|
| merge-raw-closure-on: u64 len8, scratch48, src[32..40], dst[0..8] | Check actual bidirectional_merge;34 | 0/572 (16);5/5 |
| merge-profile-closure-on: u8 N9, scratch48, both backings | Check concrete closure profile;34 | 0/1030 (68);2/2 |
| sort4-closure-on: u64 src4/dst4 | Check sort4_stable;16 | 0/753 (14);3/3 including return |
| swap-if-less-closure-on: u64 backing4 | Check swap_if_less;8 | 0/585 (12);6/6 |
| raw-legal-on: u64 ordinary sort4 src4/dst4 | Original body;16 | 0/382 (12);2/2 |
| raw-negative-on: same geometry, source[1] unwritten | Original body;16 | Exactly1/382, intended uninitialized u64 read;2/2 |

Negative binding: `sort4_stable::<u64, …read_less_u64>.safety_check.1`, smallsort.rs:751:26. Legal returns were reached; the negative's verifier exit1 is intended. These bounded closure-comparator results are not all T/N, not the function-pointer comparator profile, not whole SmallSort, and do not address #5104. No older C2 measurement is attributed to SEL1.

## Independent sorting and outstanding integration

Accepted P0/roadmap §7 inputs: [item2 plan, §3](../../PLAN-CH8-ITEM2-SORTING-v2.md), [roadmap](../../ROADMAP-CH8-ITEMS1-2-FOUR-WORKERS.md), [dispatch ledger](../../CH8-DISPATCH-LEDGER.md). Sorting S starts from std `872d5a43380752786415bc00d2a12ce0e930cb37` with clean upstream Kani `0aac16ef62da9e9d5645782d458593e5d78143ba`, uninit/value OFF, threshold16/32 and actual checked trait-method contracts. No new S proof is claimed by this package. Safety A retains its SEL1/std70ba+overlay source, arbitrary-bool closures and flags. A shared root name or upstream baseline cannot combine S functional evidence with SEL1 safety evidence.

The original [#752](https://github.com/model-checking/verify-rust-std/pull/752) proposal binds std872d to Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, not SEL1 or the proposed clean upstream. The item2 plan's organizer-pin snapshot is historical, not refreshed in this session. The [published #56 answer](https://github.com/model-checking/verify-rust-std/issues/56#issuecomment-2611410906), [challenge text](https://github.com/model-checking/verify-rust-std/blob/25b2b24c82a960734a2bab082784747b9b785177/doc/src/challenges/0008-smallsort.md), and [review archive](https://github.com/Tiramisu-Cake/verify-rust-std/blob/d70d85eb021bd7e264f22acab0c371502c2420a0/research/challenge-8/requirements-evidence-2026-10-24/cross_challenge_precedents.md) were read through the connector. The archive is secondary interpretation, not a new organizer ruling; symbolic lengths and six-body accounting are our proposal.

Open gates: owner text/status/PR-number decisions; upstream review/merges; organizer pin/step adoption and actual organizer CI. No mismatched Kani source/parent or accepted-receipt identity was found. Missing local overlay availability limits independent binding as stated above. Function-pointer/trait-object dispatch, Replace/recursion shadow transfer, delayed cycles and loop-contract havoc remain unsupported or unqualified. No historical ledger, verdict or `download_verified` field was altered.
