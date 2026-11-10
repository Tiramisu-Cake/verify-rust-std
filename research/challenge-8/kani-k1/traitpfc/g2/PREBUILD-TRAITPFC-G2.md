# TRAITPFC G2 — exact pre-build packet

Worktree `/root/verify-rust-std-kani-traitpfc`, branch `experiment/kani-k1-traitpfc-20261110`.
Owner `k1-merge`; slug `traitpfc`; stage `traitpfc-g2`; request `traitpfc-g2-20261110-01`.
Research only. PRE-BUILD review pending; no dispatch authorized; all ten proof rows NOT_RUN.
The final PRE-BUILD REVIEW marker binds the exact published source SHA of this packet.
G1 baseline `feb589a30688082588fd0bdb1084aaeffb849696`.
Tooling base `9b1758ab817af005e96fd52a5fc940d4b6acf984`.
Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, nightly-2026-10-23, unchanged.
Library commit/tree: see `identities.json` (recorded after the separate library commit).
Request/source/inventory SHA256 values: `check-report.json`.

## Exact model and contracts

`verify::trait_model` is registered without `kani_smallsort_controls` under the existing
`#[cfg(kani)] mod verify`. Only harnesses remain opt-in. No new core feature gate or API bound.
The dispatcher is `PairModel<T, F> for ()`: all four blanket-impl methods are `default`,
with one specialization `impl PairModel<u64, U64Cmp> for ()`.
Exact signatures (the tuple is Copy):

```rust
pub(crate) type U64Cmp = fn(&u64, &u64) -> bool;
pub(crate) fn canonical_less_u64(a: &u64, b: &u64) -> bool;
pub(crate) trait PairModel<T, F> {
    fn enabled(cmp: &F, len: usize) -> bool;
    fn snapshot(base: *const T, len: usize) -> (u64, u64);
    fn pair_is_sorted(base: *const T, len: usize) -> bool;
    fn pair_permutation(base: *const T, len: usize, pre: (u64, u64)) -> bool;
}
```

Default: enabled=false, snapshot=(0,0), both checks=true; no dereference or callback.
Specialization: enabled iff len==2 AND comparator address equals canonical_less_u64's address,
as a direct cast to `*const ()`, matching the existing profile comparator guard.
Canonical comparator body is `a < b`; reverse comparator body is `a > b`.
Snapshot reads exactly two initialized u64s only if len==2, otherwise returns (0,0).
Thus eager old-capture is valid even for a disabled comparator or other slice length.
Sortedness is `post.0 <= post.1`; permutation is `post == pre || post == (pre.1, pre.0)`.
No arbitrary-F downcast, transmute, size test, comparator invocation, or global ghost state.

Identical added attribute on T1, T2, T3, verbatim:

```rust
    #[cfg_attr(kani, crate::kani::ensures(|_|
        !old(<() as verify::trait_model::PairModel<T, F>>::enabled(is_less, v.len()))
            || (<() as verify::trait_model::PairModel<T, F>>::pair_is_sorted(
                v.as_ptr(), v.len(),
            )
                && <() as verify::trait_model::PairModel<T, F>>::pair_permutation(
                    v.as_ptr(), v.len(),
                    old(<() as verify::trait_model::PairModel<T, F>>::snapshot(
                        v.as_ptr(), v.len(),
                    )),
                ))
    ))]
```

Native `old`, no fallback and no new requires. Both pre-state enabled and full-value snapshot
are captured by old, not reconstructed from post-state. No old(v), clone, or retained reference.
G1 requires/modifies remain byte-identical. Disabled comparators retain G1 frame-only scope.
The G1 rule restricting comparator writes to the proved frame domains still applies.
Native old syntax follows existing old(model(...)) wrappers in this library. Acceptance of this
raw-pointer tuple capture and the new blanket specialization is a compiler/proof hypothesis.
No source check establishes Kani binding or successful formal verification.

## Rows and acceptance

Exact names, F/layout/unwind, covers, and designated failure coordinates: `expected-rows.json`.
All input values are unrestricted `kani::any()`; no assume or should_panic is introduced.

| Row | Root (trait_contracts unless qualified) | Expect | Covers |
|---|---|---|---|
| E1 | stable_ensures_u64_len2; PFC T1, array2 + scratch18 | SUCCESS | 5 |
| E2 | unstable_ensures_u64_backing4; PFC T2, active 1..3 | SUCCESS | 5 |
| E3 | freeze_ensures_u64_backing4; PFC T3, active 1..3 | SUCCESS | 5 |
| C1 | verified_forwarding_ensures_u64_backing4; T3 stub through T2 | SUCCESS | 1 |
| N1 | rejects_high_bit_corruption_u64_pair | FAILED exactly 1 | 0 |
| N2 | G1 rejects_verified_forwarding_sorted_u64_backing4, unchanged | FAILED exactly 1 | 0 |
| N3 | rejects_reverse_pointer_sorted_u64_backing4; same U64Cmp type | FAILED exactly 1 | 0 |
| W1 | G1 freeze_safety_u64_backing4, unchanged | SUCCESS | 3 |
| R1 | scratch_geometry::stable_u64_min_scratch_n2, unchanged | SUCCESS | 2 |
| R2 | forwarding_contracts::unstable_byte_n2, unchanged | SUCCESS | 7 |

