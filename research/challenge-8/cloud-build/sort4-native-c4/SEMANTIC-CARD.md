# Native-to-C4 obligation card — no trusted delta

Actual std SmallSort blob40939f922bcb6fdc7ee0d30427fa861827043827,
source85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1.
Prior C4 Builda5180cd7/proof203b5925 is a conditional bounded target, not a
callable whole-sort4 summary. Prior native typed Build46bb/proofff5d4b85 is
VF0/82 separately on native production+slice alias, not C4 effective profile.

## Gap map before fresh experiments

| Obligation | Derivation / missing requirement |
| --- | --- |
| Native thread/currentThread/F cell/F own/full source array and T owners | Derive from automatic safe &mut pre, through exact native read-only operations; source first4 via checked array/foreach split. Must freshly reprove on C4 profile. |
| type_interp T/F | Stock explicit logical producers, not automatic native heap entailment; helper controls remove one producer each. |
| v_base value equals native slice base | Actual as_mut_ptr result correspondence. Native alias delta f200a581 exists only on caller-entry chain; frozen C4 lacks that symbol alias. Need fresh first-stage failure, not imported old PASS. |
| len>=4 | Actual sort4 branch len>=8 implies it; earlier native lemma artificial ghost branch does not prove caller selection. |
| source four distinct pointer cells / permissions | Native array/foreach supplies owner resources; positive size plus checked geometry still needed. Numeric equalities never create ownership. |
| size_of T>0 | Not implied by general selected branch: len8–15 admits size0. For len>=16 selected branch forces size>16. Keep explicit positive-size external boundary until full ZST implementation; merge owns layout/ZST. |
| optional destination array_<T> | Native scratch is array<MaybeUninit<T>> and opaque MU ownership. Existing C4 pre explicitly requires optionalT, so identical posts cannot be linked without conversion or a separately proved different prefix interface. No arbitrary separation/layout premise. |
| MU inverse new(inner(old))==old | Prelude only proves inner(new(v))==v. Inspect fresh isolated forward/roundtrip diagnostics. Before C4 no destination writes/reads, so opaque MU framing is semantically sufficient for an appropriately proved prefix interface; inverse is not inherent to the runtime prefix, though old optionalT adapter exact restoration asks for it. |
| Native scratch/inline-const guards | Actual caller len earlyreturn, scratch.len()<len+16 abort and `if const {sizeofT<=16} && len>=16` select branch; earlier ghostlen>=8 lemma does not prove them. Guard-only source subset/pure implication are separate fresh candidates, not actualcaller CFG theorem. |
| C1–C4 lifetime binding and CURRENT unwind recovery | Existing exact C4 profile closes these in one target; do not move temporaries or change rules. No native strict draft needed merely to reprove native resources with scope flags off. |
| Connected consumer / control flow | Frozen C4 file-source SHA and exact-one runtimebody admission, explicitly NOT_CALLABLE_SUMMARY. Extra native caller is refused before target; cannot claim connection by calling its truncated actual sort4 summary. A distinct source-linked internal prefix needs its own accepted source/MIR/AST binding; new VF change is a blocker, not permission to implement. |

## Experiment hypothesis and exact frozen profile

Hypothesis: resource availability before as_mut_ptr can be proved from native
safe pre on frozen C4, while unchanged native read-only body specifically reveals
its as_mut_ptr profile mismatch. Source-linked guard implications and MU
storage conversion can be independently tested without a new lifetime or alias
rule. Existing C4 target/normal and eachdirect unwind must remain reproducible.
No promise that these separate pieces complete native→C1 or native→C4.

ToolHEADf76012fb518703b1d98e243ac4f487f16877cfcb,nightly2026-09-25;
translator1eab6eb54fe5c23d53ca72a6d9dfcbbff09c09ffaf26c48a4f450f5068a8d313;
kernel37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c.
All parser/exporter/refiner/effective .rsspec/std/critical identities in
FROZEN-C4-SNAPSHOT.json. Existing exact patch chain only; no slice alias overlay,
strict-cut draft, selector FRAME/cleanup, kernel/spec/parser changes.

## Candidate stages / falsifiable outcomes

1. Build exact frozen tool, prepare unchanged C4 source in Cloud, fresh paired
MIR/refinement/preAST and full VF0. Run normalfalse+four directunwindfalse
controls at independently pinned intended sites. Targetposts/unitreturn/leak
must match a518. Wrong first stage or absent target leaves outcome NOT_RUN.
2. Unchanged typed native safe-reference fixture on SAME binary, C-prefix
optins OFF, all lengths/ZST; full automatic native normal/unwind/current
source/scratch/F posts/unitreturn/leak. MissingT/F controls only count if target
and helper reached, never if as_mut_ptr frontend blocks all three.
3. Isolated before-pointer native resource subset: exact len read and safe
reference signature/domain, ghost stripped pointer value only, no actual
as_mut_ptr/callback/copy. Derive native source4/F/thread plus explicit stocktypes,
check helper then restore full source/F/opaqueMU frame/native posts. Missing
producer controls first expected at helper type_interp precondition.
4. Actual guard-only source statements, full safe pre/posts, no caller call;
pure selected-branch lemma independently proves len/scratch>=4 and
len>=16 implies size>16. ZST route counterexample may demonstrate that generic
positive size does not follow. Runtime len+16 overflow obligations are retained.
5. Isolated MU one-cell forward/rewrap-inner preservation versus exact oldvalue
roundtrip. Use existing open/close_MaybeUninit only; exact oldvalue post failure
is a model limitation diagnostic, not an axiom. No using failed helper summary.
6. Append harmless runtimebody to unchanged C4 fixture: sourceSHA admission
refusal before target expected, not semanticnegative. Frozen subsequent
exact-one-body guard documented statically, not dynamically claimed if unreached.

PASS for separate resource/guard/MU components permits only their exact claims.
Failed native alias/callable-admission rule → save minimal source/command/version,
expectedvsactual/neededlimits, continue isolated source resources/guards.
Do not port overlay/repin AST/enable semantics to bypass failure. Refinement or
setup failure → minimal authorized runner fix/newexactSHA Build while window and
account permit. Same failure without new evidence → reassess, no duplicate run.
No wholecaller/nativecomposition/profileadmission upgrade from capture/replay.
