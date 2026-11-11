# Separate uninit-checks panic
- Coordinator reports `kani-compiler` panic at `check_uninit/relevant_instruction.rs:136:73`: `internal error: entered unreachable code`.
- Seen on upstream `bf9c58e662` and with backend fix `9dddcb1134` when enabling `-Z uninit-checks` for the seven union harnesses.
- Minimal candidate input: `union U { bytes: [u8; 8], zst: [(); 2] } #[kani::proof] fn check() { let u = U { zst: [(); 2] }; unsafe { assert_eq!(u.zst.len(), 2); } }`
- Reproduction command: `kani -Z uninit-checks repro.rs`; this reduced candidate has NOT_RUN status, not an independently confirmed minimum.
- Observed input retained in commit `dc590936c5`, `tests/expected/uninit/zst-union-arm-uninit-checks/main.rs`.
- Source at line 136 rejects constant/runtime-check operands in union/reference operand handling; the triggering MIR was not inspected.
- Separate upstream union/raw-pointer uninit instrumentation limitation; excluded from this backend-only patch. No local compiler/verification run.
