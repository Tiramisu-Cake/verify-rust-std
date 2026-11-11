# KANI3300 T1b-A3 — подготовка повторного trace-прогона с исправленным validator

**Выдано координатором 2026-11-11.** Основание: `kani3300/t1b-d/RESULT-KANI3300-T1B-D.md` (validator fix 6646181d23 +
f34c6316ef; записи cbf4045a не восстановимы; sidecar 254669 B при cap 256000 — вероятно PARTIAL по общему cap на один
compiler invocation для всех 9 roots). Runtime **Codex**, одна стадия, Cloud $0 до GO. T1B/T1B-R/T1B-D и правки планера в силе.

## Требования к A3

1. **Не терять evidence при отказе validator:** sidecar (≤ 256 KiB) или его bounded footer (state, emitted/omitted, coverage,
   omission_counts) сохраняется в summary/архиве **даже при INVALID**; reader по-прежнему не отдаёт записи INVALID, но
   footer/ошибки валидатора читаются через `trace-field`/`native-field`. Service/error-path tests; ревью.
2. **Чтобы ключевые записи влезли в cap:** сузить объём — по фактическим данным `seen=4477` и коду producer. Варианты
   (выбрать и обосновать): (a) меньше roots: обязательны `cmp3_index_range_len`, calibration pair и ≥ 1 контрастный SUCCESS
   root (напр. `cmp3_manually_drop_unsized_len`); (b) уже `KANI3300_TRACE_FILTER` по функциям `IndexRange::len` и шагам 1/4;
   (c) оба. Cap producer не поднимать сверх задания T1B (≤512 records/256KiB на invocation, run ≤1MiB) без обоснования.
3. **Бюджет:** остаток под cap $0.80 = **$0.5975**. Резерв `(Σtimeout + 30) × $0.0135 ≤ $0.5975`. Longest root в A2 = 31 s
   (T1a 34 s) — допустим timeout 1m (≥ 1.9× запас); иначе меньше roots. Обосновать в PRE-BUILD.md.
4. Kani diagnostic delta (989f72351c) не менять, если не найден producer-дефект; если найден — отдельный коммит + ревью +
   компиляцию проверит координатор в fork CI до GO.

## Результат

`kani3300/t1b-a3/`: `PRE-BUILD.md` (≤ 30 строк), `RUN-REQUEST-A3.json`, tooling diff/tests/review. Коммиты `[skip ci]`, push
без force. Последней строкой `PRE-BUILD REVIEW <полный research sha>`, стоп. Dispatch — только после GO координатора.

## Запреты

- Никаких Build/dispatch/Cloud до GO; локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка
  (`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh`) — можно.
- Raw logs/archives/credentials не читать, identity guard не обходить. Никаких Actions/PR/issue/комментариев, push в Kani.
  Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.
