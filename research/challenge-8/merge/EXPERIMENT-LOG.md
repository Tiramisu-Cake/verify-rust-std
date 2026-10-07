# Independent merge geometry experiment journal

## G1 card — before proof implementation/dispatch

Actual obligation: exact pinned merge_up/down and bidirectional_merge geometry
for arbitrary n>=2 and arbitrary comparator results, including access BEFORE
advancement, reverse wrapping intermediate, even/odd/minimum/final residual.
Hypothesis: count-based invariant and induction on arbitrary decision list prove
all access/advance bounds and terminal/residual geometry without sorting laws.
Domain: n=2m+e,m>=1,e0/1;0<=a,d<=k<=m; decision list lengthm-k, arbitrary
forward-left/backward-right choices. Both possible odd residual source choices
included. No enumeration/upper bound/SWO/pointer-ownership assumption.
Full mathematical normal post: all ordered modeled accesses in[0,n); forward
cursors admissible through n after access, backward source intermediary LR>=-1
with -1 never read; destination ordinary advancement stays in[0,n]; terminal
ends in[0,n], residual source and dst valid, write count2m+e=n, scalar guard
balance characterized separately. Comparator unwind: no further events after
panic; actual Rust unwind/resources not covered by pure lemma, remains OPEN.

Tool profile official unchanged VF26.09 with PLAN pins; source full SHA32574f...
Three Rust bodies admit exact token order + full-file hash in hosted runner.
Every abstract helper/recursive body checked; reusable frozen pure classifier
checks expected==visited bodies,normal/return/leak,0error and source integrity.
Positive: full invariant/induction/event/fullpost body acceptance, arbitrary n.
Negative controls: isolated off-by-one source READ at n and incorrect cursor
advance violating invariant. Each must fail ONLY its marked false assertion,
proof stage, exact predicate/location/column after setup and antecedents.
Fail-closed altered-location/predicate/body/target/column/timeout/source controls.
Concrete minimal witnesses calibrate negatives, never replace universal proof.
Outcome: positives+intended negatives accepted -> report geometry certificate
and exact Rust transfer OPEN; parse/annotation/solver failure -> new evidence
before within-profile fix; insufficient trust/budget -> precise checkpoint.
Selection dedicated workflow_dispatch hosted merge_geometry job/branch guard,
percase180s, job<=6min, new1800total inclprep; one own hosted run. No local execution.
Source/run/cost pending. Prior networks budgets/proofSHAs preserved in STATUS.

G1 implementation review: full universal mg_entry + recursive mg_trace_safe
normal posts,8named lemma bodies; no own bodyless lemmas. Standard unchanged
stock div_rem_nonneg(n,2) provides built-in integer division/remainder laws.
Negative case names merge_geometry_negative_read/advance/wrap_read, marked
TARGET_NEGATIVE_READ/ADVANCE/WRAP_READ. Expected VC strings in initial metadata
2<2,3=2,0<=-1; exact marked lines computed in retained hosted sources. A VC
format mismatch is INCONCLUSIVE, never accepted by relaxing the frozen gate.
Wrapped -1 witness added explicitly.21independent classifiercontrols expected
(7each). Source/signature/activeoperation SHA+line admission all3functions;
fullfile/static source map reviewed, actual tools/scripts NOT executed locally.
Hosted cap6min/inner300/percase180, first experiment0/1800spent.

G1 exact dispatch: pushed/remote-verified90872439be953a960aacbb12c79886d6a87e73db,
[run37671730724](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37671730724),
proof=merge_geometry, manualdispatch, no duplicate/oldSHA rerun. Costpending.

