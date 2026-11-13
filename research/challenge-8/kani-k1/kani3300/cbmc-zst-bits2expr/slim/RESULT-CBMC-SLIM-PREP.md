# CBMC-SLIM preparation — worker15
Date: 2026-11-13. Status: PREPARED / NOT_ISSUED / NOT_RUN.
Research input: df3a3f15f585f7fa34f47f6374b830a9d41af2c1; pull --ff-only up to date.
BASE: 37a17adc07f29e1127f100debf1d8eea00532a24 (fetch origin develop; unchanged tip).
Clean source: fb9c8d53d4f5e109324d8b17fd8794ed4776b43e
Source tree: 038a4b47e21ce8d5ebfcb29124d830fd38688235
Source branch: fix/array-zero-width-elements-slim; sole parent BASE.
Source allowlist: exactly production cpp, existing unit cpp, new main.c/test.desc.
Production delta: array > becomes >=; has_value and all other guards retained.
Regression: exact audit §3 GNU empty struct/memset/typed read; one descriptor.
Unit: three unchanged case bodies after bit-order case; tags [core][util].
Make/CMake already register simplify_expr.cpp; build files unchanged.
Baseline overlay tree: 73d8992542645f35d70763ac0be0b03acb0dd26d
Test-only patch SHA256: c788e7bddbaf0aee957087d41ae8d657652d2bbb88acf371c47faf9759e84c90
Apply exported patches with --unidiff-zero; test-only overlay adds --index.
CI-only: b7f9d36ff2edf1b795b2273635872a57fd244ca1
CI tree: 4465ca1ffee74550c35cf0bf9ad982b1f654bf0f
CI branch: ci/array-zero-width-elements-slim-20261113; sole parent clean source.
CI: inherited workflow paths removed, one bounded fork-only push workflow.
Prepared scope: baseline5/fix5 focused profiles, Make4/CMake4 console cases.
Exact binary paths/allowlists/hashes: TEST-MANIFEST.json, CI-MANIFEST.json.
Static checks: pins/trees/bytes/API/registration/AST/YAML/diff checks PASS.
Project cpplint: PASS, 0 errors; Python deprecation warnings only.
Synthetic service checks: 9/9 PASS; no compiler/CBMC/solver execution.
Independent Luna HIGH review: no findings; see REVIEW.md.
Builds, executable selection, verdicts and formatter18.1.8: NOT_RUN.
PR draft: matched baseline fields/Testing pending; template/disclosure retained.
Separate Kani B3 comment/workaround/replay handoff: PR-READINESS.md; code unchanged.
Push/CI/Cloud/upstream actions: NOT_RUN; Cloud $0; old evidence untouched.
Coordinator next: approve caps/GO, push exact CI-only SHA to fork, execute narrow CI.
Preparation is not upstream-ready and grants no B1/B2/Kani proof credit.
READY fb9c8d53d4f5e109324d8b17fd8794ed4776b43e
