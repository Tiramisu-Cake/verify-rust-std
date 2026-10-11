# Native C1 bound dispatch review

2026-10-10 22:33 UTC; DRAFT / NOT_RUN. Independent source/MIR/preAST and
kernel free-path review, followed by address review of the final patch,
permits a diagnostic Cloud run. No profile acceptance or proof credit.
Translator3efc917dd38518c7cc94d12b71bb18bd26ab64e32323799e504e7f0a7e4d0ba8;
patch ed95e901c89daabffa725e1c1f38369930693b72be1d60d3548811ebafabb7ec,
base86952a6ac4a61ac854d8a9886cff98ee143a0e75ccf8148fb84e07c0a14ce544.
Kernel37ed unchanged; frozen C4 then capture then separately named bound overlay.

Fresh34bddbf7 establishes native→prepared Args.own boundary, not complete
callback/free/return theorem. Ref-own inverse undo failure is not replaced by
an adapter: actual FnMut contract consumes Args.own. Scratch MU opaque, no
optional destination, inverse MU or layout/separation assumption introduced.

Only eight callback declarations move; `_5` stays outer. Original automatic
contract survives mk_fn_decl unchanged. Normal route recovers CURRENT pair,
joins four then untouched tail, restores native F/thread/MU/types, unit/free/leak.
Direct comparator unwind closes debt inside strict child, crosses checked
escape/free boundary, runs all four native cleanup blocks and returns original
unwinding outcome. False normal/unwind controls are placed after respective
full cleanup, not at setup. Fresh post-AST and actual all-path verifier result
remain mandatory; admission and statement counts alone are insufficient.

Early compiler MIR len/add Continue edges use existing frozen primitive
lowering (ptr_len and pointer Add), without AST unwind switches. This is a
retained trusted profile assumption, not newly proved non-unwinding behavior.
No external as_mut_ptr method binding or caller/guard proof follows.

Both full MIR hashes and successful paired refinement/source immutability are
hard pre-verifier gates for all six exact-source controls; mutated source/extra
body are separate mandatory admission tests with paired support. Exact source,
preAST, storage graph/callback successor gates remain local to this source.
Root AST/JSON/hash/case/recipe dependency closure and saved/synthetic pure
classifier checks PASS. Recipe proof paths sorted unique80, infra16; no local
compiler, extractor or verifier used. Fresh positive and all targeted controls
must be inspected in raw evidence before final theorem claims.

22:56 UTC correction review: only the exact native-bound mode joins existing
source212 cut-retention special-case before original AST, then same checked
strict scope/free/escape rewrite. Fresh failure preserved in FRESH-7456 review;
no fingerprint replacement. Final translator dccb86574c32d88f9bfb41660393ea9334238a392e71b4dbe6c96bf0f4083918,
patch88430ea5202fa2d421eb7d886648de5a7bf8c5eeaa448f9f54c4f4c309d8bf96.
Static source/recipe closure unchanged; saved7456classifier replay exactPASS.
Hypothesis: original18973 now restored; if admitted proceed actualC1 normal and
directunwind fullnativeposts, otherwise identifynewfirstcause without proofcredit.

23:34 UTC CFG correction: fresh10006623 passes both explicit cleanup routes
and full automatic post/free/leak on positive terminal paths, but closes with
dead-code228,2; not VF0. Independent address review GO for moving entire
unwind epilogue between exact original root127 Goto62 and root128 Label62,
retaining root128..133 original final normal return last. Added exact seven-
statement CFG admission guard; no discarded return/cover/resources/checks.
Normal and early branches skip epilogue; direct FnMut unwind enters it.
Translator381e80ebe9a789877ee9d0e860da386f7692f54879b39775e01267f0db6f53d6;
patcheea19eda3723a0f60970df751c7600c326f98ad476d41f61e3f39442beb88693.
Recipe closure80+16/static AST/JSON/hash PASS; classifier-only saved10006623
replay all8 preserves seven earlier errors and now records positive deadcode.
Hypothesis: changed lexical placement closes dead-code while all normal/direct
unwind full original automatic posts/unit/free/leak stay checked. Fresh positive
and false controls mandatory. No source/MIR change, fingerprints18973/8e9/bde6
unchanged. Correct phase input-identity now distinct from historical baseline.

23:45 transport correction review: published8ab packager571850bytes/base64
762468/192parts exceeds191 bound378encodedbytes. NoAPI/Build/reservation.
Remove only caller-entry/prepare.py and its three source-typed fixtures from
recipe: they are read solely by native_cases(), which this explicit independent
followup skips (driver997–1011). Frozen tool/relocation/ghost-strip/source/MIR/
fullpost gates keep alldependencies. Proof76/infra16 sortedunique closurePASS;
no transport/coordinator/semantic gate relaxed. Actual payloadpreflight below
and fresh dispatch still required. Two-slotsoccupied earlier attempt also
creatednoBuild/nocharge; readyrequest retained withinmainwindow.
