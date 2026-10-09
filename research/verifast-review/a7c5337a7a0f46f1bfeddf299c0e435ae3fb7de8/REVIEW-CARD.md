# Review card — open gates

Review implementation6cb7b673 against75099c95 and final ordered profile assembly.
Kernel lifetime authority now depends on private AST tag produced only from
trusted MIR StorageLive/Dead, with original MIR span/raw local ID retained. Names
are unchanged. Examine parser inability to construct tags, ordinary CallExpr
processing, assigned-variable walkers and printers, path-local epochs and cleanup.
S-expression output omits original span; ML proof AST is provenance channel.

Evidence accepts neither raw-pointer nor lost authority separation; local reuse
negative binds MIR block7 StorageDead(tmp0=_2) before StorageLive(tmp1=_12).
Broader call audit compares identity/line event set and target operand dataflow,
not complete ordered CFG equivalence. Default in-memory exporter preprocessing
matches verifier and retains raw on-disk source hashes throughout.

Before integration: repair Rust extern contract fixture syntax using supported
frontend grammar and freshly verify reserved dead/live diverging calls, ordinary
precondition semantic negative, ordinary resource-preserving normal call and
branch/unwind paths. Current root ghost fn prototypes parse-fail atline11.
Ghost reserved-prefix rejection is separately an admission-only result. Native
C test passes but is not the Rust/MIR diverging-route qualification.
Live-local may-unwind test reaches ordinary call provenance but fails physical
points_to atline32: determine fixture versus implementation responsibility and
close both normal/unwind cleanup without weakening ownership/Drop obligations.
All full-suite/Drop/loop/reentry paths remain NOT_RUN.

For runtime extent: unit ghost size and runtime-size-result obligations fail.
Establish actual target/compiler Layout::size interpretation for storage,
pointer arithmetic/bounds/geometry; preserve specialization and ManuallyDrop
layout, including zero. Current generic positive sizeof is insufficient. No
supplied separation premise. Rerun actual only after a sound change capable of
removing its separation refusal; limited scalar result cannot replace generic
proof or true caller/comparator acceptance.

Status NOT_FOR_INTEGRATION derives from these correctness/evidence gaps,
independently of controls count and Cloud SUCCESS. Tool owner merge has not
transferred; no VeriFast receipt, fork integration or upstream approval yet.