E1-E3/C1 explicitly bind `let mut cmp: U64Cmp = canonical_less_u64`, assert and cover enabled
before calling. E1-E3 save descending/equal predicates before calling, then cover both input
branches, equal inputs, and normal return. E2/E3/C1 and N3 check both exterior backing elements.
C1 saves `(v[0], v[1])` independently of the model before calling real T2 with only T3 stubbed;
post assertions use direct u64 comparisons for sortedness and both full-value permutations.
N1 first asserts the unchanged pair passes the specialized checker, then XORs bit 63 of v[0]
and asserts the identical checker. Its sole failure must be `high-bit corruption preserves full pair`.
N2 uses its unchanged function-item F, so the model is default/disabled; its sole failure must
be `forwarded output is sorted`. N3 asserts !enabled for reverse_less before the stubbed call;
its sole failure must be `reverse pointer output is sorted`, not a requires/enabled/frame check.
W1 uses the unchanged G1 function-item F; its strong model is disabled.
All three designated failures require exact failed/total checks, full messages and locations;
expected status/substrings alone are insufficient. Require the T3 verified-stub binding diagnostic.

PASS additionally requires native cfg-off inventory exactly equal to all 235 expected names.
The unchanged gcb-k1.sh diagnostic inventory path (lines 128-138) performs list before exporting
controls RUSTFLAGS at line 166. Thus cfg-off inventory is expected; verify actual flags in evidence.
Rows run with controls on. Attribute both to one library tree and their own actual flags.
If native inventory is unavailable or controls-on, report inventory NOT_RUN and integration PARTIAL.
Do not substitute the source inventory for compiler evidence or claim PASS without ordinary compile.

## Static checks

Run `python3 -B research/challenge-8/kani-k1/traitpfc/check_traitpfc_g2.py` from this worktree.
Uses RENAMEMODS lexer/expander. All 235 ordinary roots, all 254 prior root closures, prior callback
items/attributes, and G1 opt-in root bytes are preserved. cfg-on = 254 + 6 = 260.
Exact core source stripping permits only the three ensures above; requires/modifies, runtime
bodies, signatures, bounds, inline, default, and core feature gates remain unchanged.
Library whitelist: smallsort.rs, verify.rs map/registration, trait_contracts.rs suffix, trait_model.rs.
The verify.rs module-map doc is the sole changed previous expanded item; its exact insertion is checked.
Rustfmt --check via the authorized wrapper: zero diff; no new Rust line >100 characters.
Three inherited upstream overlong comments remain byte-identical (G1 accepted exception).
G1 packet, RESULT, ledger, and evidence remain unmodified. G2 artifacts are isolated in this directory.

## Flags, timing, reservation, and execution boundary

Root RUN-REQUEST.json equals this packet copy. Diagnostic, inventory=true, controls=true,
standard4, jobs=1, ten rows, --harness-timeout 5m. Generated flags: kani-args.txt/rustflags.txt.
New roots unwind32; R1 unwind34 and R2 unwind16 unchanged. Organizer no-assert-contracts,
object-bits12, existing unstable features and default solver unchanged; uninit/value-validity off.

Unchanged dispatcher computes paid timeout = 10*5+30 = 80 minutes, <=120.
Runner cutoff = 10*5+24 = 74 minutes after validation; inventory consumes this same budget.
Planning allocation: setup/pinned Kani build 12m, cfg-off list <=49m (runner's prior estimate),
controls-on compile/ten small N2 rows 9m, remaining runner slack 4m, summary/upload 6m =80m.
This allocation relies on short N2 runs as observed in G1; it does not reserve 5m for every row
in addition to the inventory estimate. There is no timeout/completion guarantee. Preserve TIMEOUT,
RUNNER_ERROR or incomplete-row results rather than retrying. Scripts and budget formulas stay frozen.
Main worst-case reserve: 80*$0.0135 = $1.0800; eligible repair also $1.0800.
Two-build worst case $2.1600 <= own cap $3.00; own G2 spent $0, headroom after both $0.8400.
Project observed used $109.3740, unfinished reserve $0, cap $118.96; headroom $9.5860.
With both worst-case reservations: $111.5340 <= $118.96 (refresh before dispatch).
Budget receipt: prebuild-budget.txt. These calculations do not reserve a slot or authorize dispatch.
Main window300 + closeout30 minutes; T0 begins at coordinator GO, presently unset.

Before dispatch: exact-packet coordinator GO, confirmed SHA/library/tooling/request, window and budget.
One main build. One compile-error repair only, with spent+reserve <=$3 and reviewed changed packet;
limited to syntax/attribute qualification, old-capture form, or the task's conditional ghost fallback.
No retry, third build, cap/window increase, core API/body/gate change, or specialized SmallSort impl.
After dispatch immediately k1g.sh watch BUILD, then end turn; do not poll status in a loop.
On completion: smallsort-brief BUILD first. If unavailable/missing fields, record limitation and use
bounded K-1 summary/rows/peaks/log-grep/check-tooling/budget interfaces; no raw/cache/log archive reads.
Keep frontend/resolution/specialization error, unsupported, TIMEOUT, ordinary FAILED distinct.
Produce RESULT-TRAITPFC-G2.md <=40 lines with literal ensures/signatures, identities, all ten rows,
counts/times/covers/unreachable/full failed checks, actual inventory flags/names, cost and scope limits.
B1 bounded evidence only: no generic T/F, other lengths, additional UB classes or unwind proof claim.
Commit/push research [skip ci]; finish REVIEW REQUEST <sha> / TRAITPFC G2 ЗАВЕРШЁН, stop.
