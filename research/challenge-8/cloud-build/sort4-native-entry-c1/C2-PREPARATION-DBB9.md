# C2 preparation dbb9 — fresh gates, diagnostic NOT_RUN

Build dbb9d393-e8e7-4caa-9b84-5592c17443b9; proof=infra0b26303a1d873bcd5ca3d40428fa1dcb79abf244.
Create2026-10-09T23:17:18.799751588Z, finish2026-10-09T23:23:18.372936Z; 360 Cloud seconds.
Archivec4144a11e58769c013ebcab3e681be97245d5f3f07d9ceb99f7df903ac7575f1,
711/711 archived files hash checked; complete text download integrity verified.

Fresh bounded C1 now classified PREFIX_ONLY_BOUNDED_C1_THEOREM, VF0/147 and all
six controls intended, with full source/MIR/AST/helper/dead-code/posts/leak gates.
C2 translator patchd9ac74e0 compiled, resultb33ca54a; frozen kernel/spec/library
identity checked. Explicit C2-default-off C1 regression separately VF0 with same
source/pre-AST/post-node identities. These are conditional C1 proof gates only.

ECD83 source prepared exactly and unchanged runtime3602050. Both new MIR exports
exit0; refinement0. Both decodes fail1 because runner routed TRACE stderr into
binary stdout. Original C2 AST diagnostic NOT_RUN, source mutant NOT_RUN; no C2
proof/correspondence credit. Saved polluted binaries are preserved, never stripped
or treated as valid MIR.

Independent GPT-6 Sol review confirms infrastructure-only fix: separate stderr
file for artifact stdout, raw stdout wb untouched, separate stage hashes, copied
process env PWD=cwd. Same behavior as existing stock capture run_stage. No source,
translator patch/profile/kernel/spec change. Fresh Cloud export/decode required.
Abbreviated submit rejected locally before Build,0 Cloudseconds; full SHA then used.
