# KANI3300 G1R3 — repair negative/manuallydrop после G1R2A, повтор двух selectors

**Выдано координатором 2026-11-11.** Основание: `kani3300/g1r2/RESULT-KANI3300-G1R2A.md` (build `669a0594`): 18/20 PASS,
positive 63/63 SUCCESS. FAIL: aggregate negative и reject_manuallydrop_union. Runtime **Codex**, одна стадия, Cloud $0 до GO.
`TASK-KANI3300-G1.md`, правки планера, G1R/G1R2 остаются в силе. **Production не менять** (`3d085249c9`).

**Ответ на «Координатор, вопрос» из G1R2A:** дополнительных bounded counters по negative не будет; полный SUCCESS/FAILURE
negative устанавливается повторным прогоном после исправления ниже. Raw fallback по-прежнему запрещён.

## Диагноз координатора (проверить по исходнику)

- `negative/main.rs:737,747,760,772`: `std::mem::forget(union)` для `NonCopyFieldC/R` → core `mem::forget` вызывает
  `ManuallyDrop::new(union)` → G2-guard `ManuallyDrop<U>` (UnionAsField) в `ManuallyDrop::<NonCopyField*>::new`
  (`mem/manually_drop.rs:181`). Тест ловит Unsupported вместо задуманного uninit-чтения moved-from source.
- `reject_manuallydrop_union`: guard тот же и с тем же reason, но владелец свойства — `std::mem::ManuallyDrop::<U>::new`,
  а golden ждёт `reject_manuallydrop_union.unsupported_construct.`.

## Что сделать

1. Тестовым коммитом в `/root/kani-fix-3300-g1` (автор Tiramisu-Cake через `-c`, не пушить):
   - в четырёх harness заменить `std::mem::forget(union)` на `std::intrinsics::forget(union)` (как в
     `intrinsic_forget_move_source_uninit_*`; `feature(core_intrinsics)` уже есть) — или убрать forget, если union без drop
     glue; ожидание (uninit-чтение moved-from `u32`) и golden этих harness не менять. Обосновать по исходнику, что новый
     путь не попадает в G2-guard и G1 обрабатывает Move;
   - `reject_manuallydrop_union/expected`: владелец свойства → `std::mem::ManuallyDrop::<U>::new.unsupported_construct.1`
     (как наблюдалось), reason/FAILURE/summary без изменений.
2. Sweep: все G1-фикстуры на вызовы std/core, которые внутри оборачивают union в `ManuallyDrop`/иной контейнер
   (`mem::forget`, `ManuallyDrop::new`, `MaybeUninit::new`, `Option`, `ptr::read` в обёртку и т.п.) — список в
   `kani3300/g1r3/SWEEP.md` (≤ 20 строк).
3. Пакет **A3 — только два selectors**: `uninit/g1-union-pointee-negative/main.rs`,
   `uninit/g1-union-pointee-unsupported-reject_manuallydrop_union/main.rs`; build patch (production полный P1+G1 + эти
   фикстуры), applied tree, preflight, `git apply --check` на f046. `harness_timeout_minutes` ≤ 5: резерв
   `(5 + 30) × $0.0135 = $0.4725` ≤ остаток $0.476 (G1 ≤ $0.80). Пакет B не трогать.
4. Независимое ревью дельты (свой ревьюер).

## Результат

`kani3300/g1r3/`: `SWEEP.md`, `PRE-BUILD.md` (≤ 20 строк), `RUN-REQUEST.json` + патч. Коммит `[skip ci]`, push без force.
Последней строкой `PRE-BUILD REVIEW <полный research sha>`, стоп. После GO — итог с per-harness счётом negative,
насколько его даёт bounded интерфейс (иначе — native PASS/FAIL и Failed Checks из excerpt).

## Запреты

- Никаких сборок/dispatch/Cloud до GO; локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка
  (`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh`) — можно.
- Raw logs/archives/credentials не читать. Никаких Actions/PR/issue/комментариев, push в Kani-репозитории. Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.

Маркеры `PRE-BUILD REVIEW <sha>` / **KANI3300 G1R3 ПАКЕТ ГОТОВ**, одна стадия, затем стоп.
