# S1-04 envelope — preparation only

No reservation, dispatch, push, publication or ledger change. All budgets below are proposed; owner GO must allocate a new window and budget. This package does not reuse the exhausted S1 allocation.

## Measured basis and uncertainty

S1-03 COST.md: compile boundaries 25.879–32.706 s/group, two Cell exported verification times total653.346s, other15 light/model/control/legal-companion rows total53.314s; four symbolic heavy rows each timeout600s. New exact-N proof times and activation false-ensures times are NOT_RUN. Exported VT is not full root wall; group RSS is not per-root RSS. No claim that the split will be faster or satisfy R8.

Four heavy symbolic rows become16 scheduled fixed-N roots; originals remain in source and manifest legacy metadata, with acceptance only by complete same-pin union N0/1/2/3. Total35 scheduled roots. Fourteen explicit groups:3 light (3/3/9 roots),2 activation,1 Cell (2 roots),8 heavy (two N cases each).

Heavy N0/N1 and N2/N3 pairs balance export granularity and compilation:8 heavy groups versus16 singletons saves about240s at30s/group, while isolating each original target and keeping at most two fixed-N results in one export. Four-root groups would save another120s but lose finer partial/error attribution. Total compile planning≈420s versus prior3 groups≈90s; 900s compile cap is unchanged. Unwind and600s stock root timeout remain unchanged; stock timeout excludes full instrumentation wall. Group wall watchdog covers that gap; a capped/incomplete run remains UNKNOWN.

Measured light+Cell VT baseline≈706.66s; add≈420s compile planning, unmeasured activation0..1200s and fixed-N0..9600s: arithmetic sensitivity≈1127..11927s before repeated tool setup/upload/instrumentation. This is a scenario range, not a guaranteed bound or measured prediction. Tool setup wall is not available in the intake measurements; use the existing1800s hard setup envelope per job, not an invented average.

## One job

Complete conservative phase:14*900 +35*600 +14*10 cleanup =33740s (9h22m20s). Setup1800 +closeout900 gives36440s (10h7m20s), so the existing120min job cannot cover it. The new180min job also cannot host the full serial package. No smaller root/compile bounds are claimed from the split.

A serial one-job-at-a-time plan can instead dispatch four frozen partitions, each with phase8100s and setup1800/reserve900 (180min/job). Partition A light-model+corruption:5420s; B light-controls+activation-default:7820s; C activation-override+Cell+first2 heavy pairs:7840s; D remaining6 heavy pairs:12660s does not fit. Therefore at least **five dispatches** are needed: split D into3+3 pairs (6330s each). Each dispatch must select only its exact groups and have its own authorization/accounting. This alternative requires a single-job workflow variant before publication; it is not the selected frozen YAML.

## Selected matrix, max-parallel1

One workflow dispatch (one authorized matching branch publication) creates14 jobs. Four ordered stages are light→activation→Cell→heavy; stage dependencies wait for all prior group jobs to finish. `fail-fast:false` and stage `always() && !cancelled()` preserve later observations when earlier qualification remains UNKNOWN. Every job has one explicit group, independent setup, unique artifact and subset fallback. This is **one dispatch, fourteen jobs**, not fourteen dispatches. A corrective run would be another dispatch and needs separate authorization; reruns are rejected.

For k roots, group envelope=900+600k+10. Largest group (9 light roots)=6310s; adding setup1800/reserve900=9010s <10800s job cap. Phase cap8100s leaves room for watchdog/cleanup without truncating the planned group envelope. Full max-parallel1 conservative execution envelope=33740+14*2700=71540s (19h52m20s), excluding queue delays. This must be authorized as a complete workflow window/budget;180min is a per-job cap, not an overall workflow claim.

## Matrix max-parallel2 option

Requires changing and reviewing the YAML/preflight pin before publication; current frozen choice is1. With stage ordering and group durations including setup/closeout, conservative stage envelopes are14420s light,4210s activation,4810s Cell and19240s heavy: total42680s (11h51m20s), excluding queue. Aggregate job-time cap remains71540s; parallelism reduces elapsed time, not billed work. One dispatch, fourteen jobs. Each concurrent job also needs its own host memory headroom; prior group peak≈7.82GiB is not a per-root resource bound.

## Admission and collection

Owner must choose and authorize complete elapsed/aggregate budgets, hosting lane and publication. No active phase is registered here. CI runner verifies source/tool pins before each group, restores overlays, retains primary failures and original exits. Six negative assertions use exact frozen ID/file/line/class; activation wrapper oracles remain UNBOUND until independent property binding. Success messages/covers and exception-role admission remain pending with this stock exporter. Consequently execution readiness does not grant qualified acceptance or proof credit; all four union members plus exact independent binding are required.
