# KANI3300 U1T — bounded observations and reader limitation

Build `ff0988c7-d2f2-4872-b4ea-be581d9de02f`, Cloud terminal FAILURE (watch delivery).
Request `kani3300-u1t-native-20261111-01`; head `21f7d3dffc1da40f8c647237d933c9fc8f9da39a`.
Request SHA-256 `f0e8f7ca4082f69108ded989780eefe69ff89b4d4c6941427b1b07a38be2768b`.
Patch SHA-256 `37689b6c615b6c8e4f321113f07c6c8d124cdf2aa30ff94eeda909a6ba18a1e6`.
Cloud applied tree `0e16a12fd4ce531e03c121c1160243426a51f49e` exactly matches local preflight.
These are observations from the permitted reporting interface; no raw logs/archives or local raw evidence were inspected.
Historical ledgers, download_verified, U1 package, Kani code, request and candidate patch remain unchanged.

## Reporting observations

`k1g.sh summary BUILD` returned TOOL_ERROR, gate false, Kani build success, 12 native rows:

| Offset | Suffix after `maybe-uninit-` | Native | wall s | Description substring in own output |
|---|---|---|---|---|
| 0 | review-overwrite-copy | ERROR | 1.770 | uninit `[u8; 2]` |
| 1 | review-overlap-copy | ERROR | 3.025 | uninit `u8` |
| 2 | review-repeat-local | ERROR | 2.071 | uninit `u64` |
| 3 | review-reset-zst | ERROR | 1.971 | uninit `u64` |
| 4 | review-padded-manually-drop | PASS | 0.967 | uninit `Padded` |
| 5 | review-argument-return | ERROR | 1.620 | uninit `u16` |
| 6 | review-positive | PASS | 9.951 | none required |
| 7 | initialized | PASS | 10.547 | none required |
| 8 | scratch-array | PASS | 2.172 | none required |
| 9 | partial-copy | PASS | 2.824 | uninit `[u8; 4]` |
| 10 | reset-alias | PASS | 1.419 | uninit `u8` |
| 11 | volatile-read | PASS | 0.917 | uninit `*const u8` |

For each ERROR, summary reports only `requested native PASS did not pass`.
The diagnostic field is selected by substring presence; a property description can also accompany SUCCESS.
Consequently this field alone cannot distinguish a golden naming/format mismatch from a false SUCCESS or another failure.
No root cause or soundness verdict is inferred for the five ERROR selectors; overlap's two directions remain unresolved.

`native BUILD 4 2` returned VALIDATED offset 4, count 1, next_offset 5: padded selector native_status ok, exit_code 0, errors [].
Its golden requires the harness-specific FAILURE/uninit Padded, FAILED and one failed harness.
`native BUILD 5 1` returned the size error below.
`native BUILD 6 4` returned VALIDATED offsets 6–9, next_offset 10; `native BUILD 10 2` returned offsets 10–11, next_offset null.
All seven available records have native_status ok, exit_code 0, errors [].
Offsets 6–8 explicitly invoke `--require-success`; their unchanged golden totals require respectively 7, 8 and 1 successful harnesses.
The negative expected-mode selector exit 0 is compiletest's exit, and does not mean Kani verification SUCCESS.

`check-tooling BUILD c98d7cee0d509b1633ab61c9a1ae989e286c8e2a` passed pool, lane files, bound tooling,
request SHA, patch specification, published patch SHA and Cloud applied tree checks.
Native binary identities: release kani-compiler SHA-256 `d2ea5c75190b1d4f179a27d9bd3493ad30cbb2f3d9044d994f5723bbac908fe6`,
release kani-driver SHA-256 `653ba5660b15f16fb8e7b989cd0fb47b655bf93fcc415d372f988f592752de3f`; compiletest profile dev.
Generic summary says uninit checks off because harness-request flags are absent; fixture headers explicitly enable `-Z uninit-checks`.
No passing full matrix, absence of ignored/timeouts in unread records, independent formal proof credit, or full negative acceptance is asserted.

## Exact reader limitation

The unchanged reader is `research/challenge-8/kani-k1/tools/kani_k1.py`, tooling base `c98d7cee0d509b1633ab61c9a1ae989e286c8e2a`,
SHA-256 `c199cace580a89f5ee7113aafe2d6757bf23c698d873a0b14589d9f7908a43b9`.
`native BUILD 0 2` and `native BUILD 2 2` reduced internally to a single record and returned exit 2;
individual `native BUILD 1 1`, `native BUILD 3 1`, `native BUILD 5 1` also returned exit 2.
Exact response for every failed page:

```text
page-summary: one native record exceeds the bounded page size
```

Static reader inspection: `native_page` repeats build/binary metadata with each record, enforces MAX_MD_BYTES = 12000,
and raises once even one record cannot fit. It offers no property selector or excerpt subpagination.
This establishes an interface limitation, not a diagnosis of the failed Kani tests.
The current standard Brief route was also tried once:
`/usr/local/bin/smallsort-brief ff0988c7-d2f2-4872-b4ea-be581d9de02f` returned exit 1, exactly:

```text
smallsort-brief: Reader report or query route is unavailable (HTTP 404)
```

No raw fallback or alteration of reporting/tooling was attempted.
Required coordinator data: bounded `native.tests[i].errors`, `output_excerpt`, and actual property FAILURE/SUCCESS plus harness/Complete lines,
for i = 0,1,2,3,5; overlap needs both harness outcomes. Retain exact build/head/request/patch identities and excerpt coverage/truncation.
This requests specific bounded data, not authorization for raw audit or a new proof build.
If any negative SUCCESS is established, preserve its minimal fixture and source location and stop with `Координатор, вопрос`.
Production fixes, golden relaxation, and automatic retry are not authorized by the observed size error.

## Accounting and boundary

`k1g.sh budget BUILD` returned `1 0.1080 0.0000`: one finished build, actual $0.1080, reserve $0.
A repeat of this packet would reserve $0.4725, yielding $0.5805 > stage cap $0.50.
Even the lane's minimum 1-minute work + 30-minute overhead reserves $0.4185, yielding $0.5265 > cap.
No repair was prepared/dispatched; no timeout was shortened. Existing project/owner coordination remains in force.
The only remaining diagnostic work requires unavailable bounded fields; the only further native build requires budget and a new GO.
Stop at that boundary with five UNKNOWN candidate verdicts; include only confirmed padded and positive fixtures in a currently supported upstream recommendation.
