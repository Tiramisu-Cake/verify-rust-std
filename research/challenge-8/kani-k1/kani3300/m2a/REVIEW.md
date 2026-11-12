# M2-A bounded independent review — PASS (static only)

- Reviewer: one GPT-6 Luna, HIGH, fork_turns=none; no nested delegation. Scope: valid inputs, source type/signature audit, exact root/mode axes and obligation ledger; no repeated model audit.
- Reviewed preparation commit: `56fcd2abdb3b563be8e23a9b4896f566e5cd8ef3` against `9226f9a9ea42bd35a69902a56ad70a2079a7e8ca`. Final amend updates only this receipt and the review-status sentence in RESULT; reviewed payload hashes below remain identical.
- Generated smallsort-session packet SHA256: `23b2a593e069a3b9a3fefaf420c1398e0f92415850c6dc4f7d3c50842644533f`; spec SHA256: `7e49b8ea1395746c513596e5a5914f658aac60e5527c20df5a770cb1c205cf95`. Packet held locally at /tmp/kani3300-m2a-review-packet; hashes below bind the published reviewed payload without depending on that temporary directory.
- Findings: no blocking source-level issue. Explicit u8/usize operand and API-flow inspection passed, including scalar ensures first payload read; primary Rust snapshot hashes match INPUTS. This is not compilation confirmation.
- Exact filter namespace, compiler forwarding, ordinary Assert / no-assert Original / PFC SimpleCheck precedence, undecorated axis and only-codegen-before-verifier checked against pinned Kani source.
- Six configurations maximum, sequential; two inventories before conditional solver queue, no jobs flag, no disabled checks/bounds. Resource enforcement remains UNRESOLVED and blocks solver admission until coordinator receipt.
- All six original M2 roots and 41 inherited obligations retained and unresolved; scalar/mode reductions earn no original combined credit. Coordinator-reported versus independent facts remain distinguished.
- No cargo/rustc/Kani/CBMC/Miri/rustfmt/build/CI/Actions/Cloud execution; no raw logs/archives; compilation/verifier NOT_RUN, proof credit NONE.

## Reviewed payload SHA256

| Path relative to package | SHA256 |
| --- | --- |
| CI-REQUEST.md | dee33105dab63fe652ccfac582d038eb901f272ec21487e8a07dd71e10bc6bee |
| INPUTS.json | 13335baeeecb58d45fd87097472e963e7aa82e54dd1f58b532e92d7d08bd2300 |
| MINIMIZATION-LEDGER.md | 3c90e79adebea047788d7343d68d4f734c7eb69868bbe74b759c70ed84e6a885 |
| SITE-MAP.md | 1aa80f58ccc44b6833f03ee6eaa6a6d4eca64513d006f3b8ce15114602b59438 |
| TEST-MANIFEST.json | 369a31c2ad447dac21b094be091b203b1e3dcc0dfb7377e757cf1b66b41a8ee3 |
| cases/ordinary-singleton.rs | 99014f12f17699d257b9ddd44a4de05d24ca5c375863b0505b02f298a97c1bb4 |
| cases/scalar-pfc-hole.rs | 61fc369a6830c6ff185887b04db36139ca529e4de097c0025ce7b29c8323f759 |
| cases/scalar-pfc-legal.rs | fe05e646b2ccc9188d073b78b30abecd59eb877b6298abfcdfc8a27aeb3a260b |
| cases/undecorated-singleton.rs | f40a3bac0cb2847bd7e17b3cb747210efe0b437b7e3bcf8977e8e39721e9a715 |

## Main-agent static validation receipt

Exact read-only Kani commit/tree and clean worktree verified. Four original source/golden pairs match both working files and pinned git objects; source-rule and reference-document SHA256 match INPUTS. Each of four drafts has exactly one root; faithful singleton and undecorated derivations checked as exact string deltas, scalar hole byte-identical to original. Manifest JSON/argv/config count/hash consistency, 41+6 ledger IDs, research-only commit scope, result ≤25 lines and git diff --check passed. Compiler/lints/format-tool outcomes NOT_RUN; no new proof result. No post-review semantic delta.
