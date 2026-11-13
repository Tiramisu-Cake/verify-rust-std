# KANI3300 X1 inputs — worker15

Issued task: `../../TASK-KANI3300-EXPORT-CLEAN.md`, 2026-11-13.
Ownership: `../../PLAN-KANI3300-FINAL-GATES-draft.md`; only the issued X1 stage is executed.
This is correctness verification. Preparation Cloud spend $0; no dispatch authorized.

- Research checkout: `/root/verify-rust-std-kani3300-g0`, branch
  `experiment/kani-k1-kani3300g0-20261111`, starting HEAD
  `df5501c9f09ddb4c3b402b8e6f17cae2166a7869`, initially clean.
- Requested `git pull --ff-only` was attempted. It failed because configured remote
  `refs/heads/experiment/kani-k1-kani3300g0-20261111` was not fetched. Local HEAD
  matches the issued pin; no reset/stash or substitute branch was used.
- Clone source: `/root/kani-fix-3300-cc5`, initially clean at exact `94c00a8859bc9e4f0f1b7db73a95dbee88f6213a`.
- Isolated clone: `/root/kani-fix-3300-x1`, branch `fix/kani-3300-x1`.
- Source base: `94c00a8859bc9e4f0f1b7db73a95dbee88f6213a`; base tree `476f0cb1679ab41a3601b11fe465c8193cbc16e9`.
- Prepared source: `c9d3b2c17afe02ceabce73692279a797c54ddd69`; tree `b9d991ff795f35924272e448d819fb424fcda254`.
- No compiler/runtime/driver/schema/shared-validator/compiletest or Rust fixture delta.
- Local validation is Python/static only. No cargo, rustc, Kani, CBMC, Miri,
  builds, push, CI, publications or raw evidence reads. Rustfmt was unnecessary:
  no Rust file changed; only the assigned scratchpad rustfmt would be allowed.

Historical copies are byte-for-byte from `94c00a8859bc9e4f0f1b7db73a95dbee88f6213a`:

| Research file | Original export path | SHA256 |
| --- | --- | --- |
| `historical/kani3300-m2bs-handoff.md` | `docs/dev/kani3300-m2bs-handoff.md` | `9b25145b90ec032175684f61e7f272424978c26e40511e0be5deff42d3499e41` |
| `historical/kani3300-m2bs2-handoff.md` | `docs/dev/kani3300-m2bs2-handoff.md` | `86f0f8a002e90d44fc9b52aa80920a32225c7acbc7b284ae48ddad7b5547941f` |

`historical/oracles-provenance.json` preserves the original manifest SHA256,
old source base/qualification statement and each case's historical evidence
artifacts/selectors/hashes and semantic-qualification status. These are historical
source-reported records; no historical commit/result or proof credit was changed.
