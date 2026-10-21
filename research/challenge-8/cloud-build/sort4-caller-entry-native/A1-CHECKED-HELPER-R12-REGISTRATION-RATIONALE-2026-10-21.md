# R12 registration rationale

R12 is a new, independently authorized Select-R12 window after R11 closed with
its full budget accounting and no carry. It uses a fresh 3600-second account,
the exact owner and existing `o26-sort4-c1-current-recovery` lane, and a distinct
authorization phase. Its profile preserves the established A1 experiment
protocol identity; authorization and historical protocol remain separately
bound in the coordinator environment, adapter, runner, profile, and report.

The R12 adapter is a byte-pinned copy of the reviewed R11 entry/runner route.
It selects a new profile and authorization identity while preserving the same
source, tool, helper, Build, AST, and caller gates. Dependent profile hashes
initially bind the exact checked-in files and are refreshed when the integrated
closure is finalized. R10 and R11 profiles, ledgers, entries, and dispatch
semantics remain historical records.

R12 explicitly extends the reviewed R10/R11 XZ source-restore transport to this
authorization only. This keeps injected source bytes lossless, including
arbitrary JSON values, embedded NUL/newline/invalid UTF-8 payload bytes, and
empty or long inputs; transport restores the original source input byte-for-byte
before the existing verifier-side validation. The same bounded chunk, config
argument, substitution-count, deadline, queue-reserve, and package/report limits
remain in force. The other phase routes keep their prior gzip/XZ behavior.

Synthetic registration controls cover exact source round-trip, corruption and
wrong-byte rejection, real source length dispatch, JSON value preservation,
config argument and substitution limits, phase/profile separation, and
R10/R11 historical route preservation. No compiler, source extractor, verifier,
runner, or Cloud submission is used by these tests.

R12 additionally pins and runs a grammar-only preflight immediately after the
same-Build tool reconstruction and before canonical fixture preparation. Its
three fresh source pairs check the helper's Option constructor spelling and
ghost import placement, with exact diagnostic checks for the two expected
negative cases and AST selection for the positive helper. This result is
diagnostic only (`proof_credit=false`, `caller_receipt=false`); the canonical
fixtures still require their own fresh same-Build checked-helper verifier
stages before caller classification. Any missing, malformed, partial, failed,
or deadline-limited preflight leaves dependent cases `NOT_RUN` and retains the
original stage/error details.

R12 admission uses the active shared coordinator protocol for project capacity.
The historical local two-slot guard remains on earlier A1 phases, while R12
does not impose that older cap over coordinator v3's three-slot envelope for
the authorized Select owner. Owner/ledger reservation checks and the live
coordinator capacity refusal remain mandatory.
