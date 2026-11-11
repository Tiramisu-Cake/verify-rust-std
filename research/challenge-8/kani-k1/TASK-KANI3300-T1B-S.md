# KANI3300 T1b-S — статический разбор cache/DelayedUbPass + компактный producer + пакет C (5 roots)

**Выдано координатором 2026-11-11.** Рамки — планер: `kani3300/t1b-s/PLANNER-T1B-A3-ANSWER.md` (прочитать целиком, п.1–7
обязательны). Основание: `kani3300/t1b-a3/RESULT-KANI3300-T1B-A3.md`. Runtime **Codex**, одна стадия, Cloud $0 до GO.

## Что сделать

1. **Статика (п.2 планера):** `compiler_interface::codegen_items`, `BodyTransformation::body_ref/cache`,
   `DelayedUbPass::transform`, `GotocCtx::codegen_function` (Kani pin f046 + CMP2). Где кончается инвариантная локальная
   трансформация, кто и когда переписывает cache, когда пересчитывается reachability, какой body фактически идёт в GOTO
   emission каждого root. Итог — `kani3300/t1b-s/STATIC.md` (≤ 40 строк, ссылки файл:строка) + design исправления
   (свежий transformer на root либо pristine local cache + root-scoped overlay до конца emission) — только design,
   production repair не делать.
2. **Компактный producer (п.3):** отдельный минимальный диагностический коммит в `/root/kani-fix-3300-t1` поверх 989f72351c:
   убрать payload calibration/adapter и повторные неизменные MIR dumps, агрегировать zero_ops; обязательно —
   header unit/stubs/actual order, writer→body hash→consumer, targets/witness, ops и **presence/used-body hash в момент
   GOTO emission** для failing root и passing contrast. Semantic ops/cache traversal не менять; cap 256000 B не поднимать.
   Ревью + tests; компиляцию проверит координатор в fork CI до GO.
3. **Пакет C (п.4–5):** roots `cmp3_into_iter_next`, `cmp3_index_range_len`, `cmp3_manually_drop_unsized_len`,
   `pincheck_calibration_uninit_read_u8`, `pincheck_calibration_init_read_u8`; один invocation; timeout 1m каждому;
   фильтры `IndexRange::len`, `cmp3_index_range_len`, `cmp3_manually_drop_unsized_len`. Резерв (5×1+30)×$0.0135 =
   **$0.4725 ≤ $0.476**; подтвердить envelope/ledger без добавочного overhead. Library 919cc3e2, CMP2 неизменны.
   Оценить по A3 (seen/emitted, размеры записей), что компактный producer уложит ключевые записи в cap — расчёт в PRE-BUILD.
4. **Стоп-условие (п.7):** если компактный trace требует существенной переделки или envelope не помещается — остановиться
   на STATIC.md, пакет не готовить, бюджет сохранить.

## Результат

`kani3300/t1b-s/`: `STATIC.md`, при п.2–3 — `PRE-BUILD.md` (≤ 30 строк), `RUN-REQUEST-C.json`, diff/tests/review.
Коммиты `[skip ci]`, push без force. Последней строкой `PRE-BUILD REVIEW <research sha>` и `KANI DIAG <sha Kani>`, либо
`T1B-S STATIC ONLY <research sha>`; стоп.

## Запреты

- Никаких Build/dispatch/Cloud; локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка
  (`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh`, `--config-path rustfmt.toml`) — можно.
- Raw logs/archives/credentials не читать, identity guard не обходить. Никаких Actions/PR/issue/комментариев, push в Kani.
  Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.