## G1 result — full unit INCONCLUSIVE, exact evidence retained
Run37671730724/source90872439be953a960aacbb12c79886d6a87e73db, job19:04:41Z–19:04:52Z =11s, total11/1800,1789remaining. No active job.
Artifact11504383318,17607bytes, ZIP641964684f49ffdeba63499ceeb4d4e3836fecbae8578465e913ad9ebb382296 matched upload. Full sources/logs/results/environment/resources/sourceadmission inspected.
Casemerge_geometry_full:exit1,accepted=False,source07ab144f9c8bdd8b8e25ebf3d76644e3182312dcd9e1981af276a394847d003b,log4b8482a266a602778560815aeb32eedb5ea228ae7bfb8d0ec2139ae5c60dfc06,return/leak15/15.
/home/runner/work/verify-rust-std/verify-rust-std/research-results/merge-geometry/checked/merge_geometry_full.c(283,19-21): error: Assertion might not hold. (Cannot prove %(n, 2) = 0 || %(n, 2) = 1.)
Casemerge_geometry_negative_read:exit1,accepted=False,source80821649fec3d89cb7ee296b9a7ec54562ec4057b290e92dd4a4c55e134eae9f,logf2c99d67916db62f8ffd0c3e143d0c532eac22012c387f52b0b6848d90aaaae6,return/leak0/0.
/home/runner/work/verify-rust-std/verify-rust-std/research-results/merge-geometry/checked/merge_geometry_negative_read.c(136,18-19): error: Assertion might not hold. (Cannot prove mg_right(1, 1, 0) < mg_n(1, 0).)
Casemerge_geometry_negative_advance:exit1,accepted=False,source94e5b441556ac8ff6c75de88c022db63f78ab8c95b10f3d21b21b7c2c1a0d812,logb444bbced5ac0285e902c09301dfcea2da0c8c830fb73ae1e7cfaea314d30565,return/leak0/0.
/home/runner/work/verify-rust-std/verify-rust-std/research-results/merge-geometry/checked/merge_geometry_negative_advance.c(136,37-39): error: Assertion might not hold. (Cannot prove ((0 + 1) + (mg_right(1, 0, 0) + 1)) = ((1 + 0) + 1).)
Casemerge_geometry_negative_wrap_read:exit1,accepted=False,source93360c363d9f81120f6db071b417f9b796640908023420f801cba2c0c1590288,log5add0d45d47b2ba81a27da4baf6bebfb0fbcd8cd80e7c62053e2c1dfab467c10,return/leak0/0.
/home/runner/work/verify-rust-std/verify-rust-std/research-results/merge-geometry/checked/merge_geometry_negative_wrap_read.c(136,14-16): error: Assertion might not hold. (Cannot prove 0 <= (mg_left_rev(1, 0, 0) - 1).)
Full positive visits8bodies, first7complete15return/leak; entry fails only283 remainder-disjunction afterstockdiv_rem_nonneg. No full acceptance. All3negatives reachcorrectsingle proofassert136 (read18-19,advance37-39,wrap14-16), but exactmetadataVCmismatch leaves INCONCLUSIVE; no relaxation/relabel. Tool/std/classifier/sourcepinsmatch, actualactive3bodies9/9/30statements admitted.

## G2 card — explicit remainder split and exact diagnostic calibration
Same actualstd/source/domain/fullnormalposts/functional-vs-Rust-unwind boundary asG1; no assumptionsorweakening, noSWO/bounds/enumeration. Hypothesis: explicitif(e<1) fromstock0<=n%2<2 proves e==0 elsee==1 and exportsoriginalfullmg_entry. Eachnegative source/falseassert unchanged; metadata strings nowexact hostedVCs, retainingstage,line136,column/body/target/source/timeoutgates and21controls. Positiveall8fullbody/source/return/leak/0error and3intendednegatives required. Stocktool/classifier unchanged,180/proof,300inner,6minjob. Budget11/1800,1789remaining. Success->fullgeometryreport; anyfailure->new evidence-backed localproofrepresentationfix only. Source/runpending.

G2 exact dispatch: pushed/remote-verifiedb1ed0c22dafec350a64e83675d55350806d77208,
[run37672184476](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37672184476),
sole job11296646332719:08:16Z–19:08:30Z=14s; allotherjobsskipped.

