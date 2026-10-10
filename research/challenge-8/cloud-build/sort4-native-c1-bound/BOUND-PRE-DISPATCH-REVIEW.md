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
