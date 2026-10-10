# Actual C1 → C2 → C3: experimental bounded projection

Session starts 2026-10-10 10:20:59 UTC; main deadline 12:20:59, finish-only
deadline 12:50:59. Policy read: `c7ca8c467aecf10a4b53039372ee97714f854ee3`;
existing adoption/ACK retained. Separate owner select-sort4 account: 3600
createTime→finishTime seconds, no carry from closed accounts.

Actual obligation: `sort4_stable` at SmallSort source blob
`40939f922bcb6fdc7ee0d30427fa861827043827`, called by
`small_sort_general_with_scratch`. Extend fresh C1+C2 proof f4abe251 through
actual third call `is_less(&*c, &*a)`, preserving its direct unwind and all
previous outcomes. Bound after C3 recovery before C4; no callable whole-sort4
summary, native→C1 or actual caller proof is implied.

Hypothesis: source-derived Boolean pointer offsets select two owned CURRENT
cells from different halves after C2. Checked selected split and inverse join
helpers expose `(c,a)` and conserve complementary `(b,d)`, then reconstruct
four physical index owners after callback effects. No entry snapshots survive
as pointee-value promises. All four c1/c2 cases are retained.

Domain/posts are the original raw four-cell/F/thread/type/positive-size T and
optional destination contract. Normal and each reachable direct unwind retain
the complete CURRENT source/F/destination resources, original unit return and
leak checks. Source/F/types/positive-size/destination remain supplied at target
entry. No Copy/Freeze/purity/no-panic restriction, runtime/signature changes,
numeric equality ownership rule or new kernel/model/refinement semantics.

Independent GPT-6 Luna design review: conditional GO before implementation.
Fresh source, paired complete MIR and pre-AST capture must refuse before proof;
new exact bound admission pins them before any transformed proof path. Preserve
actual bool casts and pointer arithmetic, bounds/provenance and selected-cell
distinctness. Move only C3 callback `_124.._129` into a third sibling strict
scope, retain a,b,c,d,c1,c2,c3 outside, keep exact allocation/init/address/free
effects on every exit. C1/C2 unwinds never enter C3. Register C3 Output=bool
independently against the compiler HRTB; consume parsed cmp3 binding once.

New profile defaults off and rejects mixed opt-ins; frozen C1/C2 profile gates
and mandatory unbound refusal remain. Same-version selected helpers must be
proved before use. Full source inventory remains five callbacks/eight selects/
four copies. The target projection executes only the first three callbacks.
Fresh full MIR establishes omitted future C4/C5 declaration lifetimes.

Positive: full bounded VF0, helper-before-target, normal plus C1/C2/C3 unwind,
CURRENT recovery, full original posts/return/leak and fresh correspondence.
Negatives: C3 normal/unwind missing debt fail recover_pair comparison_debt;
C3 normal/unwind omitted rejoin fail original CURRENT four-owner post;
normal false post and C1/C2/C3 unwind false asserts test reachable exit paths.
Source/MIR/pre-AST mismatches and unbound refusal are admission/setup controls,
never semantic negatives. Exact first stage/predicate/location reviewed in raw
logs before claiming control acceptance.

PASS → continue actual C4 in remaining main window/budget with its own card,
scope and fresh evidence. Resource failure → localized proof fix with new SHA.
Projection/refinement failure → preserve cause and repair within this profile;
no old proof credit on changed source. New trust requirement → use only narrow
separately authorized compatible strict-cut direction after semantic card and
independent addressed review; do not silently alter the frozen C3 kernel.

## Source-linked selected ownership map (candidate, not proof)

Let x0..x3 denote the existential CURRENT values at C2's normal join.
The four cases below preserve the source's bool casts and `!` precedence;
the numbers are source-array indices, not independently supplied addresses.

| c1 | c2 | selected C3 `(c,a)` | complementary `(b,d)` |
| --- | --- | --- | --- |
| false | false | `(2,0)` = `(x2,x0)` | `(1,3)` = `(x1,x3)` |
| false | true | `(3,0)` = `(x3,x0)` | `(1,2)` = `(x1,x2)` |
| true | false | `(2,1)` = `(x2,x1)` | `(0,3)` = `(x0,x3)` |
| true | true | `(3,1)` = `(x3,x1)` | `(0,2)` = `(x0,x2)` |

Each chosen index is in 0..3; the left half is 0/1 and right half 2/3.
The source's `.add` retains base provenance. Positive T size and array bounds
give distinct selected cells; the permission source is the actual array and
foreach split, never numeric pointer equality. Frozen Bool→Int lowering in
`src/verifast1.ml` maps the cast to a 1/0 conditional. Geometry must be proved
and used **before** the runtime pointer setup, because later bounds cannot
discharge an earlier `.add` obligation.

After C3, recover_pair returns fresh existential values at c and a. The inverse
join consumes these and the complementary b/d owners in the same four cases,
reconstructing physical index order. It does not substitute x0..x3 for callback
outputs. Same-version helper bodies and the unified target must actually pass;
this source analysis alone gives no proof credit.
