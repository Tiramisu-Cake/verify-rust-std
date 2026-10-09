# Preparation audit / first experiment

Actual source and prior generated source/MIR/logs read before new Cloud submission.
Main+independent explorer confirm prior failure is excluded scratch-failure abort,
not callsite resource rejection. No verifier/spec change required for path selection.

Source filter repeats exact `if scratch.len() < len + 16 { return; }` only after
checked array invariant/size branch arithmetic. Original check with abort remains
verbatim; removing all exact insertions reconstructs original source prefix.
Native generated contract untouched. Source condition branch retains legal
scratch success only; other fragment boundaries remain explicit. This diagnostic
has different behavior on excluded paths and is NOT full caller correspondence.

Saved normal/read-only MIR, raw source certificate, fragment refiner and verifier
execution trace must independently support reachability and selected mapping.
Collector stores raw results before aggregation and cannot promote support PASS
or a reached assertion into full resource/return/leak theorem. No sort4 summary
invoked; the proof stops exactly at first source-linked callsite boundary.

Source-frame case now attempts checked split+join source4/current owners, F cell/
owner and thread for ALL selected native entries, including ZST, without a size
conditional. These lemmas carry no positive-size requirement. Full bridge retains
existing c1 size>0 conditional, never inferred from selected original branch.
Scratch optional storage does not yield initialized T owners. MU opaque owner
foreach must remain framed; conversion identity and type_interp stay separate.

Latent issue read from frozen std/lib.rsspec: close_MaybeUninit_ returns
MaybeUninit::new_maybe_uninit(inner). No inverse equality to arbitrary original
MU value is declared; complete native return may therefore need an actual
representation/invariant law. No such axiom or contract strengthening added.
Stock produce_type_interp exists with RealFunc/nonghost_callers_only gate, but
not used here and not treated as a heap consequence. First actual failure decides.

Preserve full checks; expected range/duplicate resource negatives must fail at
intended source authority obligation after boundary. Earlier failures inconclusive.
Cloud-only extraction/proof; local static Python AST/shell syntax/Git checks only.
