# First source-linked prefix failure / narrow path repair

BEFORE second experiment. First Build c7ab932c-204a-4cbc-a29e-f8c076d51dfb,
infra=proof4ab62d12ef95e3f2da2440359c3bec8594535568, fullarchive verified
c6318ff7df2700f150c30c9897b1b6988bd43e21cf127bdd2fe85418512d3539.
All four normal/read-only MIR + fragmentrefinement supports PASS, unique native
caller proof entry; positive identity lemma checked beforecaller. All verifier
exits1 at original scratch.len()<len+16 potential usize overflow BEFOREcallsite.
No c1 premise eliminated; both controls INCONCLUSIVE/wrongfirstobligation.
First classifier's prefix/bridge labeling is too coarse; raw output retained.

Reason: unfiltered fragment checks othercaller domains, including legal ZST huge
len which never reaches the selected sort4 branch. Selected original path implies
NOT(size<=16 AND len>=16) AND len>=8. Permit ONLY explicit diagnostic runtime
path filters expressing exactly that domain, after original len extraction;
retain original operations/conditions in order afterward. Pair refinement now
compares filtered diagnostic pair, never full actualcaller. Source certificate
must name added filters and reconstruct original prefix by removal. No general
cutoff, selected generic type restriction, or ownership entry precondition added.

For size>16, derive len bounds from EXISTING native array<T> authority and stock
array_inv<T>: count*sizeofT<=isizeMAX. Checked arithmetic mul_mono_l derives
len<=isizeMAX for positive-sized type. For size<=16, exact selectedbranchfilter
provides len<16, so len+16 cannot overflow. No permissions created or weakened,
no kernel/translator/spec patch. Source-linked fragment qualification narrows
execution to one requested caller/path, not arbitrarycaller total correctness.

Conservation: filters return unchanged native state on excludedpaths. Bound lemma
consumes/returns same sourcearray; foreach owners/F/scratch/thread/lifetimes frame.
All fragment posts/leak checks remain. FreezeMarker/Faliases remain unchanged.
Trust changes: NONE beyond preexisting experimental O26 model; native slice
create/reborrow model contains TODO reqtrue, so globalaliasqualification remains
open and resource-native results are conditional on that model.

Self-review/gates: exactdomainfilter spelling/source link, removal reconstructs
pinned actualprefix, ghoststrip filteredpair, fresh normal/read-only/fullrecord MIR,
refiner, nativeentrypositive/bridge/range/duplicate cases, exacttoolmodel before/
after pins. Controls must reach their intended resourceobligation or remain
INCONCLUSIVE. No c1 invocation, no c2 or fullsort4 summary.
