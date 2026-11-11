# KANI3300 G1R2 — repair тестов после G1RA, повтор пакета A

**Выдано координатором 2026-11-11.** Основание: `kani3300/g1r/RESULT-KANI3300-G1RA.md` (build `8b32494f`): production Kani
и compiletest собрались; 15 PASS, 5 FAIL — все из-за тестов. Runtime **Codex**, одна стадия, Cloud $0 до GO.
`TASK-KANI3300-G1.md`, правки планера и G1R остаются в силе. **Production не менять** (кандидат `3d085249c9`).

## Что сделать

1. В `/root/kani-fix-3300-g1` отдельным тестовым коммитом (автор Tiramisu-Cake через `-c`, не пушить) исправить:
   - `g1-union-pointee-positive/main.rs:565,580`, `g1-union-pointee-negative/main.rs:665,680` — E0133 (`holder.ptr` вне `unsafe`);
   - `reject_manuallydrop_union/main.rs:13` — deny-lint `dangerous_implicit_autorefs` (явный `&*`/`(*ptr)` или иное — так,
     чтобы тест по-прежнему доходил до **того же** guard и давал его Unsupported);
   - `reject_union_transmute/main.rs:10` — E0422 `TransmuteU` вне области видимости;
   - `reject_init_predicate` — golden: фактическое свойство `kani::mem::is_initialized::<U>.unsupported_construct.1`
     (локация `library/kani/src/lib.rs:63`). Обновить golden, только если это тот самый задуманный guard (обосновать по
     исходнику, файл:строка); иначе — исправить фикстуру.
   Семантику проверок не ослаблять; ожидания TEST-MANIFEST для 63/70 harness не менять, кроме связанных с этими строками.
2. **Тестовый компиляционный sweep** всех G1-фикстур (rustc не запускать): unsafe-контексты (edition фикстур, union field
   read, raw deref, `unsafe_op_in_unsafe_fn`), deny-by-default lints на nightly-2026-10-23, имена/импорты/`use`, типы,
   unused (warnings не фатальны, но проверить `#![deny]`), golden-строки свойств против фактического именования
   (по образцу reject_init_predicate). Итог — `kani3300/g1r2/TEST-SWEEP.md` (≤ 40 строк).
3. Пересобрать **только пакет A** (те же 20 selectors): патч, applied tree, preflight, `git apply --check` на f046.
   `harness_timeout_minutes` ≤ 16: резерв `(16 + 30) × $0.0135 = $0.621` ≤ остаток $0.6245 (G1 ≤ $0.80 суммарно).
   Пакет B не трогать (отдельный GO владельца).
4. Независимое ревью дельты тестов + sweep (свой ревьюер).

## Результат

`kani3300/g1r2/`: `TEST-SWEEP.md`, `PRE-BUILD.md` (≤ 25 строк: Kani SHA, дельта по файлам, identities A, резерв),
`RUN-REQUEST.json` + патч. Коммит `[skip ci]`, push без force. Последней строкой `PRE-BUILD REVIEW <полный research sha>`, стоп.

## Запреты

- Никаких сборок/dispatch/Cloud до GO; локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка
  (`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh`) — можно.
- Raw logs/archives/credentials не читать. Никаких Actions/PR/issue/комментариев, push в Kani-репозитории. Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.

Маркеры `PRE-BUILD REVIEW <sha>` / **KANI3300 G1R2 ПАКЕТ ГОТОВ**, одна стадия, затем стоп.
