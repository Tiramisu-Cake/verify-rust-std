# C3c bounded analysis notes

## MacOS targets and source discrepancies

`mac-times.tsv` contains nine successful SmallSort harmonics at or above 400 s. Exact names, source times, and candidate mapping are in `analysis-plan.json`. The three 600 s timeouts are the exact names supplied by TASK-C3C. This gives 12 baseline target rows; timeout durations are censored, not observed times.

The TSVs have no header or metadata block. Mac source is bound by task/source-bindings to Actions run `40748125754`, pre-C3a SHA `6cfc76cb211d088aebaff8a449bcac953e97f942`. Raw TSV counts/sums: macOS 2,313 rows (2,068 distinct names), 28,518.6 s all rows; 322 SmallSort rows, 25,367.5 s. Task facts say 28,524 s all harmonics and 25,368 s SmallSort. SmallSort agrees after rounding; all-row sum differs by 5.4 s. Ubuntu has 2,065 rows (1,826 distinct names), 8,791.2 s all rows; 105 SmallSort rows, 4,682.5 s. Task says 1,829 Ubuntu harmonics, three more than distinct TSV names. Preserve discrepancies; do not deduplicate rows to force a count. The inputs have no per-row source SHA, run id, thread, start/stop, or unfinished-harness metadata.

## Ubuntu in-flight names

The exact three Ubuntu in-flight harmonics cannot be derived from the provided TSV. Final rows, highest-time rows, or the three highest-time SmallSort rows do not establish which threads were active when the runner stopped. Do not guess. Needed: bounded stop-time per-thread snapshot or exact coordinator-provided names with run/source identities. This remains unresolved in `analysis-plan.json`.

## Matched probes

Use baseline `e96555151df91080fa0ccc106f60ee38a919c50e` and candidate `fd854ca7545df59b5307b629155ca61dc3d74d0f`, both jobs=3 and per-harness cutoff 180 s. Direct source diff confirmed START=5 exact tails END=6..16; START=6 END=7..16; route successors `route_safety_{general,noncopy,stable}_u64_n{31,32}`. Baseline has 12 target rows. Candidate target estimate is 39 successors: 15 START1 tails, 10 START6 tails, 6 n31/n32 route successors, 6 remaining heavy names, and 2 remaining timeout names. Also probe correct general/stable u8 N14 (one old model → two route models) and fallback u64 N8 (one → one) to support correct-family calibration; add the same 8 common assembly rows. Final requests contain 50 candidate rows and 22 baseline rows. Check all names/counts against final bounded inventory before dispatch.

Keep per-row times, censored counts, family timing sums, page/build/request/source identities, and bounded peaks separate. Do not compare sums across split groups as a single-harness speedup. For calibration use successful matched baseline harmonics on P-6 macOS vs GCB e965; source diff confirms P-6 to e965 changes only verify registration, smoke registration, and adds types, so common correct/merge/network models are unchanged subject to per-name solver/stub/unwind identity. Transfer of that coefficient onto the C3c candidate's changed models is a forecast inference, not a measured candidate calibration or acceptance.

## Model eligibility and censored ratios

The supplied Ubuntu measurements are not GCB data. For exact common baseline e965 models, eligible point ratios require matching names and verified same callee, stubs, solver, and unwind. Baseline default and candidate explicit solver both use CaDiCaL. Candidate `correct` rows are excluded because E moves user covers out of ordinary and R splits two models into four. Candidate `merge` rows are excluded because E changes cover obligations and R splits six models into twelve. Candidate `network` rows are excluded because E changes covers and D changes tail/dispatch model shapes. The candidate's CaDiCaL solver and reviewed D unwind are unchanged; those facts do not remove the other model differences. The C3a predicate-smoke row is excluded from P-6 pairing; other smoke rows are conditional. `types` has no P-6 counterpart.

Retain censored cases. If GCB times out but Mac succeeds, `Mac/GCB <= Mac_time / GCB_timeout` is only an upper bound. If Mac times out but GCB succeeds, `Mac/GCB >= Mac_timeout / GCB_time` is only a lower bound. Neither is a point ratio.

The candidate should also be source-checked against review fixes: `measurement_ok` must not require ordinary covers after E; the three dispatch reachability harnesses need the actual `kani::cover(true)` after dispatch; exact-tail literals must assert `START < END < 17`; controls route covers should avoid constant-stable UNSAT witnesses. Current candidate source diff confirms real post-dispatch covers and exact-tail mappings; source/proof audit of the remaining points is still required.

## Helper

`analysis-pages.py` consumes only explicitly supplied bounded `.rows.tsv` and `.inventory-*.page` exports. It preserves repeated harness-name rows, checks pagination and source identity consistency, compares inventory and result multiplicities, and reports gaps/extras, failures/timeouts, censored rows, per-family sums/maxima, slow rows, and identities. It does not fetch data, open full logs, or invent missing records. Example after pages exist:

```sh
python3 research/challenge-8/kani-k1/c3c/analysis-pages.py \
  --rows 'research/challenge-8/kani-k1/c3c/evidence/*.rows.tsv' \
  --inventory-pages 'research/challenge-8/kani-k1/c3c/evidence/*.inventory-*.page' \
  --out research/challenge-8/kani-k1/c3c/analysis-pages.json
```

## Recommendation

The Ubuntu stop snapshot is a real data gap. Expand split successors from final inventory; retain row and family sums separately with censored counts and peak memory. Use baseline P-6/e965 for unchanged-model calibration, then label any coefficient transfer to changed candidate models as forecast inference. No candidate timing, proof acceptance, or full-job claim can be made from these inputs alone.