## G2 result — full mathematical geometry ACCEPTED
Artifact11505083335,17681bytes, ZIP0844784ce64fb385aaf365ebbb6020d11442f2e1423a3b360e408b1722a1d35a matched upload. All sources/logs/results/environment/resources and exactsourceadmission read; recordedsha/log hashes matched.
merge_geometry_full: exit0,acceptedTrue,source4594f159400bcfeeea87e3086e5765472d121dced7385bd2ef216a83bf24dea8,logf5a2cb78108d732959574541c487ec292673ef15ca726f76d8498d1467d93c9f,expected==visitedTrue,return/leak17/17.
merge_geometry_negative_read: exit1,acceptedTrue,source80821649fec3d89cb7ee296b9a7ec54562ec4057b290e92dd4a4c55e134eae9f,log1828f2ecc4241bac81fcd7fe0466c5c028b7249e3c809009dbb1e0acb911cc9f,expected==visitedTrue,return/leak0/0.
Intended VC mg_right(1, 1, 0) < mg_n(1, 0),target136,all7controlsTrue.
merge_geometry_negative_advance: exit1,acceptedTrue,source94e5b441556ac8ff6c75de88c022db63f78ab8c95b10f3d21b21b7c2c1a0d812,log4980f8bc18e694fad2f0a9558d754399560d066391fe307c74ec5e5ac3c6b101,expected==visitedTrue,return/leak0/0.
Intended VC ((0 + 1) + (mg_right(1, 0, 0) + 1)) = ((1 + 0) + 1),target136,all7controlsTrue.
merge_geometry_negative_wrap_read: exit1,acceptedTrue,source93360c363d9f81120f6db071b417f9b796640908023420f801cba2c0c1590288,logede16f7e25ee202b19f2c029ce6a2983041db8d5173b00da5937a92fbc909e81,expected==visitedTrue,return/leak0/0.
Intended VC 0 <= (mg_left_rev(1, 0, 0) - 1),target136,all7controlsTrue.
All8positiveactualghostbodies/fullpost/source-integrity/0error/17return17leak PASS,88statements verified; finalentryreturn/leak294completed0.652030s. All3negatives exactly intendedsingle proofassert136 (read18-19,advance37-39,wrap14-16),21controls PASS; all3negativeCfilesbyteidenticalG1. No assertion/resource/body/post removed; only explicitintegerremaindercase split andexactVCmetadata.
Full pinned3Rust activebody/signature/order certificate f2ccc11b235e8f2224131ddef4a12c17409c58863c5712726cb13a02a4960bc7 unchangedG1/G2; fullsource32574f...,stockconsole dc672...,archive da1b...,frozenclassifier994afa...match. Stock div_rem_nonneg is existingtoolprelude integer arithmetic, not ownaxiom/correspondenceassumption.
Outerexit0,proofwall0.88s,user0.81s,peakRSS66220KiB. SummedHOSTEDcost11+14=25/1800,1775remaining,setup/evidenceincluded. Noactivejob. Networks oldbudgets1499/1800 and1649/1800unchanged,no transfer/noadapterruns.
Decision: close authorized mathematicalgeometryphase with complete invariant/induction/orderedaccess/update/terminal/scalarguard certificates. Rust provenance/overflow/ZSTmapping/permissions/initialization/FnMut/ownership/unwind and sorting functionality OPEN; no publicChallenge safety claim. No additional verification needed for documentation-only checkpoint.

## F-A1 card — authorization before functional implementation

Actual pinnedbidirectional schedule and originalG2geometrystate, source32574f...
HypothesisA: multiset count telescopes while selected fronts advance/back cursors
retreat; scalarfinalequalities exactly eliminate residual sourceintervals. Exact
destinationwriteindicesk,n-1-k,m givecoverage/unique and outputIDs beforemoves.
Domainn>=2, arbitrary independentcomparisonpairs listlenm=n/2, oddh arbitrary.
NoSWO/sortedness/keypremise. Full posts exactlengthn, eachdstexactlyonewrite,
alloriginalIDmultiplicities forarbitraryq and fullG2geometrytrace. Normalmath
complete schedule only; actualcallbackpanic/unwindresourcesnotproved.
B targetalreadyrecordedPLAN: sortedhalves/fixedSWO/immutablekeys/faithfulnormal
answers/scalaroddchoice -> guard,sortedout,permutation,stability,exactschedule.
InitiallyA beforeB; positivefullbodies/normalreturn/leak/integrity/0error; lossy
withoutguardnegativeintended exactmultiplicityassert, source/body/line/predicate/
column/timeoutsfailclosed. Tie/sortednessnegatives separatelyrequiredforB.
Stock unchanged tool/source/classifier frozen, no axioms/refinement weakening.
Hosted6minjob/percase180/inner300, oneownjob;25/1800spent1775remaining.
Routinefixonlyonnew evidence, fullAacceptance -> permittedBimplementation.
Source/runpending. Alloriginalgeometryproof/results/budgets retained.

