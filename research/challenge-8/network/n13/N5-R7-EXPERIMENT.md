# N5 R7 Cloud integration candidate

Defect: the historical R7 isolated theorem has not been transferred to source
cd371e0 through the authorized Cloud lane. The existing mathematical N13
runner has no Rust/compiler/refiner stage. Add only stage `swap-size` to N5,
using the existing lane with exact closure inventory and a separately pinned
R7 profile. The old N13 profile and all N13 stages/posts/controls are unchanged.

Applicability: isolated generic `has_efficient_in_place_swap<T>`, exact source
blob40939f922bcb6fdc7ee0d30427fa861827043827, stock VeriFast26.09 source809de459,
nightly2026-02-05/compilerdb3e99bbab28c6ca778b13222becdea54533d908, x86_64 LP64.
Runtime body/signature/CFG stay byte-exact; only the historical ghost result
contract is inserted. The original extractor is reused with its exact hash.
No kernel/prelude/spec patch, trusted bridge, axiom or caller summary is added.

Envelope: same shared120s bootstrap/archive checks, compiler setup450s and two
180s tool cases. Stage810 + setup120 + soft15 + report240 = Build1185;
queue60 is additionally reserved. The10800s N5 account, T0/deadlines, owner,
coordinatorv4, transport/IAM/shared scripts and historical records are unchanged.
Per-stage profile selection adds an R7 pin without replacing the N13 pin.

Controls: strict source/stage/target/profile/command/log identities; exact
extracted input hashes before/after tools; ghost-strip byte equality; pinned
compiler/stock executable/prelude inventory; exact named/body trace; zero
verifier/refiner exits. Synthetic tests exercise errors/timeouts/malformed,
partial/missing/null/wrong-type/NOT_RUN/mismatched receipts and input mutation,
preserving original exits/exceptions/snapshots. Historical N4 admission tests
now explicitly use their published pre-R7 recipe commit; they are retained.

Stock archive/refiner applicability and actual tool execution remain UNRUN.
A source-reported component receipt will not grant dispatch callers or B1/B2
credit. Full N13 math acceptance and R7 component transfer are separate results.
