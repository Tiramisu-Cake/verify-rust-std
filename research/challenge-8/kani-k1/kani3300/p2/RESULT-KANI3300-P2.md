# RESULT-KANI3300-P2 — KANI3300 P2 ЗАВЕРШЁН
Kani `657c2b24516b967f67ce71994299d0ef328aede9`; main `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`; 37 files changed, 1267 insertions(+), 178 deletions(-). Fetch/rebase: main не изменился, up to date, конфликтов нет; ровно один коммит; Kani не pushed.
Статика PASS: rustfmt wrapper --check --edition 2024 + rustfmt.toml (22 .rs), лицензии 15/15 новых .rs (goldens — output patterns как у соседей), git diff --check, internal-marker/reference scans, author/committer. Cloud $0; clippy/build/Kani NOT_RUN.
Кроме git mv: только две замены пути в contract-frame/expected, необходимые для нового имени; все 15 main.rs и остальные goldens побайтно прежние. Production 7/7 byte-equal; PRODUCTION-BEFORE-AFTER.diff пуст, RANGE-DIFF.txt приложен.
frame-negative: 120.548 с — историческое время selector без разбивки; вероятны DFCC + shadow argument/return paths, точный bottleneck UNKNOWN. Безопасное сокращение coverage статически не установлено; тест не менялся. Предложение: phase timings, затем solver-only comparison при прежних checks; FRAME-NEGATIVE.md.
| Старый каталог | Новый каталог |
|---|---|
| `maybe-uninit-buffer-u3-clause-pfc-negative` | `maybe-uninit-contract-clause` |
| `maybe-uninit-buffer-u3-frame-negative` | `maybe-uninit-contract-frame` |
| `maybe-uninit-buffer-u3-plain-negative` | `maybe-uninit-argument-buffer` |
| `maybe-uninit-review-argument-return` | `maybe-uninit-argument-return` |
| `maybe-uninit-review-overlap-copy` | `maybe-uninit-overlap-copy` |
| `maybe-uninit-review-overwrite-copy` | `maybe-uninit-overwrite-copy` |
| `maybe-uninit-review-positive` | `maybe-uninit-transfers` |
| `maybe-uninit-review-repeat-local` | `maybe-uninit-repeat-local` |
| `maybe-uninit-review-reset-zst` | `maybe-uninit-reset-zst` |
| `maybe-uninit-wrap-u3-padding` | `maybe-uninit-transmute-padding` |
| `maybe-uninit-wrap-u3-positive` | `maybe-uninit-transmute` |
| `maybe-uninit-wrap-u3-source-read` | `maybe-uninit-transmute-source-read` |
Commit title: `Preserve MaybeUninit storage initialization across pointer and value transfers`; body (8 строк):
```text
Track MaybeUninit byte initialization through raw pointer reads, writes and copies.
Support exact transmute conversions, flat slot arrays/slices and static repeats.
Preserve shadow state across ordinary MIR arguments and normal returns.
Keep typed payload reads, padding and uninitialized-byte checks intact.
Nested/arbitrary unions and compound slot storage remain Unsupported.
typed_swap, select_unpredictable and function-pointer/no-MIR transfers remain Unsupported.
Add positive and negative regressions in tests/expected/uninit.
Refs #3300
```