## F-A1 result and F-A2 card
A1 published/remote-verified a4c46af5f860e5117b0d46b154d32f8c8bfbdc1e,
[run37676075230](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37676075230),
job112979809233 19:39:02Z–19:39:16Z=14s, cumulative39/1800,1761remaining.
All evidence files inspected. Positive source693ea2fb4197f7574260215ba02997298eb7df7fe1e4da0b6842452f8c108ab3/log2b50cbfd5cc06f7f7d9ae2f45853aac1f32bb80518c9c876f7df19076fd8f15d;
18/19 bodies visited,48returns/leaks, failure recursive termination in
fa_trace_output_at at generated582: no inductive parameter. All prior G2/A
bodies completed. Negative sourcefa84ead5774c49912d211dd69eca449b6c05edaf6b56c46cb9f4aaf60a6ae32d,
logc25586b8805d510255dea1556f38f31ed5a9df69dbc6425d7bdb5aab5ce47ee5:
intended count assertion218 cols68-70 reached, exact predicate uses boxed_bool;
classifier metadata mismatch means INCONCLUSIVE, not accepted. Source admission
certificate f2ccc11b235e8f2224131ddef4a12c17409c58863c5712726cb13a02a4960bc7 unchanged.
A2 hypothesis: move structural decisions switch to first statement, call the
same destination lemma inside branches; stock VF can then recognize tail
recursion. Full original contracts unchanged, no added assumptions. Negative
source/assert unchanged, calibrate exact boxed diagnostic; all strict gates and
seven rejection controls required. Same A domain/full posts/stock pins/180case/
300process/6minjob. Success -> B; failure -> evidence-backed proof cuts only.

## F-A2 accepted / F-B1 card
A2 published fc4d03d31f92c6d3f3566b0baa506d0a6dec6805,
[run37677079473](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37677079473),
job11298324838319:47:02Z–19:47:19Z=17s; cumulative56/1800,1744remaining.
Full positive exit0/source11f8f381dcdadb7bbe96249f21086ceb368fd028afc7401779b500c3d8bc9623,
logb85d15cf76da882463986dc8e0eecf1c83dd72306faafe25b35a18d795b63c0b,
19/19bodies178statements55returns55leaks. Negative unchanged sourcefa84ead...
log94e6d0cd9dcc118d94c43abb5d9233d7fd38813ca5c6be5ed3189db5b166831f,
exact assert218cols68-70/boxedpredicate and7controls ACCEPTED. Full source,
logs/results/environment/resources/exit inspected and hashes matched. Official
pins/source admission unchanged. Signed indicator balance telescopes even when
cursor intervals cross; guard alone cancels residual potential. Thus no hidden
joint-remaining-set disjointness/order assumption in A. Exact chronological
writes tied to output: arbitraryp singlewrite iff0<=p<n and same nthID; arbitraryq
count exactly1 iff0<=q<n. Normal mathematical completion, actualRust OPEN.

B1 actualstd/source admission unchanged, full G2 and acceptedA bodies rechecked.
Hypothesis: four independent front/back cut inequalities, derived from original
sorted halves and exact tie laws, rule out crossed joint intervals and stale
selection, even when a joint half becomes empty. Selected forward/reverse IDs
are lex(rank,originalID) min/max of remaining sources; induction follows exact
fa_output nesting and scalar odd residual. Constructive predecessor-count SWO
bridge bodies all rechecked (unchanged e5c3f29d...); original SWO-half sortedness
and exact comparison answers translated with swo_rank_bridge at each read,
no rank correspondence axioms/reference merge assumption. Exactposts inms_entry:
scalar guard, fullgeometry, output/trace lengthn, everydstexactlyonce/tracevalue,
arbitraryIDcount, all-pair !rel(later,earlier) and equivalent=>IDascending.
Domain n>=2, length decisions=n/2, fixed finite SWO on occurrenceIDs0..n-1,
immutable pullback keys, originallysorted halves, faithful normallyreturning
comparator; oddchoice scalar a<d. No order premises added to G2 or A.
Positive all own bodies/source/returns/leaks/deadcode/0error required. Negatives:
A's n2 duplicate/loss withoutguard; ties key0, ds(false,false), output[1,0]
withguard/permutation passes but mb_lt(key,1,0) false; wronganswers keys[1,0],
ds(true,true), output[0,1] withguard/permutation passes but key0<=key1 false.
Each isolated negative confirms faulty fidelity and invalid sorted/stable output
before marked target, exactstage/line/body/column/predicate/source/timeout and
7controls each required. Tool/frozenclassifier unchanged,180case/300process/6min
job includingpreparation. Success->A/Bcomplete math report; failure->localized
new evidence-backed proof repair, never premises/posts/tool weakening.
Source/runpending. Budget56spent1744remaining, oneownrun only.

