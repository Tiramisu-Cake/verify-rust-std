# KANI3300 T1b-R — repair E0282 в diagnostic delta, compile sweep, пакет A2

**Выдано координатором 2026-11-11.** Основание: `kani3300/t1b/RESULT-KANI3300-T1B-A.md` (build `c2bec5fd`, E0282
`compiler_interface.rs:118`, все roots NOT_RUN, $0.081). Runtime **Codex**, одна стадия, Cloud $0 до GO.
`TASK-KANI3300-T1B.md` и поправки планера остаются в силе. Production CMP2 не менять.

## Что сделать

1. Коммитом в `/root/kani-fix-3300-t1` (ветка `diag/kani-3300-t1`, автор Tiramisu-Cake через `-c`, не пушить): исправить
   E0282 (`let instances: Vec<Instance> = …` или по факту типа).
2. **Полный compile sweep всей diagnostic delta** (не только строки 118): вывод типов у каждого `let` без аннотации, который
   потом используется методом; borrow/move в замыканиях; `?` в функциях без Result; неиспользуемые переменные/импорты
   (`-D warnings`); точные сигнатуры stable_mir/rustc_public по исходникам nightly-2026-10-23 (учесть G1 E0308
   `MachineSize`/`usize`). Список проверенных мест ≤ 25 строк в `kani3300/t1b-r/SWEEP.md`.
3. Независимое ревью дельты с явным фокусом «скомпилируется ли» (свой ревьюер).
4. Пакет **A2**: те же roots/recipe, что A, но бюджет: потрачено $0.081, остаток под cap $0.80 = **$0.719**. Подобрать по
   фактическим временам T1a (bounded summary) `harness_timeout_minutes` и/или число roots так, чтобы
   `(Σtimeout + 30) × $0.0135 ≤ $0.719` (напр. 9×2 → $0.648, или 7×3 → $0.6885), не теряя ключевые roots (`cmp3_index_range_len`,
   calibration pair). Обосновать в `PRE-BUILD.md`. Пакет B не трогать.
5. Новый Kani patch/applied tree/sha в `PRE-BUILD.md` (≤ 30 строк) + `RUN-REQUEST-A2.json`.

## Результат

`kani3300/t1b-r/`: `SWEEP.md`, `PRE-BUILD.md`, `RUN-REQUEST-A2.json`, патчи. Коммит `[skip ci]`, push без force.
Последней строкой `PRE-BUILD REVIEW <полный research sha>` и строкой `KANI DIAG <полный sha коммита Kani>`, стоп.
Координатор до GO проверит компиляцию diag-ветки на fork CI (бесплатно) — не запускай ничего сам.

## Запреты

- Никаких сборок/dispatch/Cloud до GO; локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка
  (`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh`) — можно.
- Raw logs/archives/credentials не читать. Никаких Actions/PR/issue/комментариев, push в Kani-репозитории. Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.
