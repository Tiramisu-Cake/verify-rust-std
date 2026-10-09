# StrictCUT false-post Cloud controls

This is a separate diagnostic after the frozen O26 baseline, same-build
`d557082b` strictCUT + `e7189430` relocation + `fa862fe8` mapped-ID
callback test, and the seventeen-case strictCUT DISCOVERY matrix have all
completed. The old matrix and actual sort4 remain unaccepted. The exact
`overnight-lifetime/cases.rs` template (`7cb5c8a8…`) is immutable; a
disposable Cloud preparer selects two cases and changes only one target
postcondition in each selected copy. The stock exporter, refinement checker,
specifications, parser, schema, production console and isolated test console
must remain byte-identical to the audited controls tool.

The first mutant selects `positive_basic` and replaces its unique target
`/*@ ens true; @*/` with `/*@ ens false; @*/`. Its unchanged body has the
strictCUT marker, token assertion and `end_lifetime`; its runtime source after
ghost stripping must be byte-identical to the existing positive. The second
selects `positive_direct_unwind` and changes only the target unwind post from
`/*@ on_unwind_ens lifetime_token(?unwind_k); @*/` to
`/*@ on_unwind_ens lifetime_token(?unwind_k) &*& false; @*/`. This retains
the full lifetime-token requirement while making that post impossible; the
normal post, call, callee contract/body, direct `Continue` unwind and all
other resources remain untouched. The callee must prove before the target.

For both copies, require successful normal/readonly export and decode,
successful refinement against the same original runtime source, complete
raw MIR binaries/text, a decoded body inventory and exact source-pair hashes.
The expected observation is a single first verifier error after the target
proof header and at the target's false post obligation. For unwind, the
same-unit callee header must precede the target, and no callee error counts.
The existing 26.10 false-post control expects the diagnostic suffix
`Cannot prove condition. (Cannot prove false.)`; the exact first source span
has **not** been observed under this profile. The new audit requires that
suffix and a span on the target false post or target closing return. Any
earlier parser, setup, kernel admission, inference, token or unrelated error
is inconclusive. The full proof logs and precise first errors must be
reviewed before crediting an intended negative.

Changing a ghost comment can shift MIR source spans. The Cloud audit therefore
compares complete baseline and mutant decoded MIR after normalizing only
numeric source-span coordinates and the **one exact reviewed target contract
raw value**. All other raw annotations, file paths, CFG, local declarations,
unwind actions and MIR content must compare byte-for-byte; the unredacted
files and SHA-256 of both are retained. Any additional difference is
inconclusive. Both controls remain
`accepted=false`; a positive-looking refusal cannot accept strictCUT or any
actual sort4 obligation. Alias, liveness, CFG mutation, heap and bound gates
remain open.