## F-B1 result / F-B2 card
B1 published08d66c14f8a8e1881898dd6f154881829c5121c5,
[run37677923322](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37677923322),
job11298610389719:53:42Z–19:53:56Z=14s; cumulative70/1800,1730remaining.
Fullartifactread: positive source2ea5ca5c5ad27c92d56b20cb3e77dec22b37b6ee41dff52a2c4eed1d12c9c9f0/log036b53d9d6bfc4dca4b6535054eef4a73dab54ff37dd986ca25d02c0334ec69e
parse649atlate nat.gh directive,0body/return/leak. Tie/cmpalso parse208,
not intended negatives, INCONCLUSIVE. Duplicate exacttarget218 all7controls PASS.
No B mathematical conclusion from parser failure. B2 hypothesis: stock ghost
headers must precede bodies; admitexactone nat directive, move it to front
of each assembledunit, preserve all body text. Alreadyaccepted G2/A/core hashes
unchanged. Addedexplicitinteger remaindercase in both Bentrybodies asG2; no
premise/post changes. SamefullBdomain/posts/negatives/source/tool/limits asB1.
Anyfailure classified byfirstcausalstage, onlylocalized evidencedrepair next.

## F-B2 result / F-B3 card
B2 published7b7dd6e6d57cb7271cbe323fe3cc4369fb9826cb,
[run37678436610](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37678436610),
job11298790060319:57:54Z–19:58:08Z=14s; cumulative84/1800,1716remaining.
Positive source75ec378eb4626a876aee65e82b26f9a5efba76da713c09074a1d265001bcd542,
logfee367fe822a32345fb1cdf2b40d34f0dde62feb79e2cffe19a7a5a0901e85be,
parse693cols20-23 at combined lexer token ==!,0body/return/leak. Both B negatives
same syntax252; not intended negatives. Duplicate accepted exact218/7controls.
B3 hypothesis: lexical whitespace between == and ! admits ordinary intended
Boolean equality followed by negation; normalize only ownproofsyntax, stock
parser unchanged. Add explicit checked forward-left/backward-right equivalent
key sourcechoice laws; no new assumptions to entries. SameBdomain/fullposts/
source/tool/negativeobligations/limits asB1. Artifact manifest distinguishes
actualfile hash from exact admittedheader-normalized assemblyhash. No dropped
body/assertion, and no functional conclusion from prior frontend failures.

## F-B3 result / F-B4 card
B3 published8c14883ae898fdce3086c10fdde0f0e2797fdb6e,
[run37679049210](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37679049210),
job11299000363520:02:47Z–20:03:17Z=30s; cumulative114/1800,1686remaining.
Positive sourceb0c72ec35be224b03447552bbf798c031e59b38cf0aedd29d050d9a7a4ca8a40,
logc3f23a8bc0d5c0c3446731d810512ddbdff9f77b72d7a37087ab3f5d86361d7d:
allG2/A andB throughmb_no_cross accepted; mb_pair_extremes post cannotderive
strictselected-endpoint order on same-half up-left/down-left branch after
mb_half_order at830; total96returns95leaks, fullBnotaccepted. No counterexample
established. Negativecomparator intended274cols31-33/log9e77db22879a2b1cf209f33d9e57cf4ecd84ea7c81964f223c3e1e5d08af09f5,
source47eb10e1834513249f36c1c8704895db96ff2d452d3b74c7ced70ba4be5952a6
all7controlsPASS. Tieintended274cols39-41/logb0885043ad6eae77bc5372e8c9444c627a3abd16abda5bc8d5d9436889ad0ced,
sourceb262cffe29a92567b5b0db404e13da2f55a937c373cac685548eace1720598cd:
reaches exactstabilityfailure butmetadatamismatch @fixpoint/<==>, INCONCLUSIVE.
Duplicate intended218/all7controlsPASS. Fullsources/logs/resultsread.
B4 hypothesis: after excluding equality, make strictintegerendpoint inequality
and mb_half_order conditional lexpost explicit in both same-halfbranches.
No newpremise/post/axiom; exactsame fullBtarget. Tiesource/assert unchanged,
calibrateexactpredicate mb_lt(@neg_equal_key, 1, 0) <==> true with strictgates.
Samepinnedtool/source/classifier/domain/posts/180case/300process/6minjob.
Success->fullBreport; failure->firstnewcausalobligation repair only.

