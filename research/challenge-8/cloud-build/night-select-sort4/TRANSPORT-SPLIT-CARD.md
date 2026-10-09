# Split at the unchanged Cloud input bound

The committed combined `o26-wrapper-controls` payload at infrastructure
`eb2e209d` and proof `00ccde64` was 606345 bytes, above the existing Cloud
substitution bound. The local preflight refused before reservation or dispatch;
it consumed zero Cloud seconds. No input, Git-object closure, or size limit is
relaxed.

The next `o26-wrapper-controls` recipe carries only the R2 full proof,
owner17/A1/component19 controls and their exact inputs. A separate
`o26-recovery-tests` recipe carries the changed mapped-ID CUT and AST-detail
diagnostics after its own canonical baseline. Both retain the same immutable
proof source, full target posts and independent diagnostic boundaries. Neither
lane promotes a TEST or PROBE to accepted verification; evidence from separate
Builds is reported separately and never merged into one accepted verdict.
