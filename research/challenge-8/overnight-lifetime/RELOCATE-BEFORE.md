# Candidate strict-cut scope of compiler temporaries, before implementation

O23's isolated CUT console entered the unchanged `callback_positive` body
then failed at `let_lft` because the strict entry freezer sees an unresolved
outer type. The MIR input `is_less` has named region `'__13`, but nonparameter
compiler temporaries `_27`–`_32` have erased reference regions. The stock
translator emits **all** nonparameter local declarations at function top,
before reconstructing the CFG. The later strict block consequently regards
these temporary declarations as outer variables although their MIR use is
inside the first comparator call. This is a representation mismatch, not
evidence that unresolved inference may be ignored generally.

The falsifiable hypothesis is that exact relocation of those declarations
lets the stock strict entry freeze proceed while preserving the existing
first-call ownership, normal and direct-unwind proof obligations. A
relocated compile or proof failure is a diagnostic result, not grounds to
relax the strict entry/exit check. A successful fixture proof triggers
the source/MIR mutation matrix and separate actual-sort4 admission; it
does not authorize inclusion in the production profile.

## Proposed source and MIR correspondence

In a separate experimental frontend overlay, relocate only the six
compiler-generated `DeclStmt`s for `_27`–`_32` into the existing synthetic
strict `Ast.BlockStmt`, after its internal scope marker and before its head
label. Remove those same declarations from the function-top list exactly
once. Their runtime MIR statements, ordering, call, cleanup, and source
signature remain unchanged. The strict kernel's entry freeze, dynamic
heap/bounds/outer-variable escape check and normal/return/goto cleanup stay
byte-identical. At normal cut exit, the existing block `free_locals` closes
the temps along with the shortened lifetime scope. At the direct Continue
unwind, the same strict block's return continuation frees them; there is no
Rust Drop or cleanup edge for these reference/tuple-of-reference temps.

The only positive admission in this candidate is the pinned isolated
`callback_positive<T,F>` source, verified SHA-256
`66bf5a6edc0188f560e72ac5a6a5636f2dcda47c65aa295ac21008fc7702e2d8`,
with O23 complete NORMAL target-body SHA-256
`10356bf128753db09e17b968e859957121cb3f5a2684c3b608abd4152f150f76`
and readonly target-body SHA-256
`9fdee7643ff66e8f3a12fc37b489100b7280ded0489a20ab1da11c67f24032c4`.
The parent tool profile is production15 plus unchanged CUT patch
`d557082b0c17771acd7386ad6caca7bc139877cf1ca513d9570da210b1b542d8`.
This overlay is opt-in TEST-only and never part of the accepted S6 profile.
The source+MIR harness must pin those complete bytes and the real
exporter/decoder/refiner/schema hashes before enabling relocation. The
internal frontend guard checks the selected function name, source file and
span, exact source MD5, unique one-lifetime cut and six local IDs/types.
The complete typed-MIR hash gate, including call and Continue successors,
is in the hosted harness, not in the frontend overlay. The harness rejects
a changed graph before it enables relocation. Source or local-shape gate
failure inside the frontend is fatal.

The path certificate is asymmetric. On every **normal** route to the marker,
MIR must StorageLive each selected temporary only inside the strict prefix,
StorageDead all six at source line 103, and have no later StorageLive/use,
address escape or Drop. On the **unwind** route from the first FnMut call,
MIR uses direct Continue, bypasses line 103 and exits the function; no
cleanup, destructor or later use may occur. The strict AST return exit must
free the relocated locals once and satisfy the full unwind post. There is
no claim that StorageDead executes on the unwind route. The readonly graph
renumbers locals, so its corresponding temp roles and path inventory must
be reviewed independently, not by copying NORMAL IDs.

Before acceptance, record a frontend AST trace showing each of the six
declarations removed once from the outer list and present once inside the
strict block, with identical type. The emitted `addresstaken=false` field
records the declaration's initial flag; by itself it does not prove that
later translation or checking never takes its address. Full proof must
reach the actual FnMut call, normal cut/token recovery and direct-unwind
return/leak checks with unchanged posts. Negative controls must alter one
selected temp's StorageDead, introduce a post-cut use, address-taking,
Drop/cleanup, a wrong temp type or a changed callback unwind successor;
each must fail its exact source/MIR gate rather than another setup stage.
Keep the positive source's complete NORMAL/readonly MIR, refinement and
actual source-body identity. Fresh S6 and ordinary no-cut callback controls
are required on the combined console.

## Trust limit and actual sort4

Relocation changes trusted AST scope even though the runtime MIR is fixed.
It is sound only with the path, alias, resource and source gates above;
the current O23 normal graph observation alone is insufficient. The first
call in actual `sort4_stable` needs a separate exact source/body and
compiler-temp certificate. Reusing six local IDs or this fixture's proof
there would be invalid. This component does not prove actual sort4, generic
ZST behavior, ordering, or comparator panic safety.

The hosted capture API, after the caller has built a **separate** CUT plus
TEST-overlay console without changing the production or CUT console, is:

```sh
python3 research/challenge-8/overnight-lifetime/capture-relocate.py \
  --tool-home "$relocate_tool_home" \
  --out "$fresh_evidence/relocate" \
  --deadline-epoch "$deadline_epoch"
```

The build wrapper must record the exact pre/post translator bytes, all
effective specs, applied diff, decoder and console hashes. The capture
pins the reviewed overlay patch, selected source and original bytes,
exporter/refiner/schema binaries, and both decoded target bodies. It runs
the no-relocation boundary and the relocation candidate with the same
source and all normal/unwind/leak/dead-code checks enabled. `0 errors`
would be only a fixture diagnostic; source/MIR mutation controls and
independent actual-body admission remain outstanding.

## Self-review before hosted activation

The first draft removed six top-level declarations but had no mandatory
check that CFG reconstruction inserted them. The revised overlay keeps
an insertion counter and rejects anything other than one matching strict
block; the hosted runner requires the corresponding trace. The frontend
checks only its exact source and local shape, while the runner checks both
complete MIR bodies. This split is explicit because the overlay has no
internal all-path liveness or address-escape checker. The trace's initial
address-taken flag is not interpreted as such a checker. No production
kernel, permission rule, exporter, decoder, specs or runtime Rust source
is changed by this TEST candidate. Static `git apply --check` succeeded
against the exact O23 CUT translator; no local build or verifier ran.
