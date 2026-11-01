# ARRAYREPRO — PRE-BUILD REVIEW (CI NOT_RUN)
Pin Kani: `9461e07af7ec929f050aa4192f29363c9be07779` (nightly-2026-10-12).
Main snapshot: `744b3e84d6eb68fd5456826997568666791bd355` (nightly-2026-10-23).
Main HEAD and both upstream toolchain files checked 2026-11-01 before GO.
Actual Kani/rustc/CBMC versions: UNKNOWN until source build and artifacts.
| Harness | Pin status / failed checks / covers | Main status / failed checks / covers |
|---|---|---|
| D1 [u8;1] | NOT_RUN / UNKNOWN / UNKNOWN | NOT_RUN / UNKNOWN / UNKNOWN |
| D2 u8 | NOT_RUN / UNKNOWN / UNKNOWN | NOT_RUN / UNKNOWN / UNKNOWN |
| F2 if | NOT_RUN / UNKNOWN / UNKNOWN | NOT_RUN / UNKNOWN / UNKNOWN |
| F5 symbolic indices | NOT_RUN / UNKNOWN / UNKNOWN | NOT_RUN / UNKNOWN / UNKNOWN |
| F7 [1]/[2] | NOT_RUN / UNKNOWN / UNKNOWN | NOT_RUN / UNKNOWN / UNKNOWN |
| W observed | NOT_RUN / UNKNOWN / UNKNOWN | NOT_RUN / UNKNOWN / UNKNOWN |
| C-other | NOT_RUN / UNKNOWN / UNKNOWN | NOT_RUN / UNKNOWN / UNKNOWN |
| C-neither | NOT_RUN / UNKNOWN / UNKNOWN | NOT_RUN / UNKNOWN / UNKNOWN |
D1 playback inputs: UNKNOWN; print exports `any` inputs, not `got`.
W playback inputs/observed byte: UNKNOWN; preservation of D1 value failure UNKNOWN.
D1 cadical vs minisat: UNKNOWN; CLI support/results pending.
Standalone reproduction and main behavior: UNKNOWN; CI awaits coordinator GO.
A standalone PASS would not override in-tree FAILED; sysroots differ.
Allowed passing-main wording: «не воспроизводится в указанной конфигурации main».
No push, dispatch, source build or proof run performed in this preparation.
