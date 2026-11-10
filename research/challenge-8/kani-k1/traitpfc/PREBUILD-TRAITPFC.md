# TRAITPFC G1 — exact pre-build packet

Branch `experiment/kani-k1-traitpfc-20261110`, worktree `/root/verify-rust-std-kani-traitpfc`.
Stable owner `k1-merge`; stage `traitpfc-g1`; request `traitpfc-g1-20261110-01`.
Research only. **PRE-BUILD review pending; no dispatch GO; every proof row is NOT_RUN.**
The final published PRE-BUILD REVIEW marker binds the exact research packet source SHA.
Library commit `ea4528ac91bf715b9477c263495e0db325957923`;
library tree `7fd692282cc522f3d12c2f1c00fc25f5557884f6`.
Tooling/base `9b1758ab817af005e96fd52a5fc940d4b6acf984`, library tree
`abeb039de15785366c0dc2807ed1ef50b85b50d7`.
Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`; nightly-2026-10-23 unchanged.
Base `slice/sort` and `library/core/Cargo.toml` match `872d5a4338` byte-for-byte.
Library diff is exactly `smallsort.rs`, `smallsort/verify.rs`, `smallsort/verify/trait_contracts.rs`.

## Contracts and domains

Exact added attribute bytes are in `contracts.json`; no ensures, including no ensures(true).
T1 requires len < 2 OR scratch capacity >= len + 16, expressed using checked_sub to avoid overflow.
The helper returns before any scratch use at len < 2; otherwise it explicitly aborts if len + 16
exceeds scratch capacity. It writes scratch via typed element copies and writes v via merge.
`modifies(v, scratch)` keeps scratch typed as `[MaybeUninit<T>]`; no assume_init or T slice cast.
For N2 the minimum satisfying capacity is 18 (even though this path writes only two scratch slots).
T2/T3 require either the fallback threshold, or len <= the selected threshold. Thus the fallback
path acquires no unnecessary length bound; network/general are bounded at 32, protecting their
32/48-element private arrays and general's extra 16 slots. For u64, T2 forwards to T3's network
specialization, and N2 takes insertion. Both write sets are exactly `modifies(v)`.
These element-only frames require comparators that write nowhere else. G1 proves only the listed
concrete comparator/type/geometry domains; no generic sorting or arbitrary-FnMut theorem is claimed.
The opt-in module uses one named `trait_less_u64` function item (`a < b`) for all six new rows.
R1/R2 preserve their existing comparators, contracts and stubs, as required for unchanged regressions.

Kani source was inspected only at the exact pinned commit; file hashes and findings are in
`kani-source-notes.json`. `library/kani/src/contracts.rs:168-174` explicitly permits any one
specification attribute and defaults absent conditions to true. `MaybeUninit<u64>` implements
Arbitrary; Pointer handles its mutable slice without reading it as initialized u64.
The pin's `generic_trait_specialization.rs` demonstrates fully qualified method-generic PFC and
stub paths on non-default specialization. Acceptance of our real blanket impls is still NOT_RUN.

## Rows and exact expectations

Full names, T/F/N, scratch, backing geometry, stubs, unwind, all cover messages and S2's exact
source hash/coordinate are frozen in `expected-rows.json`. No harness has should_panic.

| Row | Target/root (new roots in trait_contracts) | Geometry | Expect | Covers |
|---|---|---|---|---|
| P1 | stable_safety_u64_len2 / PFC T1 | array2 + separate uninit scratch18 | SUCCESS, 0 failed | 3/3 |
| P2 | unstable_safety_u64_len2 / PFC T2 | array2 | SUCCESS, 0 failed | 3/3 |
| P3 | freeze_safety_u64_backing4 / PFC T3 | backing4, active 1..3; exterior frame | SUCCESS, 0 failed | 3/3 |
| S0 | real_forwarding_sorts_u64_backing4 | backing4, active 1..3; real T2 | SUCCESS, sorted + frame | 0 |
| S1 | verified_forwarding_frame_u64_backing4 | same; T3 stub, call T2 | SUCCESS, frame | 0 |
| S2 | rejects_verified_forwarding_sorted_u64_backing4 | exact S0 body; T3 stub | FAILED, exactly 1: `forwarded output is sorted` | 0 |
| R1 | scratch_geometry::stable_u64_min_scratch_n2 | u64 array2, scratch18 | SUCCESS, 0 failed | 2/2 |
| R2 | forwarding_contracts::unstable_byte_n2 | u8 backing4, active 1..3 | SUCCESS, 0 failed | 7/7 |

P1-P3 save input_descending = v[1] < v[0] before the call, then cover that saved bool, its negation,
and normal return. P3 checks both outside elements. S0/S2 have byte-identical function bodies;
S1's body removes only the sortedness assertion. All consumer calls go through real T2, with only
T3 selected by stub_verified. Require the S0-success/S2-designated-failure pair and available T3
binding diagnostics; a mere FAILED status or the expected-check substring alone is insufficient.
R1 directly invokes the real stable Freeze specialization with minimal scratch and full-value counts.
R2's existing wrapper PFC executes the real unstable Freeze+Copy trait entry and checks sortedness,
full-value preservation and exterior frame. Neither regression root stubs the trait methods.

## Static checks and inherited line-length exception

Run `python3 -B research/challenge-8/kani-k1/traitpfc/check_traitpfc.py` from the worktree.
RENAMEMODS lexer/expander: all 571 previous expanded items and 248 conservative identifier closures
are token-identical. All previous verify files are byte-identical except the cfg-gated module map.
Removing only the exact added attributes reproduces baseline smallsort.rs bytes, preserving every
method body, signature, bound, inline(always), and default marker. Tooling/workflows/pins are frozen.
Ordinary = 235; cfg-on = 248 + 6 = 254. Expected names/hash files are source inventories, not compiler
inventory or proof evidence. No extra native-inventory build is requested.
Authorized rustfmt wrapper --check: zero diff. No NEW Rust line exceeds 100 characters.
**Review exception:** baseline smallsort.rs already contains three >100-character comment lines:
the source URL (152), PANIC SAFETY comment (103), and equal-comparison comment (103). They remain
byte-identical to obey the stronger explicit no-other-smallsort-edits restriction. The report lists
all three verbatim; literal zero overlong lines in the whole file is not claimed. Review must resolve
this task wording conflict before dispatch. Existing verify.rs trait-contract absence prose is also
left byte-identical under the one-module-entry restriction; this opt-in pilot's scope is recorded here.

## Request, flags, time and reservation

Root RUN-REQUEST.json equals this packet's copy. SHA256
`1370f5eb029023967b38644f579d221677123b63938e987114d8dde27afe9c5e`.
Diagnostic, controls=true, inventory=false, jobs=1, standard4, exactly 8 rows, --harness-timeout 5m.
`kani-args.txt` and `rustflags.txt` are generated by the unchanged validator; RUSTFLAGS is exactly
`--cfg kani_smallsort_controls`. The runner retains organizer --no-assert-contracts and object-bits 12,
its existing unstable feature flags and default solver. Uninit/value-validity checks are not enabled.
New roots unwind 32; R1 unwind 34, R2 unwind 16, unchanged. Five minutes at N2 is adequate as a bounded
trial; no automatic 10-minute expansion. Actual compile/solve times and all check counts remain unknown.

Unchanged dispatcher: paid timeout = 8 x 5 + 30 = **70 minutes**, below task maximum 120.
Runner cutoff = 8 x 5 + 24 = **64 minutes** after validation. Planning allocation: deps/setup 4 min,
new pinned Kani source build 10 min, std frontend/instrumentation 6 min, eight serial rows 40 min,
runner slack 4 min, then summary/upload 6 min. Source build is included; estimates do not prove
completion, and overruns must remain TIMEOUT/RUNNER_ERROR rather than justify a retry or cap increase.
G1 worst-case reserve = 70 x $0.0135 = **$0.9450**. Own cap $2; spent $0; headroom $1.0550.
One eligible compile-error repair, also 70 min, would make worst-case two-build spend **$1.8900**,
leaving $0.1100. Eligibility is limited to harness attribute paths/qualification or contract attribute
syntax, never core bodies/bounds/default/inline or a resolver workaround; publish a new exact packet
for review. A frontend resolution refusal is itself a result. Retry, unsupported/timeout repair,
extra inventory build and any third build are forbidden.
Project observation: 254 builds; used $109.1985; unfinished reserve $0; cap $118.96; remaining $9.7615.
With G1 reserve: $110.1435; with both worst-case reserves: $111.0885 <= project cap.
Main 300 + closeout 30 min; worst-case two 70-minute builds fit. No active T0 was supplied: bind the
execution window at coordinator GO and preserve any existing clock. Refresh budgets/slot/deadline
before dispatch; this static packet and budget snapshot do not reserve a slot or authorize a build.

## Execution only after exact-packet GO

1. Confirm published exact SHA, unchanged library/tooling/request bytes, explicit exception disposition,
   own/project cap and remaining execution window. Record GO/T0 and dispatch exactly once via k1g.sh.
2. Immediately `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`, then end the turn. No status loop.
3. On queued completion use bounded k1g.sh status, summary, summary BUILD 0 8, peaks, budget BUILD,
   check-tooling BUILD 9b1758ab817af005e96fd52a5fc940d4b6acf984; save interfaces' output under traitpfc.
4. Use bounded log-grep for complete S2 failure count/text/location, covers, T3 stub binding, warnings
   and any frontend/unsupported diagnostic; refine saturated queries. Do not read helper cache/raw logs.
   Optional smallsort-brief only if indexed. Keep resolution, unsupported, timeout and ordinary FAILED
   distinct, and never infer NOT_RUN from no-match. Do not repair historical evidence records.
5. RESULT-TRAITPFC.md <=40 lines: exact identities, literal contracts, all 8 statuses/times/counts/covers,
   every failed check in full, warning/diagnostic classes, actual expense and constrained G2 implications.
   Commit/push research [skip ci] without force; finish REVIEW REQUEST <sha> / TRAITPFC G1 ЗАВЕРШЁН; stop.
