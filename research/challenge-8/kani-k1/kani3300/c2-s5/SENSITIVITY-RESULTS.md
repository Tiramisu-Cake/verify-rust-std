# S5 sensitivity results

Prepared four independent CI-only/test-only overlays, all outside export. Exact source/patch
hashes and native compiletest selectors/argv are in SENSITIVITY-MANIFEST.json.
All four `git apply --check` checks pass against the final source files. No patch was
applied to export. No verifier, compiler, build or native compiletest was run locally.
Observed native verdict/N and actual compiletest exits remain NOT_RUN.

Positive removal retains legal behavior but deletes the own outside41 assertion required
by the strengthened SUCCESS-block oracle; the old verdict-only sibling would miss it.
Extra-failure variant retains original reached outside-assigns failure and adds an independent
root assertion; summary must reject N=2, regardless of original FAILED descriptions.
Repair removes only forbidden user write, retaining initialized read and permitted out-write;
expected intended failure/N=1 must reject SUCCESS/N=0. Golden sanity inverts required check
count0→1 in a temporary copy, with native result unchanged. Native CI must confirm all predictions;
setup errors, timeouts, early unrelated Unsupported or missing original failures are invalid.

Final candidate pinned: 6d2e9ae621310605eda4b0c9572d34d9a7ff948d, tree 6a8f2b2e11780445451640eaba8b6a7076686896; source files match previously checked patch input hashes. No new native execution.

CI43636027466 mutation attempt INVALID/skipped (not detection). Corrected source 8d67298c48eb7b2381f806a6353433d1440e3d94; all4 patches/inputs unchanged and applicable. --force-rerun already specified; valid native outcomes remain NOT_RUN.
