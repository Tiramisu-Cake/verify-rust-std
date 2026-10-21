# R15 registration and source closure design

R14 established a publication gate by replaying an unchanged proof source and
freezing its 158-input proof inventory. R15 is authorized to change checked
proof inputs and source-preserving frontend inputs, so that inventory cannot
remain the acceptance boundary. R15 instead binds its selected full Git
commit to the exact recipe closure: every declared proof path, every declared
infrastructure path, the merge recipe, and all automatically selected Python
infrastructure inputs must exist as regular committed blobs and match the
worktree bytes and modes. The existing source-input transport then carries
that same committed closure, with its current substitution-count and
per-substitution caps unchanged.

R15 phase authorization is a separate dispatcher branch bound to its fresh
ledger, owner, phase, 3600-second ceiling, merge lane, T0/main/absolute
deadlines, 1200-second timeout cap, no-carry rule, and same full source SHA for
infra and proof. It calls the R15 source gate before submit. The source gate
retains R14's publisher-control validation against the R14 probe and verifies
that the accepted R14 gate, R13/R14 closed ledgers, and R13 upload mode remain
byte-identical to the R14 probe. This allows reviewed R15 proof inputs while
keeping historical accounting and the mandatory publisher route fixed.

The R15 preflight preserves the R14 historical publication-gate checks
directly: it validates the accepted R14 gate bytes and record, all prior
budget-file identities, the exact publisher configuration, and the mandatory
upload-guard route. The old R14/R13 source preflights, R11 source/phase/service
harnesses, and R11 session/design/review notes remain in Git but leave the
runtime recipe after checking that the merge runner does not consume them.
These are local checks for earlier phase registrations and historical context.
R15 verifies its ledger identity, exact selected-source closure, and
deterministic compressed payload fit against the existing 191-part,
3990-byte-per-part source transport ceiling. At a 1200-second Build timeout,
R15 gives execute at most 840 seconds and reserves at least 360 seconds for
package/upload/verdict by adjusting only the generated execute-step deadline
and shell timeout. The Cloud Build timeout remains 1200 seconds. Service
tests use synthetic registration/transport cases and patched clocks/dispatch
helpers; they do not compile, prepare, or verify Rust.

This registration establishes source transport and bounded phase access only.
It does not establish proof acceptance or independent proof credit. A review
of the complete selected diff and its exact source closure remains required
before any R15 Build submission.

Proof1 measured execute470.227626s, package/upload383.822664s, verdict1.041706s, charge868. Before Proof2 raise the R15-only publication reserve360→420s and lower execute840→780s/soft765 at timeout1200. The measured publication+verdict384.864370s fits420 with35.1s margin; unchanged uploader/outer timeout/controls/evidence. This is a conservative deadline correction, not a new publication probe or semantic rule. Synthetic config checks must assert new budget markers and unchanged uploader.

R15 minimum usable timeout becomes510s (90 execute +420 publication); authorized upper bound1200 and budget remain unchanged. Shorter dispatches would not fit this measured plan.
