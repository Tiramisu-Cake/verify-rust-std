# C02 candidate review

**Decision: GO for C02 preparation only.** No concrete localized correctness finding was identified in the reviewed delta. This is not proof acceptance or proof credit.

## Reviewed identities

- Baseline: `64ec781bc119279ccc4365aa831d2a9d0a792fee` (tree `33e95dc779cefde33132f8e265d9588b9d905b14`)
- Candidate: `af49c7ef04d462f5f89b4b3d362b484b1d3f20d0` (tree `e10c359aba4830016105bb7e8a8b95544e4c3664`); candidate checkout was clean and at this commit.
- Review spec SHA256: `102c473161613da6fcc0a30380a8b187fb528b7f5fd81b4fa7ac83f2501ee31d`
- Review packet check: `PACKET_VALID_NOT_REVIEWED`, packet SHA256 `6bec2cd2ee2041c3554239366cbcd32d0af4637161af180309d511795eb03ae3`; expected candidate and spec matched.
- Source dependency: `597e54c5cb503955f9483edc6acc9d4752d57713`, tree `b3bd6d8c939e08b13fc7a4c6c9da694cc8a2aa97`. Its range from `d073585946093071b696eada41b8c8cac18362a7` changes only the two merge harness unwind attributes from 8 to 17. The pinned source-file SHA matches `CI-REQUEST.json`.

## Findings

- **No concrete findings.** The source-side check binds the pinned harness IDs to a single matching `proof_for_contract`/`unwind` attribute pair, checks source file and line, requires the imported helper and exact bare `bidirectional_merge` token path, and separately requires the fully qualified request target and unwind 17. `_target_tokens` compares complete Rust path tokens, so an arbitrary matching terminal segment does not satisfy target binding.
- The candidate selects only `c_merge_source_write_restore` and `c_merge_source_read_only`, both at unwind 17. Their failure matcher remains the strict `assigns` class, anchored description regex, and exact declared file/line locations; nonmatching failures still produce `UNKNOWN`.
- The package group is 2,100 seconds (900 compile + two 600-second rows). The 112-minute run-step and 150-minute job ceilings remain intact. Existing missing/partial/null/wrong-shape, timeout, inventory, coverage, and `NOT_RUN` handling remains strict and unknown-preserving.
- The declared source-label-to-generated-cover-ID and callback-write-to-`ptr.rs` frame bindings remain unresolved limitations; the candidate does not claim to establish them or independent MIR symbol resolution.

## Validation

- `python3 -m unittest test_runner test_package` from `ch8-c-control`: **36 tests passed**.
- Static `git diff --check` between baseline and candidate: clean.
- No Rust, Kani, or CBMC was run; no CI, push, publication, or ledger action was performed.

C02 rows remain `NOT_RUN`; runtime result is **UNKNOWN**, and proof credit remains **NONE**. The GO above covers preparation only.
