# KANI3300 B3R — ZST backend fix: тесты под upstream + черновик PR (ремонт, круг 1 из 2)

**Выдано координатором 2026-11-12 (ночь).** `TASK-KANI3300-B3.md` в силе. Runtime **Codex**, одна стадия, **Cloud $0**.
Kani: `/root/kani-fix-zst-b3`, ветка `fix/zst-union-codegen` (тесты `dc590936c5`, фикс `9dddcb1134` на upstream `bf9c58e662`).

## Факт: узкий fork CI

- Тесты на чистом upstream (run 43115481098): `zst-union-arm-no-checks` (**без** `-Z uninit-checks`) —
  `zst_arm_at_nonzero_offset`, `padded_typed_copy_rust`, `padded_typed_copy_c`, `array_typed_copy` →
  **CBMC failed with status 134**; `zst_array_indexing`, `all_zst_union`, `aligned_zst_typed_copy` → SUCCESS.
  ⇒ abort — существующий backend-баг Kani, не связанный с uninit-checks.
- С фиксом (run 43115485052): `zst-union-arm-no-checks` — **PASS** (все 7).
- `zst-union-arm-uninit-checks` и на base, и с фиксом: **kani-compiler panic** `relevant_instruction.rs:136:73: internal
  error: entered unreachable code` — отдельная upstream-проблема uninit-checks с union (на upstream union+raw pointer не
  поддержаны); к backend-фиксу не относится.

## Что сделать

1. Убрать `zst-union-arm-uninit-checks` из этой ветки (PR — только backend). Записать находку о панике
   (`relevant_instruction.rs:136`, минимальный вход, upstream `bf9c58e662`) в `kani3300/b3r/PANIC-NOTE.md` (≤ 10 строк).
2. Тесты ZST оформить для upstream: лучше в `tests/kani/` или `tests/expected/` по конвенции Kani для backend-регрессий
   (без `uninit` в пути допустимо — координатор проверит полным CI); имена/комментарии нейтральные. Сохранить все 7 форм.
3. Черновик описания upstream PR `kani3300/b3r/PR-DRAFT.md`: что ломалось (CBMC abort 134 на union с ZST-array arm при
   typed copy, воспроизведение без uninit-checks), причина в codegen (padded union wrapper, zero-width member), фикс,
   тесты. Последняя строка — `*Disclosure: this change and description were prepared with AI assistance.*`. Без ссылок на
   сторонние PR, без «Part 1», без внутренних путей/ID. Это только файл — публикует владелец.
4. rustfmt `--config-path rustfmt.toml`, diff --check, независимое ревью.

## Результат

Коммиты в `/root/kani-fix-zst-b3` (не пушить), research `[skip ci]`, push без force; `RESULT-KANI3300-B3R.md` (≤ 10 строк).
Последней строкой `B3R READY <sha Kani>`, стоп.

## Запреты

- Никаких сборок/dispatch/Cloud; локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка
  (`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh`) — можно.
- Raw logs/archives/credentials не читать. Никаких Actions/PR/issue/комментариев, push в Kani. Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.
