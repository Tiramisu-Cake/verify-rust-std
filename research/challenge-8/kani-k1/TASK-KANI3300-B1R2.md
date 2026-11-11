# KANI3300 B1R2 — исправить четыре новых теста B1 (после узкого fork CI)

**Выдано координатором 2026-11-12.** `TASK-KANI3300-B1.md`/`B1R.md` в силе. Runtime **Codex**, одна стадия, **Cloud $0**.

## Факт: `Uninit Quick`, ветка `uninit-ci/b1r-resolver` (B1R `29bde289d6`), run 43108072253

Format/build/clippy PASS; kani suite 22/22 (регрессия `vec-read-init` устранена), ui/script PASS; expected 79 passed, 4 failed —
только новые тесты B1:
- `unresolved-calls/pending-ops-{plain,seeded}.rs`: ждали `indirect.safety_check.`, получено
  `Failed Checks: Interaction between raw pointers and unions is not yet supported.` — фикстура использует union, а на
  upstream `bf9c58e662` union через raw pointer не поддержан. Нужна фикстура без union (например struct/массив с
  частично инициализированным `MaybeUninit`-free storage или `u8`-буфер через raw pointer), чтобы проверялась именно
  сохранность накопленных ops перед нерезолвимым вызовом.
- `unresolved-calls/shim-{plain,seeded}.rs`: golden-блок с ` - Status: FAILURE` не совпал; получено
  `Failed Checks: Kani does not support memory initialization checks across calls to bodyless Shim instances…` и
  `Complete - 0 successfully verified harnesses, 1 failures, 1 total.` Выровнять golden по фактическому формату вывода
  (compiletest: каждая строка — подстрока; строки с `\` должны идти подряд), не ослабляя смысл проверки.

## Результат

Коммиты в `/root/kani-fix-3300-b1` поверх `29bde289d6` (только тесты; production не трогать), независимое ревью.
`kani3300/b1r2/RESULT-KANI3300-B1R2.md` (≤ 10 строк), research-коммит `[skip ci]`, push без force. Последней строкой
`B1R2 READY <sha Kani>`, стоп.

## Запреты

- Никаких сборок/dispatch/Cloud; локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка
  (`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh`) — можно.
- Raw logs/archives/credentials не читать. Никаких Actions/PR/issue/комментариев, push в Kani. Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.
