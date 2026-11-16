# TASK — worker13: S1 list-инвентарь не укладывается в 600 s (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

## Факты S1-02 (run 43777127361, control `8c8ac10d67` → trigger `79542c7733`, S′ `f22f84f316`)

- Setup и сборка stock Kani 0aac — OK (215.6 s, 1.39 GiB). **P′ компилируется**: `core`, `alloc`, `std`
  и т. д. собрались, `Finished dev profile in 5m 22s` (list/stderr.log). E0599/E0369 ушли.
- Шаг «List once and run fixed S1 batch» длился ровно 600 s (23:57:04–00:07:04) → `execute(list_argv,
  timeout=MAX_ROW_SECONDS)` убит по таймауту; list/stdout.log пустой, list receipt не записан,
  все 23 строки NOT_RUN «No complete row receipt».
- `TRUNCATED.json`: в `list/target/.../build/core/<hash>/out/` лежат файлы `core-…__RNv…verify…<harness>.out`
  по ~11 MB — т. е. `kani list` на 0aac делает codegen **каждого** std harness (весь verify-std),
  а не только сбор metadata. Поэтому list по всей std не укладывается в per-root cap.
- Ledger: S1 2 из 2 израсходованы; координатор выделяет S1-03 из общего резерва пункта 2 (≤14 не меняется),
  как повтор после infra-отказов без proof-результата. S1-03 — последний; дальше только через владельца.

## Что сделать

1. По исходникам Kani 0aac (`/root/kani-upstream-ch8-s1`, read-only) установить, почему `kani list`
   для verify-std делает codegen и есть ли способ сузить его (флаги/фильтр) без потери нужных полей.
2. Выбрать минимальное изменение runner с сохранением силы binding:
   (a) отдельный list timeout (не путать с 600 s/root, R8 — это cap на root), с бюджетом job 120 мин и
   учётом ~6 мин компиляции; либо (b) отказ от глобального list в пользу per-row подтверждения
   (exact selector + PFC contract binding из export JSON строки), если export содержит нужное;
   либо (c) сужение list, если Kani это поддерживает. Обоснуй выбор фактами из исходников.
3. Runner должен писать receipt для list-фазы при любом исходе (exit/timeout/signal/elapsed/RSS,
   bounded head+tail stdout/stderr), чтобы следующая такая ошибка была видна.
4. Новый kani-host control (тот же S′ `f22f84f316`, те же 23 строки/oracles/caps на root),
   synthetic tests на новые пути, review. g0 `kani3300/ch8-s1/kani-host-list/`.
   Последней строкой `READY <control> <g0>` или `STOP <причина>`.

## Ограничения

Без push/CI/публикаций/ledger. Без локальных cargo/rustc/Kani/CBMC. Не повышать 600 s/root и 6 GiB.
