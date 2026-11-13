# CC3 source handoff — worker14

Source: 76a706f8f8c5b0471bd5c8e6b48cdaf45bab9b66.
Tree: 6730468d0cb9cf24752ad67ef6ebaab35be8e627.
Parent: accepted CC2 9631aaf89e869624fbfc8cd22d327ce194eb779d.
Clone /root/kani-fix-3300-cc3; branch fix/kani-3300-cc3; references read-only.
Research branch pulled --ff-only before work; only cc3/ staged.

Implemented actual monomorphized upvar types plus own rustc layout offsets/order,
recursive masks and current_offset; zero-size closure guard retained.
Reference masks cover slots only; by-value MU/union retains UnionAsField.
Existing aggregate setter can now obtain the supported saved-&bool upvar mask;
actual original slot/consumer/model binding is UNKNOWN pending coordinator CI.
Added3 fixtures/8 roots; changed12 future goldens without changing old Rust inputs.
Original mode sources, historical observations and8 strong oracle bindings intact.

Python/static audit13/13 PASS; existing Python oracle checker21/21 PASS.
Scratchpad rustfmt and git diff --check PASS. Rust typecheck/Kani/CBMC/CI NOT_RUN.
No local cargo/rustc/build, nested agents, push, CI or Cloud spend.
Independent semantic review PENDING_COORDINATOR; no proof/Part1 acceptance claimed.
CI-REQUEST + CI-ROOTS:35 proposed invocations/40 harness results, exact source,
roots, flags, object-bits12 and caps; request is not dispatch authorization.
Original ordinary/SimpleCheck acceptance remains UNKNOWN until execution.
Ordinary recursive Unsupported remains a release blocker; wider union support
is not added. Common-head Quick/strong suites and later gates remain outstanding.

READY 76a706f8f8c5b0471bd5c8e6b48cdaf45bab9b66