## F-B4 result — intended negatives accepted; endpoint cut still OPEN
B4 publishedb699b11ddb651d2404f770c4ffdd9a66e7277575,
[run37679577426](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37679577426),
job11299180870120:07:02Z–20:07:37Z=35s; cumulative149/1800,1651remaining.
Positive sourceef1a4ca031405a58b5c637e9824f438ef41af5de042f90223e9e571ed1248492,
log921e25f9d11224b89c24ebb37b2337f926a6f8dc67e7655dac68c3821f8c9459:
95returns/leaks, first failure explicitassert830 a<((m-k+d)-1) after excluded
equality/selectedremaining branch. Sharper evidence, not acceptance/counterexample.
All three intended negatives now exact ACCEPTED: duplicate218cols68-70;
tie274cols39-41; wrongcomparator274cols31-33. Each7controlsTRUE,21total.
Tie andcomparator sourcebyteidenticalB3, onlytieexactmetadata changed.
Fullartifactsource/log/results inspected, original pins/admission unchanged.
Next decision: analyze missing logical facts at this endpointcut before changes;
no weakerpost/extra functionalpremise or timeout escalation permitted.

## F-B5 card — derive strict endpoint gaps from next-state cuts
SameexactBsource/domain/fullposts/stockprofile/negativecontrols. New evidence-
based hypothesis: mb_frontier_step then originalmg_pair_step then mb_no_cross
at k+1 gives a+bit(up)<=m-(k+1)+d+bit(down) and corresponding rightcut.
Thus same-half upL/downL has a+1<=le-1; upR/downR r+1<=re-1, directly strict.
No reliance on disequality propagation, no extraassumptions/circularity: these
three earlier helper bodies do not depend on mb_pair_extremes and were accepted
before its failure. Keep all earlierassertions/fullposts, derive strongerfact
from exact faithful schedule. All negatives sources/asserts unchanged and must
againreach intendedtargets/all21controls. Budget149/1800,1651remaining; same
180case/300process/6minhosted bounds. Firstnewfailure guides next action.

## F-B5 result / F-B6 card
B5 published827726437cfec2add6ad6e4212a5796f43763f01,
[run37680109711](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37680109711),
job11299364638020:11:23Z–20:12:15Z=52s; cumulative201/1800,1599remaining.
Positive source312d72f4a5eb52314bf0411887b3d58d5ac081f71b3a5dce0e10a96d583f5d08,
log19b5fcaffa14118e9e3981002968c2b8516cbe10b4d3ea3a4fded8564b047871,
111return/leak, nowfullmb_pair_extremes/inner_point/inner_all/unbounded accepted.
Firstfailure mb_selected_bound's mb_id_member upperbound pre at705:
x<int_of_nat(nat_of_int(2m+e)) not derived implicitly. All3negatives intended/
all21controls accepted, sourceasserts unchanged, fullartifactread.
B6 hypothesis: explicitly split actual residual half x<m to expose0<=x<n from
existing mg_inv/remaining premise, invoke existing stock int_of_nat_of_int(n)
(normalmathconversion) before domainmembership. No newaxiom/domain/post change,
allbodycalls checked in sameunit; standard stocknat is frozen tool library.
SameBfullposts/assumptions/exactsource/negativegates/profile/bounds asB1.
Budget201spent1599remaining. Success->fullBreport, failure->nextpreciseobligation.
